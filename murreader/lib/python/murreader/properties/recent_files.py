#!/bin/env python
# -*- coding: utf-8 -*-

from raw_properties import *
from config         import RECENT_FILE, NUM_RECENT_FILES
from time           import ctime

__all__ = [ 'RecentFiles' ]
#=============================================================================#


class RecentFileFilds( RawProperties ):
  '''Свойства оформления параграфа (шрифт, цвет, размер, ...)'''
#=============================================================================#
#                                                                             #
#                               Private methods                               #
#                                      v                                      #
#=============================================================================#

  def __init__(self, name, config_file, show_warning=False ):
    ''' Инициализация экземпляра класса
      
      name          - название/номер недавно открытого файла
      config_file   - название конфигурационного файла куда будут сохраняться
                      свойства
      show_warning  - флаг. Если установлен - сообщения об ошибках будут
                      писаться в stderr. По-умолчанию не установлен       
    '''
    property_list = {
    'filename'          : { 'type':str, 'value': None, 'default': '' },
    'char'              : { 'type':int, 'value': None, 'default': 0  },
    'line'              : { 'type':int, 'value': None, 'default': 0  },
    'encoding'          : { 'type':str, 'value': None, 'default': '' },
    'open_time'         : { 'type':str, 'value': None, 'default': '' },
                    }

    RawProperties.__init__( self, name, config_file, property_list,
                            show_warning )
#=============================================================================#

  ##
  ## Очень сомневаюсь, что эти сравнения будут когда-либо нужны
  ##

  #def __lt__( self, other):
    #''' Сравнение идёт по времени открытия файла - поле open_time'''
    #return float( time.mktime( time.strptime( self.open_time) ) ) < \
           #float( time.mktime( time.strptime( other.open_time) ) )
##=============================================================================#

  #def __le__( self, other):
    #''' Сравнение идёт по времени открытия файла - поле open_time'''
    #return float( time.mktime( time.strptime( self.open_time) ) ) >= \
           #float( time.mktime( time.strptime( other.open_time) ) )
##=============================================================================#

  #def __gt__( self, other):
    #''' Сравнение идёт по времени открытия файла - поле open_time'''
    #return float( time.mktime( time.strptime( self.open_time) ) ) > \
           #float( time.mktime( time.strptime( other.open_time) ) )
##=============================================================================#

  #def __ge__( self, other):
    #''' Сравнение идёт по времени открытия файла - поле open_time'''
    #return float( time.mktime( time.strptime( self.open_time) ) ) >= \
           #float( time.mktime( time.strptime( other.open_time) ) )

#=============================================================================#
#                                     ^                                       #
#                               End of Class                                  #
#                                                                             #
#=============================================================================#


class RecentFiles():
  ''' Работа со списком последних открытых файлов. '''

  def __init__( self, num_recent=NUM_RECENT_FILES, config_file=RECENT_FILE,
                show_warning=False ):
    ''' Инициализация экземпляра класса

      num_recent    - Максимальное количество новых/недавно открытых файлов, о
                      которых будет помнить программа. По умолчанию берётся из
                      глобального конфигурационного параграфа - config.py
                      ( переменная NUM_RECENT_FILES )
      config_file   - имя конфигурационного файла куда будут сохраняться
                      свойства. По умолчанию - берётся из глобального
                      конфигурационного параграфа - config.py
                      ( переменная RECENT_FILE )
      show_warning  - флаг. Если установлен - сообщения об ошибках будут
                      писаться в stderr. По-умолчанию не установлен
    '''

    self.num_recent_files =  num_recent
    self.config_file = config_file
    self.show_warning = show_warning
    self.recent_files = []
    self.section_name_fmt = 'recent%d'  # Формат имени секции
#=============================================================================#

  def __len__(self):
    ''' Метод переопределён для удобства работы '''
    return len( self.recent_files )
#=============================================================================#

  def __iter__(self):
    ''' Метод переопределён для удобства работы '''
    for item in self.recent_files:
      yield item, self.recent_files[item]

#=============================================================================#

  def __str__(self):
    '''Метод определён для удобства работы'''
    result = '{'
    for item in range( self.len() ):
      result += "{'" + str(item) + "':\n  {\n"
      for (item_name, item_data) in self.recent_files[item]:
        result +=  "\t{'" + str(item_name) + "':" + str(item_data) + "}\n"
      result +=  "  }\n"

    return result + '}\n'
#=============================================================================#

  def __repr__(self):
    '''Метод определён для удобства работы'''
    return str( self.recent_files )
#=============================================================================#

  def __index(self, filename):
    ''' Определяет индекс записи с указанным именем файла в конфиге.
        Если такой записи нет - генерирует исключение ValueError
    '''

    # Стандартный метод ( self.recent_files.index() ) не подходит, т.к. у
    # экземпляра обьекта RecentFileFilds будут менятся все поля независимо
    # т.е. при одном и том же filename у сохранённой копии и добавляемой будут
    # различные значения полей line char, open_time, ...
    # Таким образом очень сомнительно, что тут сработает стардантный .index()
    for item in range( self.len() ):
      if self.recent_files[item].filename == filename:
        return item

    raise ValueError

#=============================================================================#
#                                                                             #
#                                Public methods                               #
#                                      v                                      #
#=============================================================================#

  def add(self, filename, line, char, encoding):
    ''' Добавляет файл в список недавно открытых.

        Количество последних файлов определяется значением переменной
        "num_recent_files". Если использованы все num_recent_files записей в
        конфигурационном файле, то добавление нового файла приведёт к удалению
        наиболее старого
    '''

    curr_file = RecentFileFilds( name = self.section_name_fmt%( self.len() ),
                                 config_file  = self.config_file,
                                 show_warning = self.show_warning )
    curr_file.filename  = filename
    curr_file.line      = line
    curr_file.encoding  = encoding
    curr_file.open_time = ctime()

    try:
      #self.recent_files[ self.__index( filename) ] = curr_file
      del self.recent_files[ self.__index( filename) ]
    except ValueError:
      if self.len() >= self.num_recent_files:
        del self.num_recent_files[0]

    self.recent_files.append( curr_file )
  
    return True
#=============================================================================#

  def len(self):
    ''' Метод определён для удобства работы '''
    return len( self.recent_files )
#=============================================================================#

  def read(self):
    '''Читает настройки для всех записей "оптом"'''

    # На момент выполнения этой функции неизвестно точное количество записей в
    # конфиге. Также возможен случай, когда self.num_recent_files == 0, а
    # конфигурациооный файл заполнен "под завязку"
    for item in range( self.num_recent_files ):
      curr_file = RecentFileFilds( name = self.section_name_fmt%( self.len() ),
                                  config_file = self.config_file,
                                  show_warning = self.show_warning )
      curr_file.read()
      if not curr_file.filename: break
      self.recent_files.append( curr_file )

    return True
#=============================================================================#

  def save(self):
    '''Сохраняет настройки для всех записей "оптом"'''
    for item in range( self.len() ):
      self.recent_files[item].section = self.section_name_fmt%item
      self.recent_files[item].save()
#=============================================================================#

  def reset(self):
    '''Сбрасывает "оптом" все значения для всех записей в дефолтные'''
    for item in range( self.len() ):
      self.recent_files[item].reset()
#=============================================================================#

  def clear_config(self):
    '''Полностью очищает файл конфигурации (размер файла == 0)'''

    curr_file = open( self.config_file, 'w')
    curr_file.close()
    return True
#=============================================================================#

  def item(self, item_no=0):
    '''Возвращает элемент с указанным номером'''
    if len( self.recent_files ) > item_no:
      return self.recent_files[item_no]

    return None
#=============================================================================#

  def filename(self, item_no=0):
    '''Возвращает имя файла элемента с указанным номером'''
    if len( self.recent_files ) > item_no:
      return self.recent_files[item_no].filename

    return None
#=============================================================================#

  def line(self, item_no=0):
    '''Возвращает номер строки элемента с указанным номером'''
    if len( self.recent_files ) > item_no:
      return self.recent_files[item_no].line

    return None
#=============================================================================#

  def char(self, item_no=0):
    '''Возвращает номер символа элемента с указанным номером'''
    if len( self.recent_files ) > item_no:
      return self.recent_files[item_no].char

    return None
#=============================================================================#

  def encoding(self, item_no=0):
    '''Возвращает кодировку файла элемента с указанным номером'''
    if len( self.recent_files ) > item_no:
      return self.recent_files[item_no].encoding

    return None
#=============================================================================#

  def open_time(self, item_no=0):
    '''Возвращает время последнего окрытия файла элемента с указанным номером'''
    if len( self.recent_files ) > item_no:
      return self.recent_files[item_no].open_time

    return None
#=============================================================================#
#                                     ^                                       #
#                               End of Class                                  #
#                                                                             #
#=============================================================================#
