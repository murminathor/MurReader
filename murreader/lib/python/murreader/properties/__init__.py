#!/usr/bin/env python
# -*- coding: utf-8 -*-

class PyVersionError( Exception ):
  def __init__(self, msg ):
    self.message = msg
    Exception.__init__(self, msg)

from sys import version_info
if version_info < (2, 3):
  raise PyVersionError, \
        "Your python version to low (%s). Required >= 2.3"%(str(version_info))

#__all__  = [ 'properties' ]
from properties   import Properties
#from text_styles  import TextStyles
from recent_files import RecentFiles