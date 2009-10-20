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

#
# openvpn stuff
#

import os
import sys
from subprocess import Popen, PIPE, STDOUT
import glob


import thinfilter.logger as lg
import thinfilter.config
import thinfilter.common

import web
render = web.template.render(thinfilter.config.BASE + 'templates/')

"""
  396  . ./vars 
  397  ./clean-all 
  398  ./build-ca 
  409  ./build-key-server server
  412  ./build-key cliente1
  425  openssl dhparam -out dh1024.pem 1024
  KEY_EMAIL="xxx@xxx" PASSIN="xxx" PASSOUT="xxxxx" ./build-key-pass

# show info
openssl x509 -text -in etc_openvpn/keys/server.crt | grep "Subject:"
"""

OPENVPN_DIR="/etc/openvpn"


def file_exists(fname):
    absfile=os.path.join(OPENVPN_DIR, fname)
    if os.path.isfile( absfile ):
        lg.debug("OpenVpn::genCA() %s exists"%absfile, __name__)
        return True
    lg.debug("OpenVpn::genCA() %s ***NO*** exists, creating..."%absfile, __name__)
    return False



class OpenVpn(object):
    def __init__(self):
        self.dir=OPENVPN_DIR

    def genCA(self):
        buildCA=False
        if file_exists("keys/ca.key"):
            return True
        cmd="%s/build-ca"%(self.dir)
        lg.debug("OpenVpn::genCA()  cmd=%s"%cmd, __name__)
        p = Popen(cmd, shell=True, bufsize=4096, stdout=PIPE, stderr=STDOUT, close_fds=True)
        for _line in p.stdout.readlines():
            line=_line.replace('\n','')
            lg.debug("OpenVpn::genCA()   %s"%line, __name__)
            if "writing new private" in line:
                buildCA=True
        return buildCA

    def genDH(self):
        buildDH=False
        if file_exists("keys/dh1024.pem"):
            return True
        cmd="%s/build-dh"%(self.dir)
        lg.debug("OpenVpn::genDH()  cmd=%s"%cmd, __name__)
        p = Popen(cmd, shell=True, bufsize=4096, stdout=PIPE, stderr=STDOUT, close_fds=True)
        for _line in p.stdout.readlines():
            line=_line.replace('\n','')
            lg.debug("OpenVpn::genDH()   %s"%line, __name__)

        if file_exists("keys/dh1024.pem"):
            buildDH=True
        return buildDH

    def genServer(self):
        buildServer=False
        if file_exists("keys/server.key"):
            return True
        cmd="%s/build-key-server server"%(self.dir)
        lg.debug("OpenVpn::genServer()  cmd=%s"%cmd, __name__)
        p = Popen(cmd, shell=True, bufsize=4096, stdout=PIPE, stderr=STDOUT, close_fds=True)
        for _line in p.stdout.readlines():
            line=_line.replace('\n','')
            lg.debug("OpenVpn::genServer()   %s"%line, __name__)
            if "writing new private" in line:
                buildServer=True
        return buildServer

    def genClient(self, name, email, password):
        name=name.strip()
        if file_exists("keys/%s.key"%name):
            return True
        #KEY_EMAIL="xxx@xxx" PASSIN="xxx" PASSOUT="xxxxx" ./build-key-pass
        buildClient=False
        name=name.strip()
        sslenv={'FORCE_KEY_EMAIL':str(email), 'PASSIN':str(password), 'PASSOUT':str(password) }
        cmd="%s/build-key-pass '%s'"%(self.dir, name)
        lg.debug("OpenVpn::genClient()  cmd=%s"%cmd, __name__)
        p = Popen(cmd, shell=True, bufsize=4096, env=sslenv, stdout=PIPE, stderr=STDOUT, close_fds=True)
        for _line in p.stdout.readlines():
            line=_line.replace('\n','')
            lg.debug("OpenVpn::genClient()   %s"%line, __name__)
            if "writing new private" in line:
                buildClient=True
        return buildClient

    def revokeClient(self, name):
        """
        in server.conf need a line like this:
        crl-verify /etc/openvpn/keys/crl.pem
        """
        name=name.strip()
        if not file_exists("keys/%s.key"%name):
            return True
        revoked=False
        name=name.strip()
        cmd="%s/revoke-full '%s'"%(self.dir, name)
        lg.debug("OpenVpn::revokeClient()  cmd=%s"%cmd, __name__)
        p = Popen(cmd, shell=True, bufsize=4096, stdout=PIPE, stderr=STDOUT, close_fds=True)
        for _line in p.stdout.readlines():
            line=_line.replace('\n','')
            lg.debug("OpenVpn::revokeClient()   %s"%line, __name__)
            if "certificate revoked" in line:
                revoked=True
        for f in glob.glob( os.path.join(self.dir, "keys/%s.*"%name) ):
            absf=os.path.abspath(os.path.join(self.dir,f))
            lg.debug("OpenVpn::revokeClient() deleting %s"%absf, __name__)
            os.unlink( absf )
        return revoked

    def getUser(self, user):
        # return info about user
        cmd="openssl x509 -in %s/keys/%s.crt -text"%(self.dir, user)
        lg.debug("OpenVpn::getUser()  cmd=%s"%cmd, __name__)
        p = Popen(cmd, shell=True, bufsize=4096, stdout=PIPE, stderr=STDOUT, close_fds=True)
        info=[]
        created=""
        expires=""
        for _line in p.stdout.readlines():
            line=_line.replace('\n','')
            #lg.debug("OpenVpn::getUser()   %s"%line, __name__)
            if "Subject:" in line:
                info=line.split(', ')[1:]
            elif "Not Before:" in line:
                created=line.strip().split(":",1)[1:]
                #lg.debug("OpenVpn::getUser() %s"%line, __name__)
            elif "Not After :" in line:
                expires=line.strip().split(":",1)[1:]
                #lg.debug("OpenVpn::getUser() %s"%line, __name__)
        info.append("Creado=%s"%" ".join(created).strip())
        info.append("Expira=%s"%" ".join(expires).strip())
        return info


class FileLoader(object):
    def __init__(self, fname):
        self.fname=fname
        self.data=[]
        self.raw=[]
        self.__load()
    def __load(self):
        if not os.path.isfile( os.path.join(OPENVPN_DIR, self.fname) ):
            return
        f=open( os.path.join(OPENVPN_DIR, self.fname), 'r' )
        for line in f.readlines():
            self.raw.append(line)
            if line.startswith("#") or line.strip() == "":
                continue
            self.data.append(line.strip())
    def get(self):
        return self.data


class FileVars(FileLoader):
    __super_init = FileLoader.__init__
    def __init__(self, fname="vars"):
        self.__super_init(fname)

    def get(self):
        data={}
        for var in self.data:
            for key in ["KEY_SIZE", "CA_EXPIRE", "KEY_EXPIRE", "KEY_COUNTRY", "KEY_PROVINCE", "KEY_CITY", "KEY_ORG", "KEY_EMAIL"]:
                if key in var:
                    data[key]=var.split("%s="%key)[1].strip().replace("'",'').replace('"','')
                    lg.debug("FileVars(): data[%s]='%s' "%(key, var.split("%s="%key)[1].strip()), __name__ )
        return data

class FileServer(FileLoader):
    __super_init = FileLoader.__init__
    def __init__(self, fname="server.conf"):
        self.__super_init(fname)


class vpn(object):
    @thinfilter.common.islogged
    @thinfilter.common.layout(body='', title='Configuración de OpenVPN')
    def GET(self, options=None):
        openvpn_vars=FileVars().get()
        return render.vpn(openvpn_vars, 'Guardar')

    @thinfilter.common.islogged
    def POST(self):
        # FIXME guardar formulario
        return web.seeother('/vpn')


class getUsers(object):
    def __init__(self):
        ipp=FileLoader('ipp.txt').get()
        self.users={}
        for f in glob.glob("%s/keys/*.key"%OPENVPN_DIR):
            if "server.key" in f or "ca.key" in f: continue
            user=os.path.basename(f).replace('.key','')
            self.users[user]=OpenVpn().getUser(user)
            # Add LastIP
            for line in ipp:
                if line.startswith("%s,"%user):
                    self.users[user].append('LastIP=%s'%(line.split(',')[1]) )

    def get(self):
        return self.users


class users(object):
    @thinfilter.common.islogged
    @thinfilter.common.layout(body='', title='Configuración de usuarios VPN')
    def GET(self, options=None):
        openvpn_users=getUsers().get()
        return render.vpn_users(openvpn_users, 'Guardar')

    @thinfilter.common.islogged
    def POST(self):
        return web.seeother('/vpn/users')


def init():
    # nothing to check
    lg.debug("openvpn::init()", __name__)
    """
        '/vpn',       'vpn',
        '/vpn/users', 'users',
    """
    thinfilter.common.register_url('/vpn',    'thinfilter.modules.openvpn.vpn')
    thinfilter.common.register_url('/vpn/users',  'thinfilter.modules.openvpn.users')
    
    """
    <li><span class="dir">VPN</span>
        <ul>
            <li><a href="/vpn">Configuración</a></li>
            <li><a href="/vpn/users">Usuarios</a></li>
            <li><a href="/vpn/remote">Tunel</a></li>
        </ul>
    </li>
    """
    menu=thinfilter.common.Menu("", "VPN")
    menu.appendSubmenu("/vpn", "Configuración")
    menu.appendSubmenu("/vpn/users", "Usuarios")
    menu.appendSubmenu("/vpn/remote", "Tunel")
    thinfilter.common.register_menu(menu)


if __name__ == "__main__":
    thinfilter.config.daemon=False
    thinfilter.config.debug=True
    
    #print OpenVpn().genCA()
    #print OpenVpn().genDH()
    #print OpenVpn().genServer()
    #print OpenVpn().genClient('mario.izquierdo3', 'mario@thinetic.es', 'prueba1')
    #print OpenVpn().revokeClient('mario.izquierdo')
    #print OpenVpn().revokeClient('mario.izquierdo4')
    #print OpenVpn().revokeClient('mario.izquierdo5')
    #print OpenVpn().genClient('mario', 'mario@thinetic.es', 'prueba1')
    #print OpenVpn().revokeClient('mario')
    #print OpenVpn().getUser('mario')
    
    #print FileLoader("vars").get()
    #print FileVars().get()
    #print FileServer().get()

    print getUsers().get()



