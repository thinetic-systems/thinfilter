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

# http://code.activestate.com/recipes/496786/

import sys
import thinfilter.config
import thinfilter.logger as lg

if "--debug" in sys.argv:
    thinfilter.config.daemon=False
    thinfilter.config.debug=True
else:
    sys.stderr = lg.stderr()
    sys.stdout = lg.stdout()

from thinfilter.servercommon import SecureXMLRpcRequestHandler
from thinfilter.servercommon import SecureXMLRPCServer
import thinfilter.servercommon


def main():
    # create XMLRPC server
    server_address = (thinfilter.servercommon.LISTEN_HOST, thinfilter.servercommon.LISTEN_PORT)
    server = SecureXMLRPCServer(server_address, SecureXMLRpcRequestHandler)
    server.register_instance(thinfilter.servercommon.xmlrpc_registers())
    sa = server.socket.getsockname()
    lg.debug("Serving HTTPS on %s:%s"%(sa[0], sa[1]), __name__)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        lg.debug("Catch KeyboardInterrupt, stopping...")


if __name__ == '__main__':
    
    # init Database
    sql=thinfilter.servercommon.ServerDB()
    sql.start()
    sql.close()
    
    # run app
    main()



