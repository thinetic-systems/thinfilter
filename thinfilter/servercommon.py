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


import os
import sys
import types
import thinfilter.config
import thinfilter.logger as lg
from thinfilter.common import ThinFilterException

# http://code.activestate.com/recipes/496786/

LISTEN_HOST=''
LISTEN_PORT=thinfilter.config.SERVER_PORT

KEYFILE=os.path.abspath(os.path.join(thinfilter.config.BASE, '../server/server.key'))
CERTFILE=os.path.abspath(os.path.join(thinfilter.config.BASE, '../server/server.crt'))


import SocketServer
import BaseHTTPServer
import SimpleHTTPServer
import SimpleXMLRPCServer
import xmlrpclib
import traceback
import base64
import string

import socket, os
from OpenSSL import SSL

class AuthException(Exception):
    pass

def Auth(user, apikey):
    # clean data (only letters and numbers)
    for l in user:
        if not l in string.letters+string.digits:
            lg.warning("Auth() SQLINJECTION in user='%s'"%user, __name__)
            return False
    for l in apikey:
        if not l in string.letters+string.digits:
            lg.warning("Auth() SQLINJECTION in apikey='%s'"%apikey, __name__)
            return False

    sql=ServerDB()
    sql.start()
    result=sql.select("select * from auth WHERE user='%s' and apikey='%s'"%(user, apikey) )
    sql.close()
    if len(result) == 1:
        return True
    return False




class SecureXMLRPCServer(BaseHTTPServer.HTTPServer,SimpleXMLRPCServer.SimpleXMLRPCDispatcher):
    def __init__(self, server_address, HandlerClass, logRequests=True):
        """Secure XML-RPC server.

        It it very similar to SimpleXMLRPCServer but it uses HTTPS for transporting XML data.
        """
        self.logRequests = logRequests

        try:
            SimpleXMLRPCServer.SimpleXMLRPCDispatcher.__init__(self)
        except TypeError:
            # An exception is raised in Python 2.5 as the prototype of the __init__
            # method has changed and now has 3 arguments (self, allow_none, encoding)
            #
            SimpleXMLRPCServer.SimpleXMLRPCDispatcher.__init__(self, False, None)

        SocketServer.BaseServer.__init__(self, server_address, HandlerClass)
        lg.debug("SecureXMLRPCServer::__init__ KEYFILE=%s CERTFILE=%s"%(KEYFILE, CERTFILE), __name__)
        ctx = SSL.Context(SSL.SSLv23_METHOD)
        ctx.use_privatekey_file (KEYFILE)
        ctx.use_certificate_file(CERTFILE)
        self.socket = SSL.Connection(ctx, socket.socket(self.address_family,
                                                        self.socket_type))
        self.server_bind()
        self.server_activate()

class SecureXMLRpcRequestHandler(SimpleXMLRPCServer.SimpleXMLRPCRequestHandler):
    """Secure XML-RPC request handler class.

    It it very similar to SimpleXMLRPCRequestHandler but it uses HTTPS for transporting XML data.
    """
    def setup(self):
        self.connection = self.request
        self.rfile = socket._fileobject(self.request, "rb", self.rbufsize)
        self.wfile = socket._fileobject(self.request, "wb", self.wbufsize)

    def _marshaled_dispatch(self, data, dispatch_method = None):
        """Dispatches an XML-RPC method from marshalled (XML) data.

        XML-RPC methods are dispatched from the marshalled (XML) data
        using the _dispatch method and the result is returned as
        marshalled data. For backwards compatibility, a dispatch
        function can be provided as an argument (see comment in
        SimpleXMLRPCRequestHandler.do_POST) but overriding the
        existing method through subclassing is the prefered means
        of changing method dispatch behavior.
        """

        try:
            #lg.debug("_marshaled_dispatch() data=%s"%(data) , __name__)
            params, method = xmlrpclib.loads(data)
            #lg.debug("_marshaled_dispatch() params=%s method=%s"%(params, method) , __name__)

            # generate response
            if dispatch_method is not None:
                response = dispatch_method(method, params)
            else:
                response = self.server._dispatch(method, params)
            # wrap response in a singleton tuple
            response = (response,)
            response = xmlrpclib.dumps(response, methodresponse=1,
                                       allow_none=self.server.allow_none, encoding=self.server.encoding)
        except ThinFilterException, err:
            response = xmlrpclib.dumps(
                xmlrpclib.Fault(err.errcode, err.errmsg),
                encoding=self.server.encoding, allow_none=self.server.allow_none,
                )
            traceback.print_exc(file=sys.stderr)
        except xmlrpclib.Fault, fault:
            lg.error("SecureXMLRpcRequestHandler::_marshaled_dispatch() xmlrpclib.Fault, fault=%s"%fault, __name__)
            response = xmlrpclib.dumps(fault, allow_none=self.server.allow_none,
                                       encoding=self.server.encoding)
        except Exception, err:
            lg.error("SecureXMLRpcRequestHandler::_marshaled_dispatch() Exception, err=%s"%err, __name__)
            traceback.print_exc(file=sys.stderr)
            # report exception back to server
            response = xmlrpclib.dumps(
                xmlrpclib.Fault(1, "%s:%s" % (sys.exc_type, sys.exc_value)),
                encoding=self.server.encoding, allow_none=self.server.allow_none,
                )

        return response


    def do_POST(self):
        """Handles the HTTPS POST request.

        It was copied out from SimpleXMLRPCServer.py and modified to shutdown the socket cleanly.
        """
        # authenticate
        #lg.debug(self.headers, __name__)
        try:
            user,apikey = base64.decodestring(self.headers["authorization"].split()[1]).split(':')
            #lg.debug("user=%s apikey=%s"%(user, apikey), __name__)
            if not Auth(user, apikey):
                raise AuthException('Not allowed')
        
        except Exception, err:
            lg.warning("SecureXMLRpcRequestHandler::do_POST() AUTH Exception, err=%s"%err, __name__)
            self.send_response(403)
            self.end_headers()
        
        #lg.debug("do_POST() headers=%s"%self.headers, __name__)
        try:
            # get arguments
            data = self.rfile.read(int(self.headers["content-length"]))
            #lg.debug("do_POST() data=%s"%(data) , __name__ )
            # In previous versions of SimpleXMLRPCServer, _dispatch
            # could be overridden in this class, instead of in
            # SimpleXMLRPCDispatcher. To maintain backwards compatibility,
            # check to see if a subclass implements _dispatch and dispatch
            # using that method if present.
            #response = self.server._marshaled_dispatch(
            #        data, getattr(self, '_dispatch', None)
            #    )
            response = self._marshaled_dispatch(
                    data, getattr(self.server, '_dispatch', None)
                )
            #lg.debug("SecureXMLRpcRequestHandler::do_POST() response=\n%s"%response, __name__)
        except ThinFilterException, err:
            traceback.print_exc(file=sys.stderr)
            self.send_response(200)
            self.send_header("Content-type", "text/xml")
            self.send_header("Content-length", str(len(response)))
            self.end_headers()
            
            
        except Exception, err: # This should only happen if the module is buggy
            # internal error, report as HTTP server error
            lg.warning("SecureXMLRpcRequestHandler::do_POST() Exception, err=%s"%err, __name__)
            traceback.print_exc(file=sys.stderr)
            self.send_response(500)
            self.end_headers()
        else:
            # got a valid XML RPC response
            self.send_response(200)
            self.send_header("Content-type", "text/xml")
            self.send_header("Content-length", str(len(response)))
            self.end_headers()
            self.wfile.write(response)

            # shut down the connection
            self.wfile.flush()
            self.connection.shutdown() # Modified here!





class xmlrpc_registers(object):
    def __init__(self):
        import string
        self.python_string = string
        
        # register all server methods
        import thinfilter.server
        for mod in dir(thinfilter.server):
            if mod.startswith("__"): continue
            
            obj=getattr(thinfilter.server, mod)
            
            if hasattr(obj, 'init'):
                # call init() in module
                init=getattr(obj, 'init')
                method=init()
                if type(method) == types.FunctionType:
                    # register as method
                    setattr(self, method.func_name, method)
                
                # if list register every method
                if type(method) == types.ListType:
                    for submethod in method:
                        setattr(self, submethod.func_name, submethod)
            else:
                lg.error("Module '%s' don't have init() method"%mod, __name__)
        
        __allmods__=[]
        for mod in dir(self):
            if mod.startswith('__'): continue
            if "python_string" in mod: continue
            __allmods__.append(mod)
        lg.debug("xmlrpc_registers allmods=%s"%__allmods__, __name__)


###############################################################################
import thinfilter.db

class ServerDB(thinfilter.db.Sqlite3):
    def __init__(self, db='server.db'):
        self.db=db
        thinfilter.db.Sqlite3().__init__('server.db')
        self.start()

    def create(self):
        self.execute("""CREATE TABLE lists (id INTEGER,
                                            type TEXT, 
                                            mode TEXT, 
                                            text TEXT, 
                                            description TEXT,
                                            creator TEXT
                                            ) """)
        self.execute("""CREATE TABLE auth (user TEXT, 
                                           apikey TEXT
                                           ) """)

    def start(self):
        if not os.path.isfile(self.db):
            # create database
            self.create()




#if __name__=='__main__':
#    thinfilter.config.debug=True
#    sql=ServerDB()
#    sql.start()
#    for row in sql.select("select * from config"):
#        print row
#    sql.close()
#    #thinfilter.config.debug=True
#    #lg.info("running", __name__)
#    db='people.db'
#    sql=Sqlite3(db)
#    sql.execute("create table people2(name,first)")
#    sql.execute("insert into people2 values('VAN ROSSUM','Guido')")
#    sql.execute("insert into people2 values('TORVALDS','Linus')")
#    for row in sql.select("select first, name from people2"):
#        print row
#    print "db.py: exiting..."
