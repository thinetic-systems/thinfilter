#!/usr/bin/env python
# -*- coding: UTF-8 -*-


import xmlrpclib
import base64

import thinfilter.config
import thinfilter.logger as lg
import thinfilter.common

# from http://aspn.activestate.com/ASPN/Cookbook/Python/Recipe/501148
class CookieAuthXMLRPCSafeTransport(xmlrpclib.SafeTransport):
    """xmlrpclib.Transport that sends basic HTTP Authentication"""

    # override the xmlrpclib user_agent field
    user_agent = "%s - %s"%(thinfilter.config.name, thinfilter.config.version)
    credentials = ()
        
    def send_basic_auth(self, connection):
        """Include HTTP Basic Authentication data in a header"""
        
        auth = base64.encodestring("%s:%s"%self.credentials).strip()
        auth = 'Basic %s' %(auth,)
        connection.putheader('Authorization',auth)

    def send_host(self, connection, host):
        """Override the send_host hook to also send authentication info"""

        xmlrpclib.Transport.send_host(self, connection, host)
        self.send_basic_auth(connection)




def getXmlrpcClient(server_uri, auth = ()):
    """ this will return an xmlrpc client which supports
    basic authentication/authentication through cookies 
    """

    trans = CookieAuthXMLRPCSafeTransport()
    if auth!= ():
        trans.credentials = auth
    client = xmlrpclib.Server(server_uri, transport=trans, verbose=False)
    
    return client

class XMLRPCAuthClient(object):
    def __init__(self, server_uri, auth=(), verbose=False):
        self.trans = CookieAuthXMLRPCSafeTransport()
        self.server_uri=server_uri
        if auth!= ():
            self.trans.credentials = auth
        self.server = xmlrpclib.Server(server_uri, transport=self.trans, verbose=verbose)

    def __repr__(self):
        return '<XMLRPCAuthClient to server ' + self.server_uri + '>'

    def run(self, method, args):
        result=[]
        try:
            result=getattr(self.server, method)(args)
            return result
        
        except xmlrpclib.ProtocolError, err:
            if err.errcode == 403:
                lg.error("Error 403, not allowed")
            else:
                lg.error("Unknow exception='%s'"%err, __name__)
        
        except xmlrpclib.Fault, err:
            if err.faultCode == 600:
                lg.error("Error 600: %s"%err)
            else:
                lg.error("Unknow exception='%s'"%faultString, __name__)
        
        return result

thinfilter.config.daemon=False
thinfilter.config.debug=True
app=XMLRPCAuthClient('https://localhost:16895', ('user','12345'), False)
print app.run('save_list', ('url', 'black', 'google.es', 'Block google', 'me') )
print app.run('lists', '' )

#server = getXmlrpcClient('https://localhost:16895', ('user','12345\'\hag'))

#server.save_list('url', 'black', 'google.es', 'Block google', 'me')
#print server.lists()

#try:
#    retstr = server.lists()
#    print retstr

#except Exception, e:
#    print e

