#!/usr/bin/env python
# -*- coding: utf-8 -*-
# (c) Con Radchenko mailto:bofh@pochta.ru

import sys, os

import time
import gtk, gobject

from glob               import glob
from ConfigParser       import ConfigParser
from gtk                import glade, gdk
from dialog             import select_file
from properties_dialog  import PropertiesDialog
from properties         import Properties, RecentFiles
from config             import *
from content_area       import ContentArea
#=============================================================================#

__all__ = ['InterfaceMain']

#=============================================================================#
CURR_DIR               = os.path.dirname( __file__ )
GLADE_FILE             = os.path.join( CURR_DIR, 'main.glade' )
PROPSDIALOG_GLADE_FILE = os.path.join( CURR_DIR, 'propsdialog.glade' )
#=============================================================================#

class InterfaceMain:

#=============================================================================#
#                                                                             #
#                               Private methods                               #
#                                      v                                      #
#=============================================================================#
    def __init__(self, filename=None, fullscreen=False, hidemenu=False):

        self.filename = None
        self.encoding = 'utf-8'
        self.line = 0
        self.char = 0

        self.is_fullscreen = False
        self.prev_geometry = (0, 0)

        self.properties   = Properties()
        self.properties.read()

        self.recent_files = RecentFiles()
        self.recent_files.read()

        self.create_widgets()

        if filename:
            self.filename = filename
        else:
            self.filename = self.recent_files.filename()
            self.line     = self.recent_files.line()
            self.char     = self.recent_files.char()

        gobject.idle_add( self.open_file, self.filename )

        if fullscreen and gtk.pygtk_version >= (2, 2):
            self.on_fullscreen_activate()
            self.prev_geometry = (self.properties.window.width,
                                  self.properties.window.height)
        if hidemenu:
            self.main_menubar.hide()

        #self.timeout_cb()
        gobject.idle_add(lambda : self.timeout_cb() and False)
        gobject.timeout_add(10000, self.timeout_cb)

        #self.window.connect('key-release-event', self.key_press_event_cb)
        self.window.connect('key-press-event', self.key_press_event_cb)
#=============================================================================#
#                                                                             #
#                                Public methods                               #
#                                      v                                      #
#=============================================================================#

    def create_widgets(self):

        self.glade_file = GLADE_FILE
        self.propsdialog_glade_file = PROPSDIALOG_GLADE_FILE

        wTree = glade.XML( self.glade_file, 'main_window')
        wTree.signal_autoconnect(self)

        self.window = wTree.get_widget('main_window')
        top_vbox = wTree.get_widget('top_vbox')

        self.main_menubar = wTree.get_widget('main_menubar')
        # (un)fullscreen available in PyGTK 2.2 and above
        if gtk.pygtk_version < (2, 2):
            wTree.get_widget('fullscreen_menu').set_sensitive(False)

        #self.open_recent_file_menu = wTree.get_widget('open_recent_file_menu')
        self.content_menu          = wTree.get_widget('content_menu')
        self.background_menu       = wTree.get_widget('background_menu')
        self.skins_menu            = wTree.get_widget('skins_menu')
        self.hyphenation_menu      = wTree.get_widget('hyphenation_menu')

        self.text_widget = ContentArea( self, self.properties )
        top_vbox.pack_start( self.text_widget )
        self.text_widget.realize()
        #text_widget.connect('position-changed', self.position_changed_cb)
        #self.text_widget = text_widget

        #self.properties.read()
        self.window.resize( self.properties.window.width,
                            self.properties.window.height )


        self.update_background_menu()
        self.update_skins_menu()
        self.update_hyphenation_menu()


        self.window.show_all()
        self.text_widget.initialize()
#=============================================================================#

    def open_file(self, filename):
        #print 'open_file', filename

        try:
            open(filename)
        except IOError, err:
            #sys.stderr.write('ERROR: can\'t open file: %s: %s\n'
            #                 % (filename, err[1]))
            error_dialog( self.window, "Can't open file %s: %s" %
                         (filename, err[1])
                        )
            return

        if self.filename: # save previous file
            #print 'save previous file', self.text_widget.current_page_line_index
            self.recent_files.add(
                                   self.filename,
                                   self.text_widget.current_page_line_index,
                                   self.text_widget.current_page_char_index,
                                   self.text_widget.content.encoding,
                                 )
            self.text_widget.open_file( self.filename,
                                        line=self.line,
                                        char=self.char
                                      )
            #self.text_widget.initialize()
            #self.text_widget.draw_text()
#=============================================================================#

    def timeout_cb(self):

        title = self.properties.window.title_format
        title = title.replace('%f', '%(filename)s')
        title = title.replace('%a', '%(authors)s')
        title = title.replace('%b', '%(book_title)s')
        title = title.replace('%p', '%(position)d%%')
        title = title.replace('%t', '%(time)s')

        authors = self.text_widget.content.authors
        #authors = authors[:64]
        book_title = self.text_widget.content.title

        try:
            title = title % {'filename'  : fix_filename(self.filename),
                             'authors'   : authors,
                             'book_title': book_title,
                             'position'  : int(self.text_widget.calc_position()*100),
                             'time'      : time.strftime('%H:%M', time.localtime()),
                             }
        except:
            title = PROGRAM_NAME + ' [invalid format]'
        self.window.set_title(title)

        #self.text_widget.draw_status()
        self.text_widget.drawStatus()

        return True
#=============================================================================#

    def update_recent_files_menu(self):
        menu = gtk.Menu()
        menu.show()
        #rf = self.recent_files
        #rf.reverse()
        #for f in rf: #self.properties.recent_files:
            #menuitem = gtk.MenuItem(fix_filename(f[0]))
            #menuitem.get_child().set_use_underline(False)
            #menuitem.connect('activate', self.recent_files_activate_cb, f[0])
            #menu.add(menuitem)
            #menuitem.show()
        #self.open_recent_file_menu.set_submenu(menu)
#=============================================================================#

    def update_hyphenation_menu(self):
        menu = gtk.Menu()
        menu.show()
        from hyphenation import Hyphenation
        langs = Hyphenation().get_langs()
        for l, n in langs:
            menuitem = gtk.MenuItem(n)
            menuitem.get_child().set_use_underline(False)
            menuitem.connect('activate', self.hyphenation_menu_activate_cb, l)
            menu.add(menuitem)
            menuitem.show()
        self.hyphenation_menu.set_submenu(menu)
#=============================================================================#

    def update_background_menu(self):

        backgrounds = []
        if os.path.exists( USER_SKIN_DIR ) and os.path.isdir( USER_SKIN_DIR ):
            backgrounds_dirs = [ USER_SKIN_DIR ]
        else:
            backgrounds_dirs = []

        for d in sys.path:
            f = os.path.join(d, CONFIG_PREFIX, self.properties.text.path_to_background )
            if os.path.exists(f) and os.path.isdir(f):
                backgrounds_dirs.append(f)
                break

        for d in backgrounds_dirs:
            f = os.path.join(d, '*.jpg')
            backgrounds.extend(glob(f))

        menu = gtk.Menu()
        menu.show()
        for f in backgrounds:
            fn = os.path.abspath(f)
            menuitem = gtk.MenuItem(fn)
            menuitem.get_child().set_use_underline(False)
            menuitem.connect('activate', self.background_menu_activate_cb, fn)
            menu.add(menuitem)
            menuitem.show()
        self.background_menu.set_submenu(menu)
#=============================================================================#

    def background_menu_activate_cb(self, w, filename):
        self.text_widget.set_background(filename)
        self.properties.text.path_to_background = filename
        self.text_widget.draw_text()
#=============================================================================#

    def hyphenation_menu_activate_cb(self, w, lang):
        self.text_widget.content.lang = lang
        self.text_widget.draw_text()
#=============================================================================#

    def update_skins_menu(self):
        pass
        #self.skins_menu.set_submenu(menu)
#=============================================================================#
    def skins_menu_activate_cb(self, w, skin):
        pass
        #self.properties.read_skin(skin)
        ##self.properties.current_skin = skin
        ##self.properties.read_properties()
        #self.text_widget.initialize()
        #self.text_widget.draw_text()
#=============================================================================#

    def on_new_skin_activate(self, *args):
        pass
        #s = entry_dialog(self.window, 'Save skin', 'Skin name: ')
        #if s:
            #self.properties.save_skin(s)
            #self.update_skins_menu()
#=============================================================================#

    def recent_files_activate_cb(self, w, filename):
        self.open_file(filename)
#=============================================================================#

    def on_open_activate(self, *args):
        filename = select_file( self.window, self.filename )
        if filename:
            self.filename = filename
            self.open_file(filename)
        return
#=============================================================================#

    def on_go_to_position_activate(self, *args):
        s = entry_dialog(self.window, 'Go to position', 'Go to position: (%) ')
        try:
            pos = float(s)
        except:
            return
        if 100 < pos < 0:
            return
        self.text_widget.set_position(pos/100)
#=============================================================================#

    def on_quit_activate(self, *args):
        self.window.destroy()
#=============================================================================#

    def on_main_window_unrealize(self, *args):
        if self.is_fullscreen:
            self.properties.window.width, self.properties.window.height = self.prev_geometry
        else:
            self.properties.window.width, self.properties.window.height = self.window.get_size()
        #self.properties.file_select_path = OpenFileDialog.file_select_path

        if self.filename:
            self.recent_files.add(
                                    self.filename,
                                    self.text_widget.current_page_line_index,
                                    self.text_widget.current_page_char_index,
                                    self.text_widget.content.encoding,
                                 )
        self.properties.save()
        #save_config_file(self.main_properties)
        #self.bookmarks.save_bookmarks()
#=============================================================================#

    def on_properties_activate(self, *args):
        dlg = PropertiesDialog( self.window,
                                self.properties,
                                self.propsdialog_glade_file
                              )
        dlg.connect('properties-apply', self.apply_properties_cb, dlg)
#=============================================================================#

    def apply_properties_cb(self, w, dlg):
        #self.properties = dlg.properties
        #self.text_widget.properties = dlg.properties
        self.text_widget.initialize()
        self.timeout_cb()
        self.text_widget.draw_text()
#=============================================================================#

    def on_increase_font_activate(self, *args):
        self.text_widget.incr_font(1)
        self.text_widget.draw_text()
#=============================================================================#

    def on_decrease_font_activate(self, *args):
        self.text_widget.incr_font(-1)
        self.text_widget.draw_text()
#=============================================================================#

    def on_fullscreen_activate(self, *args):
        if gtk.pygtk_version < (2, 2):
            return True

        if self.is_fullscreen:
            self.window.unfullscreen()
            self.main_menubar.show()
            self.is_fullscreen = False
            return True
        else:
            if self.properties.window.hide_menu:
                self.main_menubar.hide()
            self.window.fullscreen()
            self.prev_geometry = self.window.get_size()
            self.is_fullscreen = True
            return True
        return False
#=============================================================================#

    def on_hide_menu_activate(self, *args):
        if self.main_menubar.get_property('visible'):
            self.main_menubar.hide()
        else:
            self.main_menubar.show()
#=============================================================================#

    def key_press_event_cb(self, w, event):
        inc_font_keys = (gtk.keysyms.plus, gtk.keysyms.equal, gtk.keysyms.KP_Add)
        dec_font_keys = (gtk.keysyms.minus, gtk.keysyms.KP_Subtract)
        if event.keyval == gtk.keysyms.F11:
            self.on_fullscreen_activate()
            return True
        elif event.state == gdk.CONTROL_MASK and event.keyval == gtk.keysyms.q:
            self.window.destroy()
            return True
        elif event.state == gdk.CONTROL_MASK and event.keyval in inc_font_keys:
            self.on_increase_font_activate()
            return True
        elif event.state == gdk.CONTROL_MASK and event.keyval in dec_font_keys:
            self.on_decrease_font_activate()
            return True
        elif event.state == gdk.CONTROL_MASK and event.keyval == gtk.keysyms.o:
            self.on_open_activate()
            return True
        elif (event.state not in (gdk.CONTROL_MASK,) and
              event.keyval == gtk.keysyms.m):
            self.on_hide_menu_activate()
            return True
        elif event.state == gdk.CONTROL_MASK and event.keyval == gtk.keysyms.m:
            #self.on_books_manager_activate()
            return True
        return False
#=============================================================================#
#                                     ^                                       #
#                               End of Class                                  #
#                                                                             #
#=============================================================================#

if __name__ == '__main__':
    npbr = NewPyBR()
    npbr.window.connect('destroy', lambda w: gtk.main_quit())
    gtk.main()
