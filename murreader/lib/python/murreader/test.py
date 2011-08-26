#!/usr/bin/python
# -*- coding: utf-8 -*-

#from readfile import *
from content import *
from sys import argv


#for item in readFile( argv[1] ).content :
#  print( item.data.encode('utf-8') )
print( Content(argv[1]) )


