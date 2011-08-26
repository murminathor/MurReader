#!/bin/env python
# -*- coding: utf-8 -*-

from sys import argv, exit
from properties import TextStyles as test_prop
#from properties.recent_files import RecentFiles as test_prop
#from properties.properties import Properties as test_prop

styles = test_prop()
#styles = test_prop(config_file  = '/home/jura/tmp/test-config.conf',
                    #show_warning = True )
print( "Before read")
print( styles )

styles.read()
print( "After read" )
print( styles )


#styles.cite.font_size = 30
#styles.title.font_family = "Arial"
#styles.title.italic = True
#styles.append( filename = "/home/jura/work/books/soc/Dolnik_Neposlushnoe_ditya_biosferyi._Beseda_tretya_i_chetvertaya.132274.fb2.zip",
               #line = 200, char= 20, encoding="cp-1251" )

#styles.append( filename = "/home/jura/work/books/soc/Protopopov_Traktat_o_lyubvi_kak_ee_ponimaet_zhutkiy_zanuda_4-ya_redaktsiya_.114645.fb2.zip",
               #line = 100, char= 0, encoding="cp-1251" )
#for style_name, curr_style in styles:
  #curr_style.font_size = 20

#print( "After append" )
#print( styles )

#print( "After save" )
#styles.clear_config()
#styles.save()
#print( styles )