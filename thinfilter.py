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



import thinfilter
#thinfilter.init()



import thinfilter.config
thinfilter.config.debug=False
if "--debug" in sys.argv:
    thinfilter.config.debug=True


import thinfilter.logger as lg

# load daemonize con configure
import thinfilter.daemonize
lg.old_stderr=sys.stderr
lg.old_stdout=sys.stdout


import web
web.config.debug = False


if "--debug" in sys.argv:
    web.config.debug=True
    thinfilter.config.daemon=False
else:
    sys.stderr = lg.stderr()
    sys.stdout = lg.stdout()


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
    session = web.session.Session(app, web.session.DiskStore(thinfilter.config.SESSIONS_DIR), {'user': ''})
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
        lg.debug("daemonize....")
        #thinblue.daemonize.start_server()
        app.run()
    
    elif "--stop" in args:
        #thinblue.daemonize.stop_server(sys.argv[0])
        pass
    
    else:
        print >> lg.old_stderr , """
thinfilter:
        --start    - start web daemon
        --stop     - stop daemon

    You can access interface in http://localhost:9090
"""
