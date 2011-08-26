#!/bin/env python
# -*- coding: utf-8 -*-

from raw_properties import *
from config         import STYLES_LIST, STYLES_FILE, DEFAULT_CATEGORY

__all__ = [ 'TextStyles' ]
#=============================================================================#


class ParagraphStyle( RawProperties ):
  '''Свойства оформления параграфа (шрифт, цвет, размер, ...)'''
#=============================================================================#
#                                                                             #
#                               Private methods                               #
#                                      v                                      #
#=============================================================================#

  def __init__(self, name, config_file, show_warning=False ):
    ''' Инициализация экземпляра класса
      
      name          - название стиля параграфа
      config_file   - название конфигурационного файла куда будут сохраняться
                      свойства
      show_warning  - флаг. Если установлен - сообщения об ошибках будут
                      писаться в stderr. По-умолчанию не установлен       
    '''
    property_list = {
    'ascent'            : { 'type':int,  'value': None, 'default': 0         },
    'bold'              : { 'type':bool, 'value': None, 'default': False     },
    'color'             : { 'type':str,  'value': None, 'default': '#000000' },
    'descent'           : { 'type':int,  'value': None, 'default': 0         },
    'font_family'       : { 'type':str,  'value': None, 'default': 'Sans'    },
    'font_size'         : { 'type':int,  'value': None, 'default': 16        },
    'first_line_indent' : { 'type':int,  'value': None, 'default': 20        },
    'hyphenate'         : { 'type':bool, 'value': None, 'default': True      },
    'italic'            : { 'type':bool, 'value': None, 'default': False     },
    'justify'           : { 'type':str,  'value': None, 'default': 'fill'    }, # left | right | center | fill
    'left_indent'       : { 'type':int,  'value': None, 'default': 20        },
    'monospace'         : { 'type':bool, 'value': None, 'default': False     },
    'pixels_above_line' : { 'type':int,  'value': None, 'default': 10        },
    'pixels_below_line' : { 'type':int,  'value': None, 'default': 10        },
    'pixels_inside_wrap': { 'type':int,  'value': None, 'default': 10        },
    'right_indent'      : { 'type':int,  'value': None, 'default': 20        }
                    }

    RawProperties.__init__( self, name, config_file, property_list,
                            show_warning )
#=============================================================================#
#                                     ^                                       #
#                               End of Class                                  #
#                                                                             #
#=============================================================================#


class TextStyles( RawPropertiesWrap ):
  ''' Набор текстовых стилей

      При чтении настроек стилей из файла дефолтные значения всех свойств всех
       стилей выставляются равными значению "базового" стиля - 'paragraph'
  '''

  def __init__( self, config_file=STYLES_FILE, show_warning=False ):
    ''' Инициализация экземпляра класса

      config_file   - имя конфигурационного файла куда будут сохраняться
                      свойства. По умолчанию - берётся из глобального
                      конфигурационного параграфа - config.py
                      ( переменная IFACE_FILE )
      show_warning  - флаг. Если установлен - сообщения об ошибках будут
                      писаться в stderr. По-умолчанию не установлен

      Список стилей параграфов  ( переменная STYLES_LIST ) берётся из
      глобального конфигурационного файла - config.py 
    '''

    # Использование в классе глобальных переменных STYLES_LIST и
    # DEFAULT_CATEGORY обусловлено ленью :)) - Мне лень переписывать все методы
    # класса-предка для этого класса.
    # А переписывать методы придётся, как только появится новое поле класса
    # к примеру self.styles_list. Причина проста - все методы класса-предка
    # предполагают, что в self.__dict__ находятся исключительно экземпляры 
    # класса RawProperties или его потомков. Но никак не строка
    # (<type 'str'>)

    for curr_style in STYLES_LIST:
      self.__dict__[curr_style] = ParagraphStyle( curr_style, config_file,
                                                  show_warning )
    # Некоторые изменения для разных стилей
    self.title.font_size      = 30
    self.title.justify        = 'center'
    self.title.bold           = True

    self.subtitle.font_size   = 25
    self.subtitle.justify     = 'center'
    self.subtitle.bold        = True

    self.epigraph.left_indent = 100
    self.cite.left_indent     = 40
    self.cite.right_indent    = 40
    self.cite.italic          = True

    self.footnote.font_size   = 12

    self.stanza.font_size     = 12
    self.stanza.left_indent   = 30

    self.text_author.italic   = True
    self.text_author.justify  = 'right'

    self.strong.bold          = True
    self.emphasis.italic      = True
#=============================================================================#
#                                                                             #
#                                Public methods                               #
#                                      v                                      #
#=============================================================================#

  def read(self):
    '''Читает настройки для всех стилей "оптом"'''

    # Метод переопределён для того, чтобы у всех стилей дефолтные значения
    # были равны значениям одного, выбранного стиля DEFAULT_CATEGORY

    bs_id = STYLES_LIST.index( DEFAULT_CATEGORY )

    # Читаем настройки базового стиля
    self.__dict__[ DEFAULT_CATEGORY ].read()

    # Читаем настройки всех стилей КРОМЕ базового
    for curr_style in STYLES_LIST[ :bs_id ] + STYLES_LIST[ bs_id + 1 : ]:
      # Для каждого свойства стиля
      for name,curr_item in self.__dict__[curr_style]:
        # приводим его дефолтное значение в соответствии с значением
        # базового стиля
        self.__dict__[curr_style].item_default_set(
                                name,
                                self.__dict__[ DEFAULT_CATEGORY ].item( name )
                                                  )

      self.__dict__[curr_style].read()    
#=============================================================================#
#                                     ^                                       #
#                               End of Class                                  #
#                                                                             #
#=============================================================================#
