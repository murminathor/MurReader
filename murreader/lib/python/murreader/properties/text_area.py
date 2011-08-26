#!/bin/env python
# -*- coding: utf-8 -*-

from raw_properties import RawProperties
from config         import CONFIG_FILE, USER_SKIN_DIR

__all__ = [ 'TextArea' ]
#=============================================================================#

class TextArea( RawProperties ):
  ''' Свойства области, где отрисовывается текст книги '''

  def __init__( self, config_file=CONFIG_FILE, show_warning=False ):
    ''' Инициализация экземпляра класса

      config_file   - имя конфигурационного файла куда будут сохраняться
                      свойства. По умолчанию - берётся из глобального
                      конфигурационного параграфа - config.py
                      ( переменная CONFIG_FILE )
      show_warning  - флаг. Если установлен - сообщения об ошибках будут
                      писаться в stderr. По-умолчанию не установлен
    '''
    property_list = {
      'background_color'      : { 'type':str,  'value': None, 'default': '#ffffff'     },
      'gradient_color'        : { 'type':str,  'value': None, 'default': '#ffffff'     },
      'margin_bottom'         : { 'type':int,  'value': None, 'default': 10            },
      'margin_left'           : { 'type':int,  'value': None, 'default': 20            },
      'margin_right'          : { 'type':int,  'value': None, 'default': 20            },
      'margin_top'            : { 'type':int,  'value': None, 'default': 30            },
      'new_page'              : { 'type':bool, 'value': None, 'default': False         },
      'path_to_background'    : { 'type':str,  'value': None, 'default': USER_SKIN_DIR },
      'single_column'         : { 'type':bool, 'value': None, 'default': False         },
      'spaces_between_column' : { 'type':int,  'value': None, 'default': 30            },
      'use_background'        : { 'type':bool, 'value': None, 'default': True          },
      'use_gradient'          : { 'type':bool, 'value': None, 'default': False         }
                    }

    RawProperties.__init__( self, 'text_area', config_file, property_list,
                            show_warning )
#=============================================================================#
#                                     ^                                       #
#                               End of Class                                  #
#                                                                             #
#=============================================================================#
