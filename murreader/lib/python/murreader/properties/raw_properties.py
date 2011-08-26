#!/bin/env python
# -*- coding: utf-8 -*-
import sys

from ConfigParser import ConfigParser #, DuplicateSectionError

__all__ = [ 'RawProperties', 'RawPropertiesWrap' ]

#=============================================================================#

class RawProperties():
  '''Абстрактный класс для свойств. Нужен для лучшей масштабируемости'''

  section = ''       # Имя секции в конфигурационном файле
  config_file = ''   # Имя файла конфигурации
  show_warning = None
  # Чтобы не проверять одно и то же  по многу раз в циклах
  # Функция для вывода сообщений об ошибках
  __error_msg       = None
#=============================================================================#
#                                                                             #
#                               Private methods                               #
#                                      v                                      #
#=============================================================================#

  def __init__(self, name, config_file, property_list, show_warning=False ):
    '''Инициализация класса

      name          - имя группы свойств/секции в конфигурационном файле
      config_file   - название конфигурационного файла куда будут сохраняться
                      свойства
      property_list - список свойств в формате:
                      { # Имя свойства/параметра в конфигурационном файле
                        property_name: { # функция, определяющая тип значения
                                        'type':   int|float|str|bool,
                                        # Собственно само значение или None
                                        'value':   None,
                                        # Значение по-умолчанию. Использутеся
                                        # если 'value' is None
                                        'default': default_value},
                       ...
                      }
      show_warning -  флаг. Если установлен - сообщения об ошибках будут
                      писаться в stderr. По-умолчанию не установлен
    '''
    self.__dict__['section']     = name
    self.__dict__['config_file'] = config_file
    self.__dict__['__prop']      = property_list

    # Чтобы не проверять одно и то же  по многу раз в циклах
    # Функция для вывода сообщений об ошибках
    self.__dict__['_RawProperties__error_msg'] = self.__error_msg_dummy
    if show_warning:
      self.__dict__['_RawProperties__error_msg'] = self.__error_msg_work

#=============================================================================#

  def __setattr__(self, name, value):
    '''Метод задания свойств и их значений переопределён для обеспечения
       возможности:
          - использовать значения свойств по умолчанию;
          - "автоматическое" приведение типов (особенно при чтении/записи
            в/из файл(а) )
          - защита от случайного задания нового свойства
    '''
    try:
      if self.__dict__.has_key(name):
        self.__dict__[name] = value
      else:
        raise KeyError
    except KeyError:
      # Значение может содержать и False, которое тоже требуется принимать
      if value is None:
        self.__dict__['__prop'][name]['value'] = \
        self.__dict__['__prop'][name]['default']
      else:
        self.__dict__['__prop'][name]['value'] = \
        self.__dict__['__prop'][name]['type']( value )

    return True
#=============================================================================#

  def __getattr__(self, name):
    '''Метод задания свойств и их значений переопределён для обеспечения
       возможности:
          - использовать значения свойств по умолчанию;
          - "автоматическое" приведение типов (особенно при чтении/записи
            в/из файл(а) )
    '''
    try:
      self.__dict__[name]
    except KeyError:
      if self.__dict__['__prop'][name]['value']:
        return self.__dict__['__prop'][name]['value']

      return self.__dict__['__prop'][name]['default']
#=============================================================================#

  def __str__(self):
    '''Метод определён для удобства отладки'''
    return "\t" + str( self.__dict__['__prop'] ) + "\n"
#=============================================================================#

  def __len__(self):
    '''Метод определён для удобства работы'''
    return len( self.__dict__['__prop'] )
#=============================================================================#

  def __iter__(self):
    '''Метод определён для удобства работы'''
    for item in self.__dict__['__prop']:
      yield item, self.__dict__['__prop'][item]
#=============================================================================#

  def __repr__(self):
    '''Метод определён для удобства работы'''
    return str( self.__dict__['__prop'] )
#=============================================================================#

  def __error_msg_work( self, error ):
    '''__error_msg_work( error )

        \param  error       - само сообщение
        Выводит сообщение об ошибке, возникшей при работе с конфигурационными
        файлами
    '''
    sys.stderr.write(
                      "ERROR: (file '%s'; section '%s'): %s\n" % \
                      ( self.config_file, self.section, str(error) )
                    )
    return True
#=============================================================================#

  def __error_msg_dummy( self, error ):
    '''__error_msg_dummy( error, section='main' )

        \param  error       - само сообщение
        Заглушка для вывода сообщений об ошибке, возникшей при работе с
        конфигурационными файлами.
    '''
    return True

#=============================================================================#
#                                                                             #
#                                Public methods                               #
#                                      v                                      #
#=============================================================================#

  def item(self, item_name ):
    '''Возвращает указанный элемент/поле/"стиль"'''

    return self.__getattr__( item_name )
#=============================================================================#

  def item_type(self, item_name ):
    '''Возвращает тип элемента/поля/"стиля"'''

    return self.__dict__['__prop'][item_name]['type']
#=============================================================================#

  def item_default(self, item_name ):
    '''Возвращает значение по-умолчанию элемента/поля/"стиля"'''

    return self.__dict__['__prop'][item_name]['default']
#=============================================================================#

  def item_default_set(self, item_name, default_value ):
    '''Изменяет значение по-умолчанию элемента/поля/"стиля"'''

    self.__dict__['__prop'][item_name]['default'] = \
                  self.__dict__['__prop'][item_name]['type'](default_value)
#=============================================================================#

  def item_value_set(self, item_name, value ):
    '''Изменяет значение элемента/поля/"стиля"/

       Использутеся когда нужен доступ к отдельному элементу из функции/цикла
      ( конструкции вида somth.item( item_name ) =>
                         somth.item_value_set( item_name, new_value )
      )
    '''

    self.__dict__['__prop'][item_name]['value'] = \
                  self.__dict__['__prop'][item_name]['type'](value)
#=============================================================================#


  def read(self):
    '''Читает список параметров из файла конфигурации и инициализирует их
      значения. Если какого-то значения нет - берётся значение по умолчанию
    '''
    try:
      config_file = open(  self.config_file , 'rb')
    except IOError, err:
      self.__error_msg( str(err) + " Can't open config file" )
      # Нечего дальше делать - в любом случае дефолтные  значения доступны
      return

    cfgp = ConfigParser()
    cfgp.read( self.config_file )

    for prop in self.__dict__['__prop']:
      # Читаем свойство из конфига
      try:
        # в зависимости от типа переменной выбираем нужную функцию чтения
        # выбирается отдельная функция вместо простого приведения типов
        # т.к. bool("True") == True, НО! bool("False") == bool("Yes") == True
        if self.__dict__['__prop'][prop]['type'] is int:
          self.__dict__['__prop'][prop]['value'] = \
                cfgp.getint(self.section, prop)

        elif self.__dict__['__prop'][prop]['type'] is bool:
          self.__dict__['__prop'][prop]['value'] = \
                cfgp.getboolean(self.section, prop)

        elif self.__dict__['__prop'][prop]['type'] is float:
          self.__dict__['__prop'][prop]['value'] = \
                cfgp.getfloat(self.section, prop)

        else:
          self.__dict__['__prop'][prop]['value'] = \
                self.__dict__['__prop'][prop]['type'](
                                       cfgp.get(self.section, prop)
                                                     )
      except Exception, err:
        # Если что-то не так - берём значение по-умолчанию
        self.__dict__['__prop'][prop]['value'] = \
              self.__dict__['__prop'][prop]['default']

    config_file.close()
    return True
#=============================================================================#

  def save(self):
    '''Сохраняет список параметров в файл конфигурации. Если значение какого-то
       параметра равно его дефолтному значению, то такой параметр НЕ
       сохраняется (а смысл? ;) )

      Файл конфигурации открывается на ДОПОЛНЕНИЕ!!! Иначе в одном файле никак
      не "уживётся" более одного набора свойств. Для очистки файла конфигурации
      используйте clear_config()
    '''
    try:
      config_file = open(  self.config_file , 'a')
    except IOError, err:
      self.__error_msg( str(err) + " Can't open config file" )
      # Нечего дальше делать - в любом случае дефолтные  значения доступны
      return

    cfgp = ConfigParser()
    cfgp.add_section( self.section )

    for prop in self.__dict__['__prop']:
      # Значение может содержать и False, которое тоже требуется записывать
      if ( self.__dict__['__prop'][prop]['value']  is not None ) and not \
         ( self.__dict__['__prop'][prop]['value']  == \
           self.__dict__['__prop'][prop]['default']  ):

        cfgp.set( self.section, prop,
                        self.__dict__['__prop'][prop]['value']
                )
    # Если секция пуста - бесмысленно её записывать
    if cfgp.options( self.section ):
      cfgp.write( config_file )

    config_file.close()
    return True
#=============================================================================#

  def reset(self):
    '''Сбрасывает все значения в дефолтные'''
    for prop in self.__dict__['__prop']:
      self.__dict__['__prop'][prop]['value'] = None
    return True
#=============================================================================#

  def clear_config(self):
    '''Полностью очищает файл конфигурации (размер файла == 0)'''
    try:
      config_file = open(  self.config_file , 'w')
    except IOError, err:
      self.__error_msg( str(err) + " Can't clear config file" )

    config_file.close()
    return True
#=============================================================================#
#                                     ^                                       #
#                               End of Class                                  #
#                                                                             #
#=============================================================================#

class RawPropertiesWrap():
  ''' Обёртка для наследования. Исключительно для уменьшения работы'''

#=============================================================================#
#                                                                             #
#                               Private methods                               #
#                                      v                                      #
#=============================================================================#

  def __str__(self):
    '''Метод определён для удобства работы'''
    result = ''
    for item in self.__dict__:
      result += "{'" + str(item) + "':\n  {\n"
      for (item_name, item_data) in self.__dict__[item]:
        result +=  "\t{'" + str(item_name) + "':" + str(item_data) + "}\n"
      result +=  "  }\n}\n"

    return result
#=============================================================================#

  def __iter__(self):
    '''Метод определён для удобства работы'''
    for item in self.__dict__:
      yield item, self.__dict__[item]

#=============================================================================#
#                                                                             #
#                                Public methods                               #
#                                      v                                      #
#=============================================================================#

  def item(self, item_name ):
    '''Возвращает указанный элемент/поле/"стиль"'''

    # Возвращение "указателя" на элемент, а не его копии НЕ случайность
    # Такой "финт ушами" нужен для доступа к произвольному элементу/полю класса
    # внутри "чужих" функций/циклов и т.п.
    return self.__dict__[ item_name ]
#=============================================================================#

  def read(self):
    '''Читает настройки для всех стилей "оптом"'''
    for item in self.__dict__:
      self.__dict__[item].read()
#=============================================================================#

  def save(self):
    '''Сохраняет настройки для всех стилей "оптом"'''
    for item in self.__dict__:
      self.__dict__[item].save()
#=============================================================================#

  def reset(self):
    '''Сбрасывает "оптом" все значения для всех стилей в дефолтные'''
    for item in self.__dict__:
      self.__dict__[item].reset()
#=============================================================================#

  def clear_config(self):
    '''Полностью очищает файл конфигурации (размер файла == 0)'''

    # Быдлокодище... Но сейчас я тупо не знаю как получить произвольный элемент
    # словаря не  зная ни одного ключа этого самого словаря :(...
    for item in self.__dict__:
      self.__dict__[item].clear_config()
      break
#=============================================================================#
#                                     ^                                       #
#                               End of Class                                  #
#                                                                             #
#=============================================================================#
