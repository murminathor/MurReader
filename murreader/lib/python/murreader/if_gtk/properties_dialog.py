#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys, os

#sys.path.append('../')

#import copy

import gtk
import pango
import gobject
from properties import *
from gtk        import gdk, glade
from config     import *
from dialog     import select_color, select_font, select_folder
from gradient   import create_buffer_rgb

__all__ = [ 'PropertiesDialog' ]

#JUSTIFY_LIST = ( 'left', 'right', 'center', 'fill')

class PropertiesDialog(gobject.GObject):
#=============================================================================#
#                                                                             #
#                               Private methods                               #
#                                      v                                      #
#=============================================================================#

    def __init__(self, parent_window, properties, glade_file):

        gobject.GObject.__init__(self)

        wTree = glade.XML(glade_file, 'prop_dialog')
        self.window = wTree.get_widget('prop_dialog')
        self.window.set_transient_for(parent_window)
        wTree.signal_autoconnect(self)
        self.wTree = wTree
        
        #self.properties = copy.copy(properties)
        self.properties = properties

        self.properties.read()

        for w_item in (
                       # Настройки окна программы
                       'window_title_format_entry',
                       'window_hide_menu_check',

                       # Настройки строки состояния
                       'status_show_check',
                       'status_y_spin',
                       'status_percent_show_check',
                       'status_percent_x_spin',
                       'status_clock_show_check',
                       'status_clock_x_spin',

                       # Настройки области отрисовки текста
                       'text_single_column_check',
                       'text_new_page_check',
                       'text_use_background_check',
                       'text_path_to_background_entry',
                       'text_use_gradient_check',
                       'text_margin_top_spin',
                       'text_margin_bottom_spin',
                       'text_margin_left_spin',
                       'text_margin_right_spin',
                       'text_spaces_between_column_spin'
                      ):
          self.__widget_set_value( w_item )


        self.wTree.get_widget('styles_justify_list').set_active(0)

        self.current_style = 'paragraph'
        self.get_style_settings( self.current_style )

        self.wTree.get_widget('styles_style_list').set_active(0)

        # Выставляем начальную подсказку о ...
        self.__build_tooltip_status_color() # ... цвете шрифта статуса
        self.__build_tooltip_status_font()  # ... самом шрифте 

        self.window.show()

#=============================================================================#

    def __build_font_description(self, family, size='', is_italic=False,
                                 is_bold=False):
        '''Строит описание шрифта подобное pango.FontDescription.to_string()

           \param family - семейство шрифтов (имя шрифта)
           \param size   - размер шрифта
           \param is_italic - True если курсив и False в ином случае
           \param is_bold   - True если полужирнй и False в ином случае
           \return          - строка с описанием шрифта
        '''
        desc = str( family ) + ' '
        if is_italic: desc += 'italic '
        if is_bold:   desc += 'bold '
        desc += str( size )

        return desc
#=============================================================================#

    def __build_tooltip_status_color( self ):
        '''Формирует и наполняет всплывающую подсказку с информацией о цвете
           шрифта "строки состояния"
        '''

        for widget in ('status_color_button', 'status_color_label'):
            self.wTree.get_widget(widget).set_tooltip_text(
                             self.properties.status.color )
#=============================================================================#

    def __build_tooltip_status_font( self ):
        '''Формирует и наполняет всплывающую подсказку с информацией о шрифте
           "строки состояния"
        '''

        for widget in ('status_font_button', 'status_font_label'):
            self.wTree.get_widget(widget).set_tooltip_text(
                             self.properties.status.font  )
#=============================================================================#


    def __style_build_font_description(self, curr_style ):
        '''Строит описание шрифта подобное pango.FontDescription.to_string()
           для указанного стиля

           \param curr_style - стиль, для которого нужно построить
                               описание шрифта
           \return          - строка с описанием шрифта
        '''
        return self.__build_font_description(
                                      curr_style.font_family,
                                      curr_style.font_size,
                                      curr_style.italic,
                                      curr_style.bold
                                            )
#=============================================================================#


    def __is_font_eq_default(self, curr_prop):
        '''Определяет является-ли текущий шрифт (семейство + размер + стили)
           идентичным значениям по-умолчанию

           \param curr_prop - текущее свойство, для которого нужно определить
                              равенство шрифта значению по-умолчанию

           return True если все значения равны дефолтным и False в ином случае
        '''

        return ( curr_prop.font_family == \
                 curr_prop.item_default('font_family') ) and \
               ( curr_prop.font_size == \
                 curr_prop.item_default('font_size')   ) and \
               ( curr_prop.italic == \
                 curr_prop.item_default('italic')      ) and \
               ( curr_prop.bold == \
                 curr_prop.item_default('bold')        )
#=============================================================================#

    def __redraw_gradient_area(self):

        da = self.wTree.get_widget('text_gradient_drawingarea')
        if not da.window: return
        style = da.get_style()
        gc = style.fg_gc[gtk.STATE_NORMAL]
        x, y, w, h, depth = da.window.get_geometry()

        c1 = self.properties.text.background_color
        if self.wTree.get_widget('text_use_gradient_check').get_active():
            c2 = self.properties.text.gradient_color
            buff = create_buffer_rgb(w, h, c1, c2)
        else:
            buff = create_buffer_rgb(w, h, c1)

        da.window.draw_rgb_image(gc, 0, 0, w, h, gdk.RGB_DITHER_NONE, buff, w*3)
#=============================================================================#

    def __set_style_checks_active(self, style):
        '''Выставляет флажки чек-боксов в "on" если значение свойства
           отличается от значения по-умолчанию. И, соответственно в "off" в ином
           случае
        '''

        curr_style_items = self.properties.styles.item( style )

        # Пробегаемся по флажкам
        for prop_name in (
                      'color',
                      'first_line_indent',
                      'left_indent',
                      'right_indent',
                      'pixels_above_line',
                      'pixels_below_line',
                      'pixels_inside_wrap',
                      'hyphenate',
                      'justify'
                      ):
            self.wTree.get_widget('styles_' + prop_name + '_check').set_active(
                              curr_style_items.item( prop_name )        != \
                              curr_style_items.item_default( prop_name )
                                                                            )
        # Теперь то же самое - для шрифта
        self.wTree.get_widget('styles_font_check').set_active(
                             not self.__is_font_eq_default( curr_style_items )
                                                             )
#=============================================================================#

    def __widget_set_value( self, widget_name ):
        '''Выбирает виджет и устанавливает его значения исходя значения
           сответствующего свойства (properties)

           \param widget_name - имя виджета
        '''

        # Знаю, что через *опу...
        prop_name_end   = widget_name.rfind('_') + 1
        prop_name_begin = widget_name.find('_')
        widget_suffix   = widget_name[ prop_name_end : ]
        section         = widget_name[ :prop_name_begin]
        prop_name       = widget_name[ prop_name_begin + 1 : prop_name_end-1 ]
        value           = self.properties.item( section ).item(prop_name)

        curr_widget = self.wTree.get_widget( widget_name )

        if widget_suffix == 'check':
          curr_widget.set_active( value )
        elif widget_suffix == 'spin':
          curr_widget.set_value( value )
        else:
          curr_widget.set_text( value )
#=============================================================================#
#                                                                             #
#                                Public methods                               #
#                                      v                                      #
#=============================================================================#

    def get_style_settings(self, style):
        '''Получает значения элементов вкладки со стилями для выбранного стиля
           из конфигурационного файла
           
           \param style - имя/название стиля
        '''

        # Для сокращения длины записи
        curr_style_items = self.properties.styles.item( style )

        # Пробегаемся по счётчикам
        for prop_name in ( 'first_line_indent',
                           'left_indent',
                           'right_indent',
                           'pixels_above_line',
                           'pixels_below_line',
                           'pixels_inside_wrap'
                         ):
             self.wTree.get_widget('styles_' + prop_name + '_spin').set_value(
                                      curr_style_items.item( prop_name )
                                                                             )

        # Определяем отдельно значения для шрифта ...
        font_desc = self.__build_font_description(
                                      curr_style_items.font_family,
                                      curr_style_items.font_size,
                                      curr_style_items.italic,
                                      curr_style_items.bold
                                                            )


        self.wTree.get_widget('styles_font_description_label').set_text(
                              self.__build_font_description(
                                      curr_style_items.font_family,
                                      curr_style_items.font_size,
                                      curr_style_items.italic,
                                      curr_style_items.bold
                                                            )
                                                                 )
        # ..., переноса слов ...
        #curr_prop =  curr_style_items.hyphenate
        self.wTree.get_widget('styles_hyphenate_setter').set_active(
                               curr_style_items.hyphenate
                                                                   )
        # ... и выравнивания
        curr_prop =  curr_style_items.justify
        self.wTree.get_widget('styles_justify_list').set_active (
                                                JUSTIFY_LIST.index( curr_prop )
                                                                )

        # И наконец расставляем флажки
        self.__set_style_checks_active( style )
#=============================================================================#

    def on_styles_style_list_changed(self, entry):
        style = entry.get_active_text()
        if not style: return

        self.current_style = style.lower()

        self.get_style_settings( self.current_style )
#=============================================================================#

    def on_close_clicked(self, *args):
        self.window.destroy()
#=============================================================================#

    def on_apply_clicked(self, *args):
        '''Сохраняем изменения в конфигурационных файлах и отправляем сообщение
           о свершившихся изменениях
        '''

        self.properties.save()
        self.emit('properties-apply')
#=============================================================================#

    def on_styles_font_button_clicked(self, w):
        curr_style = self.properties.styles.item( self.current_style )
        f_desc = self.__style_build_font_description( curr_style )

        pango_font = select_font( self.window, f_desc, 'Style font' )

        if pango_font:
            curr_style.font_family = str( pango_font.get_family() )
            curr_style.font_size = int( pango_font.get_size()/pango.SCALE )
            curr_style.bold = \
                 bool( pango_font.get_weight() > pango.WEIGHT_NORMAL )
            curr_style.italic = \
                 bool( pango_font.get_style() == pango.STYLE_ITALIC )

            self.wTree.get_widget('styles_font_description_label').set_text(
                 pango_font.to_string()   )
#=============================================================================#

    def on_status_font_button_clicked(self, w):
        pango_font = select_font(
                                  self.window,
                                  self.properties.status.font,
                                  'Status font'
                                )
        if pango_font:
            self.properties.status.font = pango_font.to_string()
            self.__build_tooltip_status_font()
#=============================================================================#

    def on_status_color_button_clicked(self, w):
        self.properties.status.color = select_color(
                                              self.window,
                                              self.properties.status.color,
                                              'Select status color'
                                                    )
        self.__build_tooltip_status_color()
#=============================================================================#

    def on_styles_color_setter_clicked(self, w):
        curr_style = self.properties.styles.item( self.current_style )
        curr_style.color = \
             select_color( self.window, curr_style.color, 'Select font color' )
#=============================================================================#

    def on_text_bg_color_button_clicked(self, w):
        self.properties.text.background_color = select_color(
                                          self.window,
                                          self.properties.text.background_color,
                                         'Select background color'
                                                             )
        self.__redraw_gradient_area()
#=============================================================================#

    def on_text_gradient_color_button_clicked(self, w):
        self.properties.text.gradient_color = select_color(
                                        self.window,
                                        self.properties.text.gradient_color,
                                       'Select gradient color'
                                                          )
        self.__redraw_gradient_area()
#=============================================================================#

    def on_text_select_path_button_clicked(self, w):
        filename = select_folder( self.window,
                                  'Select path to background',
                                  self.properties.text.path_to_background
                                )
        if filename:
            self.wTree.get_widget('text_path_to_background_entry').set_text(
                  filename)
            self.properties.text.path_to_background = filename
#=============================================================================#

    def on_text_use_background_check_toggled(self, w):
        is_w_active = w.get_active()

        self.wTree.get_widget('text_path_to_background_entry').set_sensitive( is_w_active )
        self.wTree.get_widget('text_select_path_button').set_sensitive( is_w_active )
        self.wTree.get_widget('text_bg_color_button').set_sensitive( not is_w_active )
        self.wTree.get_widget('text_use_gradient_check').set_sensitive( not is_w_active )

        if is_w_active:
            self.wTree.get_widget('text_gradient_color_button').set_sensitive(False)
        else:
            self.wTree.get_widget('text_gradient_color_button').set_sensitive(
                self.wTree.get_widget('text_use_gradient_check').get_active())
#=============================================================================#

    def on_styles_hyphenate_check_toggled(self, widget ):
        self.wTree.get_widget('styles_hyphenate_setter').set_sensitive(
                                                  widget.get_active() )
#=============================================================================#

    def on_styles_font_check_toggled(self, check):
        self.wTree.get_widget('styles_font_button').set_sensitive(
            check.get_active() )
#=============================================================================#

    def on_styles_color_check_toggled(self, check):
        self.wTree.get_widget('styles_color_setter').set_sensitive(
            check.get_active())
#=============================================================================#

    def on_styles_justify_check_toggled(self, check):
        self.wTree.get_widget('styles_justify_list').set_sensitive(
            check.get_active())
#=============================================================================#

    def on_styles_hyphenate_setter_toggled(self, widget ):
        widget.set_label( widget.get_active() and 'Yes' or 'No' )
        #self.properties.styles.item( self.current_style ).hyphenate = \
        self.properties.styles.item( self.current_style ).item_value_set(
                                                     'hyphenate',
                                                      widget.get_active()
                                                                        )
        #print( self.properties.styles.item( self.current_style) )
#=============================================================================#

    def on_gradient_check_toggled(self, check):
        self.wTree.get_widget('text_gradient_color_button').set_sensitive(
            check.get_active())
        self.__redraw_gradient_area()
#=============================================================================#

    def on_status_show_check_toggled( self, check):
        is_check_active = check.get_active()
        for item in ( 'status_y_spin',
                      'status_font_button',
                      'status_color_button',
                      'status_percent_show_check',
                      'status_percent_x_spin',
                      'status_clock_show_check',
                      'status_clock_x_spin'
                    ):
            self.wTree.get_widget( item ).set_sensitive( is_check_active )
#=============================================================================#

    def on_text_gradient_drawingarea_expose_event(self, *args):
        self.__redraw_gradient_area()
#=============================================================================#

    def on_window_title_format_entry_changed( self, ch_widget ):
        self.properties.window.title_format = ch_widget.get_text()
#=============================================================================#

    def on_styles_check_toggled( self, widget ):
      '''Обработка событий при изменении "флажков"/check's стилей.
         При этом эти флаги относятся к свойствам строки (секция Line в
         диалоговом окне )
      '''
      # len( 'check' ) == 5
      self.wTree.get_widget( widget.get_name()[:-5] + 'spin'
                           ).set_sensitive( widget.get_active() )
#=============================================================================#

    def on_spin_value_changed( self, ch_widget ):
      '''Обработка событий при изменении разнообразных "вертушек"/spin's'''

      # Монструозный код вызван попыткой соединить "всё в одном"
      # Тем более, что быстродействие тут не критично
      widget_name = ch_widget.get_name()[:-5] # len( '_spin' ) == 5
      section_end = widget_name.find('_')

      self.properties.item( widget_name[ : section_end ] ).item_value_set(
                                        widget_name[ section_end + 1: ],
                                        ch_widget.get_value()            )
#=============================================================================#

    def on_style_spin_value_changed( self, ch_widget ):
      '''Обработка событий при изменении "вертушек"/spin's стилей'''

      # len('styles_') == 7 and len( '_spin' ) == 5
      self.properties.styles.item( self.current_style ).item_value_set(
                                        ch_widget.get_name()[7:-5],
                                        ch_widget.get_value()         )
#=============================================================================#


    def on_prop_dialog_destroy( self, *args):
        # При закрытии окна  наново читаем их из конфигурационных файлов.
        #  Если сохранение изменений свойств не подтверждено - дабы сбросить
        #  возможные изменения в экземпляре класса в памяти
        #  Если подтверждено - чтобы переустановить дефолтные значения стилей
        #  (см. TextStyles.read() )

        self.properties.read()
#=============================================================================#
#                                     ^                                       #
#                               End of Class                                  #
#                                                                             #
#=============================================================================#

# signals
gobject.signal_new( 'properties-apply',
                    PropertiesDialog,
                    gobject.SIGNAL_RUN_LAST,
                    gobject.TYPE_NONE, ()
                  )

if __name__ == '__main__':
    def properties_apply_cb(w):
        print 'properties_apply_cb'

    def run_props_dlg(w, parrent):
        print 'run_props_dlg'
        pd = PropertiesDialog(parrent, props, 'propsdialog.glade')
        pd.connect('properties-apply', properties_apply_cb)

    props = Properties()
    w = gtk.Window()
    w.connect('destroy', lambda w: gtk.main_quit())
    b = gtk.Button('Properties')
    b.connect('clicked', run_props_dlg, w)
    w.add(b)
    w.show_all()
    gtk.main()




