#!/usr/bin/env python
# -*- coding: utf-8 -*-


import string, os, sys, exceptions, codecs, gzip, locale
import gtk

#from config import default_encoding

##----------------------------------------------------------------------

default_encoding = locale.getlocale()[1]
if not default_encoding:
    default_encoding='iso8859-1'

##----------------------------------------------------------------------

def entry_dialog(parent, title, label_text, text=''):

    dialog = gtk.Dialog(title, parent,
                        gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT,
                        (gtk.STOCK_OK, gtk.RESPONSE_OK,
                         gtk.STOCK_CANCEL, gtk.RESPONSE_REJECT))
    hbox = gtk.HBox()
    dialog.vbox.pack_start(hbox, True, True, 0)
    label = gtk.Label(label_text)
    hbox.pack_start(label, expand=False)
    entry = gtk.Entry()
    entry.set_text(text)
    entry.connect('activate', lambda w:
                  dialog.emit ('response', gtk.RESPONSE_OK))
    hbox.pack_start(entry)
    dialog.show_all()
    response = dialog.run()
    str = None
    if response == gtk.RESPONSE_OK:
        str = entry.get_text()
    dialog.destroy()
    return str

##----------------------------------------------------------------------

def fix_filename(filename):
    # from locale encoding to utf-8
    # TODO: G_BROKEN_FILENAMES
    enc = default_encoding
    fn = filename.decode(enc).encode('utf-8')
    return fn

##----------------------------------------------------------------------

def fix_filename_2(filename):
    # from utf-8 encoding to locale encoding
    # TODO: G_BROKEN_FILENAMES
    enc = default_encoding
    fn = filename.decode('utf-8').encode(enc)
    return fn

##----------------------------------------------------------------------

def error_dialog(parent, msg, encoded_msg=None):

    if encoded_msg:
        #enc = locale.getlocale()[1]
        enc = default_encoding
        msg += encoded_msg.decode(enc, 'replace').encode('utf-8')

    dialog = gtk.MessageDialog(parent, gtk.DIALOG_MODAL \
                               | gtk.DIALOG_DESTROY_WITH_PARENT,
                               gtk.MESSAGE_ERROR, gtk.BUTTONS_OK,
                               msg)

    dialog.run()
    dialog.destroy()

##----------------------------------------------------------------------

class OpenFileDialog:

    file_select_path = os.path.expanduser('~/')

    def __init__(self, win, select_multiple=None, save_as=None, filename=None):

        #dialog = gtk.FileSelection()
        #dialog.set_transient_for(win)
        dialog = gtk.FileChooserDialog("Select file",
                                   win,
                                   gtk.FILE_CHOOSER_ACTION_OPEN,
                                   (gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL,
                                    gtk.STOCK_OPEN, gtk.RESPONSE_OK))        
        dialog.set_transient_for(win)
        dialog.set_default_response(gtk.RESPONSE_OK)
        if filename:
            dialog.set_filename(os.path.join(self.file_select_path, filename))
        else:
            dialog.set_filename(self.file_select_path)
        dialog.show()
        #dialog.run()
        self.filename = None
        self.files_list = None

        if select_multiple:
            dialog.set_select_multiple(True)
            button = gtk.Button('Select _all')
            button.connect('clicked', lambda w:
                           dialog.file_list.get_selection().select_all())
            dialog.button_area.pack_end(button)
            button.show()

        while 1:

            response = dialog.run()
            if response == gtk.RESPONSE_OK:

                filename = dialog.get_filename()

                if os.path.isdir(filename): # go to selected dir and continue
                    model, iter = dialog.dir_list.get_selection().get_selected()
                    if iter:
                        dirname = os.path.normpath(filename
                                                   + model.get_value(iter, 0)) \
                                                   + os.sep
                    else:
                        dirname = os.path.normpath(filename) + os.sep
                    OpenFileDialog.file_select_path = dirname
                    dialog.set_filename(dirname)
                    continue

                if select_multiple: # select multiple

                    OpenFileDialog.file_select_path \
                        = os.path.dirname(filename) + os.sep

                    sel = dialog.file_list.get_selection()
                    files_list = []
                    sel.selected_foreach(lambda model, path, iter:
                        files_list.append(fix_filename_2(model.get_value(iter, 0))))
                    self.filename = filename
                    self.files_list = files_list
                    if not files_list and filename:
                        self.files_list = [filename]
                    dialog.destroy()
                    return

                elif save_as:
                    if os.path.exists(filename):

                        md = gtk.MessageDialog(dialog, gtk.DIALOG_MODAL \
                                               | gtk.DIALOG_DESTROY_WITH_PARENT,
                                               gtk.MESSAGE_WARNING,
                                               gtk.BUTTONS_OK_CANCEL,
                                               'File %s exists. Overwrite?' \
                                               % fix_filename(filename))

                        response = md.run()
                        if response == gtk.RESPONSE_OK:
                            md.destroy()
                            self.filename = filename
                        else:
                            md.destroy()
                            continue
                    else:
                        self.filename = filename

                    dialog.destroy()
                    return

                else:

                    try:
                        open(filename)
                    except IOError, err:
                        error_dialog(dialog, "Can't open file %s: %s" \
                                     % (fix_filename(filename), err[1]))
                        continue
                    else:
                        self.filename = filename
                        OpenFileDialog.file_select_path \
                            = os.path.dirname(filename) + os.sep
                        dialog.destroy()
                        return

            else: # response != gtk.RESPONSE_OK
                dialog.destroy()
                return

##----------------------------------------------------------------------
