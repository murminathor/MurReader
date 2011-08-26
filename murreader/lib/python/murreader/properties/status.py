#!/bin/env python
# -*- coding: utf-8 -*-

from raw_properties import RawProperties
from config         import CONFIG_FILE

__all__ = [ 'Status' ]
#=============================================================================#

class Status( RawProperties ):
  ''' Свойства строки состояния '''

  def __init__( self, config_file=CONFIG_FILE, show_warning=False ):
    ''' Инициализация экземпляра класса

      config_file   - имя конфигурационного файла куда будут сохраняться
                      свойства. По умолчанию - берётся из глобального
                      конфигурационного параграфа - config.py
                      ( переменная CONFIG_FILE )
      show_warning  - флаг. Если установлен - сообщения об ошибках будут
                      писаться в stderr. По-умолчанию не установлен
    '''

    # TODO: Перевести оформление текста на ParagraphStyle
    property_list = {
      'font'         : { 'type':str,  'value': None, 'default': 'Sans 16' },
      'color'        : { 'type':str,  'value': None, 'default': '#000000' },
      'show'         : { 'type':bool, 'value': None, 'default': True      },
      'y'            : { 'type':int,  'value': None, 'default': 10        },
      'clock_x'      : { 'type':int,  'value': None, 'default': 30        },
      'clock_show'   : { 'type':bool, 'value': None, 'default': True      },
      'percent_x'    : { 'type':int,  'value': None, 'default': 30        },
      'percent_show' : { 'type':bool, 'value': None, 'default': True      }
                    }
    RawProperties.__init__( self, 'status', config_file, property_list,
                            show_warning )

#=============================================================================#
#                                     ^                                       #
#                               End of Class                                  #
#                                                                             #
#=============================================================================#
