#!/bin/env python
# -*- coding: utf-8 -*-

from raw_properties import RawProperties
from config         import WINDOW_FILE, DEFAULT_SKIN, PROGRAM_NAME, USER_SKIN_DIR

__all__ = [ 'Window' ]
#=============================================================================#

class Window( RawProperties ):
  ''' Общие свойства окна программы '''

  def __init__( self, config_file=WINDOW_FILE, title=PROGRAM_NAME,
                show_warning=False ):
    ''' Инициализация экземпляра класса

      config_file   - имя конфигурационного файла куда будут сохраняться
                      свойства. По умолчанию - берётся из глобального
                      конфигурационного параграфа - config.py
                      ( переменная CONFIG_FILE )
      title         - Текст в "шапке" окна
      show_warning  - флаг. Если установлен - сообщения об ошибках будут
                      писаться в stderr. По-умолчанию не установлен
    '''
    property_list = {
      'hide_menu'       : { 'type':bool, 'value': None, 'default': False },
      'width'           : { 'type':int,  'value': None, 'default': 800   },
      'height'          : { 'type':int,  'value': None, 'default': 600   },
      'title_format'    : { 'type':str,  'value': None, 'default': title }
                    }

    RawProperties.__init__( self, 'window', config_file, property_list,
                            show_warning )

#=============================================================================#
#                                     ^                                       #
#                               End of Class                                  #
#                                                                             #
#=============================================================================#
