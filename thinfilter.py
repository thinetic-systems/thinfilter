#!/usr/bin/env python
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
import os
import string
import traceback
import time



import thinfilter
import thinfilter.config

import getopt

def usage():
    print >> sys.stderr , """
thinfilter [options] action
    Options:
        --help -h   (this help)
        --debug     (enable debug mode)
        --devel     (enable devel flag)
        --demo      (don't exec actions)
        --daemon    (fork on background)
        --enablessl (enable HTTPS SSL)
        --forceip=xx.xx.xx.xx (force internal IP)
        
    Actions:
        --start  (start daemon)
        --stop   (stop daemon)
        --status (return 0 if running and 1 if not)
    
    Example:
        thinfilter --debug --nodaemon --devel --demo --start
"""

try:
    opts, args = getopt.getopt(sys.argv[1:], "h", ["help", "debug", "devel", "demo", "daemon", "start", "stop", "status", "enablessl", "forceip="])
except getopt.GetoptError, err:
    print >> sys.stderr , "thinfilter ERROR: %s"%(str(err))
    usage()
    sys.exit(2)

stop=False
start=False
status=False

for o, a in opts:
    if o in ("-h", "--help"):
        usage()
        sys.exit(0)
    elif o == "--debug":
        thinfilter.config.debug=True
        
    elif o == "--devel":
        thinfilter.config.devel=True
        
    elif o == "--demo":
        thinfilter.config.demo=True
        
    elif o == "--daemon":
        thinfilter.config.daemon=True
        
    elif o == "--enablessl":
        thinfilter.config.ssl=True
    elif "forceip" in o:
        thinfilter.config.FORCE_IP=a
    
    elif o == "--start":
        start=True
    elif o == "--stop":
        stop=True
    elif o == "--status":
        status=True
    
    else:
        assert False, "thinfilter ERROR, unknow commandline option %s"%(o)

if not start and not stop and not status:
    print >> sys.stderr , "ERROR start|stop|status action required"
    usage()
    sys.exit(1)


################################################################################
import web
if start:
    web.config.debug = False
    if thinfilter.config.debug:
        web.config.debug=True
        thinfilter.config.daemon=True

import thinfilter.logger as lg


# load daemonize
import thinfilter.daemonize




# load SSL cert
from web.wsgiserver import CherryPyWSGIServer

#FIXME enable SSL
if thinfilter.config.ssl:
    CherryPyWSGIServer.ssl_certificate = "thinfilter/ssl/server.crt"
    CherryPyWSGIServer.ssl_private_key = "thinfilter/ssl/server.key"


#if start:
#    if thinfilter.config.debug:
#        web.config.debug=True
#        if not thinfilter.config.daemon:
#            thinfilter.config.daemon=False
#        
#    elif thinfilter.config.daemon:
#        sys.stderr = lg.stderr()
#        sys.stdout = lg.stdout()



################################################################################
#
# Overwrite web.utils.safeunicode
# can't load stop web
# http://images.google.es/images?hl=es&source=hp&ie=ISO-8859-1&q=foo&btnG=Buscar+im%E1genes&gbv=1&aq=f&oq=
#

def Mysafeunicode(obj, encoding='utf-8'):
    r"""
    Converts any given object to unicode string.
    
        >>> safeunicode('hello')
        u'hello'
        >>> safeunicode(2)
        u'2'
        >>> safeunicode('\xe1\x88\xb4')
        u'\u1234'
    """
    if isinstance(obj, unicode):
        return obj
    elif isinstance(obj, str):
        try:
            return obj.decode(encoding)
        except Exception, err:
            lg.debug("Mysafeunicode() exception, error=«%s»\nobj=%s"%(err,obj), __name__)
            return unicode(obj, errors='ignore')
    else:
        if hasattr(obj, '__unicode__'):
            return unicode(obj)
        else:
            return str(obj).decode(encoding)

web.utils.safeunicode=Mysafeunicode
################################################################################
#
# Use shelve for Storage sessions
#
import shelve
class ShelfStore(web.session.ShelfStore):
    def __getitem__(self, key):
        atime, v = self.shelf[key]
        self[key] = v # update atime
        return v

store = ShelfStore(shelve.open(thinfilter.config.SESSIONS_DIR + '/sessions.shelf'))
################################################################################
#
# Overwrite runsimple() function
#    * disable /static
#    * log to logger
#
import web.httpserver

def runsimple(func, server_address=("0.0.0.0", thinfilter.config.WEB_PORT)):
    func = lg.LogThinFilter(func)
    from web.wsgiserver import CherryPyWSGIServer
    server=CherryPyWSGIServer(server_address, func, server_name="localhost")
    
    lg.info("\n\n\t\tserver started: http://%s:%d/\n"%server_address)
    try:
        server.start()
    except KeyboardInterrupt:
        server.stop()


web.httpserver.runsimple=runsimple
################################################################################


if start:
    # config server IP
    if thinfilter.config.FORCE_IP != "":
        thinfilter.config.WEB_IP=thinfilter.config.FORCE_IP
    else:
        import thinfilter.common
        ifaces=thinfilter.common.Interfaces().get()
        #from pprint import pprint
        #pprint(ifaces)
        for net in ifaces:
            if net['gateway'] is None and "eth" in net['iface']:
                #print "net=%s"%net
                thinfilter.config.WEB_IP=net['addr']
                lg.debug("server IP ===> %s"%(thinfilter.config.WEB_IP))
                break
    
    # init database
    import thinfilter.db
    thinfilter.db.start()
    
    # start firts time install scripts if needed
    try:
        firsttime=thinfilter.db.query("SELECT value FROM config where varname='firsttime'")
        thinfilter.common.FirstRun(firsttime[0][0])
    except:
        pass
    #sys.exit(0)
    
    lg.debug("Loading modules", __name__)
    import thinfilter.modules
    thinfilter.common.register_role_desc('admin', "Administrador")
    thinfilter.common.init_modules(thinfilter.modules)
    lg.debug("Modules loaded, here we go....", __name__)
    
    
    # global app
    app = web.application(thinfilter.common.geturls(), globals())
    render = web.template.render(thinfilter.config.BASE + 'templates/')

    # from http://webpy.org/cookbook/session_with_reloader
    # use only one session instead of debug=True
    if web.config.get('_session') is None:
        session = web.session.Session(app, store, {'user': ''} )
        web.config._session = session
    else:
        session = web.config._session





if __name__ == "__main__":
    args=[]
    for arg in sys.argv[1:]:
        args.append(arg)
    
    lg.info("main() sys.argv=%s args=%s debug=%s daemon=%s" %(sys.argv,args, thinfilter.config.debug, thinfilter.config.daemon) ,__name__)
    if start:
        sys.argv=[sys.argv[0], str(thinfilter.config.WEB_PORT)]
        
        # change procname
        try:
            thinfilter.daemonize.set_proc_name('thinfilter.daemon')
            sys.argv=['thinfilter', str(thinfilter.config.WEB_PORT)]
        except Exception, err:
            print "Exception changing name of process, error=%s"%err

        if thinfilter.config.daemon:
            lg.debug("daemonize....", __name__)
            #thinfilter.daemonize.start_server()
        
        app.run()
        lg.info("main() closing...", __name__)
        
        
        # set None in shelf object or Exceptions ocurr in close()
        # http://stackoverflow.com/questions/2180946/really-weird-issue-with-shelve-python
        # http://bugs.python.org/issue6294
        store.shelf=None
    
    elif stop:
        store.shelf=None
        thinfilter.daemonize.stop_server('thinfilter.daemon')
    
    elif status:
        store.shelf=None
        thinfilter.daemonize.status()



