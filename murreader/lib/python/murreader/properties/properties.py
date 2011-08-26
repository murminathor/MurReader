#!/usr/bin/env python
# -*- coding: utf-8 -*-

from raw_properties import RawPropertiesWrap
from status         import Status
from text_area      import TextArea
from text_styles    import TextStyles
from window         import Window
from config         import STYLES_FILE, WINDOW_FILE, CONFIG_FILE #, RECENT_FILE
__all__ = [ 'Properties' ]
#=============================================================================#


class Properties( RawPropertiesWrap ):
  ''' Все свойства в одном '''
#=============================================================================#
#                                                                             #
#                               Private methods                               #
#                                      v                                      #
#=============================================================================#

  def __init__( self, cfg_styles=STYLES_FILE, cfg_text_area=CONFIG_FILE,
                cfg_status=CONFIG_FILE, cfg_window=WINDOW_FILE,
                show_warning=True ):
    ''' Начальная инициализация экземпляра класса.

        Внимание!!! Для разных полей (styles, text_area, status...) используйте
        РАЗНЫЕ конфигурационные файлы, т.к. перед записью они будут полностью
        ощичены (длина файла == 0 )
    '''
    self.status = Status(config_file=cfg_status,show_warning=show_warning)
    self.styles = TextStyles(config_file=cfg_styles,show_warning=show_warning)
    self.text   = TextArea(config_file=cfg_text_area,show_warning=show_warning)
    self.window = Window(config_file=cfg_window, show_warning=show_warning)
#=============================================================================#
#                                                                             #
#                                Public methods                               #
#                                      v                                      #
#=============================================================================#

  def save( self ):
    ''' Сохраняет все свойства "оптом" '''
    for item in self.__dict__: self.__dict__[item].clear_config()
    for item in self.__dict__: self.__dict__[item].save()
#=============================================================================#

  def clear_config( self ):
    '''Полностью очищает файлы конфигурации (размер файла == 0)'''
    for item in self.__dict__:
      self.__dict__[item].clear_config()
#=============================================================================#
#                                     ^                                       #
#                               End of Class                                  #
#                                                                             #
#=============================================================================#
