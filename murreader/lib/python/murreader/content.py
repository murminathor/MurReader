#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''Предоставляет инструменты для чтения файла в память. 
   В т.ч. и с разархивированием.
   При этом изначальный формат файла теряет своё значение, т.к. результат работы
   функции представлятеся в виде экземпляра класса "Content"
'''
__all__ = [ 'Content' ]

from cStringIO import StringIO
from textparagraph import TextParagraph

# Класс исключения для случая неизвестного архиваторов
class UnpackError( Exception ): pass

class Content:
  '''Класс, имеющий целью унифицировать представление содержимого книги
    вне зависимости от её начального формата (fb2, text, html, ... )
  '''

  def __init__(self, fileName = None, encoding = None, lang = None):
    self.content     = []
    self.title       = ''
    self.authors     = ''
    self.titles      = []
    self.footnotes   = {}
    self.images      = {}
    self.cover       = []
    self.description = []
    self.genres      = []
    self.textLength  = 0
    self.fileName    = fileName
    self.encoding    = encoding
    self.lang        = lang
    self.fileContent = ''

    if fileName:
        self.get( self.fileName )
        self.contentLen = len( self.content )
  #============================================================================

  def get( self, fileName ):
    '''Читает файла в память. В т.ч. и с разархивированием.
      При этом изначальный формат файла теряет своё значение,
      т.к. результат работы функции представлятеся в виде BookData
    '''
    self.fileName    = fileName
    self.fileContent = open( self.fileName ).read()

    # Пытаемся распаковать файл.
    try:
      self.unpackFile()
    # Если это не удаётся - ничего страшного, возможно файл просто не упакован
    except UnpackError:
      pass
    
    # Если это xml, то, возможно это FB2
    if self.fileContent.startswith('<?xml'):
      self.openFB2()

    # Иначе - пробуем читать как обычный текст
    else:
      self.openPlainTextFile()

    # Вычисляем общую длину текста
    if self.content:
      self.textLength = reduce(lambda x, y: x+len(y.data),
                                self.content, 0)
    return True
  #============================================================================

  def unpackFile( self ):
    '''Распаковывает файл, для следующих наборов архиваторов:
      gzip, bzip2, zip

      Для zip-архивов не вероятен случай, когда в архиве находится несколько
      файлов. В таком случае будут пропущены файлы 'file_id.diz' и 'comment.txt'
      (без учёта регистра) и выбран ПЕРВЫЙ в файл из списка.

      Во всех остальных случаях генерирует ошибку: "Unknown archive format"
    '''
    
    if not self.fileContent:
      return False

    # Пробуем распаковать файл. При этом ориентируемся на оглавления файлов, 
    # а не их расширения      
    if self.fileContent.startswith('\x1f\x8b'):
      import gzip
      self.fileContent = gzip.GzipFile( fileobj = StringIO( self.fileContent ) 
                                      ).read()
      return True

    elif self.fileContent.startswith('BZh'):
      import bz2
      self.fileContent = bz2.decompress( self.fileContent )
      return True

    elif self.fileContent.startswith('PK\x03\x04'):
      import zipfile
      self.fileContent = zipfile.ZipFile( StringIO( self.fileContent ) )

      # Для zip-архивов не вероятен случай, когда в архиве находится
      # несколько файлов
      for name in self.fileContent.namelist():
        if name.lower() not in ['file_id.diz', 'comment.txt']:
          self.fileContent = self.fileContent.read( name )
          return True
          #break

    # Если ничего не сработало - формат архива неизвестен
    raise UnpackError, 'Unknown archive format'
  #============================================================================

  def  openPlainTextFile( self ):
    '''Обрабатыавет простой текст: перекодирование в utf-8, уборка "мусора", 
      приведение в независимое представление
    '''
    if not self.fileContent:
      return False
    
    if not self.encoding:
      from detectcharset import detectcharset
      import locale
      self.encoding = detectcharset( StringIO( self.fileContent ) ) or \
                      locale.getdefaultlocale()[1]    or \
                      'iso8859-1'

    # remove \x00 chars
    self.fileContent = self.fileContent.replace('\0', '')
    self.fileContent = unicode( self.fileContent, self.encoding )

    # Переводим результат парсинга в незавсимое от начального формата файла
    # представление
    self.content = []
    for l in self.fileContent.splitlines():
      paragraph = TextParagraph( 'paragraph' )
      paragraph.data = l
      self.content.append( paragraph )
    #BookData.content = content

    # Конвертируем всё содержимое в utf-8
    # FIXME: Проблема с кодировками в hyphenation.py
    #        требуется привести все словари к utf-8
    #self.__content_to_utf8()

    return True
  #============================================================================

  def openFB2( self ):
    '''Парсит fb2-файл и переводит его в независимое представление'''
    
    if not self.fileContent:
      return False
    
    from fb2parser import FB2Parser
    from libxml2 import parserError
    from string import join

    fb = FB2Parser( TextParagraph )
    fb.parseFB2( self.fileContent )

    # Переводим результат парсинга в незавсимое от начального формата файла
    # представление
    self.content    = fb.content
    self.lang       = fb.lang
    self.title      = fb.book_title
    self.authors    = join( fb.authors, ', ' )
    self.titles     = fb.titles_list
    self.images     = fb.images
    self.cover      = fb.cover
    self.footnotes  = fb.footnotes
    self.genres     = fb.genres
    
    # Чистим память
    fb = None

    # Конвертируем всё содержимое в utf-8
    # FIXME: Проблема с кодировками в hyphenation.py
    #        требуется привести все словари к utf-8
    #self.__content_to_utf8()
    
    return True
  #============================================================================

  def __getitem__( self, key ):
    '''Позволяет получить или конкретный параграф или же срез (слайс) из
    параграфов простым указанием индекса(ов)
    '''
    
    from types import SliceType
    if type(key) == SliceType:
        return self.content[key.start:key.stop]
    else:
        return self.content[key]
  #============================================================================

  def __len__(self):
    '''Возвращает количество параграфов'''
    return len( self.content )
  #============================================================================

  def __str__(self):
    '''Возвращает текстовое представление параграфов - "всё в одном"'''
    data = ''
    for item in self.content:
      data += item.data.encode('utf-8') + "\n"
    return data
  #============================================================================

  def __content_to_utf8(self):
    '''__content_to_utf8()

      Меняет кодировку всему контенту на utf-8
    '''
    content = []
    contentItem = None

    for item in self.content:
      contentItem = item
      contentItem.data = item.data.encode('utf-8')
      content.append( contentItem )

    self.content = content
#==============================================================================

