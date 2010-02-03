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



import thinfilter
#thinfilter.init()



import thinfilter.config
thinfilter.config.debug=False
if "--debug" in sys.argv:
    thinfilter.config.debug=True

if "--devel" in sys.argv:
    thinfilter.config.devel=True


import thinfilter.logger as lg

# load daemonize con configure
import thinfilter.daemonize
lg.old_stderr=sys.stderr
lg.old_stdout=sys.stdout


import web
web.config.debug = False

# load SSL cert
from web.wsgiserver import CherryPyWSGIServer

# uncomment to enable SSL
#CherryPyWSGIServer.ssl_certificate = "thinfilter/ssl/server.crt"
#CherryPyWSGIServer.ssl_private_key = "thinfilter/ssl/server.key"


if "--debug" in sys.argv:
    web.config.debug=True
    thinfilter.config.daemon=False
else:
    sys.stderr = lg.stderr()
    sys.stdout = lg.stdout()


################################################################################
#try:
#    import cPickle as pickle
#except ImportError:
#    import pickle
#import base64

#class DiskStore(web.session.DiskStore):
#    def decode(self, session_data):
#        """decodes the data to get back the session dict """
#        #lg.debug("Store::decode() session_data=%s"%session_data, __name__)
#        pickled = base64.decodestring(session_data)
#        #lg.debug("Store::decode() pickled=%s"%pickled, __name__)
#        try:
#            data=pickle.loads(pickled)
#            #lg.debug("Store::decode() data=%s"%data, __name__)
#        except Exception, err:
#            #lg.error("Store::decode() Exception: session_data '%s'"%session_data, __name__)
#            #lg.error("Store::decode() Exception: pickled '%s'"%pickled, __name__)
#            lg.error("Store::decode() Exception: error '%s'"%err, __name__)
#            traceback.print_exc(file=sys.stderr)
#            #return {'ip':'', 'user':'', 'session_id':''}
#            return None
#        #print data
#        return data

#class MySession(web.session.Session):
#    def _load(self):
#        """Load the session from the store, by the id from cookie"""
#        cookie_name = self._config.cookie_name
#        cookie_domain = self._config.cookie_domain
#        self.session_id = web.cookies().get(cookie_name)

#        # protection against session_id tampering
#        if self.session_id and not self._valid_session_id(self.session_id):
#            self.session_id = None

#        self._check_expiry()
#        if self.session_id:
#            d = self.store[self.session_id]
#            try:
#                self.update(d)
#            except:
#                print "store=>%s"%self.store
#                print "session_id=>", self.session_id
#                print "d=>", d
#                traceback.print_exc(file=sys.stderr)
#            self._validate_ip()
#        
#        if not self.session_id:
#            self.session_id = self._generate_session_id()

#            if self._initializer:
#                if isinstance(self._initializer, dict):
#                    self.update(self._initializer)
#                elif hasattr(self._initializer, '__call__'):
#                    self._initializer()
# 
#        self.ip = web.ctx.ip

#web.session.Session=MySession
################################################################################

import shelve
class ShelfStore(web.session.ShelfStore):
    def __getitem__(self, key):
        atime, v = self.shelf[key]
        self[key] = v # update atime
        return v

store = ShelfStore(shelve.open(thinfilter.config.SESSIONS_DIR + '/session.shelf'))
################################################################################

# init database
import thinfilter.db
thinfilter.db.start()

lg.debug("Loading modules", __name__)
import thinfilter.modules
thinfilter.common.init_modules(thinfilter.modules)
lg.debug("Modules loaded, here we go....", __name__)



# global app
app = web.application(thinfilter.common.geturls(), globals())
render = web.template.render(thinfilter.config.BASE + 'templates/')

#db = web.database(dbn='sqlite', db=thinfilter.config.DBNAME)

# from http://webpy.org/cookbook/session_with_reloader
# use only one session instead of debug=True
if web.config.get('_session') is None:
    #session = web.session.Session(app, DiskStore(thinfilter.config.SESSIONS_DIR), {'user': ''})
    session = web.session.Session(app, store, {'user': ''} )
    web.config._session = session
else:
    session = web.config._session



import thinfilter.common





if __name__ == "__main__":
    args=[]
    for arg in sys.argv[1:]:
        args.append(arg)
    sys.argv=[sys.argv[0], '9090']
    lg.debug("main() sys.argv=%s args=%s" %(sys.argv,args) )
    if "--start" in args:
        if not "--nodaemon" in args:
            lg.debug("daemonize....")
            thinfilter.daemonize.start_server()
        app.run()
    
    elif "--stop" in args:
        thinfilter.daemonize.stop_server(sys.argv[0])
        pass
    
    else:
        print >> lg.old_stderr , """
thinfilter:
        --start    - start web daemon
        --stop     - stop daemon

    You can access interface in http://localhost:9090
"""
