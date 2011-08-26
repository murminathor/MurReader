#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys, os
import copy

import gtk
import pango
import gobject

from properties_old import *
from gtk            import gdk, glade
from ConfigParser   import ConfigParser
from miscutils      import fix_filename, OpenFileDialog
from config         import *


PANGO_SCALE = pango.SCALE


## def skin_filename(skin_name):
##     user_skin_dir = os.path.expanduser('~/.pybr/skins')
##     return os.path.join(user_skin_dir, str(skin_name))+'.skin'
#=============================================================================#

class Style(BaseStyle):

    def __init__(self, args={}, is_default=False, default_settings=None):
        BaseStyle.__init__(self, args, is_default, default_settings )

        self.font = pango.FontDescription( self.font_family + ' ' +\
                                           str(self.font_size) )
#=============================================================================#

    def set_font_desc(self, da):
        self.font = pango.FontDescription( self.font_family + ' ' + \
                                           str(self.font_size) )
        if self.__dict__.has_key('bold') and self.bold:
            self.font.set_weight( pango.WEIGHT_BOLD )

        if self.__dict__.has_key('italic') and self.italic:
            self.font.set_style( pango.STYLE_ITALIC )

        pangolayout = da.create_pango_layout(' ')
        pangolayout.set_font_description(self.font)
        self.space_width = pangolayout.get_extents()[1][2] / PANGO_SCALE
        #+self.space_width_incr
        self.font_height = pangolayout.get_extents()[1][3] / PANGO_SCALE #\
                           #+ self.pixels_inside_wrap

        self.gdk_color = gdk.color_parse(self.color)

#=============================================================================#
#                                     ^                                       #
#                               End of Class                                  #
#                                                                             #
#=============================================================================#

class Properties:

    default_styles = {
        #'defaultSt'     : {},
        'paragraph'   : {'first_line_indent': 20},
        'title'       : {'font_size': 30, 'justify': 'center', 'hyphenate': False, 'bold': True},
        'subtitle'    : {'font_size': 25, 'justify': 'center', 'hyphenate': False, 'bold': True},
        'epigraph'    : {'left_indent': 100},
        'cite'        : {'left_indent': 40, 'right_indent': 40, 'italic': True},
        'footnote'    : {'font_size': 12},
        'hyperlink'   : {},
        'stanza'      : {'font_size': 12, 'left_indent': 30},
        'text_author' : {'italic': True, 'justify': 'right'},
        'strong'      : {'bold': True},
        'emphasis'    : {'italic': True},
        }

    styles = {} # {'style name': Style() object, ...}

    recent_files = []
    # recent_files: list:
    # [
    #   [filename, line_index, char_index, encoding, lang],
    #   ...
    # ]



    def __init__(self):

        #self.props_file = props_file

        self.show_status                = True
        self.title_format               = PROGRAM_NAME
        self.num_recent_files           = 40
        self.single_column              = False
        self.new_page                   = False
        self.hide_menu                  = False
        self.use_background             = True
        self.path_to_background         = ''
        self.background_color           = '#ffffff'
        self.use_gradient               = False
        self.gradient_color             = '#ffffff'
        self.text_left_margin           = 30
        self.text_right_margin          = 30
        self.text_top_margin            = 30
        self.text_bottom_margin         = 50
        self.text_spaces_between_column = 30
        self.status_show_percent        = True
        self.status_show_clock          = True
        self.status_y_position          = 10
        self.status_percent_x_position  = 30
        self.status_clock_x_position    = 30
        self.status_font                = 'Sans 16'
        self.status_color               = '#000000'

        self.footnote_line_width        = 2

        self.main_window_width          = 600
        self.main_window_height         = 400
        self.file_select_path           = ''

        self.current_skin = 0
        self.skins = {} # { 0: 'skin name', }

        for st in STYLES_LIST:
            if st == 'defaultSt':
                default_settings = Style(is_default=True)
                self.styles['defaultSt'] = default_settings
            else:
                self.styles[st] = Style(self.default_styles[st],
                                        default_settings=default_settings)


    def read_properties(self, config_files=None, show_warning=False):

        if not config_files:
            config_files = (CONFIG_FILE, IFACE_FILE)

        cf = ConfigParser()

        #if config_files:
        files = []
        for f in config_files:
            try:
                curr_file = open(f, 'r')
            except IOError, err:
                print >> sys.stderr, 'ERROR: can\'t open config file: %s: %s\n' % (f, str(err))
            else:
                files.append(f)
                curr_file.close()

        #print '>>>', files

        if not files:
            return

        cf.read(files)
            #current_skin = cf.getint('main', 'current_skin')
            #skin_file = skin_filename(current_skin)
            #cf.read((skin_file,))

        #else:
        #    cf.read((skin_filename(self.current_skin),))

        # -- section "main" --

        # int
        for prop in ( 'main_window_width',
                      'main_window_height',
                      'num_recent_files',
                      'text_left_margin',
                      'text_right_margin',
                      'text_top_margin',
                      'text_bottom_margin',
                      'text_spaces_between_column',
                      'status_y_position',
                      'status_percent_x_position',
                      'status_clock_x_position',
                     ):
            try:
                self.__dict__[prop] = cf.getint('main', prop)
            except Exception, err:
                if show_warning:
                    print >> sys.stderr, 'WARNING: error in config file: section "main": %s' % str(err)

        # str
        for prop in ('title_format',
                     'file_select_path',
                     'path_to_background',
                     'background_color',
                     'gradient_color',
                     'status_font',
                     'status_color'):
            try:
                self.__dict__[prop] = cf.get('main', prop)
            except Exception, err:
                if show_warning:
                    print >> sys.stderr, 'WARNING: error in config file: section "main": %s' % str(err)


        # boolean
        for prop in ('show_status',
                     'single_column',
                     'new_page',
                     'hide_menu',
                     'use_background',
                     'use_gradient',
                     'status_show_percent',
                     'status_show_clock'):
            try:
                if sys.version_info >= (2, 3):
                    self.__dict__[prop] = cf.getboolean('main', prop)
                else:
                    self.__dict__[prop] = cf.get('main', prop) == 'True' and 1 or 0
            except Exception, err:
                if show_warning:
                    print >> sys.stderr, 'WARNING: error in config file: section "main": %s' % str(err)

        # -- skins --
        try:
            num_skins = cf.getint('main', 'num_skins')
        except Exception, err:
            if show_warning:
                print >> sys.stderr, 'WARNING: error in config file: section "main": %s' % str(err)
        else:
            for i in range(num_skins):
                try:
                    self.skins[i] = cf.get('skins', str(i))
                except:
                    pass

        # -- styles --
        for style in STYLES_LIST:

            # int
            for prop in ('font_size',
                         'left_indent',
                         'right_indent',
                         'first_line_indent',
                         'pixels_inside_wrap',
                         'pixels_above_line',
                         'pixels_below_line'):
                try:
                    if cf.has_option(style, prop):
                        self.styles[style].__dict__[prop] = cf.getint(style, prop)
                    elif style != 'defaultSt' and self.styles[style].__dict__.has_key(prop):
                        del self.styles[style].__dict__[prop]

                except Exception, err:
                    if show_warning:
                        print >> sys.stderr, 'WARNING: error in config file: section "%s": %s' % (style, str(err))

            # str
            for prop in ('font_family', 'color', 'justify'):
                try:
                    if cf.has_option(style, prop):
                        self.styles[style].__dict__[prop] = cf.get(style, prop)
                    elif style != 'defaultSt' and self.styles[style].__dict__.has_key(prop):
                        del self.styles[style].__dict__[prop]

                except Exception, err:
                    if show_warning:
                        print >> sys.stderr, 'WARNING: error in config file: section "%s": %s' % (style, str(err))

            # boolean
            for prop in ('italic', 'bold', 'hyphenate'):
                try:
                    if sys.version_info >= (2, 3):
                        if cf.has_option(style, prop):
                            self.styles[style].__dict__[prop] = cf.getboolean(style, prop)
                        elif style != 'defaultSt' and self.styles[style].__dict__.has_key(prop):
                            del self.styles[style].__dict__[prop]
                    else:
                        if cf.has_option(style, prop):
                            self.styles[style].__dict__[prop] = cf.get(style, prop) == 'True' and 1 or 0
                        elif style != 'defaultSt' and self.styles[style].__dict__.has_key(prop):
                            del self.styles[style].__dict__[prop]

                except Exception, err:
                    if show_warning:
                        print >> sys.stderr, 'WARNING: error in config file: section "%s": %s' % (style, str(err))


        rf = []
        for i in range(self.num_recent_files):
            section = 'recent%d' % i
            if cf.has_section(section):
                try:
                    rf.append((cf.get(section, 'filename'),
                               cf.getint(section, 'line'),
                               cf.getint(section, 'index'),
                               cf.get(section, 'encoding'),
                               cf.get(section, 'lang')))
                except Exception, err:
                    if show_warning:
                        print >> sys.stderr, 'WARNING: error in config file: section "%s": %s' % (section, str(err))
                else:
                    self.recent_files = rf

    def save_properties(self):
        try:
            fd = open( CONFIG_FILE, 'w' )
        except IOError, err:
            print >> sys.stderr, 'ERROR: can\'t open config file: %s: %s' % (CONFIG_FILE, str(err))
            return

        cf = ConfigParser()

        cf.add_section('main')

        # int | str
        for prop in (
            'main_window_width',
            'main_window_height',
            'title_format',
            'num_recent_files',
            'file_select_path',
            'current_skin',
            ):
            cf.set( 'main', prop, self.__dict__[prop] )

        # boolean
        for prop in ( 'new_page', 'hide_menu' ):

            if sys.version_info >= (2, 3):
                cf.set( 'main', prop, self.__dict__[prop] )
            else:
                cf.set( 'main', prop, self.__dict__[prop] and 'True' or 'False' )

        if self.skins:
            num_skins = max([int(i) for i in self.skins])+1
        else:
            num_skins = 0
        cf.set('main', 'num_skins', num_skins)

        i = 0
        for filename, line, index, encoding, lang in self.recent_files:
            section = 'recent%d' % i
            cf.add_section(section)
            cf.set(section, 'filename', filename)
            cf.set(section, 'line', line)
            cf.set(section, 'index', index)
            cf.set(section, 'encoding', encoding)
            cf.set(section, 'lang', lang)
            i+=1

        cf.add_section('skins')
        for skin in self.skins:
            cf.set('skins', str(skin), self.skins[skin])

        cf.write(fd)

        self.save_iface_properties( IFACE_FILE )


    def save_skin(self, skin_name):

        skin_num = -1
        for n in self.skins:
            if self.skins[n] == skin_name:
                skin_num = n
                break
        if skin_num < 0:
            if self.skins:
                skin_num = max([int(i) for i in self.skins])+1
            else:
                skin_num = 0

        skin_file = os.path.join( USER_SKIN_DIR, 'skin'+str(skin_num))+'.conf'
        self.save_iface_properties(skin_file)
        self.skins[skin_num] = skin_name


    def read_skin(self, skin_num):
        if skin_num not in self.skins:
            return
        skin_file = os.path.join( USER_SKIN_DIR, 'skin'+str(skin_num))+'.conf'
        self.read_properties( (skin_file,) )


    def save_iface_properties(self, file_name):

        #skin_file = skin_filename(skin_name)
        try:
            fd = open(file_name, 'w')
        except IOError, err:
            print >> sys.stderr, 'ERROR: can\'t open config file: %s: %s' % (file_name, str(err))
            return

        cf = ConfigParser()

        cf.add_section('main')

        # int | str
        for prop in (
            'text_left_margin',
            'text_right_margin',
            'text_top_margin',
            'text_bottom_margin',
            'text_spaces_between_column',
            'status_y_position',
            'status_percent_x_position',
            'status_clock_x_position',
            'path_to_background',
            'background_color',
            'gradient_color',
            'status_font',
            'status_color',
            ):

            cf.set('main', prop, self.__dict__[prop])

        # boolean
        for prop in (
            'show_status',
            'single_column',
            'use_background',
            'use_gradient',
            'status_show_percent',
            'status_show_clock',
            ):

            if sys.version_info >= (2, 3):
                cf.set('main', prop, self.__dict__[prop])
            else:
                cf.set('main', prop, self.__dict__[prop] and 'True' or 'False')


        for style in STYLES_LIST:
            cf.add_section(style)

            # int | str
            for prop in (
                'font_size',
                'left_indent',
                'right_indent',
                'first_line_indent',
                'pixels_inside_wrap',
                'pixels_above_line',
                'pixels_below_line',
                'font_family',
                'color',
                'justify',
                ):

                if self.styles[style].__dict__.has_key(prop):
                    cf.set(style, prop, self.styles[style].__dict__[prop])

            # boolean
            for prop in ('italic',
                         'bold',
                         'hyphenate'):
                if sys.version_info >= (2, 3):
                    if self.styles[style].__dict__.has_key(prop):
                        cf.set(style, prop, self.styles[style].__dict__[prop])
                else:
                    if self.styles[style].__dict__.has_key(prop):
                        cf.set(style, prop, self.styles[style].__dict__[prop] and 'True' or 'False')

        cf.write(fd)
        fd.close()
        cf = None

class PropertiesDialog(gobject.GObject):

    def __init__(self, parent_window, properties, glade_file):

        gobject.GObject.__init__(self)

        wTree = glade.XML(glade_file, 'prop_dialog')
        self.window = wTree.get_widget('prop_dialog')
        self.window.set_transient_for(parent_window)
        wTree.signal_autoconnect(self)
        self.wTree = wTree

        self.properties = copy.copy(properties)

        menu = gtk.Menu()
        for j in JUSTIFY_LIST:
            menuitem = gtk.MenuItem(j.title())
            menuitem.set_data('value', j)
            menuitem.show()
            menu.add(menuitem)
        wTree.get_widget('st_justify_setter').set_menu(menu)

        self.set_style_settings('defaultSt')

        for prop in ('text_top_margin',
                     'text_bottom_margin',
                     'text_left_margin',
                     'text_right_margin',
                     'text_spaces_between_column',
                     'status_y_position',
                     'status_percent_x_position',
                     'status_clock_x_position'):
            wTree.get_widget(prop+'_spin').set_value(properties.__dict__[prop])

        for prop in ('single_column',
                     'new_page',
                     'show_status',
                     'hide_menu',
                     'use_background',
                     'use_gradient',
                     'status_show_percent',
                     'status_show_clock'):
            wTree.get_widget(prop+'_check').set_active(properties.__dict__[prop])

        self.on_use_background_check_toggled(wTree.get_widget('use_background_check'))

        wTree.get_widget('title_format_entry').set_text(properties.title_format)
        wTree.get_widget('path_to_background_entry').set_text(properties.path_to_background)
        wTree.get_widget('bg_color_button_label').set_text(properties.background_color)
        wTree.get_widget('gradient_color_button_label').set_text(properties.gradient_color)
        wTree.get_widget('status_font_label').set_text(self.properties.status_font)
        wTree.get_widget('status_color_label').set_text(self.properties.status_color)

        self.set_checks_sensitive(False)

        self.current_style = 'defaultSt'

        self.window.show()


    def set_checks_sensitive(self, sens):
        for check in ('st_font_family_check',
                      'st_font_size_check',
                      'st_bold_check',
                      'st_italic_check',
                      'st_color_check',
                      'st_justify_check',
                      'st_hyphenate_check',
                      'st_left_indent_check',
                      'st_right_indent_check',
                      'st_first_line_indent_check',
                      'st_pixels_inside_wrap_check',
                      'st_pixels_above_line_check',
                      'st_pixels_below_line_check'):
            self.wTree.get_widget(check).set_sensitive(sens)


    def set_style_settings(self, style):

        for st in ('font_size',
                   'left_indent',
                   'right_indent',
                   'first_line_indent',
                   'pixels_inside_wrap',
                   'pixels_above_line',
                   'pixels_below_line'):
            self.wTree.get_widget('st_'+st+'_setter').set_value(self.properties.styles[style].get_value(st))

        for st in ('italic',
                   'bold',
                   'hyphenate'):
            self.wTree.get_widget('st_'+st+'_setter').set_active(self.properties.styles[style].get_value(st))

        self.wTree.get_widget('st_font_button_label').set_text(self.properties.styles[style].get_value('font_family'))
        self.wTree.get_widget('st_color_button_label').set_text(self.properties.styles[style].get_value('color'))
        self.option_menu_set_active('st_justify_setter', JUSTIFY_LIST.index(self.properties.styles[style].get_value('justify')))


    def read_style_settings(self):

        props = self.properties.styles[self.current_style]
        #print '>>', self.current_style

        # spinbuttons
        for st in ('font_size',
                   'left_indent',
                   'right_indent',
                   'first_line_indent',
                   'pixels_inside_wrap',
                   'pixels_above_line',
                   'pixels_below_line'):

            if self.wTree.get_widget('st_'+st+'_check').get_active():
                props.__dict__[st] = self.wTree.get_widget('st_'+st+'_setter').get_value_as_int()
            elif props.__dict__.has_key(st):
                del props.__dict__[st]

        # togglebuttons
        for st in ('italic',
                   'bold',
                   'hyphenate'):
            if self.wTree.get_widget('st_'+st+'_check').get_active():
                props.__dict__[st] = self.wTree.get_widget('st_'+st+'_setter').get_active()
            elif props.__dict__.has_key(st):
                del props.__dict__[st]


        if self.wTree.get_widget('st_font_family_check').get_active():
            props.font_family = self.wTree.get_widget('st_font_button_label').get_text()
        elif props.__dict__.has_key('font_family'):
            del props.font_family

        if self.wTree.get_widget('st_color_check').get_active():
            props.color = self.wTree.get_widget('st_color_button_label').get_text()
        elif props.__dict__.has_key('color'):
            del props.color

        if self.wTree.get_widget('st_justify_check').get_active():
            props.justify = self.wTree.get_widget('st_justify_setter').get_menu().get_active().get_data('value')
        elif props.__dict__.has_key('justify'):
            del props.justify


    def on_st_style_combo_entry_changed(self, entry):
        style = entry.get_text()
        if not style:
            return
        style = style.lower()

        self.read_style_settings()

        self.current_style = style

        # set properties
        self.set_checks_sensitive(style != 'defaultSt')
        self.set_style_settings(style)

        for st in SETTINGS_LIST:
            check_name = 'st_'+st+'_check'
            self.wTree.get_widget(check_name).set_active(self.properties.styles[style].__dict__.has_key(st))



    def on_close_clicked(self, *args):
        self.window.destroy()


    def on_apply_clicked(self, *args):

        self.read_style_settings()

        for prop in ('text_top_margin',
                     'text_bottom_margin',
                     'text_left_margin',
                     'text_right_margin',
                     'text_spaces_between_column',
                     'status_y_position',
                     'status_percent_x_position',
                     'status_clock_x_position'):
            self.properties.__dict__[prop] = self.wTree.get_widget(prop+'_spin').get_value_as_int()

        for prop in ('single_column',
                     'new_page',
                     'show_status',
                     'hide_menu',
                     'use_background',
                     'use_gradient',
                     'status_show_percent',
                     'status_show_clock'):
            self.properties.__dict__[prop] = self.wTree.get_widget(prop+'_check').get_active()

        self.properties.title_format = self.wTree.get_widget('title_format_entry').get_text()
        self.properties.path_to_background = self.wTree.get_widget('path_to_background_entry').get_text()
        self.properties.background_color = self.wTree.get_widget('bg_color_button_label').get_text()
        self.properties.gradient_color = self.wTree.get_widget('gradient_color_button_label').get_text()
        self.properties.status_font = self.wTree.get_widget('status_font_label').get_text()
        self.properties.status_color = self.wTree.get_widget('status_color_label').get_text()

        self.emit('properties-apply')



    def option_menu_set_active(self, menu_name, index):
        option_menu = self.wTree.get_widget(menu_name)
        menu = option_menu.get_menu()
        option_menu.remove_menu()
        menu.set_active(index)
        option_menu.set_menu(menu)


    def on_st_font_family_setter_clicked(self, w):
        dialog = gtk.FontSelectionDialog('Select font')
        dialog.set_font_name(self.properties.styles[self.current_style].font_family+' '+str(self.properties.styles[self.current_style].font_size))

        dialog.set_transient_for(self.window)
        dialog.show()

        response = dialog.run()

        if response  == gtk.RESPONSE_OK:
            font_desc = pango.FontDescription(dialog.get_font_name())
            self.wTree.get_widget('st_font_button_label').set_text(font_desc.get_family())

        dialog.destroy()

    def on_status_font_button_clicked(self, w):
        pango_font = self.select_font(self.properties.status_font)
        if pango_font:
            self.wTree.get_widget('status_font_label').set_text(pango_font.to_string())


    def select_font(self, font):
        dialog = gtk.FontSelectionDialog('Select font')
        dialog.set_font_name(font)

        dialog.set_transient_for(self.window)
        dialog.show()

        response = dialog.run()
        if response  == gtk.RESPONSE_OK:
            pango_font = pango.FontDescription(dialog.get_font_name())
        else:
            pango_font = None

        dialog.destroy()
        return pango_font

    def on_status_color_button_clicked(self, w):
        self.select_color('status_color_label')

    def on_st_color_setter_clicked(self, w):
        self.select_color('st_color_button_label')

    def on_bg_color_button_clicked(self, w):
        self.select_color('bg_color_button_label')
        self.redraw_gradient_area()

    def on_gradient_color_button_clicked(self, w):
        self.select_color('gradient_color_button_label')
        self.redraw_gradient_area()

    def select_color(self, button_label):

        dialog = gtk.ColorSelectionDialog('Select color')

        dialog.colorsel.set_has_palette(True)
        dialog.colorsel.set_current_color(gdk.color_parse(
            self.wTree.get_widget(button_label).get_text()))
        dialog.set_transient_for(self.window)
        dialog.show()

        response = dialog.run()

        if response == gtk.RESPONSE_OK:
            color = dialog.colorsel.get_current_color()
            color_str = '#%02x%02x%02x' % (color.red>>8, color.green>>8, color.blue>>8)
            self.wTree.get_widget(button_label).set_text(color_str)

        dialog.destroy()


    def redraw_gradient_area(self):
        from ornamentbook import createBufferRGB

        da = self.wTree.get_widget('gradient_drawingarea')
        if not da.window: return
        style = da.get_style()
        gc = style.fg_gc[gtk.STATE_NORMAL]
        x, y, w, h, depth = da.window.get_geometry()

        c1 = self.wTree.get_widget('bg_color_button_label').get_text()
        if self.wTree.get_widget('use_gradient_check').get_active():
            c2 = self.wTree.get_widget('gradient_color_button_label').get_text()
            buff = createBufferRGB(w, h, c1, c2)
        else:
            buff = createBufferRGB(w, h, c1)

        da.window.draw_rgb_image(gc, 0, 0, w, h, gdk.RGB_DITHER_NONE, buff, w*3)


    def on_select_path_button_clicked(self, w):
        dialog = OpenFileDialog(self.window)
        filename = dialog.filename
        if filename:
            self.wTree.get_widget('path_to_background_entry').set_text(
                fix_filename(filename))


    def on_use_background_check_toggled(self, w):
        if w.get_active():
            self.wTree.get_widget('path_to_background_entry').set_sensitive(True)
            self.wTree.get_widget('select_path_button').set_sensitive(True)
            self.wTree.get_widget('bg_color_button').set_sensitive(False)
            self.wTree.get_widget('use_gradient_check').set_sensitive(False)
            self.wTree.get_widget('gradient_color_button').set_sensitive(False)
            #self.wTree.get_widget('use_gradient_check').get_active())
        else:
            self.wTree.get_widget('path_to_background_entry').set_sensitive(False)
            self.wTree.get_widget('select_path_button').set_sensitive(False)
            self.wTree.get_widget('bg_color_button').set_sensitive(True)
            self.wTree.get_widget('use_gradient_check').set_sensitive(True)
            self.wTree.get_widget('gradient_color_button').set_sensitive(
                self.wTree.get_widget('use_gradient_check').get_active())


    def on_st_bold_setter_toggled(self, w):
        w.set_label(w.get_active() and 'Yes' or 'No')

    def on_st_italic_setter_toggled(self, w):
        w.set_label(w.get_active() and 'Yes' or 'No')

    def on_st_hyphenate_setter_toggled(self, w):
        w.set_label(w.get_active() and 'Yes' or 'No')

    def on_st_font_family_check_toggled(self, check):
        self.wTree.get_widget('st_font_family_setter').set_sensitive(
            check.get_active())

    def on_st_font_size_check_toggled(self, check):
        self.wTree.get_widget('st_font_size_setter').set_sensitive(
            check.get_active())

    def on_st_bold_check_toggled(self, check):
        self.wTree.get_widget('st_bold_setter').set_sensitive(
            check.get_active())

    def on_st_italic_check_toggled(self, check):
        self.wTree.get_widget('st_italic_setter').set_sensitive(
            check.get_active())

    def on_st_color_check_toggled(self, check):
        self.wTree.get_widget('st_color_setter').set_sensitive(
            check.get_active())

    def on_st_justify_check_toggled(self, check):
        self.wTree.get_widget('st_justify_setter').set_sensitive(
            check.get_active())

    def on_st_hyphenate_check_toggled(self, check):
        self.wTree.get_widget('st_hyphenate_setter').set_sensitive(
            check.get_active())

    def on_st_left_indent_check_toggled(self, check):
        self.wTree.get_widget('st_left_indent_setter').set_sensitive(
            check.get_active())

    def on_st_right_indent_check_toggled(self, check):
        self.wTree.get_widget('st_right_indent_setter').set_sensitive(
            check.get_active())

    def on_st_first_line_indent_check_toggled(self, check):
        self.wTree.get_widget('st_first_line_indent_setter').set_sensitive(
            check.get_active())

    def on_st_pixels_inside_wrap_check_toggled(self, check):
        self.wTree.get_widget('st_pixels_inside_wrap_setter').set_sensitive(
            check.get_active())

    def on_st_pixels_above_line_check_toggled(self, check):
        self.wTree.get_widget('st_pixels_above_line_setter').set_sensitive(
            check.get_active())

    def on_st_pixels_below_line_check_toggled(self, check):
        self.wTree.get_widget('st_pixels_below_line_setter').set_sensitive(
            check.get_active())

    def on_gradient_check_toggled(self, check):
        self.wTree.get_widget('gradient_color_button').set_sensitive(
            check.get_active())
        self.redraw_gradient_area()

    def on_gradient_drawingarea_expose_event(self, *args):
        self.redraw_gradient_area()


## signals
gobject.signal_new('properties-apply', PropertiesDialog,
                   gobject.SIGNAL_RUN_LAST,
                   gobject.TYPE_NONE, ())


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




