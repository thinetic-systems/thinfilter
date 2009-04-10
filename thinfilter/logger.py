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

import logging
import thinfilter.config

loglevel=logging.INFO

if thinfilter.config.debug:
    loglevel=0


logging.basicConfig(level=loglevel,
                    format='%(asctime)s [%(levelname)s] %(message)s',
                    filename=thinfilter.config.DAEMON_LOG_FILE,
                    filemode='a')
__logger=logging.getLogger()

def setloglevel():
    global loglevel
    if thinfilter.config.debug:
        loglevel=logging.DEBUG
    __logger.setLevel(loglevel)
    


def debug(txt, name=thinfilter.config.name):
    if thinfilter.config.daemon:
        setloglevel()
        logging.debug("%s:: %s" % (name, txt))
    elif thinfilter.config.debug:
        print "D:%s => %s" % (name, txt)

def log(txt, name=thinfilter.config.name):
    debug(txt, name)

def info(txt, name=thinfilter.config.name):
    if thinfilter.config.daemon:
        logging.info("%s:: %s" % (name, txt))
    elif thinfilter.config.debug:
        print "I:%s => %s" % (name, txt)

def warning(txt, name=thinfilter.config.name):
    if thinfilter.config.daemon:
        logging.warning("%s:: %s" %(name, txt))
    else:
        print "W:%s => %s" % (name, txt)

def error(txt, name=thinfilter.config.name):
    if thinfilter.config.daemon:
        logging.error("%s:: %s" %(name, txt))
    else:
        print "***ERROR**** %s => %s" % (name, txt)

class stderr(object):
    def write(self, data):
        if data == '\n': return
        warning(data.replace('\n\n','\n'), "STDERR")

class stdout(object):
    def write(self, data):
        if data == '\n': return
        warning(data.replace('\n\n','\n'), "STDOUT")
