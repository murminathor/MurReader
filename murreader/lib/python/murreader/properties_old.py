#!/usr/bin/env python
# -*- coding: koi8-r; -*-

import sys, os
import copy

from ConfigParser import ConfigParser
from config       import *

#==============================================================================
class BaseStyle:

    def __init__(self, args={}, is_default=False, default_settings=None):

    ## Если is_default == True
    ##   объект Style является дефолтным и имеет все аттрибуты
    ## иначе
    ##   объект обладает только теми атрибутами, которые переопределяют
    ##   дефолтные установки. Остальные использует из объекта default_settings

        if is_default:
            self.font_family        = 'Sans'
            self.font_size          = 16
            self.italic             = False
            self.bold               = False
            self.ascent             = None
            self.descent            = None
            self.monospace          = False
            self.color              = '#000000'
            self.justify            = 'fill'     # left | right | center | fill
            self.hyphenate          = True
            self.left_indent        = 20
            self.right_indent       = 20
            self.first_line_indent  = 20
            self.pixels_inside_wrap = 6
            self.pixels_above_line  = 0
            self.pixels_below_line  = 10
            self.settings           = self.__dict__.keys()
        else:
            self.settings = args.keys()

        self.__dict__.update(args)
        self.default_settings = default_settings
#==============================================================================

    def __getattr__(self, name):
        return self.__dict__['default_settings'].__dict__[name]
#==============================================================================

    def get_value(self, name):
        if self.__dict__.has_key(name):
            return self.__dict__[name]
        #else:
        return self.default_settings.__dict__[name]
#=============================================================================#
#                                     ^                                       #
#                               End of Class                                  #
#                                                                             #
#=============================================================================#

class BaseProperties:

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
#=============================================================================#
#                                                                             #
#                               Private methods                               #
#                                      v                                      #
#=============================================================================#

    def __init__(self, title_format = PROGRAM_NAME ):
        self.show_status                = True
        self.title_format               = title_format
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
#=============================================================================#

    def __error_msg( self, error, section='main', config_file=CONFIG_FILE ):
      '''__error_msg( error, section='main', config_file=CONFIG_FILE )

         \param  error       - само сообщение
         \param  section     - секция в конфигурационном файлу
         \param  config_file - имя конфигурационного файла
          Выводит сообщение об ошибке, возникшей при работе с конфигурационными
          файлами
      '''
      sys.stderr.write(
                        "ERROR: (file '%s'; section '%s'): %s\n" % \
                        (config_file, section, error)
                      )
      return True

#=============================================================================#
#                                                                             #
#                                Public methods                               #
#                                      v                                      #
#=============================================================================#

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
                self.__error_msg( "Can't open config file", f, str(err) )
            else:
                files.append(f)
                curr_file.close()

        if not files:
            return

        cf.read(files)

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
#==============================================================================

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
#==============================================================================

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
#==============================================================================

    def read_skin(self, skin_num):
        if skin_num not in self.skins:
            return
        skin_file = os.path.join( USER_SKIN_DIR, 'skin'+str(skin_num))+'.conf'
        self.read_properties( (skin_file,) )
#==============================================================================

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
#=============================================================================#
#                                     ^                                       #
#                               End of Class                                  #
#                                                                             #
#=============================================================================#
