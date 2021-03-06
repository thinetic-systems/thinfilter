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

import glob as __glob__
import os   as __os__
import sys  as __sys__
import traceback as __traceback__

def __init__():
    """
    read contents of extensions dir and put in __all__ list
    """
    _ext_dir=__os__.path.dirname( __file__ )
    _ext=[]
    for file_ in __glob__.glob(_ext_dir+"/*.py"):
        if file_ == "__init__.py":
            continue
        _ext_name = __os__.path.basename(file_).split('.py')[0]
        if _ext_name == "__init__":
            continue
        _ext.append( _ext_name )
        #import thinfilter.config
        #print "modules/__init__ load %s daemon=%s devel=%s"%(_ext_name, thinfilter.config.daemon, thinfilter.config.devel)
        try:
            if __sys__.version_info[0:3] < (2, 5, 0):
                __import__('thinfilter.modules.' + _ext_name, globals(), locals(), ['modules'] ) 
            else:
                __import__('thinfilter.modules.' + _ext_name, fromlist = ['modules'] ) 
        except Exception, err:
            print "Exception importing module='%s', err='%s'"%(_ext_name, err)
            __traceback__.print_exc(file=__sys__.stderr)
            continue
        #print "                      %s daemon=%s devel=%s"%(_ext_name, thinfilter.config.daemon, thinfilter.config.devel)
    return _ext



__all__=__init__()
