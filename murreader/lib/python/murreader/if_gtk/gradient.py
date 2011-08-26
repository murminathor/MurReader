#!/usr/bin/env python
# -*- coding: utf-8 -*-

def create_buffer_rgb( width, height, color1, color2 = None ):
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
#=============================================================================#
