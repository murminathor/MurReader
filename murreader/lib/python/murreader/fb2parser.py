#!/usr/bin/env python
# -*- coding: utf-8  -*-

import libxml2

__DEBUG__ = False

class FB2Parser:
    '''Парсер FB2 - парсит fb2-файлы и превращает в python-обьект'''

    def __init__(self, TextParagraph ):
        '''Начальная инициализация параметров'''

        self.current_paragraph = None

        #self.content = TextContent()
        self.content = []
        self.footnotes = {}
        self.footnotes_index = 1
        self.images = {}
        self.genres = []
        self.book_title = ''
        self.authors = []
        self.lang = ''

        self.title_level = 0
        self.titles_list = []

        self.cover = []
        self.description = []

        self.body_is_footnote = False

        #self.current_footnote = None
        self.current_footnote_id = None

        self.TextParagraph = TextParagraph

    def addEmptyLine(self):
        # добавляет пустую строку, если предыдущая не пустая
        if self.content and self.content[-1].data: # todo self.content[-1].type != 'image'
            # предыдущий параграф не пустой
            self.content.append(self.TextParagraph('paragraph'))


    def parseFB2(self, data):

        doc = libxml2.parseMemory(data, len(data))

        current = doc.children

        # skip comment
        while current:
            if current.name == 'FictionBook':
                break
            current = current.next
        current = current.children

        while current:

            if current.name == 'stylesheet':
                self.parseStylesheet(current)

            elif current.name == 'description':
                self.parseDescription(current)

            elif current.name == 'body':
                self.parseBody(current)

            elif current.name == 'binary':
                self.parseBinary(current)

            current = current.next

        doc.freeDoc()


    def parseStylesheet(self, current):
        #print 'parseStylesheet'
        pass


    def parseDescription(self, current):
        #print 'parseDescription'
        current = current.children

        while current:

            if current.name == 'title-info':
                self.parseTitleInfo(current)
            elif current.name == 'document-info':
                self.parseDocumentInfo(current)

            current = current.next


    def parseTitleInfo(self, current):
        current = current.children

        while current:

            if current.name == 'genre':
                if current.children and current.children.content:
                    self.genres.append(current.children.content)

            elif current.name == 'lang':
                if current.children and current.children.content:
                    self.lang = current.children.content

            elif current.name == 'author':
                self.parseAuthor(current)

            elif current.name == 'book-title':
                if current.children and current.children.content:
                    self.book_title = current.children.content

            elif current.name == 'annotation':
                self.parseAnnotation(current)
                self.description = self.content
                self.content = []

            elif current.name == 'coverpage':
                # cover
                c = current.children
                while c:
                    if c.name == 'image' and c.prop('href'):
                        self.cover.append(c.prop('href')[1:])
                    c = c.next

            current = current.next


    def parseAuthor(self, current):
        current = current.children
        author = []
        while current:
            if current.name in ['first-name', 'middle-name', 'last-name']:
                author.append(unicode(current.content, 'utf-8'))
            elif current.name == 'nick-name':
                author.append('('+unicode(current.content, 'utf-8')+')')
            current = current.next
        author = ' '.join(author)
        self.authors.append(author)
        #print '>%s<' % author


    def parseDocumentInfo(self, current):
        current = current.children

        while current:

            if current.name == 'title':
                self.parseTitle(current)

            elif current.name == 'section':
                self.parseSection(current)

            current = current.next


    def parseBody(self, current):
        #print 'parseBody'

        if current.prop('name'): # in ['footnote', 'notes']:
            self.body_is_footnote = True
        else:
            self.body_is_footnote = False

##         if current.prop('name'):
##             self.current_body_name = current.prop('name')

        current = current.children

        while current:

            if current.name == 'title':
                self.parseTitle(current)
                # + empty-line

            elif current.name == 'section':
                self.parseSection(current)

            elif current.name == 'image':
                self.parseImage(current)

            elif current.name == 'epigraph':
                self.parseEpigraph(current)

            elif __DEBUG__ and current.name != 'text':
                print 'unsupported tag:', 'parseBody:', current.name

            current = current.next


    def parseTitle(self, current):
        #print 'parseTitle'
        title_text = []
        title_index = len(self.content)

        current = current.children

        self.addEmptyLine()

        while current:

            if current.name == 'p':

                self.current_paragraph = self.TextParagraph('title')
                self.content.append(self.current_paragraph)
                self.current_paragraph.title_level = self.title_level
                self.parseP(current)

                title_text.append(self.current_paragraph.data)

            elif current.name == 'empty-line':
                self.addEmptyLine()

            elif __DEBUG__ and current.name != 'text':
                print 'unsupported tag:', 'parseTitle:', current.name


            current = current.next

        self.titles_list.append((' '.join(title_text).replace('\n', ' ').strip(),
                                 title_index))
        # + empty-line
        self.addEmptyLine()


    def parseSection(self, current):
        #print 'parseSection'

        self.title_level += 1

        footnote_name = None
        if self.body_is_footnote and current.prop('id'):
            footnote_name = current.prop('id')
            footnotes_start = len(self.content)

        current = current.children

        while current:

            if current.name == 'title':
                if footnote_name:
                    footnotes_start += 1
                self.parseTitle(current)

            elif current.name == 'subtitle':
                self.parseSubtitle(current)

            elif current.name == 'epigraph':
                self.parseEpigraph(current)

            elif current.name == 'image':
                self.parseImage(current)

            elif current.name == 'annotation':
                self.parseAnnotation(current)

            elif current.name == 'section':
                self.parseSection(current)

            elif current.name == 'p':
                self.current_paragraph = self.TextParagraph('paragraph')
                self.content.append(self.current_paragraph)
                self.parseP(current)

            elif current.name == 'poem':
                self.parsePoem(current)

            elif current.name == 'cite':
                self.parseCite(current)

            elif current.name == 'empty-line':
                self.addEmptyLine()

            elif __DEBUG__ and current.name != 'text':
                print 'unsupported tag:', 'parseSection:', current.name

            current = current.next

        if footnote_name:
            #print footnote_name
            #print '>>', self.current_paragraph.data.encode('koi8-r', 'replace'), '<<'

            self.footnotes[footnote_name] = []

            if self.content[footnotes_start].type == 'title' \
               and len(self.content[footnotes_start:]) >= 3:

                par = self.TextParagraph('paragraph')
                title = self.content[footnotes_start].data
                if title[:2] == '* ' and title[-2:] == ' *':
                    title = title[2:-2]
                if title[-1] != '.': title += '.'
                par.data = title+' '+self.content[footnotes_start+2].data #[1:]??
                par.styles.append((0, len(title), 'strong'))
                self.footnotes[footnote_name].append(par)
                footnotes_start += 3

            for par in self.content[footnotes_start:]:
                self.footnotes[footnote_name].append(par)

        self.title_level -= 1


    def parseEpigraph(self, current):
        #print 'parseEpigraph'

        current = current.children

        while current:

            if current.name == 'p':
                self.current_paragraph = self.TextParagraph('epigraph')
                self.content.append(self.current_paragraph)
                self.parseP(current)

            elif current.name == 'poem':
                self.parsePoem(current)

            elif current.name == 'cite':
                self.parseCite(current)

            elif current.name == 'text-author':
                paragraph = self.TextParagraph('text_author')
                self.content.append(paragraph)
                paragraph.data = unicode(current.children.content, 'utf-8')

            elif current.name == 'empty-line':
                self.addEmptyLine()

            elif __DEBUG__ and current.name != 'text':
                print 'unsupported tag:', 'parseEpigraph:', current.name

            current = current.next

        self.addEmptyLine()


    def parseImage(self, current):
        #print 'parseImage'

        if current.prop('href'):
            paragraph = self.TextParagraph('image')
            self.content.append(paragraph)
            paragraph.href = current.prop('href')[1:]


    def parseAnnotation(self, current):

        current = current.children

        while current:

            if current.name == 'p':
                self.current_paragraph = self.TextParagraph('paragraph')
                self.content.append(self.current_paragraph)
                self.parseP(current)

            elif current.name == 'poem':
                self.parsePoem(current)

            elif current.name == 'cite':
                self.parseCite(current)

            elif current.name == 'empty-line':
                self.addEmptyLine()

            elif __DEBUG__ and current.name != 'text':
                print 'unsupported tag:', 'parseAnnotation:', current.name

            current = current.next


    def parseP(self, current):
        #print 'parseP'

        footnote_name = None
        if self.body_is_footnote and current.prop('id'):
            footnote_name = current.prop('id')
            self.footnotes[footnote_name] = []
            self.current_footnote_id = footnote_name

        current = current.children

        while current:

            if current.name == 'style':
                self.parseStyle(current)

            elif current.name == 'strong':
                self.parseStrong(current)

            elif current.name == 'emphasis':
                self.parseEmphasis(current)

            elif current.name == 'a':
                self.parseLink(current)

            elif __DEBUG__ and current.name != 'text':
                print 'unsupported tag:', 'parseP:', current.name

            elif current.content:
                s = unicode(current.content, 'utf-8')
                self.current_paragraph.data += s

            current = current.next

        if footnote_name or self.current_footnote_id:
            #print footnote_name
            #print self.current_paragraph.data.encode('koi8-r', 'replace')
            #self.footnotes[footnote_name].append(self.current_paragraph)
            self.footnotes[self.current_footnote_id].append(self.current_paragraph)

    def parseStrong(self, current):

        current = current.children

        p = self.current_paragraph

        if current and current.content: # ???

            s = unicode(current.content, 'utf-8')
            self.current_paragraph.styles.append((len(self.current_paragraph.data), len(s), 'strong'))
            self.current_paragraph.data += s


    def parseEmphasis(self, current):

        current = current.children

        p = self.current_paragraph

        if current and current.content: # ???

            s = unicode(current.content, 'utf-8')
            self.current_paragraph.styles.append((len(self.current_paragraph.data), len(s), 'emphasis'))
            self.current_paragraph.data += s


    def parseStyle(self, current):

        ## style name="foreign lang" xml:lang="fr"
        lang = None
        if current.prop('name') == 'foreign lang':
            lang = current.prop('lang')
            offset = len(self.current_paragraph.data)

        #print '>>', current.prop('name'), current.prop('lang')

        current = current.children

        while current:
            if current.name == 'style':
                self.parseStyle(current)

            elif current.name == 'strong':
                self.parseStrong(current)

            elif current.name == 'emphasis':
                self.parseEmphasis(current)

            elif current.name == 'a':
                self.parseLink(current)

            elif __DEBUG__ and current.name != 'text':
                print 'unsupported tag:', 'parseStyle:', current.name

            elif current.content:
                s = unicode(current.content, 'utf-8')
                self.current_paragraph.data += s

            current = current.next

        if lang:
            self.current_paragraph.styles.append((offset, len(self.current_paragraph.data)-offset, 'lang=%s'%lang))


    def parseLink(self, current):
        #print 'parseLink'
        #print 'type->', current.prop('type')
        #print 'href->', current.prop('href')

        footnote_name = None

        if current.prop('type') == 'note' and current.prop('href'):
            footnote_name = current.prop('href')
            link_type = 'footnote'
            footnote_start = len(self.current_paragraph.data)
        elif current.prop('href'):
            footnote_name = current.prop('href')
            #footnote_start = -1
            link_type = 'hyperlink'
            footnote_start = len(self.current_paragraph.data)

        current = current.children

        while current:
            if current.name == 'style':
                self.parseStyle(current)

            elif current.name == 'strong':
                self.parseStrong(current)

            elif current.name == 'emphasis':
                self.parseEmphasis(current)

            elif __DEBUG__ and current.name != 'text':
                print 'unsupported tag:', 'parseLink:', current.name

            elif current.content:

                s = unicode(current.content, 'utf-8')
                if (s[0] == '[' and s[-1] == ']') \
                       or (s[0] == '{' and s[-1] == '}'):
                    s = s[1:-1]
                self.current_paragraph.data += s

            current = current.next

        if footnote_name:

            footnote_end = len(self.current_paragraph.data)
            footnote_length = footnote_end - footnote_start
            self.current_paragraph.footnotes.append((footnote_start,
                                                     footnote_end,
                                                     footnote_name[1:]))

            self.current_paragraph.styles.append((footnote_start,
                                                  footnote_length,
                                                  link_type))

##             if link_type == 'hyperlink': #footnote_start == -1:
##                 footnote_start = len(self.current_paragraph.data)
##                 self.current_paragraph.data += str(self.footnotes_index)
##                 self.footnotes_index += 1
##             else: # footnote
##                 footnote_end = len(self.current_paragraph.data)
##                 footnote_length = footnote_end - footnote_start
##                 self.current_paragraph.footnotes.append((footnote_start,
##                                                          footnote_end,
##                                                          footnote_name[1:]))
##                 self.current_paragraph.styles.append((footnote_start,
##                                                       footnote_length,
##                                                       'footnote'))


    def parsePoem(self, current):

        current = current.children

        while current:

            if current.name == "title":
                self.parseTitle(current)

            elif current.name == "epigraph":
                self.parseEpigraph(current)

            elif current.name == "p":
                self.parseP(current)

            elif current.name == "empty-line":
                self.addEmptyLine()

            elif current.name == "stanza":
                self.addEmptyLine()
                self.parseStanza(current)

            elif current.name == 'text-author':
                paragraph = self.TextParagraph('text_author')
                self.content.append(paragraph)
                paragraph.data = unicode(current.children.content, 'utf-8')

            elif __DEBUG__ and current.name != 'text':
                print 'unsupported tag:', 'parsePoem:', current.name

            current = current.next

        self.addEmptyLine()


    def parseStanza(self, current):

        current = current.children

        while current:
            #print current.name

            if current.name == 'v':
                self.current_paragraph = self.TextParagraph('stanza')
                self.content.append(self.current_paragraph)
                self.parseV(current)

            elif __DEBUG__ and current.name != 'text':
                print 'unsupported tag:', 'parseStanza:', current.name

            current = current.next


    def parseV(self, current):

        current = current.children

        while current:
            #print current.name

            if current.name == 'a':
                self.parseLink(current)

            elif current.name == 'style':
                self.parseStyle(current)

            elif current.name == 'strong':
                self.parseStrong(current)

            elif current.name == 'emphasis':
                self.parseEmphasis(current)

            elif __DEBUG__ and current.name != 'text':
                print 'unsupported tag:', 'parseV:', current.name

            elif current.content:
                s = unicode(current.content, 'utf-8')
                self.current_paragraph.data += s

            current = current.next


    def parseSubtitle(self, current):

        self.addEmptyLine()
        self.current_paragraph = self.TextParagraph('subtitle')
        self.content.append(self.current_paragraph)
        self.parseP(current)
        self.addEmptyLine()

##         current = current.children
##         self.current_paragraph = self.TextParagraph('subtitle')
##         self.content.append(self.current_paragraph)
##         while current:
##             if current.name == 'p':
##                 self.parseP(current)
##             elif __DEBUG__ and current.name != 'text':
##                 print 'unsupported tag:', 'parseSubtitle:', current.name
##             elif current.content:
##                 s = unicode(current.content, 'utf-8')
##                 self.current_paragraph.data += s
##             current = current.next
##         self.addEmptyLine()


    def parseCite(self, current):
        current = current.children

        while current:

            if current.name == 'p':
                self.current_paragraph = self.TextParagraph('cite')
                self.content.append(self.current_paragraph)
                self.parseP(current)

            elif current.name == 'poem':
                self.parsePoem(current)

            elif current.name == 'empty-line':
                self.addEmptyLine()

            elif current.name == 'text-author':
                paragraph = self.TextParagraph('text_author')
                self.content.append(paragraph)
                paragraph.data = unicode(current.children.content, 'utf-8')

            elif current.name == 'subtitle':
                self.parseSubtitle(current)

            elif __DEBUG__ and current.name != 'text':
                print 'unsupported tag:', 'parseCite:', current.name

            current = current.next


    def parseBinary(self, current):

        if current.prop('id'):
            id = current.prop('id')
            data = ''
            current = current.children

            while current:
                if current.content:
                    data += current.content
                current = current.next

            if data:
                self.images[id]=data

# test
if __name__ == '__main__':

    import sys

    if len(sys.argv) != 2:
        sys.exit('usage: %s filename' % sys.argv[0])

    fb = FB2Parser()
    fb.parseFB2(open(sys.argv[1]).read())



    #for i in fb.content:
    #    print i.type

    #print len(fb.content)

##     i = 0
##     for p in fb.content:
##         if p.type == 'image':
##             print 'href:', p.href, i, len(fb.images[p.href])
##         i += 1

##     for c in fb.cover:
##         print 'cover:', c, len(fb.images[c])

##     for i in fb.images:
##         print '---- id ----', i
##         print '-'*70
##         print fb.images[i]
##         print '-'*70

##     for p in fb.content:
##         for f in p.footnotes:
##             print '-'*72
##             print fb.footnotes[f[2]].data.encode('koi8-r', 'replace')





