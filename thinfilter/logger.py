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

import sys
import logging
import thinfilter.config

loglevel=logging.INFO
#if not thinfilter.config.daemon:
#    loglevel=0

if thinfilter.config.debug:
    loglevel=0


logging.basicConfig(level=loglevel,
                    format='%(asctime)s [%(levelname)s] %(message)s',
                    filename=thinfilter.config.DAEMON_LOG_FILE,
                    filemode='a')
__logger=logging.getLogger()


def debug(txt, name=thinfilter.config.name):
    if thinfilter.config.debug:
        print "D:%s => %s" % (name, txt)
    else:
        #setloglevel()
        __logger.debug("%s:: %s" % (name, txt))

def log(txt, name=thinfilter.config.name):
    debug(txt, name)

def info(txt, name=thinfilter.config.name):
    if thinfilter.config.debug:
        print "I:%s => %s" % (name, txt)
    else:
        __logger.info("%s:: %s" % (name, txt))

def logweb(txt, time=''):
    if thinfilter.config.debug:
        print "%s %s"%(time, txt)
    else:
        __logger.info(txt)

def warning(txt, name=thinfilter.config.name):
    if thinfilter.config.debug:
        print "W:%s => %s" % (name, txt)
    else:
        __logger.warning("%s:: %s" %(name, txt))

def error(txt, name=thinfilter.config.name):
    if thinfilter.config.debug:
        print "***ERROR**** %s => %s" % (name, txt)
    else:
        __logger.error("%s:: %s" %(name, txt))

class stderr(object):
    def __init__(self):
        warning("stderr::__init__")
    def write(self, data):
        if data == '\n': return
        warning(data.replace('\n\n','\n'), "STDERR")
    def close(self):
        pass

class stdout(object):
    def __init__(self):
        warning("stdout::__init__")
    def write(self, data):
        if data == '\n': return
        warning(data.replace('\n\n','\n'), "STDOUT")
    def close(self):
        pass


class LogThinFilter:
    """WSGI middleware for logging the status."""
    def __init__(self, app):
        self.app = app
        self.format = '%s - - [%s] "%s %s %s" - %s'
    
        from BaseHTTPServer import BaseHTTPRequestHandler
        import StringIO
        f = StringIO.StringIO()
        
        class FakeSocket:
            def makefile(self, *a):
                return f
        
        # take log_date_time_string method from BaseHTTPRequestHandler
        self.log_date_time_string = BaseHTTPRequestHandler(FakeSocket(), None, None).log_date_time_string
        
    def __call__(self, environ, start_response):
        def xstart_response(status, response_headers, *args):
            out = start_response(status, response_headers, *args)
            self.log(status, environ)
            return out

        return self.app(environ, xstart_response)
             
    def log(self, status, environ):
        import web
        outfile = environ.get('wsgi.errors', web.debug)
        req = environ.get('PATH_INFO', '_')
        protocol = environ.get('ACTUAL_SERVER_PROTOCOL', '-')
        method = environ.get('REQUEST_METHOD', '-')
        host = "%s:%s" % (environ.get('REMOTE_ADDR','-'), 
                          environ.get('REMOTE_PORT','-'))

        time = self.log_date_time_string()

        msg = self.format % (host, time, protocol, method, req, status)
        #print >> outfile, utils.safestr(msg)
        logweb('%s - - "%s %s %s" - %s'%(host, protocol, method, req, status), time)
