#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re

import gtk
gdk = gtk.gdk
import pango
import gobject

from bookmarks import Book
from config import file_types, default_description_length, default_encoding
from miscutils import zip_get_filename
from parsers import *

##----------------------------------------------------------------------

def new_book(filename, category=None):
    import zipfile

    if zipfile.is_zipfile(filename): #filename.endswith('.zip'):
        fn = zip_get_filename(filename)
    else:
        fn = filename

    # сортируем по длине расширений: длинные в начале
    # т.е. вначале .html.gz  а потом .gz
    file_types_l = list(file_types)
    file_types_l.sort(lambda ft1, ft2:
                      cmp(max(map(len, file_types[ft2][0])),
                          max(map(len, file_types[ft1][0]))))

    # search parser
    for type in file_types_l:
        for s in file_types[type][0]:
            if fn.endswith(s):
                file_parser = file_types[type][1]()
                external_filter = file_types[type][2]
                encoding = file_types[type][3]
                book = file_parser.new_book(
                    filename, category=category,
                    external_filter=external_filter,
                    encoding=encoding)
                return book, file_parser

    # suffix not found -> plain text
    file_parser = plain_text_parser()
    book = file_parser.new_book(filename, category=category)
    return book, file_parser


##----------------------------------------------------------------------

class BookBuffer(gtk.TextBuffer):

    bookmark_tag_color = '#ff0000'

    def __init__(self):

        gtk.TextBuffer.__init__(self)

        self.book = None

        # tags
        self.bookmark_tag = self.create_tag('mark tag',
                                            foreground=self.bookmark_tag_color)

        #self.search_tag = self.create_tag('search')
        #self.search_tag.set_property('background', '#9090ec')

        self.link_tag = self.create_tag('link_tag',
                                        foreground='#0000a9',
                                        underline=pango.UNDERLINE_SINGLE)
        #self.link_tag.set_property('underline', pango.UNDERLINE_SINGLE)
        self.link_tag.connect('event', self.link_tag_event_cb)

        self.note_tag = self.create_tag('note_tag', foreground='#0000a9')
        self.note_tag.connect('event', self.link_tag_event_cb)

        self.pixmap_tag = self.create_tag('pixmap_tag',
                                          justification=gtk.JUSTIFY_CENTER,
                                          wrap_mode=gtk.WRAP_WORD)

        self.title_tag = self.create_tag('title_tag',
                                         weight=pango.WEIGHT_BOLD,
                                         justification=gtk.JUSTIFY_CENTER,
                                         wrap_mode=gtk.WRAP_WORD)

        self.strong_tag = self.create_tag('strong_tag',
                                          weight=pango.WEIGHT_BOLD)
                                          #style=pango.STYLE_OBLIQUE)

        self.emphasis_tag = self.create_tag('emphasis_tag',
                                            style=pango.STYLE_ITALIC)



##"style" pango.STYLE_NORMAL, pango.STYLE_OBLIQUE, pango.STYLE_ITALIC.

        # search vars
        self.search_iter = None
        self._search_string = ''
        self.regexp_pattern = None
        self.search_regexp_offset = 0

##----------------------------------------------------------------------

    def link_tag_event_cb(self, texttag, widget, event, iter):
        if event.type == gdk.BUTTON_RELEASE:
            link_offset = self.file_parser.goto_link(iter.get_offset())
            self.emit('goto-link', link_offset)

        return False

##----------------------------------------------------------------------

    def set_book(self, book):

        self.book = book
        self.file_parser = file_types[book.file_type][1]()

##----------------------------------------------------------------------

    def load_file(self):

        # clear buffer
        start, end = self.get_bounds()
        self.delete(start, end)
        # load file in buffer
        bookmarks = map(lambda m: m.offset, self.book.marks_list)
        self.file_parser.load_file(self, self.book, bookmarks)
        # highlight bookmarks (to parser?)
        for bm in self.book.marks_list:
            self.highlight_bookmark(bm.offset, bm.length)

##----------------------------------------------------------------------

    def new_book(self, filename, category=None):
        self.book, self.file_parser = new_book(filename, category)
        return self.book

##----------------------------------------------------------------------

    def book_description(self):
        return self.file_parser.book_description(self.book)

##----------------------------------------------------------------------

    def mark_description(self, offset):

        start = self.get_iter_at_offset(offset)
        end = self.get_iter_at_offset(offset+default_description_length)

        desc = self.get_text(start, end, True)
        desc += ' ...'

        return desc

##----------------------------------------------------------------------

    def preview(self, offset=None):
        # clear buffer
        start, end = self.get_bounds()
        self.delete(start, end)

        self.file_parser.preview(self, self.book, offset)
        iter = self.get_start_iter()
        self.place_cursor(iter)

##----------------------------------------------------------------------

    def binary_content(self, cover_only=False):
        return self.file_parser.binary_content(self.book.filename, cover_only)

    def get_content(self):
        return self.file_parser.get_content()

##----------------------------------------------------------------------

    def highlight_bookmark(self, offset, length=0):

        iter = self.get_iter_at_offset(offset)
        iter_start = iter.copy()
        if length <= 0:
            iter.forward_word_end()
        else:
            iter.forward_chars(length)
        self.apply_tag(self.bookmark_tag, iter_start, iter)

##----------------------------------------------------------------------

    def update_highlight_bookmarks(self):
        start, end = self.get_bounds()
        self.remove_tag(self.bookmark_tag, start, end)
        for mark in self.book.marks_list:
            self.highlight_bookmark(mark.offset, mark.length)

##----------------------------------------------------------------------

    def change_bookmark_tag_color(self, color):
        BookBuffer.bookmark_tag_color = color
        self.bookmark_tag.set_property('foreground', color)

    def change_link_tag_color(self, color):
        BookBuffer.link_tag_color = color
        self.link_tag.set_property('foreground', color)
        self.note_tag.set_property('foreground', color)

    def change_title_tag_font(self, font):
        BookBuffer.title_tag_font = font
        self.title_tag.set_property('font', font)

##----------------------------------------------------------------------

    def apply_link_tag(self, start, end, link_offset):
        iter_start = self.get_iter_at_offset(start)
        iter_end = self.get_iter_at_offset(end)
        self.apply_tag(self.bookmark_tag, iter_start, iter_end)

##----------------------------------------------------------------------
##-- search ------------------------------------------------------------

    def search_regexp(self, strng):

        if strng:

            #strng = strng.decode('utf-8')
            self.regexp_pattern = re.compile(unicode(strng, 'utf-8'),
                                             re.I|re.U)

            iter = self._do_search_regexp()

            if not self._do_search_regexp():
                self.regexp_pattern = None

            return iter

##----------------------------------------------------------------------

    def search_regexp_again(self):

        if self.regexp_pattern:
            return self._do_search_regexp()
        else:
            return None

##----------------------------------------------------------------------

    def _do_search_regexp(self):

        start, end = self.get_bounds()
        text = self.get_text(start, end, True)
        text = unicode(text, 'utf-8') #.decode('utf-8')

        mo = self.regexp_pattern.search(text, self.search_regexp_offset)

        if mo:

            iter_start = self.get_iter_at_offset(mo.start())
            iter_end = self.get_iter_at_offset(mo.end())
            self._search_highlight((iter_start, iter_end))
            self.search_regexp_offset = mo.end()

            return iter_start

        else:

            return None

##----------------------------------------------------------------------

    def search_string(self, strng):

        if strng:

            search_iter = self.get_iter_at_offset(0)
            search_ret = search_iter.forward_search(strng,
                                                    gtk.TEXT_SEARCH_TEXT_ONLY,
                                                    None)
            self._search_string = strng
            return self._search_highlight(search_ret)

##----------------------------------------------------------------------

    def search_string_again_forward(self):

        if self.search_iter:
            search_ret = self.search_iter.forward_search(self._search_string,
                                                         gtk.TEXT_SEARCH_TEXT_ONLY,
                                                         None)
            return self._search_highlight(search_ret)

##----------------------------------------------------------------------

    def search_string_again_backward(self):

        if self.search_iter:
            self.search_iter.backward_chars(1)
            search_ret = self.search_iter.backward_search(self._search_string,
                                                          gtk.TEXT_SEARCH_TEXT_ONLY,
                                                          None)
            return self._search_highlight(search_ret)

##----------------------------------------------------------------------

    def _search_highlight(self, search_ret):

        if not search_ret:
            return None

        iter_start, iter_end = search_ret

        #start, end = self.get_bounds()
        #self.remove_tag_by_name('search', start, end)
        #self.apply_tag(self.search_tag, iter_start, iter_end)

        self.move_mark_by_name('insert', iter_start)
        self.move_mark_by_name('selection_bound', iter_end)

        self.search_iter = iter_end

        return self.search_iter

##----------------------------------------------------------------------
##----------------------------------------------------------------------

    def regexp_bookmarks_init(self, strng):

        if strng:

            strng = unicode(strng, 'utf-8')
            self._bookmarks_regexp_pat = re.compile(strng, re.I | re.U)

            start, end = self.get_bounds()
            text = self.get_text(start, end, True)
            text = unicode(text, 'utf-8')
            self._bookmarks_regexp_lines = string.split(text, '\n')
            self._bookmarks_regexp_offset = 0
            self._bookmarks_regexp_index = 0
            self._bookmarks_regexp_numder = 0
            self._bookmarks_regexp_text_len = len(text)

            #self.line_count = self.get_line_count()
            #self.line_index = 1


    def regexp_bookmarks_next(self):

        for line in self._bookmarks_regexp_lines[self._bookmarks_regexp_index:]:

            mo = self._bookmarks_regexp_pat.search(line)

            #self.line_index += 1

            if mo:

                offset = self._bookmarks_regexp_offset+mo.start()
                pos = float(offset)/self._bookmarks_regexp_text_len
                desc = self.mark_description(offset)
                self.book.add_bookmark(pos, offset, 0, desc)
                self.highlight_bookmark(offset)
                self._bookmarks_regexp_numder += 1
                self._bookmarks_regexp_offset += len(line)+1
                self._bookmarks_regexp_index += 1

                return 1

            else:

                self._bookmarks_regexp_offset += len(line)+1
                self._bookmarks_regexp_index += 1

                return 0


    def regexp_bookmarks_finally(self):

        ret = self._bookmarks_regexp_numder

        del self._bookmarks_regexp_pat
        del self._bookmarks_regexp_lines
        del self._bookmarks_regexp_offset
        del self._bookmarks_regexp_index
        del self._bookmarks_regexp_numder
        del self._bookmarks_regexp_text_len

        return ret

##----------------------------------------------------------------------

##     def make_regexp_bookmarks(self):
##         strng = entry_dialog(self, 'Regexp', 'Regexp: ')
##         if strng:
##             start, end = self.get_bounds()
##             text = self.get_text(start, end, True)
##             text = unicode(text, 'utf-8')
##             strng = unicode(strng, 'utf-8')
##             pat = re.compile(strng, re.I | re.U)
##             offset = 0
##             n = 0
##             text_len = len(text)
##             #tbl = string.maketrans('', '')
##             for line in string.split(text, '\n'):
##                 mo = pat.search(line)
##                 if mo:
##                     pos = float(offset)/text_len # ??? this is not exactly
##                     desc = self.mark_description(offset)
##                     self.current_book.add_bookmark(pos, offset, 0, desc)
##                     self.highlight_bookmark(offset)
##                     n += 1
##                 offset = offset+len(line)+1
##             info_dialog(self, 'Created %d bookmarks' % n)
##             if self.bookmarks_manager:
##                 self.bookmarks_manager.update_treeview()
##         self.update_bookmarks_menu()

##----------------------------------------------------------------------
##----------------------------------------------------------------------

gobject.signal_new('goto-link', BookBuffer,
                   gobject.SIGNAL_RUN_LAST,
                   gobject.TYPE_NONE,
                   (gobject.TYPE_INT,))
