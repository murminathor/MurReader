#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys, string, gzip, os

import types
import formatter, htmllib
try:
    from cStringIO import StringIO
except ImportError:
    from StringIO import StringIO
import base64

import zipfile
import tempfile

import miscutils, bookmarks, config, detectcharset, filters
## from bookmarks import Book
## from miscutils import zip_get_filename
## from config import default_description_length, default_encoding, preview_length
## from detectcharset import detectcharset
## import filters

##----------------------------------------------------------------------

def get_file(filename):
    if zipfile.is_zipfile(filename): #filename.endswith('.zip'):
        fn = tempfile.mktemp()
        zip_fn = miscutils.zip_get_filename(filename)
        open(fn, 'w').write(zipfile.ZipFile(filename).read(zip_fn))
    else:
        fn = filename

    return fn


##----------------------------------------------------------------------
##----------------------------------------------------------------------

class basic_parser:
    def new_book(self, filename):
        """Create new book object"""
        pass
    def load_file(self, buffer, book):
        """Load file in buffer"""
        pass
    def preview(self, buffer, book, offset):
        """Create preview: load part of file in buffer"""
        pass

##----------------------------------------------------------------------
##----------------------------------------------------------------------


class plain_text_parser:

##----------------------------------------------------------------------

    def new_book(self, filename, category=None, external_filter=None, encoding=None):
        """Create new book object"""

        book = bookmarks.Book()
        book.filename = filename

        if external_filter:
            book.externalfilter = external_filter
            if not encoding:
                fileobj = StringIO(self._read_from_pipe(filename, external_filter))
                encoding = detectcharset.detectcharset(fileobj)
        else:
            fn = get_file(filename)
            fileobj = open(fn)
            encoding = detectcharset.detectcharset(fileobj)
            if fn != filename: os.remove(fn)

        if encoding:
            book.encoding = encoding
        else:
            book.encoding = config.default_encoding

        book.file_type = 'plain_text'
        book.description = self.book_description(book)
        if category:
            book.categories = [category]


        return book

    def get_content(self):
        return []

##----------------------------------------------------------------------

    def load_file(self, buffer, book, bookmarks):
        """Load file in buffer"""

        data = self._read_file(filename=book.filename,
                               int_filters=book.internalfilters,
                               ext_filter=book.externalfilter,
                               charset=book.encoding, bookmarks=bookmarks)

        buffer.set_text(data)

##----------------------------------------------------------------------

    def preview(self, buffer, book, offset):
        """Create preview: load part of file in buffer"""

        data = self._read_file(filename=book.filename,
                               offset=offset, length=config.preview_length,
                               charset=book.encoding,
                               int_filters=book.internalfilters,
                               ext_filter=book.externalfilter)

        buffer.set_text(data)

##----------------------------------------------------------------------

    def binary_content(self, filename, cover_only=False):
        return []

##----------------------------------------------------------------------

    def _read_from_pipe(self, filename, command):

        fn = get_file(filename)

        if command.find('%s') > 0:
            command = command % ('"' + fn + '"')
        else:
            command = command + ' ' + fn
        stdin, stdout, stderr = os.popen3(command)
        data = stdout.read()
        err = stderr.read()
        if err:
            raise IOError, err
            #error_dialog(None, '', err)

        if fn != filename: os.remove(fn)

        return data

##----------------------------------------------------------------------

    def _read_file(self, filename, charset, offset=None, length=None,
                   int_filters=None, ext_filter=None, bookmarks=None):


        if ext_filter:
            data = self._read_from_pipe(filename, ext_filter)

            #pipe = os.popen(command)
            #data = pipe.read()
            #pipe.close()

        else:

            fn = get_file(filename)
            fd = open(fn)
            data = fd.read()
            fd.close()
            if fn != filename: os.remove(fn)

        data = self._get_slice(data, charset, offset, length,
                               int_filters, bookmarks)


        return data

##----------------------------------------------------------------------
    # FIXME: rename
    def _get_slice(self, data, charset, offset=None, length=None,
                   int_filters=None, bookmarks=None):

        # delete invalid (\0) chars
        tbl = string.maketrans('', '')
        data = string.translate(data, tbl, '\0')

        data = unicode(data, charset, 'replace')
        if offset or length:
            if offset:
                data = data[offset:]
            if length:
                data = data[:length]
        data = data.encode('utf-8')

        if int_filters:
            for fltr in int_filters:
                func = getattr(filters, fltr)
                data = func(data, bookmarks=bookmarks)

        return data

##----------------------------------------------------------------------

    def book_description(self, book):
        """Create description of book"""

        data = self._read_file(filename=book.filename, charset=book.encoding,
                               length=config.default_description_length,
                               ext_filter=book.externalfilter)

        data += ' ...'

        return data

##----------------------------------------------------------------------
##----------------------------------------------------------------------

class gzipped_plain_text_parser(plain_text_parser):

    def _read_file(self, filename, charset, offset=None, length=None,
                   int_filters=None, ext_filter=None, bookmarks=None):

        fd = gzip.open(filename)
        data = fd.read()
        fd.close()

        data = self._get_slice(data, charset, offset, length,
                               int_filters, bookmarks)

        return data

##----------------------------------------------------------------------

    def new_book(self, filename, category=None,
                 external_filter=None, encoding=None):
        """Create new book object"""

        book = bookmarks.Book()
        book.filename = filename

        fileobj = gzip.open(filename)
        encoding = detectcharset.detectcharset(fileobj)
        if encoding:
            book.encoding = encoding
        else:
            book.encoding = config.default_encoding

        book.file_type = 'gzipped_plain_text'
        book.description = self.book_description(book)
        if category:
            book.categories=[category]

        return book

##----------------------------------------------------------------------
##----------------------------------------------------------------------

class MyDumbWriter(formatter.NullWriter):

    def __init__(self):

        self.data = []

        self.bookmarks = []
        self.current_bookmark = 0

        self.styles = []
        self.current_italic = 0
        self.current_bold = 0

        self.index = 0
        formatter.NullWriter.__init__(self)

    def send_paragraph(self, blankline):
        s = '\n'*blankline
        self.data.append(s)
        self.index += len(s)

    def send_line_break(self):
        self.data.append('\n')
        self.index += 1

    def send_hor_rule(self, *args, **kw):
        self.data.append('\n')
        #self.data.append('\n')
        self.index += 1

    def send_literal_data(self, data):
        self.data.append(data)
        self.index += len(data)

    def send_flowing_data(self, data):
        if not data: return
        self.data.append(data)
        self.index += len(data)

    def new_font(self, font):
        # font = (size, italic, bold, teletype)
        # add headers (<h1> <h2> ... ) to bookmarks
        if font:

            if font[0]: # begin of header
                self.current_bookmark_offset = self.index
                self.current_bookmark = 1
            if font[1]: # italic
                self.current_italic_offset = self.index
                self.current_italic = 1
            if font[2]: # bold
                self.current_bold_offset = self.index
                self.current_bold = 1

            return

        if self.current_bookmark: # end of header
            self.current_bookmark = 0
            self.bookmarks.append((self.current_bookmark_offset, self.index))

        if self.current_italic:
            self.current_italic = 0
            self.styles.append((self.current_italic_offset, self.index, 'italic'))

        if self.current_bold:
            self.current_bold = 0
            self.styles.append((self.current_bold_offset, self.index, 'bold'))


##----------------------------------------------------------------------

class MyHTMLParser(htmllib.HTMLParser):
    def __init__(self, formatter):
        htmllib.HTMLParser.__init__(self, formatter)
        self.anchor_list_offset = []

    def anchor_bgn(self, href, name, type):
        self.anchor = href
        if self.anchor:
            self.anchorlist.append(href)

    def anchor_end(self):
        if self.anchor:
            self.handle_data("[%d]" % len(self.anchorlist))
            self.anchor = None

##----------------------------------------------------------------------
##----------------------------------------------------------------------

class html_parser(plain_text_parser):

    def new_book(self, filename, category=None, external_filter=None, encoding=None):
        """Create new book object"""

        book = bookmarks.Book()
        book.filename = filename

        fn = get_file(filename)

        if external_filter:
            book.externalfilter = external_filter
            fileobj = StringIO(self._read_from_pipe(fn, external_filter))
            if not encoding:
                encoding = detectcharset.detectcharset(fileobj)
        else:
            fileobj = open(fn)
            encoding = detectcharset.detectcharset(fileobj)

        if encoding:
            book.encoding = encoding
        else:
            encoding = book.encoding = config.default_encoding

        book.file_type = 'html'
        book.description = self.book_description(book)
        if category:
            book.categories = [category]

        ret = self._html_new_book(fileobj, book, encoding)
        if fn != filename: os.remove(fn)
        return ret

##----------------------------------------------------------------------

    def _html_new_book(self, fileobj, book, encoding):

        fileobj.seek(0)
        ex = fileobj.read()
        w = MyDumbWriter()
        h = htmllib.HTMLParser(formatter.AbstractFormatter(w))
        h.feed(ex)
        data = ''.join(w.data)
        if h.title:
            book.name = unicode(h.title, encoding, 'replace').encode('utf-8')

        text_len = len(data)
        data = unicode(data, encoding, 'replace')

##         for bm in w.bookmarks:
##             desc = data[bm[0]:bm[1]]
##             desc = desc.encode('utf-8')
##             book.add_bookmark(float(bm[0])/text_len, bm[0], bm[1]-bm[0], desc)

        return book

##----------------------------------------------------------------------

    def _read_file(self, filename, charset, offset=None, length=None,
                   int_filters=None, ext_filter=None, bookmarks=None):

        if ext_filter:
            data = self._read_from_pipe(filename, ext_filter)
        else:
            fn = get_file(filename)
            data = open(fn).read()
            #print '--->', fn
            if fn != filename: os.remove(fn)

        ret = self._parse_html(data, charset, offset, length,
                               int_filters, ext_filter, bookmarks)

        return ret

#----------------------------------------------------------------------

    def _parse_html(self, ex, charset, offset, length,
                    int_filters, ext_filter, bookmarks):

        w = MyDumbWriter()
        h = htmllib.HTMLParser(formatter.AbstractFormatter(w))
        h.feed(ex)
        self._writer = w
        data = string.join(w.data, '')
        if len(h.anchorlist) > 0:
            # add links
            data += '\n\nLinks:\n'
            n = 1
            for i in h.anchorlist:
                data += '  [%d] %s\n' % (n, i)
                n += 1

        text_len = len(data)
        u_data = unicode(data, charset, 'replace')
        content = []
        for bm in w.bookmarks:
            desc = u_data[bm[0]:bm[1]]
            desc = desc.encode('utf-8') #, 'replace')
            content.append((bm[0], float(bm[0])/text_len, desc))

        self._content = content

        data = self._get_slice(data, charset, offset, length,
                               int_filters, bookmarks)

        return data

##----------------------------------------------------------------------

    def load_file(self, buffer, book, bookmarks):

        data = self._read_file(filename=book.filename,
                               int_filters=book.internalfilters,
                               ext_filter=book.externalfilter,
                               charset=book.encoding, bookmarks=bookmarks)

        buffer.set_text(data)

        for mark in self._writer.bookmarks:
            start, end = mark
            #end = start + length
            iter_start = buffer.get_iter_at_offset(start)
            iter_end = buffer.get_iter_at_offset(end)
            buffer.apply_tag(buffer.title_tag, iter_start, iter_end)




##     def load_file(self, buffer, book, bookmarks):
##         """Load file in buffer"""
##         #print book.filename
##         ex = open(book.filename).read()
##         w = MyDumbWriter()
##         h = htmllib.HTMLParser(formatter.AbstractFormatter(w))
##         h.feed(ex)
##         data = string.join(w.data, '')
##         if len(h.anchorlist) > 0:
##             # add links
##             data += '\n\nLinks:\n'
##             n = 1
##             for i in h.anchorlist:
##                 data += '  [%d] %s\n' % (n, i)
##                 n += 1
##         data = self._get_slice(data, book.encoding)
##         text_len = len(data)
##         u_data = unicode(data, book.encoding, 'replace')
##         content = []
##         #print len(data)
##         buffer.set_text(data)
##         for mark in w.bookmarks:
##             start, end = mark
##             #end = start + length
##             iter_start = buffer.get_iter_at_offset(start)
##             iter_end = buffer.get_iter_at_offset(end)
##             buffer.apply_tag(buffer.title_tag, iter_start, iter_end)

##             desc = u_data[start:end]
##             desc = desc.encode('utf-8')
##             content.append((start, float(start)/text_len, desc))

##         self._content = content

##         for style in w.styles:
##             start, end, type = style
##             #end = start + length
##             iter_start = buffer.get_iter_at_offset(start)
##             iter_end = buffer.get_iter_at_offset(end)
##             if type == 'bold':
##                 buffer.apply_tag(buffer.strong_tag, iter_start, iter_end)
##             else: # italic
##                 buffer.apply_tag(buffer.emphasis_tag, iter_start, iter_end)

    def get_content(self):
        return self._content
##         content = []
##         for bm in self._writer.bookmarks:
##             desc = data[bm[0]:bm[1]]
##             desc = desc.encode('utf-8')
##             content.append((float(bm[0])/text_len, bm[0], bm[1]-bm[0], desc)



##----------------------------------------------------------------------

class gzipped_html_parser(html_parser):

    def new_book(self, filename, category=None,
                 external_filter=None, encoding=None):
        """Create new book object"""

        book = bookmarks.Book()
        book.filename = filename

        fileobj = gzip.open(filename)
        encoding = detectcharset.detectcharset(fileobj)

        if encoding:
            book.encoding = encoding
        else:
            encoding = book.encoding = config.default_encoding

        book.file_type = 'gzipped_html'
        book.description = self.book_description(book)
        if category:
            book.categories = [category]

        return self._html_new_book(fileobj, book, encoding)

##----------------------------------------------------------------------

    def _read_file(self, filename, charset, offset=None, length=None,
                   int_filters=None, ext_filter=None, bookmarks=None):

        fd = gzip.open(filename)
        data = fd.read()
        fd.close()

        return self._parse_html(data, charset, offset, length,
                                int_filters, ext_filter, bookmarks)

##----------------------------------------------------------------------
##----------------------------------------------------------------------
##----------------------------------------------------------------------

class LibRuWriter(formatter.NullWriter):


    def __init__(self):
        print '--== LibRuWriter ==--'

        self.data = []

        self.bookmarks = []
        self.current_bookmark = 0

        self.styles = []
        self.current_italic = 0
        self.current_bold = 0

        self.index = 0
        self.teletype = False
        formatter.NullWriter.__init__(self)

    def send_paragraph(self, blankline):
        s = '\n'*blankline
        self.data.append(s)
        self.index += len(s)

    def send_line_break(self):
        self.data.append('\n')
        #self.index += 1

    def send_hor_rule(self, *args, **kw):
        self.data.append('\n')
        #self.data.append('\n')
        self.index += 1

    def send_literal_data(self, data):
        #print '>>', len(data)
        print data
        if self.teletype: #data[-1] == '\n':
            data = data.rstrip()
            data = filters.internal_filter_3(data)
        self.data.append(data)
        self.index += len(data)



    def send_flowing_data(self, data):
        if not data: return
        self.data.append(data)
        self.index += len(data)

    def new_font(self, font):
        # font = (size, italic, bold, teletype)
        # add headers (<h1> <h2> ... ) to bookmarks
        print '-->', font

        if font:
            if font[3]:
                self.teletype = True

            if font[0]: # begin of header
                self.current_bookmark_offset = self.index
                self.current_bookmark = 1
            if font[1]: # italic
                self.current_italic_offset = self.index
                self.current_italic = 1
            if font[2]: # bold
                self.current_bold_offset = self.index
                self.current_bold = 1

            return

        self.teletype = False

        if self.current_bookmark: # end of header
            self.current_bookmark = 0
            self.bookmarks.append((self.current_bookmark_offset, self.index))

        if self.current_italic:
            self.current_italic = 0
            self.styles.append((self.current_italic_offset, self.index, 'italic'))

        if self.current_bold:
            self.current_bold = 0
            self.styles.append((self.current_bold_offset, self.index, 'bold'))


#----------------------------------------------------------------------

class lib_ru_parser(html_parser):

    def _parse_html(self, ex, charset, offset, length,
                    int_filters, ext_filter, bookmarks):

        w = LibRuWriter()
        h = htmllib.HTMLParser(formatter.AbstractFormatter(w))
        h.feed(ex)
        data = ''.join(w.data)
        if len(h.anchorlist) > 0:
            data += '\n\nLinks:\n'
            n = 1
            for i in h.anchorlist:
                data += '  [%d] %s\n' % (n, i)
                n += 1

        data = self._get_slice(data, charset, offset, length,
                               int_filters, bookmarks)

        return data


##----------------------------------------------------------------------
##----------------------------------------------------------------------

class fb2_parser(plain_text_parser):

    def new_book(self, filename, category=None,
                 external_filter=None, encoding=None):
        """Create new book object"""
        from fictionbook2 import FictionBook2

        book = bookmarks.Book()
        book.filename = filename
        book.encoding = 'utf-8'
        book.file_type = 'fb2'

        fn = get_file(filename)
        fb = FictionBook2(fn)
        if fn != filename: os.remove(fn)

        book.author = fb.author
        book.name = fb.name
        book.description = fb.description
##         text = fb.text
##         u_text = text.decode('utf-8')
##         text_len = len(u_text)
##         for b in fb.bookmarks:
##             offset = b[0]
##             length = b[1]
##             book.add_bookmark(float(b[0])/text_len, offset, length,
##                               u_text[b[0]:b[0]+b[1]].encode('utf-8'))

        book.categories = book.genres = fb.genres

        return book

    def get_content(self):

        text = self._fb.text
        u_text = text.decode('utf-8')
        text_len = len(u_text)
        content = []
        for b in self._fb.bookmarks:
            offset = b[0]
            length = b[1]
            position = float(b[0])/text_len
            content.append(
                (offset, position, u_text[b[0]:b[0]+b[1]].encode('utf-8')))
                #(offset, length, u_text[b[0]:b[0]+b[1]].encode('utf-8')))

        return content


##----------------------------------------------------------------------

    def _read_file(self, filename, charset, offset=None, length=None,
                   int_filters=None, ext_filter=None, bookmarks=None):
        from fictionbook2 import FictionBook2

        fn = get_file(filename)
        fb = FictionBook2(fn)
        if fn != filename: os.remove(fn)
        data = self._get_slice(fb.text, 'utf-8', offset, length,
                               int_filters, bookmarks)

        return data

##----------------------------------------------------------------------

    def binary_content(self, arg, cover_only=False):
        from fictionbook2 import FictionBook2

        content = []

        if type(arg) is types.StringType:
            fn = get_file(arg)
            fb = FictionBook2(fn)
            if fn != arg: os.remove(fn)
        else:
            fb = arg

        if cover_only:

            for bin_id, bin_ct, bin_data, bin_offset in fb.binaries:
                if bin_id == fb.cover_href[1:]:
                    try:
                        data=base64.decodestring(bin_data)
                    except Exception, err:
                        return None
                    return bin_id, bin_ct, data

        else:
            for bin_id, bin_ct, bin_data, bin_offset in fb.binaries:
                try:
                    data=base64.decodestring(bin_data)
                except Exception, err:
                    print >> sys.stderr, \
                          'Error in base64.decodestring: id: %s: %s' \
                          % (bin_id, err)
                    continue
                content.append((bin_id, bin_ct, data, bin_offset))
            return content

##----------------------------------------------------------------------

    def load_file(self, buffer, book, bookmarks):
        """Load file in buffer"""
        from fictionbook2 import FictionBook2
        import gtk

        fn = get_file(book.filename)
        fb = FictionBook2(fn)
        if fn != book.filename: os.remove(fn)
        self._fb = fb
        text = fb.text

##         data = self._read_file(filename=book.filename,
##                                int_filters=book.internalfilters,
##                                ext_filter=book.externalfilter,
##                                charset=book.encoding, bookmarks=bookmarks)

        buffer.set_text(text)

        for mark in fb.bookmarks:
            start, length = mark
            end = start + length
            iter_start = buffer.get_iter_at_offset(start)
            iter_end = buffer.get_iter_at_offset(end)
            buffer.apply_tag(buffer.title_tag, iter_start, iter_end)

        for style in fb.styles:
            start, length, type = style
            end = start + length
            if type in ('strong', 'emphasis'):
                iter_start = buffer.get_iter_at_offset(start)
                iter_end = buffer.get_iter_at_offset(end)
                if type == 'strong':
                    buffer.apply_tag(buffer.strong_tag, iter_start, iter_end)
                else:
                    buffer.apply_tag(buffer.emphasis_tag, iter_start, iter_end)

        binary_content = self.binary_content(fb)
        for bin_id, bin_ct, bin_data, bin_offset in binary_content:

            if bin_offset < 0: continue

            tmp_file = tempfile.mktemp()
            try:
                open(tmp_file, 'w').write(bin_data)
                pb = gtk.gdk.pixbuf_new_from_file(tmp_file)

                start = buffer.get_iter_at_offset(bin_offset)
                end = buffer.get_iter_at_offset(bin_offset+1)
                buffer.delete(start, end)
                iter = buffer.get_iter_at_offset(bin_offset-1)
                buffer.insert_pixbuf(iter, pb)

                # place pixmap to center
                start = buffer.get_iter_at_offset(bin_offset-1)
                end = buffer.get_iter_at_offset(bin_offset)
                buffer.apply_tag(buffer.pixmap_tag, start, end)

                #pixmap, mask = pb.render_pixmap_and_mask()
                #self.binary_image.set_from_pixmap(pixmap, mask)

            finally:
                os.remove(tmp_file)

        for lnk in fb.links:
            start, end, link_start, link_end, type = lnk
            iter_start = buffer.get_iter_at_offset(start)
            iter_end = buffer.get_iter_at_offset(end)
            if type == 'link_type':
                buffer.apply_tag(buffer.link_tag, iter_start, iter_end)
            else: # note_type
                buffer.apply_tag(buffer.note_tag, iter_start, iter_end)




##----------------------------------------------------------------------

    def goto_link(self, offset):

        for lnk in self._fb.links:
            start, end, link_start, link_end, type = lnk
            if start<=offset<=end:
                return link_start
                #return len(unicode(self._fb.text[:link_start], 'utf-8'))


if __name__ == '__main__':
    if len(sys.argv) < 2:
        sys.exit('usage: %s file' % sys.argv[0])

    #parser = LibRuWriter()
    #
    w = LibRuWriter()
    h = htmllib.HTMLParser(formatter.AbstractFormatter(w))
    h.feed(open(sys.argv[1]).read())
    data = ''.join(w.data)
    #print data
