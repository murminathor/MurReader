#!/usr/bin/env python
# -*- coding: utf-8 -*-

import gtk, pango

__all__ = [ 'select_color', 'select_font', 'error_msg', 'select_file',
            'select_folder'
          ]
#=============================================================================#

def select_color( window, current_color="#000000", title='Select color' ):
    '''Формирует и инициализирует диалог выбора цвета, а также возвращает
       результат выбора

       \param window        - gtk.window() - окно, к которому будет
                               "привязан" диалог
       \param current_color - цвет по-умолчанию, цвет, который будет
                              отображаться как текущий в окне выбора
       \param title         - "Шапка" диалогового окна
       \return Шестнадцатиричный код цвета 0xRRGGBB
    '''

    dialog = gtk.ColorSelectionDialog( title )

    dialog.colorsel.set_has_palette(True)
    dialog.colorsel.set_current_color( gtk.gdk.color_parse( current_color ) )
    dialog.set_transient_for( window )
    dialog.show()

    if dialog.run() == gtk.RESPONSE_OK:
        color = dialog.colorsel.get_current_color()
        current_color = '#%02x%02x%02x' % ( color.red>>8,
                                            color.green>>8,
                                            color.blue>>8
                                          )

    dialog.destroy()

    return current_color
#=============================================================================#

def select_font( window, description='Sans 14', title='Select font' ):
    '''Формирует и инициализирует диалог выбора шрифта, а также возвращает
       результат выбора

       \param window      - gtk.window() - окно, к которому будет
                            "привязан" диалог
       \param description - Описание шрифта по-умолчанию, шрифта, который будет
                            отображаться как текущий в окне выбора
       \param title       - "Шапка" диалогового окна
       \return pango.FontDescription()

    '''

    dialog = gtk.FontSelectionDialog( title )
    dialog.set_font_name( description )

    dialog.set_transient_for( window )
    dialog.show()

    pango_font = None
    if dialog.run() == gtk.RESPONSE_OK:
        pango_font = pango.FontDescription( dialog.get_font_name() )

    dialog.destroy()
    return pango_font
#=============================================================================#

def error_msg( window, msg ):
    '''Формирует и инициализирует сообщение об ошибке

       \param window - gtk.window() - окно, к которому будет
                       "привязан" диалог
       \param msg    - Текст ошибки
    '''

    dialog = gtk.MessageDialog(
                             window,
                             gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT,
                             gtk.MESSAGE_ERROR,
                             gtk.BUTTONS_OK,
                             msg
                              )

    dialog.run()
    dialog.destroy()
#=============================================================================#

def select_file( window, title='Select file', file_name=None ):
    '''Формирует и инициализирует диалог выбора файла, а также возвращает
       результат выбора

       \param window     - gtk.window() - окно, к которому будет
                           "привязан" диалог
       \param file_name - имя файла, который будет отображаться как текущий
                          (выбраный) в окне выбора
       \param title     - "Шапка" диалогового окна
       \return Имя файла или None, если ничего не было выбрано

    '''
    dialog = gtk.FileChooserDialog( title, window,
                                    gtk.FILE_CHOOSER_ACTION_OPEN,
                                    (gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL,
                                     gtk.STOCK_OPEN,   gtk.RESPONSE_OK)
                                  )

    if file_name: dialog.set_filename( file_name )
    dialog.set_transient_for( window )
    dialog.show()

    file_name = None
    if dialog.run() == gtk.RESPONSE_OK:
        file_name = dialog.get_filename()

    dialog.destroy()
    return file_name
#=============================================================================#

def select_folder( window, title='Select folder', dir_name=None ):
    '''Формирует и инициализирует диалог выбора директории, а также возвращает
       результат выбора

       \param window    - gtk.window() - окно, к которому будет
                          "привязан" диалог
       \param dir_name - имя директории, которая будет отображаться как текущая
                         (выбраная) в окне выбора
       \param title    - "Шапка" диалогового окна
       \return Имя директории или None, если ничего не было выбрано
    '''
    dialog = gtk.FileChooserDialog( title, window,
                                    gtk.FILE_CHOOSER_ACTION_SELECT_FOLDER,
                                    ( gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL,
                                      gtk.STOCK_OPEN,   gtk.RESPONSE_OK      )
                                  )

    if dir_name: dialog.set_current_folder( dir_name )
    dialog.set_transient_for( window )
    dialog.show()

    dir_name = None
    if dialog.run() == gtk.RESPONSE_OK:
        dir_name = dialog.get_current_folder()

    dialog.destroy()
    return dir_name
#=============================================================================#

