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


import thinfilter.config
import thinfilter.logger as lg

import os
import pwd

import thinfilter.db

def init():
    import thinfilter.config
    
    # set rights of database dir
    if not os.path.isdir( os.path.dirname(thinfilter.config.DBNAME) ):
        os.mkdir( os.path.dirname(thinfilter.config.DBNAME) )
    
    if not os.path.isfile(thinfilter.config.DBNAME):
        thinfilter.db.create_db()
    
    #os.chown(thinfilter.config.DBNAME, uid[2], uid[3])

    
    lg.debug("loading settings from database", __name__)
    
    
    # set stop to 0
    thinfilter.db.query("UPDATE config SET stop=0;")
    thinfilter.config.stop=False
    
    lg.debug("init() settings loaded", __name__)
    thinfilter.db.close()

def do_stop():
    thinfilter.db.query("UPDATE config SET stop=1;")
    thinfilter.config.stop=True
    #lg.info("Stopping...", __name__)
    thinfilter.db.close()

def is_stoping(dosql=False):
    #print "is stopping"
    if not dosql:
        return thinfilter.config.stop
    try:
        stop=thinfilter.db.query("SELECT stop from config;")[0][0]
    except Exception, err:
        lg.error("Exception can't read stop status '%s'"%err, __name__)
        return False
    
    if stop == 1:
        lg.info("is_stopping() True...", __name__)
        return True
    elif stop == 2:
        # reload config
        lg.info("Reloading configuration...", __name__)
        init()
        return False
    else:
        #lg.info("is_stopping() False...", __name__)
        return False


__all__=['logger', 'config', 'db', 'daemonize', 'rules', 'configparser', 'common', 'static']
