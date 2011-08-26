#!/usr/bin/env python
# -*- coding: utf-8 -*-

# from __future__ imports must occur at the beginning of the file
# Only for python <= 2.2
from __future__      import generators
from cStringIO       import StringIO
from gtk             import gdk
from content         import Content
from hyphenation     import Hyphenation
from miscutils       import error_dialog, fix_filename
from properties_gtk  import STYLES_LIST

import string, sys, os, time
import gobject, gtk, pango
#import config
import base64
#==============================================================================


__all__ = [ 'OrnamentBook', 'createBufferRGB' ]

skins_dir = 'skins'

PANGO_SCALE = pango.SCALE
#PANGO_SCALE = 1024

default_lang = 'ru'
#==============================================================================

def createBufferRGB( width, height, color1, color2 = None ):
  #
  # Теоретис-с-ски это функция для создания некоего цветового буфера
  # Но почему именно таким образом организованная - пока что не понятно.
  #

  #r1, g1, b1 = int(color1[1:3], 16), int(color1[3:5], 16), int(color1[5:7], 16)
  r1 = int( color1[1:3], 16 )
  g1 = int( color1[3:5], 16 )
  b1 = int( color1[5:7], 16 )

  if color2: # gradient
    buff = []
    #r2, g2, b2 = int(color2[1:3], 16), int(color2[3:5], 16), int(color2[5:7], 16)
    r2 = int( color2[1:3], 16 )
    g2 = int( color2[3:5], 16 )
    b2 = int( color2[5:7], 16 )

    for i in range( height ):
      r = int( r1 - ( r1 - r2 ) * i / float( height - 1 ) )
      g = int( g1 - ( g1 - g2 ) * i / float( height - 1 ) )
      b = int( b1 - ( b1 - b2 ) * i / float( height - 1 ) )
      buff.append( ( chr(r) + chr(g) + chr(b) ) * width )

    buff = '' . join(buff)

  else:
    buff = ( chr(r1) + chr(g1) + chr(b1) ) * ( width * height )

  return buff
#==============================================================================

def split_line(line):
  # split line, f.e.:
  # '\taa bbbb  cc    ddd' ->
  # [('\taa', 0, 4), ('bbbb', 4, 9), (' cc', 9, 13),
  #  (' ', 13, 15), (' ddd', 15, 20)]
  word       = ''
  curr_char_id = 0
  prev_char_id = 0

  for c in line:
    curr_char_id += 1
    if c in string.whitespace:
      if word:
        yield (word, prev_char_id, curr_char_id)
        prev_char_id = curr_char_id
        word       = ''
        continue
    #else:
    word += c
  if word: yield (word, prev_char_id, curr_char_id + 1 )
  return
#==============================================================================

class RectangleData():
  '''Своеобразный контейнер для нужд некоторых функций в основном классе модуля
  '''
  def __init__(self):
    self.left   = 0
    self.top    = 0
    self.width  = 0
    self.height = 0
    self.data   = None
#==============================================================================


class OrnamentBook(gtk.DrawingArea):

    keysyms_next = (gtk.keysyms.KP_Page_Down,
                    gtk.keysyms.Page_Down,
                    gtk.keysyms.space,
                    gtk.keysyms.Right,
                    gtk.keysyms.Down
                   )
    keysyms_prev = (gtk.keysyms.KP_Page_Up,
                    gtk.keysyms.Page_Up,
                    gtk.keysyms.Left,
                    gtk.keysyms.Up
                   )

#=============================================================================#
#                                                                             #
#                               Private methods                               #
#                                      v                                      #
#=============================================================================#

    def __init__(self, main_win):

        default_background = 'golden.jpg'
        background_file = None
        for d in sys.path:
            f = os.path.join(d, 'ornamentbook', skins_dir, default_background)
            if os.path.exists(f):
                background_file = f
                break
        if not background_file:
            sys.exit('ERROR: can\'t find default background file %s' % default_background)
        self.background_file = background_file

        gtk.DrawingArea.__init__(self)

        # Hyphenation
        self.hyph = Hyphenation()
        #self.lang = default_lang

        self._parent = main_win.window
        #self.gc = None
        #self.area = gtk.DrawingArea()

##         self.set_size_request(950, 400)
##         self.width = 950
##         self.height = 400

        gobject.signal_new( 'position-changed', OrnamentBook,
                             gobject.SIGNAL_RUN_LAST,
                             gobject.TYPE_NONE,
                            (gobject.TYPE_FLOAT,)
                          )

        self.set_size_request(600, 400)
        self.width   = 600
        self.height  = 400
        self.textArea = {'width':0, 'height':0}
        self.statusTimeFormat = '%H:%M' # Формат строки со временем в статусе

        #self.set_events(gdk.ALL_EVENTS_MASK)
        #self.add_events(gdk.BUTTON_PRESS_MASK|gdk.BUTTON_RELEASE_MASK)
        #self.add_events(gdk.BUTTON_RELEASE_MASK)
        self.add_events(gdk.BUTTON_PRESS_MASK)
        #self.add_events(gdk.BUTTON_PRESS_MASK|gdk.BUTTON_RELEASE_MASK|gdk.KEY_PRESS_MASK|gdk.KEY_RELEASE_MASK)
        #self.set_events(gdk.ALL_EVENTS_MASK)

        self.connect('expose-event', self.__area_expose_cb)
        #self.connect('button_release_event', self.button_event_cb)
        self.connect('button_press_event', self.button_event_cb)
        #self.realize()

        self._parent.connect('key_press_event', self.key_event_cb)
        #self._parent.connect('key-release-event', self.key_event_cb)

        self.properties   = main_win.properties
        self.content_menu = main_win.content_menu

        self.current_page_line_index = 0
        self.current_page_char_index = 0

        self.next_page_line_index = 0
        self.next_page_char_index = 0

        self.pixmap_area = None
        #self.prev_pixmap_area = None
        self.next_pixmap_area = None

        #self.content = [] # ???
        self.content = Content()
        self.content.textLength = 0

        self.footnotes_list  = []
        self.prev_index_list = []

        return
#==============================================================================

    def __create_background_pixmap( self, width, height, depth ):

        if self.properties.use_gradient:
            buff = createBufferRGB( width, height,
                                    self.properties.background_color,
                                    self.properties.gradient_color
                                  )
        else:
            buff = createBufferRGB( width, height,
                                    self.properties.background_color
                                  )

        self.background_pixmap = gdk.Pixmap( None, width, height, depth )
        self.background_pixmap.draw_rgb_image( self.gc, 0, 0, width, height,
                                               gdk.RGB_DITHER_NONE, buff,
                                               width * 3
                                             )
#==============================================================================

    def __area_expose_cb(self, area, event):
        x, y, w, h, d = self.window.get_geometry()
        if self.pixmap_area and self.width == w and self.height == h:
            self.window.draw_drawable(self.gc, self.pixmap_area,
                                      0, 0, 0, 0, w, h)
        else:
            self.draw_text()
#==============================================================================

    def __prepareTextToDraw(self):
      '''__prepareTextToDraw()

        Различные подготовительные работы для отрисовки текста
      '''

      x, y, widget_width, widget_height, depth = self.window.get_geometry()

      if not self.pixmap_area \
            or self.width  != widget_width \
            or self.height != widget_height:
        if self.pixbuf:
          self.cur_pixbuf = self.pixbuf.scale_simple( widget_width,
                                                      widget_height,
                                                      gdk.INTERP_BILINEAR
                                                    )
        else:
          self.__create_background_pixmap( widget_width, widget_height, depth )

        self.width  = widget_width
        self.height = widget_height

        self.next_pixmap_area = self.pixmap_area = \
                  gdk.Pixmap( None, widget_width, widget_height, depth )

        #self.next_pixmap_area = gdk.Pixmap( None, widget_width, widget_height, depth )

        self.status_pixmap_area = gdk.Pixmap(
                                      None, self.width,
                                      self.properties.status_font_height + \
                                      self.properties.status_y_position,
                                      depth
                                    )
#==============================================================================

    def __drawNextPage(self):
      '''__drawNextPage()

        Рисует следующую страницу
      '''

      line_id, char_id = self.__draw( self.pixmap_area,
                                       self.current_page_line_index,
                                       self.current_page_char_index
                                    )
      self.next_page_line_index = line_id
      self.next_page_char_index = char_id
#==============================================================================

    def __drawPrevPage(self):
      '''__drawPrevPage()

        Рисует предыдущую страницу
      '''
      self.next_page_line_index = self.next_next_page_line_index
      self.next_page_char_index = self.next_next_page_char_index

      # Эта конструкция позволяет осуществить ОБМЕН значениями переменных
      # БЕЗ использования промежуточной переменной !!!
      self.pixmap_area, self.next_pixmap_area = \
                        self.next_pixmap_area, self.pixmap_area
#==============================================================================

    def __prepareStatusPercent(self):
      '''__prepareStatusPercent()

        Подготавливает "почву" для отрисовки прочитаннго в процентах
        Возвращает True в любом случае
      '''
      if self.properties.status_show_percent:
        pos         = self.calc_position()
        pangolayout = self.create_pango_layout( str( int(pos * 100) ) + '%' )

        pangolayout.set_font_description( self.properties.status_pango_font_desc )
        self.status_pixmap_area.draw_layout(
            self.gc, self.properties.status_percent_x_position, 0, pangolayout,
            foreground=gdk.color_parse(self.properties.status_color)
        )

      return True
#==============================================================================

    def __prepareStatusTime(self):
      '''__prepareStatusTime()

        Подготавливает "почву" для отрисовки текущего времени
        Возвращает True в любом случае
      '''
      if self.properties.status_show_clock:

        t = time.strftime( self.statusTimeFormat, time.localtime() )

        pangolayout = self.create_pango_layout( t )
        pangolayout.set_font_description( self.properties.status_pango_font_desc )

        x_pos =  self.width - self.properties.status_clock_x_position - \
                 pangolayout.get_extents()[1][2] / PANGO_SCALE
        self.status_pixmap_area.draw_layout(
          self.gc, x_pos, 0, pangolayout,
          foreground=gdk.color_parse(self.properties.status_color)
        )
      return True
#==============================================================================

    def __calc_text_area_geometry(self):
      '''Расчитывает геометрические размеры текстовой области'''
      self.textArea['height'] = self.height - \
                                self.properties.text_top_margin - \
                                self.properties.text_bottom_margin
      self.textArea['width']  = self.width - \
                                self.properties.text_left_margin - \
                                self.properties.text_right_margin

      if not self.properties.single_column:
         self.textArea['width'] = ( self.textArea['width'] - \
                                    self.properties.text_spaces_between_column
                                  ) / 2
      return True
#==============================================================================

    def __calcGeometry(self):
      '''__calcGeometry()

          Расчитывает геометрические размеры виджета
      '''
      self.__calc_text_area_geometry()

      self.offsetX  = self.properties.text_left_margin
      self.offsetY  = self.properties.text_top_margin

      if not self.properties.single_column:
         # Смещение для правой страницы при двостраничном отображении
         # при одностраничном не использутеся
         self.offsetXr = self.textArea['width'] + \
                         self.properties.text_left_margin + \
                         self.properties.text_spaces_between_column

      return True
#==============================================================================

    def __base64Img2Pixbuf( self, imageId ):
      '''__base64Img2Pixbuf( imageId )

        Конвертирует изображение из base64-"упаковки" в gtk.gdk.Pixbuf БЕЗ
        использования промежуточных файлов.

        imageId - индекс требуемого изображения в общем словаре изображений
                  self.content.images

        Возвращает gtk.gdk.Pixbuf
      '''
      pixbufLoader = gtk.gdk.PixbufLoader()
      pixbufLoader.write( base64.decodestring( self.content.images[ imageId ] ) )
      pixbufLoader.close()

      return pixbufLoader.get_pixbuf()
#==============================================================================

    def __getImageScaled( self, imageId ):
      '''__getImageScaled( imageId, max_width, max_height )

        Масштабирует при необходимости изображение, дабы его размеры
        не превышали указанные максимальные значения max_width, max_height
        ширину и высоту, соответственно

        imageId - индекс требуемого изображения в общем словаре изображений
                self.content.images

        Возвращает gtk.gdk.Pixbuf
      '''

      pb = self.__base64Img2Pixbuf( imageId )
      w  = pb.get_width()
      h  = pb.get_height()

      # max_width  = self.textArea['width']
      # max_height = self.textArea['height']
      if w > self.textArea['width'] or h > self.textArea['height']:
        scale = min( float( self.textArea['width'] )/w, \
                     float( self.textArea['height'] )/h
                   )
        pb    = pb.scale_simple( int( w * scale ), int( h * scale ),
                                  gdk.INTERP_BILINEAR
                               )
      return pb
#==============================================================================

    def __drawImage( self, area_window, imageId, offsetX, offsetY ):
      '''__drawImage( area_window, imageId, offset_x, offset_y)

        Рисует требуемое изображение в указанной области окна ( area_window )
        с заданным смещением ( offsetX, offsetY ). При этом нарисованное
        изображение не будет превышать указанные максимальные размеры
        ( self.textArea['width'], self.textArea['height'] )

        В случае ошибки возвращает -1. Иначе - нижнюю координату изображения
        ( offsetY + height )
      '''
      pb = self.__getImageScaled( imageId )
      is_top = offsetY == self.properties.text_top_margin and 1 or 0

      width  = pb.get_width()
      height = pb.get_height()

      if not is_top and offsetY + height > self.textArea['height']:
        return -1

      area_window.draw_pixbuf(
          self.gc, pb, 0, 0,
          offsetX + ( self.textArea['width'] - width ) / 2, offsetY,
          width, height,  False, 0, 0)

      return offsetY + height
#==============================================================================

    def __paragraph_has_image(self, par_index):
      '''__paragraph_has_image( par_index )

        Возвращает True если параграф № par_index имеет изображения
        и False в ином случае
      '''
      return self.content[ par_index ].type == 'image'
#==============================================================================

    def __paragraph_has_footnotes(self, par_index):
      '''__paragraph_has_footnotes( par_index )

        Возвращает True если параграф № par_index имеет сноски
        и False в ином случае
      '''
      return bool( self.content[line_id].footnotes )
#==============================================================================

    def __calc_footnotes_height(self):
      ''' Рассчитывает высоту строки/текста(?) сноски'''
      ft_note_height = 0
      ft_note_style = self.properties.styles['footnote']

      # ---
      ft_note_height = ft_note_style.font_height
      for ft in self.footnotes_list[:-1]:
        ft_note_height += ft_note_style.font_height \
                         +ft_note_style.pixels_inside_wrap
        if ft == []:
          ft_note_height += ft_note_style.pixels_below_line \
                           -ft_note_style.pixels_inside_wrap

      return ft_note_height
#==============================================================================

    def __create_pl_word(self, par, curr_style, word, text_start, text_end):

        font = curr_style.font

        # TODO:  Осуществить конвертирование всего текста в utf-8 сразу
        #        по добавлению данных
        # Почему-то тут в некоторых словах вылазит глюк, если в самом начале
        # изменить кодировку всего фрагмента
        #word = word.encode('utf-8')

        # create_pango_layout наследуется из родительского класса gtk.DrawingArea
        pangolayout = self.create_pango_layout( word.encode('utf-8') )
        pangolayout.set_font_description(font)


        attr_list = None

        for start, length, st in par.styles:
            if start + length > text_start and start < text_end:

                if not attr_list:
                    attr_list = pango.AttrList()

                s = start - text_start
                e = s + length
                if s < 0: s = 0
                s = len( word[:s].encode('utf-8') )
                e = len( word[:e].encode('utf-8') )

                if st in ('emphasis', 'strong', 'hyperlink'):
                    if self.properties.styles[st].__dict__.has_key('italic'):
                        attr_list.insert(pango.AttrStyle(
                            pango.STYLE_ITALIC, s, e) )
                    if self.properties.styles[st].__dict__.has_key('bold'):
                        attr_list.insert(pango.AttrWeight(
                            pango.WEIGHT_BOLD, s, e))
                    if self.properties.styles[st].__dict__.has_key('font_family'):
                        attr_list.insert(pango.AttrFamily(
                            self.properties.styles[st].font_family, s, e))
                    if self.properties.styles[st].__dict__.has_key('color'):
                        attr_list.insert(pango.AttrForeground(
                            self.properties.styles[st].gdk_color.red,
                            self.properties.styles[st].gdk_color.green,
                            self.properties.styles[st].gdk_color.blue,
                            s, e))

                    if self.properties.styles[st].__dict__.has_key('font_size'):
                        attr_list.insert(pango.AttrSize(
                            self.properties.styles[st].font_size*PANGO_SCALE, s, e))

                elif st == 'footnote':
                    attr_list.insert(pango.AttrRise(PANGO_SCALE * curr_style.font_height/4, s, e))
                    attr_list.insert(pango.AttrFontDesc(self.properties.styles['footnote'].font, s, e))

        if attr_list:
            pangolayout.set_attributes(attr_list)

        return pangolayout
#==============================================================================

    def __findHypenateLang(self, paragraph, text_start, text_end):
      '''__findHypenateLang( paragraph, text_start, text_end )

        Находит язык для указанного сегмента текста
      '''

      lang = self.content.lang
      for start, length, stl in paragraph.styles:
        if start + length  > text_start and \
                   start   < text_end   and \
                   stl[:4] == 'lang':
          lang = stl[5:]
          break

      return lang
#==============================================================================

    # TODO: Уменьшить количество аргументов!!!
    def __hyphenate1( self, paragraph, word, curr_style, text_start, text_end,
                      ch_begin, total_width, text_width, p_index, c_index  ):

      '''__hyphenate1( paragraph, word, curr_style, text_start, text_end,
                       ch_begin, total_width, text_width, p_index, c_index )

        Перенос слова по слогам. Первая функция
      '''
      font = curr_style.font
      lang = self.__findHypenateLang( paragraph, text_start, text_end )

      word_parts_list = self.hyph.hyphenate( word, lang )

      for word_part in word_parts_list:
          text_start = ch_begin + p_index
          text_end   = ch_begin + c_index
          wp_pl = self.__create_pl_word( paragraph, curr_style,
                                         word_part + u'-',
                                         text_start, text_end
                                       )
          wp_width = wp_pl.get_extents()[1][2]/PANGO_SCALE

          if total_width + wp_width < self.textArea['width']:
              text_width += wp_width
              c_index -= len( word ) - len( word_part ) + 1
              # skip leading '-'
              if word[ len( word_part ) ] == '-':
                  c_index += 1

              self.pangolayout_list.append( (wp_pl, wp_width, c_index) )
              p_index = c_index
              break

      return ( c_index, p_index, text_start, text_end )
#==============================================================================

    # TODO: Уменьшить количество аргументов!!!
    def __hyphenate1_dummy( self, paragraph, word, curr_style,
                            text_start, text_end, ch_begin, total_width,
                            text_width, p_index, c_index ):
      '''__hyphenate1_dummy( paragraph, word, curr_style, text_start, text_end,
                             ch_begin, total_width, text_width, p_index,
                             c_index )

          Перенос слова по слогам. Заглушка для первой функции. Используется
          если в свойствах эта возсожность отключена
      '''

      return ( c_index, p_index, text_start, text_end )
#==============================================================================

    # TODO: Уменьшить количество аргументов!!!
    def __hyphenate2( self, paragraph, line, curr_style, text_start,
                      text_end, p_text_start, ch_begin, total_width,
                      text_width, p_index, c_index ):

      '''__hyphenate2( paragraph, line, curr_style, text_start, text_end,
                       p_text_start, ch_begin, total_width, text_width,
                       p_index, c_index )

        Перенос слова по слогам. Вторая функция
      '''
      font = curr_style.font
      lang = self.__findHypenateLang( paragraph, text_start, text_end )

      word = line[ p_text_start:p_index ]
      word_parts_list = self.hyph.hyphenate( word, lang )

      if word_parts_list:
        word_part  = word_parts_list[0]
        text_start = ch_begin + p_text_start
        text_end   = ch_begin + len( word_part )

        wp_pl = self.__create_pl_word( paragraph, curr_style,
                                       word_part + u'-',
                                       text_start, text_end
                                     )
        wp_width = wp_pl.get_extents()[1][2] / PANGO_SCALE

        c_index = p_text_start + len( word_part )
        # skip leading '-'
        if word[ len(word_part) ] == '-':
            c_index += 1
        self.pangolayout_list.append( (wp_pl, wp_width, c_index) )

        p_text_start += len( word_part )

      return ( c_index, p_index, text_start, text_end, p_text_start )
#==============================================================================

    # TODO: Уменьшить количество аргументов!!!
    def __hyphenate2_dummy( self, paragraph, line, curr_style,
                            text_start, text_end, p_text_start, ch_begin,
                            total_width, text_width, p_index, c_index ):
      '''__hyphenate2_dummy( paragraph, line, curr_style, text_start, text_end,
                             p_text_start, ch_begin, total_width, text_width,
                             p_index, c_index )

          Перенос слова по слогам. Заглушка для второй функции. Используется
          если в свойствах эта возсожность отключена
      '''

      return ( c_index, p_index, text_start, text_end, p_text_start )
#==============================================================================

    def __create_pl_line(self, par, style_type, char_begin=0, char_end=None):

        '''create list:
          [[pangolayout, width, char_id] [pangolayout, width, char_id] [...]]
        '''
        line  = par.data[ char_begin:char_end ]

        style = self.properties.styles[ style_type ]
        font  = style.font

        #print style.font_family

        space_width = style.space_width

        text_width  = 0
        total_width = 0
        new_char_id = 0

        self.pangolayout_list = []
        prev_text_start  = 0


        #   Глупо проверять множесто раз в цикле одну и ту же переменную -
        # она же не меняется, после установки значения вначале функции.
        # А делать то же самое в двух местах цикла - глупость в квадрате!
        #   Оптимальный вариант - вынести содержимое ветки `if hyphenate:`
        # в отдельную функцию. После этого ПЕРЕД циклом определить переменую-
        # функцию, которую и вызывать в цикле.
        hyphenate1 = self.__hyphenate1_dummy
        hyphenate2 = self.__hyphenate2_dummy
        if style.hyphenate:
          hyphenate1 = self.__hyphenate1
          hyphenate2 = self.__hyphenate2
        word_list = []
        for word, prev_char_id, curr_char_id in split_line(line):

            text_start = char_begin + prev_char_id
            text_end   = char_begin + curr_char_id
            pl_word    = self.__create_pl_word( par, style, word,
                                                text_start, text_end )
            width      = pl_word.get_extents()[1][2] / PANGO_SCALE
            word_list.append(word)

            if total_width + width > self.textArea['width']:

                curr_char_id, prev_char_id, text_start, text_end = \
                           hyphenate1( par, word, style, text_start, text_end,
                                       char_begin, total_width, text_width,
                                       prev_char_id, curr_char_id
                                     )

                new_char_id = char_begin + prev_char_id

                pl_len = len( self.pangolayout_list )

                # Эта ветка работает если отключена функция переноса слов
                if  pl_len == 0:
                    # слово не влазит в строку
                    for i in range( len(word), 0, -1 ):
                        char    = word[:i]
                        char_pl = self.__create_pl_word(
                                             par, char, style,
                                             char_begin, char_begin + i + 1
                                                       )
                        char_width = char_pl.get_extents()[1][2] / PANGO_SCALE
                        if total_width + char_width < self.textArea['width']:
                            text_width += char_width
                            prev_char_id  = i
                            new_char_id   = char_begin + i
                            self.pangolayout_list.append(( char_pl, char_width,
                                                           char_begin + i ))
                            break

                elif pl_len > 4 and \
                     prev_char_id < len(line)    and \
                     line[prev_char_id] in u'-\u2013\u2014':
                    # строка не должна начинаться с тире
                    del self.pangolayout_list[-1]

                    curr_char_id, prev_char_id, text_start, text_end, prev_text_start = \
                        hyphenate2( par, line, style, text_start, text_end,
                                    prev_text_start, char_begin, total_width,
                                    text_width, prev_char_id, curr_char_id )

                    new_char_id = char_begin + prev_text_start


                break

            text_width     += width
            total_width    += width + space_width
            prev_text_start = prev_char_id
            self.pangolayout_list.append( (pl_word, width, curr_char_id) )
        return new_char_id
#==============================================================================

    def __get_cb_index_list(self, paragraph, style_type, char_id = None):
      '''Не разобрался толком что делает.
         Создание вызвано технической необходимостью - этот фрагмент кода
         используется 2 раза в __calc_back_1
      '''
      new_char_id = 0
      index_list = [0]
      while True:
        new_char_id = self.__create_pl_line( paragraph, style_type,
                                           new_char_id, char_id )
        if new_char_id == 0: break
        index_list.append(new_char_id)

      index_list.reverse()

      return index_list
#==============================================================================

    def __create_footnotes_list( self, line_id, begin, end ):
      ''' __create_footnotes_list( line_id, begin, end )

          Формирует список сносок/примечаний в формате PangoLayout

          \param line_id - индекс параграфа, для которого нужно создать
                              список сносок/примечаний
          \param begin      - начало (отображаемой) строки (???)
          \param end        - конец (отображаемой) строки  (???)
      '''
      footnotes_list = []
      for f in self.content[line_id].footnotes:
        if begin <= f[1] <= end and self.content.footnotes.has_key(f[2]):
          for fn_par in self.content.footnotes[ f[2] ]:
            fn_index = 0
            # TODO: Убрать "вечный" цикл. По возможности
            while True:
              fn_index = self.__create_pl_line( fn_par, 'footnote', fn_index )

              footnotes_list.append( self.pangolayout_list )
              if fn_index == 0: break

            footnotes_list.append([])

      return footnotes_list
#==============================================================================

    def __draw_footnotes(self, area_window, offset_x, y):

        style = self.properties.styles['footnote']
        font_height = style.font_height
        space_width = style.space_width
        pixels_inside_wrap = style.pixels_inside_wrap
        pixels_below_line = style.pixels_below_line

        if y+font_height > self.textArea['height']:
            #+self.properties.text_top_margin:
            #print '++'
            return

        list_index = 0

        area_window.draw_line( self.gc, offset_x, y + font_height * 2/3,
                               offset_x + self.textArea['width'] / 3,
                               y + font_height * 2/3 )
        y += font_height

        for pl in self.footnotes_list:

            if not self.footnotes_list[list_index]:
                # empty list -> new paragraph
                list_index += 1
                continue

            #print y, font_height, self.textArea['height']
            if y + font_height + pixels_inside_wrap > \
               self.textArea['height'] + self.properties.text_top_margin:
                #print '--', y, pixels_inside_wrap
                break

            text_width = reduce( lambda a, b: a+b, map(lambda x: x[1], pl), 0 )

            if len(pl) <= 1:
                # single word
                space = 0
            elif not self.footnotes_list[list_index+1]:
                # last line in this paragraph
                space = space_width
            else:
                space = (self.textArea['width'] - text_width )/(len(pl)-1)


            x = offset_x

            for i in range(len(pl)):

                if i == len(pl)-1 and self.footnotes_list[list_index+1]:
                    # and not char_id == 0: # and not is_title:
                    # last word in this line
                    x = offset_x + self.textArea['width'] - pl[i][1]

                self.gc.set_rgb_fg_color(style.gdk_color)
                area_window.draw_layout(self.gc, x, y, pl[i][0])
                                        #foreground=style.gdk_color)

                x += pl[i][1]+space

            if not self.footnotes_list[list_index+1]:
                # last line in this paragraph
                y += font_height+pixels_below_line
            else:
                y += font_height+pixels_inside_wrap
            list_index += 1

        self.footnotes_list = self.footnotes_list[list_index:]
#==============================================================================

    def __decor_text_line( self, line_id, char_id, offset_x, offset_y ):
      '''__decor_text_line( line_id, char_id, offset_x, offset_y )
         
         Оформляет/уточняет положение строки на странице: отступы, выравнивание
         размеры (высота, ширина)...
      '''

      result = []

      new_char_id  = 0
      par_type     = self.content[line_id].type
      par_style    = self.properties.styles[ par_type ]
      font_height  = par_style.font_height
      indent_right = par_style.right_indent

      line_bottom = offset_y
      if char_id == 0:
        line_bottom += par_style.pixels_above_line

      if line_bottom + font_height > self.textArea['height'] + \
        self.properties.text_top_margin:
        return line_bottom, new_char_id, None

      if not self.content[line_id].data:
        # empty line
        return line_bottom + font_height, -1, None

      indent_left = par_style.left_indent
      if char_id == 0:
        indent_left += par_style.first_line_indent

      ta_width = self.textArea['width'] - indent_left - indent_right

      # Пока что непонятно зачем нужен этот кусок кода.
      # Закоментирую-ка его "на всякий пожарный"
      #while not len(self.content[line_id].data) <= char_id and \
                 #self.content[line_id].data[char_id].isspace():
        #char_id += 1

      oldWidth = self.textArea['width']
      self.textArea['width'] = ta_width
      new_char_id = self.__create_pl_line( self.content[line_id],
                                            par_type, char_id )

      # Только для сокращения общей длины строки
      pl_list = self.pangolayout_list

      pl_list_len = len( pl_list )

      self.textArea['width'] = oldWidth
      oldWidth = None

      text_width = reduce( lambda a, b: a+b,
                                        map(lambda x: x[1], pl_list), 0
                          )

                                    #v last line in this paragraph
      if par_style.justify != 'fill' or new_char_id == 0:
        space = par_style.space_width
      elif pl_list_len <= 1:
        # single word
        space = 0
      else:
        # pl_list в знаменателе и может быть равно нулю.
        space = float( ta_width - text_width )/( pl_list_len - 1 )

      x = offset_x + indent_left
      if par_style.justify in ('center', 'right'):
        x1 = ta_width - ( pl_list_len - 1 ) * space - text_width
        if par_style.justify == 'center': x1 = x1 / 2
        x += x1

      for i in range( pl_list_len ):
        pl_word = RectangleData()

        if space and i == pl_list_len - 1 and not new_char_id == 0 \
           and par_style.justify == 'fill':
          # Последнее слово в этой строке
          x = offset_x + self.textArea['width'] - pl_list[i][1] - indent_right

        # из-за надстрочных символов
        pl_word.top = line_bottom + font_height + par_style.pixels_inside_wrap\
                     -pl_list[i][0].get_extents()[1][3] / PANGO_SCALE

        pl_word.left  = int(x)
        pl_word.width = pl_list[i][1]
        pl_word.data  = pl_list[i][0]

        result.append( pl_word )
        #area_window.draw_layout(self.gc, int(x), yy, pl_list[i][0])

        x += pl_list[i][1] + space

      line_bottom += font_height
      if new_char_id == 0:
        # Новый параграф
        line_bottom += par_style.pixels_below_line
      else:
        line_bottom += par_style.pixels_inside_wrap
      if new_char_id == 0:
        new_char_id = -1
      #else:
        #char_id = new_char_id

      return line_bottom, new_char_id, result
#==============================================================================

    def __assemble_paragraph( self, line_id, char_id, offset_x, offset_y ):
      '''__assemble_paragraph( line_id, char_id, offset_x, offset_y )
        
        Собирает параграф из строк. Если параграф нарисован полностью -
        возвращает line_id + 1
      '''
      paragraph_height = 0
      result = []

      # Нужен цикл с пост-условием. Но пока что не нашёл такого :(
      while True:
        if offset_y + paragraph_height > self.properties.text_top_margin + \
          self.textArea['height']:
          break

        line_bottom, char_id, data = \
        self.__decor_text_line( self, line_id, char_id, offset_x, offset_y )

        # Возможна ситуация, когда нет слов, а строку нужно нарисовать.
        # Например - пустая строка.
        paragraph_height += line_bottom

        if char_id == -1 or not data:
          char_id  = 0
          line_id += 1
          break

        # Упаковываем всё в один массив непрерывный, для удобства
        result.extend( data )

      return paragraph_height, line_id, char_id, result
#==============================================================================

    #
    # FIXME Чрезвычайно тупой алгоритм: рисуем данные последовательно
    #       при этом каждый раз высчитываем: поместится или нет.
    #       Как следствие - расчёт высоты ОДНОЙ И ТОЙ ЖЕ сноски может
    #       производится несколько ДЕСЯТКОВ!!! раз
    #
    def __draw_paragraph( self, area_window, line_id, char_id,
                          offset_x, offset_y ):
        # если параграф нарисован до конца - возвращает -1

        # Пдозреваю, что эта функция рисует не параграф, а страницу...

        new_char_id = 0

        type  = self.content[line_id].type
        style = self.properties.styles[type]

        footnote_style = self.properties.styles['footnote']
        font_height    = style.font_height
        indent_right   = style.right_indent

        self.gc.set_rgb_fg_color( style.gdk_color )

        y = offset_y
        if char_id == 0:
            y += style.pixels_above_line

        while True:

            # FIXME: Этот фрагмет кода просчитывается десятка полтора раз
            #        для одной сноски. Бред!!!
            footnotes_height = 0
            if self.footnotes_list:
                footnotes_height = self.__calc_footnotes_height()

            # Тут ">=", а не, скажем, "<=", поскольку сноска НЕ рисуется
            # пока не цикл в своём продвижении по оси OY не доберётся до её
            # позиции
            if footnotes_height and y + footnotes_height >= \
               self.textArea['height']:

                self.__draw_footnotes( area_window, offset_x, y )
                y = self.height
                new_char_id = char_id
                break

            if y + font_height > self.textArea['height'] + \
               self.properties.text_top_margin:
                break

            if not self.content[line_id].data:
                # empty line
                y += font_height
                new_char_id = -1
                break

            indent_left = style.left_indent
            if char_id == 0:
                indent_left += style.first_line_indent

            ta_width = self.textArea['width'] - indent_left - indent_right

            # Пока что непонятно зачем нужен этот кусок кода.
            # Закоментирую-ка его "на всякий пожарный"
            #while not len(self.content[line_id].data) <= char_id and \
                      #self.content[line_id].data[char_id].isspace():
                #char_id += 1

            oldWidth = self.textArea['width']
            self.textArea['width'] = ta_width
            new_char_id = self.__create_pl_line( self.content[line_id],
                                                 type, char_id )

            # Только для сокращения общей длины строки
            pl_list = self.pangolayout_list

            self.textArea['width'] = oldWidth
            oldWidth = None

            text_width = reduce( lambda a, b: a+b,
                                              map(lambda x: x[1], pl_list), 0
                               )

                                          #v last line in this paragraph
            if style.justify != 'fill' or new_char_id == 0:
                space = style.space_width
            elif len( pl_list ) <= 1:
                # single word
                space = 0
            else:
                # pl_list в знаменателе и может быть равно нулю.
                space = float( ta_width - text_width )/( len( pl_list ) - 1 )

            x = offset_x + indent_left
            if style.justify in ('center', 'right'):
                x1 = ta_width - ( len( pl_list ) - 1 ) * space - text_width
                if style.justify == 'center': x1 = x1 / 2
                x += x1


            for i in range(len( pl_list )):

                if space and i == len( pl_list )-1 and not new_char_id == 0 \
                       and style.justify == 'fill':
                    # last word in this line
                    x = offset_x + self.textArea['width'] - pl_list[i][1]-indent_right

                # из-за надстрочных символов
                yy = y + font_height + style.pixels_inside_wrap \
                     - pl_list[i][0].get_extents()[1][3] / PANGO_SCALE
                #  self.properties.styles['defaultSt'].text_height \

                #self.gc.set_rgb_fg_color(style.gdk_color)
                area_window.draw_layout(self.gc, int(x), yy, pl_list[i][0])
                                        #foreground=style.gdk_color)

                x += pl_list[i][1] + space

            y += font_height
            if new_char_id == 0:
                # new paragraph
                y += style.pixels_below_line
            else:
                y += style.pixels_inside_wrap

            # -- footnotes --
##         for f in self.content[line_id].footnotes:
##             if begin <= f[1] <= end:
##                 for par in self.content.footnotes[f[2]]:

            if self.content[line_id].footnotes:

                ni = new_char_id
                if not new_char_id:
                    ni = len(self.content[line_id].data)
                #ni = new_char_id == 0 \
                     #and len(self.content[line_id].data) \
                     #or  new_char_id
                footnotes_list = self.__create_footnotes_list(
                                               line_id, char_id, ni
                                                             )
                if footnotes_list:
                    self.footnotes_list.extend(footnotes_list)

            if new_char_id == 0:
                new_char_id = -1
                break
            else:
                char_id = new_char_id

        return y, new_char_id
#==============================================================================

    def __draw_1(self, area_window, line_id, char_id, offset_x, offset_y):
      #print 'draw_1', line_id, char_id

      is_top = True

      if char_id: # draw tail of line if need
        is_top = False
        offset_y, char_id = self.__draw_paragraph( area_window, line_id,
                                                   char_id, offset_x, offset_y
                                                 )

        if char_id == -1:
          char_id  = 0
          line_id += 1

      elif len( self.content ) > 0:
        # пропускаем пустые строки в начале страницы
        while len(self.content) > line_id           and \
              self.content[line_id].type != 'image' and \
              self.content[line_id].data == ''           :
          line_id += 1

      for par in self.content[line_id:]:
        if par.type != 'title' and par.data:
          is_top = False

        if par.type == 'image':
          if not self.content.images.has_key(par.href):
            # workaround
            char_id = -1
            line_id += 1
            continue

          yy = self.__drawImage( area_window, par.href, offset_x, offset_y )
          if yy >= 0:
            char_id = -1
            offset_y = yy
            line_id += 1
          else: # не поместилось
            break

        else:
          if self.properties.new_page and not is_top and par.type == 'title':
            break

          if offset_y + self.properties.styles[par.type].font_height > \
              self.properties.text_top_margin + self.textArea['height']:
            break

          offset_y, char_id = self.__draw_paragraph(
                                                     area_window, line_id, 0,
                                                     offset_x, offset_y
                                                   )

          if char_id == -1:
            char_id = 0
            line_id += 1

      return line_id, char_id
#==============================================================================

    def __draw(self, area_window, line_id, char_id):
      if self.pixbuf:
        area_window.draw_pixbuf( self.gc, self.cur_pixbuf,
                                  0, 0, 0, 0, -1, -1, False, 0, 0
                               )
      else:
        area_window.draw_drawable( self.gc, self.background_pixmap,
                                  0, 0, 0, 0, self.width, self.height
                                 )

      # Нужно бы поместить эту строчку в __init__(). Но пока что тут
      self.__calcGeometry()

      # Рисуем одиночный столбец/одинарную страницу.
      # Если отображаются 2 столбца - рисуем только левый столбец/левую
      # страницу. Их положение и/или размер определяется значениями
      # self.textArea['width'] и self.offsetX
      line_id, char_id = self.__draw_1( area_window, line_id, char_id,
                                         self.offsetX, self.offsetY
                                       )

      # Если отображаются 2 столбца - рисум дополнительно правый столбец/
      # правую страницу.
      if not self.properties.single_column:
        line_id, char_id = self.__draw_1( area_window, line_id, char_id,
                                           self.offsetXr, self.offsetY
                                         )

      self.next_page_line_index = line_id
      self.next_page_char_index = char_id

      #area_window.thaw_updates()

      return line_id, char_id
#==============================================================================

    def __get_cb_indexes(self, par_style, y, index_list ):
      '''Не разобрался толком что делает.
         Создание вызвано технической необходимостью - этот фрагмент кода
         используется 2 раза в __calc_back_1
      '''

      for new_char_id in index_list:
        y += par_style.font_height
        if new_char_id == 0:
          # new paragraph
          y += par_style.pixels_below_line
        else:
          y += par_style.pixels_inside_wrap

        if y + par_style.font_height + par_style.pixels_below_line > \
          self.textArea['height']:
          return new_char_id, y

      return  0, y
#==============================================================================

    def __calc_back_1(self, line_id, char_id ):
        new_line_index = line_id
        #new_char_id = char_id

        par = self.content[line_id]
        type = par.type

        # FIXME: В оригинале этого условия не требовалось. Что изменилось?
        try:
            style = self.properties.styles[type]
        except KeyError:
            return line_id-1, char_id

        y = 0
        if char_id:
            # tail of line
            index_list = self.__get_cb_index_list( par, par.type, char_id )
            new_char_id, y = self.__get_cb_indexes( style, y, index_list )
            if new_char_id:
                return new_line_index, new_char_id

        paragraphs = self.content[:new_line_index]
        paragraphs.reverse()

        for par in paragraphs:
            type = par.type
            #line = par.data

            new_line_index -= 1
            if type == 'image':
                y += style.font_height
                #print len(self.content.images[par.href])

                pb = self.__getImageScaled( par.href )
                h = pb.get_height()

                if y + h >= self.textArea['height']:
                    return new_line_index, 0
                y += h #+self.properties.styles['defaultSt'].text_height
                continue

            style = self.properties.styles[type]

            index_list = self.__get_cb_index_list( par, type )
            if not index_list:
                # empty line
                y += style.font_height + style.pixels_below_line
                if y + style.font_height + style.pixels_below_line > \
                   self.textArea['height']:
                    return new_line_index, 0
                continue

            new_char_id, y = self.__get_cb_indexes( style, y, index_list )
            if new_char_id:
                return new_line_index, new_char_id

        return 0, 0
#==============================================================================

    def __calc_back(self):
        self.__calc_text_area_geometry()

        line_id = self.current_page_line_index
        char_id = self.current_page_char_index

        # Вся страница, если установлен флаг single_column 
        # или левая страница в ином случае
        line_id, char_id = self.__calc_back_1(line_id, char_id )

        if not self.properties.single_column:
            # Правая страница
            line_id, char_id = self.__calc_back_1( line_id, char_id )

        return line_id, char_id

#=============================================================================#
#                                                                             #
#                                Public methods                               #
#                                      v                                      #
#=============================================================================#

    def set_background(self, filename):
        '''Устанавливает фон "книги" из файла'''
        try:
            open(filename)
        except IOError, err:
            sys.stderr.write('ERROR: can\'t open file: %s: %s\n'
                             % ( filename, str(err) )
                            )
            return False

        self.background_file = filename

        self.pixbuf      = gdk.pixbuf_new_from_file( self.background_file )
        self.cur_pixbuf  = self.pixbuf.scale_simple( self.width, self.height,
                                                     gdk.INTERP_BILINEAR )
        self.properties.use_background = True
#==============================================================================

    def initialize(self):

        for st in STYLES_LIST:
            self.properties.styles[st].set_font_desc(self)

        style   = self.get_style()
        self.gc = self.window.new_gc()

        self.gc.set_colormap(self.style.fg_gc[gtk.STATE_NORMAL].get_colormap())
        self.gc.set_line_attributes( self.properties.footnote_line_width,
                                     gdk.LINE_SOLID,
                                     gdk.CAP_NOT_LAST,
                                     gdk.JOIN_MITER
                                   )

        self.pixbuf = None

        if self.properties.use_background: # and self.properties.path_to_background:
            # FIXME
            if not self.properties.path_to_background:
                self.properties.path_to_background = self.default_background_file
            try:
                self.pixbuf = gdk.pixbuf_new_from_file(
                    self.properties.path_to_background )
            except Exception, err:
                print >> sys.stderr, 'WARNING:', str(err)


        x, y, widget_width, widget_height, depth = self.window.get_geometry()

        if self.pixbuf:
            self.cur_pixbuf = self.pixbuf.scale_simple( self.width,
                                                        self.height,
                                                        gdk.INTERP_BILINEAR
                                                       )
        else:
            self.__create_background_pixmap( self.width, self.height, depth )

        pango_font_desc = pango.FontDescription(self.properties.status_font)
        pangolayout     = self.create_pango_layout(' ')

        pangolayout.set_font_description(pango_font_desc)
        font_height = pangolayout.get_extents()[1][3] / PANGO_SCALE

        self.properties.status_font_height     = font_height
        self.properties.status_pango_font_desc = pango_font_desc

        self.status_pixmap_area = gdk.Pixmap(
                          None, self.width,
                          font_height + self.properties.status_y_position,
                          depth
                                            )
#==============================================================================

    def incr_font( self, incr ):
        # if incr > 0 -> increase, else -> decrease
        for st in STYLES_LIST:
            if self.properties.styles[st].__dict__.has_key('font_size'):
                self.properties.styles[st].font_size += incr > 0 and 1 or -1
            self.properties.styles[st].set_font_desc(self)
#==============================================================================

    def open_file(self, filename, encoding=None, line=0, char_id=0, lang=None):
        #print 'open_file', filename

        self.current_page_line_index = line
        self.current_page_char_index = char_id
        self.content = Content(filename, encoding, lang)

        self.draw_text()

        menu = gtk.Menu()
        menu.show()
        for title, title_index in self.content.titles:
            menuitem = gtk.MenuItem(title)
            menuitem.connect('activate',
                             self.content_menu_activate_cb, title_index)
            menu.add(menuitem)
            menuitem.show()
        self.content_menu.set_submenu(menu)

        return True
#==============================================================================

    def content_menu_activate_cb(self, w, title_index):
        self.current_page_line_index = title_index
        self.current_page_char_index = 0
        self.draw_text()
#==============================================================================

    def realize(self):
        gtk.DrawingArea.realize(self)
#==============================================================================

    def draw_text(self, go=None):
        # go => 'fore' or 'back'

        # очищаем списки
        if go is None:
            self.footnotes_list  = []
            self.prev_index_list = []
        elif go == 'back':
            self.footnotes_list  = []

        self.__prepareTextToDraw()

        # current page

        if go == 'fore':
            self.__drawPrevPage()
        else:
            self.__drawNextPage()

        self.drawStatus( self.pixmap_area )

        self.window.draw_drawable(self.gc, self.pixmap_area,
                                  0, 0, 0, 0, self.width, self.height)

        # next page
        line_id, char_id = self.__draw( self.next_pixmap_area,
                                        self.next_page_line_index,
                                        self.next_page_char_index
                                      )
        self.next_next_page_line_index = line_id
        self.next_next_page_char_index = char_id
#==============================================================================

    def drawStatus(self, drawingArea = None ):
      '''drawStatus( drawingArea )

        Рисует строку состояния: прочинанное в процентах, время...
        drawingArea - слой, на котором происходит рисование
        
        Возвращает всегда True
      '''
      
      # drawingArea разный для разных "владельцев"/екземпляров классов/окон
      # Требуется в т.ч. и для того, чтобы можно было обновлять время в статусе
      # "по-таймеру", а не только по нажатию кнопки на клавиатуре (или любого 
      # подобного события

      if not self.properties.show_status:
        return True

      if not drawingArea:
        drawingArea = self.window

      width  = self.width
      height = self.properties.status_font_height + \
                self.properties.status_y_position

      if self.pixbuf:
        self.status_pixmap_area.draw_pixbuf(
                      self.gc, self.cur_pixbuf, 0, self.height - height, 0, 0,
                      width, height, False, 0, 0
                                            )
      else:
        self.status_pixmap_area.draw_drawable(
                      self.gc, self.background_pixmap,
                      0, self.height - height, 0, 0, width, height
                                              )
      self.__prepareStatusPercent()
      self.__prepareStatusTime()

      drawingArea.draw_drawable(self.gc, self.status_pixmap_area,
                        0, 0, 0, self.height - height, width, height )

      return True
#==============================================================================

    def go_fore_page(self):
        if len(self.content) <= self.next_page_line_index:
            return

        self.prev_index_list.append((self.current_page_line_index,
                                     self.current_page_char_index))

        #if self.next_page_line_index == len(self.lines):
        #    return
        self.current_page_line_index = self.next_page_line_index
        self.current_page_char_index = self.next_page_char_index
        self.draw_text(go='fore')
#==============================================================================

    def go_back_page(self):
        if self.current_page_line_index == 0 \
           and self.current_page_char_index == 0:
            return
        if self.prev_index_list:
            line_id, char_id = self.prev_index_list[-1]
            del self.prev_index_list[-1]
        else:
            line_id, char_id = self.__calc_back()

        self.current_page_line_index = line_id
        self.current_page_char_index = char_id
        self.draw_text(go='back')
#==============================================================================

    def calc_position(self):
        if self.next_page_line_index == len(self.content):
            return 1.0
        if self.content.textLength:
            cur_pos = reduce(lambda x, y: x+len(y.data),
                             self.content[:self.next_page_line_index], 0)
            return float(cur_pos)/self.content.textLength
        else:
            return 0.0
#==============================================================================

    get_position = calc_position
#==============================================================================

    def get_offset(self):
        offset = reduce(lambda x, y: x+len(y.data),
                        self.content[:self.next_page_line_index], 0)
        return offset
#==============================================================================

    def set_position(self, pos):
        char_id = self.content.textLength * pos
        i = 0
        n = 0
        for par in self.content:
            if char_id <= n:
                break
            n += len(par.data)
            i += 1
        self.current_page_line_index = i
        self.current_page_char_index = 0
        self.draw_text()
#==============================================================================

    def key_event_cb(self, w, event):
        if event.keyval in self.keysyms_next:
            self.go_fore_page()
            return True
        if event.keyval in self.keysyms_prev:
            self.go_back_page()
            return True
        return False
#==============================================================================

    def button_event_cb(self, w, event):
        if event.button == 1:
            self.go_fore_page()
        elif event.button == 2:
            #print 'event.button == 2'
            self.go_back_page()
#=============================================================================#
#                                     ^                                       #
#                               End of Class                                  #
#                                                                             #
#=============================================================================#

if __name__ == '__main__':
    #import sys
    if len(sys.argv) != 2:
        sys.exit('usage: %s file' % sys.argv[0])

    window = gtk.Window()
    window.connect('destroy', lambda w: gtk.main_quit())
    ob = OrnamentBook(window)
    window.add(ob)

    #text = ''
    #for i in xrange(20):
    #    text = text+str(i)*3+' '
    #text = (text+' aa bb cc ddddd\n')*7
    text = open(sys.argv[1]).read()
    ob.set_text(unicode(text, 'utf-8'))
    ob.realize()
    window.show_all()

    gtk.main()
