#!/usr/bin/env python
# -*- coding: utf-8 -*-


import os
import shelve

from miscutils import *
from config import PROGRAM_VERSION, DEFAULT_ENCODING, BOOKMARKS_FILE

##----------------------------------------------------------------------
##----------------------------------------------------------------------


class Bookmarks:

    def __init__(self):
        # categories {category_name: [filename ...], ...}
        self.categories_list = {}
        # all books filename
        self.books_list = []
        # for books menu {filename: title, ...}
        self.titles_list = {}
        #self.current_book = None

        # created only in bookmarks manager
        # {filename: book, ...}
        self.all_books = None

        # list of books for preserve
        self._books = {}
        # list of books for removal,
        # this book has been removed in func save_bookmarks
        # (before exit from program)
        self._deleted_books = []

        if not os.path.exists( BOOKMARKS_FILE ):
            self.bookmarks_db = shelve.open( BOOKMARKS_FILE )
            return

        self.bookmarks_db = shelve.open( BOOKMARKS_FILE )

        if not self.bookmarks_db.has_key('categories_list'):
            return

        self.categories_list = self.bookmarks_db['categories_list']
        self.books_list = self.bookmarks_db['books_list']
        self.titles_list = self.bookmarks_db['titles_list']

        #self.get_all_books()

##     def __del__(self):
##         self.bookmarks_db.close()
##         print 'bookmarks - del'

##----------------------------------------------------------------------

    def make_new_category(self, name):
        if not self.categories_list.has_key(name) and len(name) > 0:
            self.categories_list[name] = []

##----------------------------------------------------------------------

##     def make_new_book(self, filename, cat_list=None):
##         # save book ?
##         book=Book()
##         book.filename = filename
##         return self.add_new_book(filename, cat_list)

##----------------------------------------------------------------------

    def add_new_book(self, book):
        # save book ?
        #if not book.categories:
        #    self.make_new_category('Default')
        #    self.categories_list['Default'].append(book.filename)
        #else:
        for cat in book.categories:
            self.make_new_category(cat)
            self.categories_list[cat].append(book.filename)

        if not self.all_books is None:
            # may be empty, but already created
            self.all_books[book.filename] = book
        #if not self._books.has_key(book.filename):
        self._books[book.filename] = book
        self.books_list.append(book.filename)
        self.titles_list[book.filename] = book.get_title()
        return book

##----------------------------------------------------------------------

    def move_book(self, filename, old_cat=None, new_cat=None):
        # move book to new category
        # if old_cat is None: remove from all cat and set to new_cat

        if old_cat and new_cat:
            if filename in self.categories_list[old_cat]:
                self.categories_list[old_cat].remove(filename)
                self.categories_list[new_cat].append(filename)
                book = self.get_book(filename)
                #if old_cat in book.categories:
                book.categories.remove(old_cat)
                book.categories.append(new_cat)
                self.save_book(book)
                return 1
        elif old_cat is None and new_cat:

            for cat in self.categories_list:
                if filename in self.categories_list[cat]:
                    self.categories_list[cat].remove(filename)
            self.categories_list[new_cat].append(filename)
            book = self.get_book(filename)
            book.categories = [new_cat]
            self.save_book(book)
            return 1

        return 0

##----------------------------------------------------------------------

    def remove_book(self, filename, category=None):
        # if category == None -> remove book from ALL categories
        removed = 0
        if category is None:
            for cat in self.categories_list:
                if filename in self.categories_list[cat]:
                    self.categories_list[cat].remove(filename)
            self._remove_book_from_db(filename)
            removed = 1

        else:
            if filename in self.categories_list[category]:
                self.categories_list[category].remove(filename)
                book = self.get_book(filename)
                if category in book.categories:
                    book.categories.remove(category)
                if len(book.categories) == 0:
                    self._remove_book_from_db(filename)
                    removed = 1

        return removed

    def _remove_book_from_db(self, filename):
        self._deleted_books.append(filename)
        if self.all_books.has_key(filename):
            del self.all_books[filename]
        if filename in self.books_list:
            self.books_list.remove(filename)
        if self.titles_list.has_key(filename):
            del self.titles_list[filename]
        if self._books.has_key(filename):
            del self._books[filename]

##----------------------------------------------------------------------

    def remove_bookmark(self, filename, mark_number):
        book = self.get_book(filename)
        for mark in book.marks_list:
            if mark_number == mark.number:
                book.marks_list.remove(mark)
                return 1
        return 0

##----------------------------------------------------------------------

    def get_book(self, filename):
        if not filename in self.books_list:
            return None
        if self.all_books:
            return self.all_books[filename]
        if self._books.has_key(filename):
            return self._books[filename]
        book = self.bookmarks_db[filename]
        self._books[book.filename] = book
        return book

##----------------------------------------------------------------------

    def get_any_book(self):
        if len(self.books_list) == 0:
            return None
        book = self.bookmarks_db[self.books_list[0]]
        self._books[book.filename] = book
        return book

##----------------------------------------------------------------------

    def get_all_books(self): # for bookmarks manager
        if self.all_books:
            return self.all_books
        all_books = {}
        #print 'get_all_books start'
        for filename in self.books_list:
            if self._books.has_key(filename): # уже загрузили
                all_books[filename] = self._books[filename]
            else:
                all_books[filename] = self.bookmarks_db[filename]
        self.all_books = all_books
        #print 'get_all_books end'
        return all_books

##----------------------------------------------------------------------

    def get_mark(self, book, mark_number):
        for mark in book.marks_list:
            if mark_number == mark.number:
                return mark
        return None

##----------------------------------------------------------------------

    def save_book(self, book):
        self._books[book.filename] = book
        #self.titles_list[book.filename] = book.get_title()

##----------------------------------------------------------------------

    def get_current_book(self):
        if self.bookmarks_db.has_key('current_book'):
            filename = self.bookmarks_db['current_book']
            return self.get_book(filename)
        return None


    def save_current_book(self, book):
        if book:
            self.bookmarks_db['current_book'] = book.filename
            self.bookmarks_db.sync()


    def save_bookmarks(self):
        for filename in self._deleted_books:
            if self.bookmarks_db.has_key(filename):
                del self.bookmarks_db[filename]
        self.bookmarks_db['categories_list'] = self.categories_list
        self.bookmarks_db['books_list'] = self.books_list
        self.bookmarks_db['titles_list'] = self.titles_list
        self.bookmarks_db['bookmarks_db_version'] = PROGRAM_VERSION
        for filename in self._books:
            self.bookmarks_db[filename] = self._books[filename]
        self.bookmarks_db.sync()

##bookmarks_db.close()

##----------------------------------------------------------------------
##----------------------------------------------------------------------

class Book:

    def __init__(self):

        self.filename = None # absolute path. NB: filename is in locale charset
        self.author = ''
        self.name = ''
        self.description = None
        self.current_position = 0.0
        self.current_offset = 0
        self.encoding = DEFAULT_ENCODING
        self.file_type = 'plain_text'
        self.internalfilters = []
        self.externalfilter = None
        self.marks_list = []

        # exclusive view
        self.exclusive_view = 0
        self.font = None
        self.fg_color = None
        self.bg_color = None
        self.bm_color = None
        self.link_color = None

        self.genres = ['Default']
        self.categories = self.genres # "categories" is aliased to "genres"


    def __setstate__(self, state): # for backward compatible

        if 'externalfilter' not in state:
            self.externalfilter = None
            self.internalfilters = None

        if 'exclusive_view' not in state:
            self.exclusive_view = 0
            self.font = None
            self.fg_color = None
            self.bg_color = None
            self.bm_color = None

        if 'link_color' not in state:
            self.link_color = None

        if 'genres' not in state:
            self.genres = []

        if 'categories' not in state:
            self.categories = []

        self.__dict__.update(state)


    def add_bookmark(self, position, offset, length, description):

        mark = _Mark()
        mark.position = position
        mark.offset = offset
        mark.length = length
        mark.description = description

        # search uniq number
        num = 0
        while 1:
            found = 0
            for i in self.marks_list:
                if i.number == num:
                    found = 1
                    break
            if not found:
                break
            num = num+1

        mark.number = num
        self.marks_list.append(mark)

        # sort by offset
        self.marks_list.sort(lambda x, y: cmp(x.offset, y.offset))

        return mark

##----------------------------------------------------------------------

    def remove_bookmark(self, mark_number):
        found = 0
        n = 0
        for m in self.marks_list:
            if m.number == mark_number:
                del self.marks_list[n]
                found = 1
                break
            n = n+1
        return found

##----------------------------------------------------------------------

    def get_title(self):
        if self.author and self.name:
            name = self.author + ' - ' +  self.name
        elif self.author:
            name = self.author
        elif self.name:
            name = self.name
        else:
            name = fix_filename(self.filename)
        return name

##----------------------------------------------------------------------

    def get_mark(self, mark_number):
        for mark in self.marks_list:
            if mark_number == mark.number:
                return mark
        return None

##----------------------------------------------------------------------

    def get_mark_at_offset(self, offset):
        for m in self.marks_list:
            if offset >= m.offset and offset <= m.offset+20: #FIXME: length
                return m
        return None

##----------------------------------------------------------------------
##----------------------------------------------------------------------

class Category:

    def __init__(self):

        self.name = 'Default'
        self.description = ''

##----------------------------------------------------------------------

class _Mark:

    def __init__(self):

        self.number = 0       # uniq for this book
        self.position = 0.0
        self.description = ''

        self.author = ''
        self.name = ''

        # offset in file
        self.offset = 0
        # offset in text_buffer (after parsers and filters)
        self.current_offset = 0
        # length of mark
        self.length = 0

    def __setstate__(self, state): # for backward compatible
        if 'current_offset' not in state:
            self.current_offset = 0
        if 'length' not in state:
            self.length = 0
        self.__dict__.update(state)

##----------------------------------------------------------------------
##----------------------------------------------------------------------

if(__name__=="__main__"):

    bookmarks = Bookmarks()

    print '****** books_list ******'
    print

    for book in bookmarks.books_list:

        print 'category =', book.category
        print 'filename =', book.filename
        print 'author =', book.author
        print 'name =', book.name
        print 'description =', book.description
        print 'current_position =', book.current_position
        print 'encoding =', book.encoding
        print

        print '   *** marks_list ***'
        print

        for mark in book.marks_list:

            print '   namber =', mark.number
            print '   offset =', mark.offset
            print '   position =', mark.position
            print '   description =', mark.description
            print '   author =', mark.author
            print '   name =', mark.name
            print

