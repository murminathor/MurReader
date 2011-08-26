#!/usr/bin/env python
# -*- coding: utf-8; -*-
# (c) Con Radchenko mailto:lankier@gmail.com

import os, locale

PROGRAM_NAME            = 'MurReader'
PROGRAM_VERSION         = '0.5'
CONFIG_PREFIX           = PROGRAM_NAME.lower()
CONFIG_DIR              = os.path.expanduser('~/.' + CONFIG_PREFIX )
CONFIG_FILE             = os.path.join( CONFIG_DIR, CONFIG_PREFIX + '.conf' )
IFACE_FILE              = os.path.join( CONFIG_DIR, CONFIG_PREFIX + '-iface.conf' )
STYLES_FILE             = os.path.join( CONFIG_DIR, 'styles' )
WINDOW_FILE             = os.path.join( CONFIG_DIR, 'window' )
RECENT_FILE             = os.path.join( CONFIG_DIR, 'recent' )
NUM_RECENT_FILES        = 40
USER_SKIN_DIR           = os.path.join( CONFIG_DIR,    'skins' )
DEFAULT_SKIN            = os.path.join( USER_SKIN_DIR, 'golden.jpg' )
BOOKMARKS_FILE          = os.path.join( USER_SKIN_DIR, 'bookmarks' )
FILETYPES_FILE          = os.path.join( CONFIG_DIR,    'filetypes' )
DICTCLIENT_RC_FILE      = os.path.join( CONFIG_DIR,    'dictclient.rc' )
DICTCLIENT_HISTORY_FILE = os.path.join( CONFIG_DIR,    'dictclient_history' )
CHARSETS_LIST           = ( 'koi8-r', 'cp1251', 'cp866', 'iso8859-5', 'utf-8' )
PREVIEW_LENGTH          = 4000
DEFAULT_CATEGORY        = 'paragraph'

DEFAULT_ENCODING        = locale.getlocale()[1]
if not DEFAULT_ENCODING:
    DEFAULT_ENCODING    = 'iso8859-1'

DEFAULT_DESCRIPTION_LENGTH = 200

STYLES_LIST = (
    'paragraph',
    'title',
    'subtitle',
    'epigraph',
    'cite',
    'stanza',
    'footnote',
    'hyperlink',
    'text_author',
    'strong',
    'emphasis',
    #'code'
    #'superscript'
    #'subscript'
    #-'verse',
    )

SETTINGS_LIST = (
    'font_family',
    'font_size',
    'italic',
    'bold',
    #'ascent',
    #'descent',
    #'monospace',
    'color',
    'justify',
    'hyphenate',
    'left_indent',
    'right_indent',
    'first_line_indent',
    'pixels_inside_wrap',
    'pixels_above_line',
    'pixels_below_line'
    )

JUSTIFY_LIST = (
    'left',
    'right',
    'center',
    'fill'
    )
