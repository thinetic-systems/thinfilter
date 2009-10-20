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

import thinfilter.logger as lg
import thinfilter.servercommon
import types
import sys

from thinfilter.common import ThinFilterException


def lists(*args):
    lg.debug("lists() with args=%s"%str(args), __name__)
    # FIXME add filters to list
    # read table lists
    sql=thinfilter.servercommon.ServerDB()
    sql.start()
    result=[]
    for row in sql.select("SELECT type, mode, text, description, creator from lists"):
        result.append( [row[0], row[1], row[2], row[3], row[4]])
    
    #return pickle.dumps(result)
    return result


def save_list(*args):
    if type(args) == types.TupleType:
        args=args[0]
    lg.debug("save_list() with args=%s type=%s"%(str(args), type(args)), __name__)
    if len(args) != 5:
        raise ThinFilterException(600, "bad argument number (%s)"%len(args))
    
    # connect to sqlite and save list
    sql=thinfilter.servercommon.ServerDB()
    sql.start()
    try:
        sql.execute("""INSERT INTO lists (type, mode, text, description, creator) 
                                   VALUES ('%s', '%s', '%s', '%s',         '%s')"""
                              %(args[0], args[1],args[2], args[3], args[4]) )
        return "ok"
        sql.close()
    except Exception, err:
        lg.error("save_list() Exception, err=%s"%err, __name__)
        sql.close()
        raise ThinFilterException(600, "error inserting")
    sql.close()


def init(*args):
    lg.debug("Called init() with args=%s"%str(args), __name__)
    return [lists, save_list]




