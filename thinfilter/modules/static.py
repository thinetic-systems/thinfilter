# -*- coding: UTF-8 -*-
##########################################################################
# ThinFilter writen by MarioDebian <mario.izquierdo@thinetic.es>
#
#    ThinFilter
#
# Copyright (c) 2009 Mario Izquierdo <mario.izquierdo@thinetic.es>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2, or (at your option)
# any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA
# 02111-1307, USA.
###########################################################################

#
# static controller
#    web.py don't have a way to set static path
#

import os

import thinfilter.logger as lg
import thinfilter.config
import thinfilter.common

import web
import time






class static:
    def GET(self, sfile):
        if not os.path.isfile( os.path.join(thinfilter.config.BASE, 'static' , sfile) ):
            # return 404
            return web.notfound()

        # set headers (javascript, css, or images)
        extension = sfile.split('.')[-1]
        mode='r'
        if extension in thinfilter.config.IMAGE_EXTENSIONS:
            mode='rb'
        # set common headers
        f=open(os.path.join(thinfilter.config.BASE, 'static' , sfile), mode)
        fs = os.fstat( f.fileno())
        web.header("Expires", thinfilter.common.date_time_string(time.time()+60*60*2)) # expires in 2 hours
        web.header("Last-Modified", thinfilter.common.date_time_string(fs.st_mtime))
        web.header("Content-Length", str(fs[6]))
        web.header("Cache-Control", "max-age=3600, must-revalidate") 
        f.close()
        
        if extension == "css":
            web.header("Content-Type","text/css; charset=utf-8")
        elif extension == "js":
            web.header("Content-Type","application/javascript; charset=utf-8")
        elif extension in thinfilter.config.IMAGE_EXTENSIONS:
            web.header('Content-Type', 'image/%s' %(extension) )
        
        
        return open(os.path.join(thinfilter.config.BASE, 'static', sfile)).read()

class favicon:
    def GET(self):
        f=open(os.path.join(thinfilter.config.BASE, 'static' , 'favicon.ico'), 'rb')
        fs = os.fstat( f.fileno())
        web.header("Expires", thinfilter.common.date_time_string(time.time()+60*60*2)) # expires in 2 hours
        web.header("Last-Modified", thinfilter.common.date_time_string(fs.st_mtime))
        web.header("Content-Length", str(fs[6]))
        web.header("Cache-Control", "max-age=3600, must-revalidate")
        f.close()
        web.header('Content-Type', 'image/ico')
        return open(os.path.join(thinfilter.config.BASE, 'static', 'favicon.ico')).read()

def init():
    # nothing to check
    lg.debug("static::init()", __name__)
    """
        '/data/([a-zA-Z0-9-.]*)', 'static'
    """
    thinfilter.common.register_url('/data/([a-zA-Z0-9-.]*)',      'thinfilter.modules.static.static')
    thinfilter.common.register_url('/favicon.ico',      'thinfilter.modules.static.favicon')



