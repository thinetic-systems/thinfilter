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
import shutil
import time

sys.path.append('/home/mario/thinetic/git/thinfilter')
sys.path.append('/mnt/thinetic/git/thinfilter')

import thinfilter.logger as lg
import thinfilter.config
import thinfilter.common

import web
render = web.template.render(thinfilter.config.BASE + 'templates/')

"""
   ./vars 
   ./clean-all 
   ./build-ca 
   ./build-key-server server
   ./build-key cliente1
  openssl dhparam -out dh1024.pem 1024
  KEY_EMAIL="xxx@xxx" PASSIN="xxx" PASSOUT="xxxxx" ./build-key-pass

# show info
openssl x509 -text -in etc_openvpn/keys/server.crt | grep "Subject:"
"""


#delete this
if thinfilter.config.devel:
    #lg.debug("openvpn devel active", __name__ )
    thinfilter.config.OPENVPN_DIR="./openvpn"

def file_exists(fname):
    absfile=os.path.join(thinfilter.config.OPENVPN_DIR, fname)
    if os.path.isfile( absfile ):
        #lg.debug("OpenVpn::file_exists() %s exists"%absfile, __name__)
        return True
    lg.debug("OpenVpn::file_exists() %s ***NO*** exists, creating..."%absfile, __name__)
    return False



class OpenVpn(object):
    def __init__(self):
        self.dir=thinfilter.config.OPENVPN_DIR

    def genCA(self):
        buildCA=False
        if file_exists("keys/ca.key"):
            return True
        # exec clean-all
        thinfilter.common.run("%s/clean-all"%(self.dir), verbose=True, _from=__name__)
        # build ca
        cmd="%s/build-ca"%(self.dir)
        lg.debug("OpenVpn::genCA()  cmd=%s"%cmd, __name__)
        out=thinfilter.common.run(cmd, verbose=True)
        for line in out:
            lg.debug("OpenVpn::genCA()   %s"%line, __name__)
            if file_exists("keys/ca.crt"):
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

    def genCRL(self):
        buildCRL=False
        if file_exists("keys/crl.pem"):
            return True
        cmd="%s/make-crl crl.pem"%(self.dir)
        lg.debug("OpenVpn::genCRL()  cmd=%s"%cmd, __name__)
        p = Popen(cmd, shell=True, bufsize=4096, stdout=PIPE, stderr=STDOUT, close_fds=True)
        for _line in p.stdout.readlines():
            line=_line.replace('\n','')
            lg.debug("OpenVpn::genCRL()   %s"%line, __name__)
            if file_exists("keys/crl.pem"):
                buildCRL=True
        return buildCRL

    def genClient(self, name, email, password):
        name=name.strip()
        if file_exists("keys/%s.key"%(name)):
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
        if not file_exists("keys/%s.key"%(name) ):
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
#        for f in glob.glob( os.path.join(self.dir, "keys/%s.*"%name) ):
#            absf=os.path.abspath(os.path.join(self.dir,f))
#            lg.debug("OpenVpn::revokeClient() deleting %s"%absf, __name__)
#            os.unlink( absf )
        return revoked

    def getName(self, serial):
        out=thinfilter.common.run("openssl x509 -text -in %s/keys/%s.pem"%(self.dir, serial), verbose=False, _from=__name__)
        for line in out:
            if "Subject" in line:
                for item in line.split():
                    if "CN=" in item:
                        name=item.split('=')[1].split('/')[0]
                return name
        return ''

    def getRevoked(self):
        cmd="%s/list-crl"%(self.dir)
        found=False
        index=0
        revoked=[]
        out=thinfilter.common.run(cmd, verbose=False, _from=__name__)
        for line in out:
            if "Revoked Certificates:" in line:
                found=True
                continue
            if found and "Serial" in line:
                #print line.split()
                revoked.append({'serial': line.split()[2]})
                continue
            if found and "Revocation Date" in line:
                revoked[index]['date']=" ".join(line.split()[2:])
                revoked[index]['name']=self.getName(revoked[index]['serial'])
                index=index+1
                continue
        return revoked

    def isUserRevoked(self, user):
        for cert in self.getRevoked():
            if cert.has_key('name') and user == cert['name']:
                return True
        return False

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
            #print line
            #lg.debug("OpenVpn::getUser()   %s"%line, __name__)
            if "Subject:" in line:
                print line.split(', ')
                info=line.split(', ')[5:]
            elif "Not Before:" in line:
                created=line.strip().split(":",1)[1:]
                #lg.debug("OpenVpn::getUser() %s"%line, __name__)
            elif "Not After :" in line:
                expires=line.strip().split(":",1)[1:]
                #lg.debug("OpenVpn::getUser() %s"%line, __name__)
        info.append("Creado=%s"%" ".join(created).strip())
        info.append("Expira=%s"%" ".join(expires).strip())
        info.append("Revocado=%s"%( self.isUserRevoked(user) ))
        return info

    def run(self):
        out=thinfilter.common.run("/etc/init.d/openvpn restart", verbose=False, _from=__name__)
        for line in out:
            lg.debug(line, __name__)

    def reset(self):
        cmd="%s/scripts/init-openvpn.sh only"%(thinfilter.config.OPENVPN_DIR)
        out=thinfilter.common.run(cmd, verbose=False, _from=__name__)
        for line in out:
            lg.debug(line, __name__)
        try:
            os.unlink( os.path.join(thinfilter.config.OPENVPN_DIR, "server.conf") )
        except Exception,err:
            lg.debug("Exception deleting server.conf")

class FileLoader(object):
    def __init__(self, fname):
        self.fname=fname
        self.data=[]
        self.raw=[]
        self.__load()
    def __load(self):
        lg.debug("OPENVPN_DIR='%s' fname='%s'"%(thinfilter.config.OPENVPN_DIR, self.fname), __name__)
        if not os.path.isfile( os.path.join(thinfilter.config.OPENVPN_DIR, self.fname) ):
            return
        f=open( os.path.join(thinfilter.config.OPENVPN_DIR, self.fname), 'r' )
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
    
    def save(self, data):
        lg.debug("FileVars()::save(%s)"%data, __name__)
        f=open( os.path.join(thinfilter.config.OPENVPN_DIR, self.fname), 'w' )
        for line in self.raw:
            key=None
            for k in ["KEY_SIZE", "CA_EXPIRE", "KEY_EXPIRE", "KEY_COUNTRY", "KEY_PROVINCE", "KEY_CITY", "KEY_ORG", "KEY_EMAIL"]:
                if k in line:
                    key=k
            if key:
                f.write("export %s=\"%s\"\n"%(key,data[key]) )
            else:
                f.write(line)
        f.close()

class FileServer(FileLoader):
    __super_init = FileLoader.__init__
    def __init__(self, fname="server.conf"):
        self.__super_init(fname)
    
    def get(self):
        data={'server':'10.8.0.0'}
        for var in self.data:
            if var.startswith("server "):
                data['server']=var.split(' ')[1].strip()
                # netmask is always 255.255.255.0
        return data
    
    def save(self, serverip):
        if len(self.raw) == 0:
            shutil.copy(os.path.join(thinfilter.config.OPENVPN_DIR, self.fname + ".tpl"), 
                        os.path.join(thinfilter.config.OPENVPN_DIR, self.fname))
            self.__super_init(self.fname)
        lg.debug("FileServer()::save(%s)"%serverip, __name__)
        f=open( os.path.join(thinfilter.config.OPENVPN_DIR, self.fname), 'w' )
        for line in self.raw:
            key=None
            if line.startswith("server "):
                f.write("server %s 255.255.255.0\n"%(serverip))
            else:
                f.write(line)
        f.close()


class vpn(object):
    @thinfilter.common.islogged
    @thinfilter.common.isinrole('openvpn.vpn')
    @thinfilter.common.layout(body='', title='Configuración de OpenVPN')
    def GET(self, options=None):
        openvpn_vars=FileVars().get()
        if os.path.isfile("/var/run/openvpn.server.pid"):
            running=True
        else:
            running=False
        conf=FileServer().get()
        lg.debug(conf, __name__)
        return render.vpn(openvpn_vars, running, conf, 'Guardar')

    @thinfilter.common.islogged
    @thinfilter.common.isinrole('openvpn.vpn')
    def POST(self):
        openvpn_vars=FileVars().get()
        formdata=web.input()
        lg.debug(openvpn_vars, __name__)
        lg.debug(formdata, __name__)
        for key in openvpn_vars:
            if formdata.has_key(key):
                openvpn_vars[key]=formdata[key]
        
        if not thinfilter.config.demo:
            # save server.conf
            srv=FileServer().save(formdata.server)
            # save data
            FileVars().save(openvpn_vars)
            # create certs
            OpenVpn().genCA()
            OpenVpn().genDH()
            OpenVpn().genServer()
            OpenVpn().genCRL()
            # run vpn
            OpenVpn().run()
        return web.seeother('/vpn')

class restart(object):
    @thinfilter.common.islogged
    @thinfilter.common.isinrole('openvpn.restart')
    @thinfilter.common.layout(body='', title='Configuración de OpenVPN')
    def GET(self, options=None):
        if not thinfilter.config.demo:
            OpenVpn().run()
        return web.seeother('/vpn')

class reset(object):
    @thinfilter.common.islogged
    @thinfilter.common.isinrole('openvpn.restart')
    @thinfilter.common.layout(body='', title='Configuración de OpenVPN')
    def GET(self, options=None):
        if not thinfilter.config.demo:
            OpenVpn().reset()
        return web.seeother('/vpn')


class Users(object):
    def __init__(self):
        ipp=FileLoader('ipp.txt').get()
        self.users={}
        for f in glob.glob("%s/keys/*.key"%thinfilter.config.OPENVPN_DIR):
            if "server.key" in f or "ca.key" in f: continue
            user=os.path.basename(f).replace('.key','')
            self.users[user]=OpenVpn().getUser(user)
            # Add LastIP
            out=thinfilter.common.run("%s/scripts/openvpn-get-ip.sh '%s' >/dev/null"%(thinfilter.config.OPENVPN_DIR, user), verbose=True, _from=__name__)
            if len(out) > 0:
                last=out[-1].split()[-1]
                if last != "/var/log/ipp.txt":
                    self.users[user].append('LastIP="%s"'%(last))
            #for line in ipp:
            #    if line.startswith("%s,"%user):
            #        self.users[user].append('LastIP=%s'%(line.split(',')[1]) )

    def get(self):
        return self.users

    def add(self, formdata):
        username=None
        email=None
        password=None
        if formdata.has_key('username') and formdata.username != '':
            username=formdata.username
        if formdata.has_key('email') and formdata.email != '':
            email=formdata.email
        if formdata.has_key('password') and formdata.has_key('password2') and formdata.password == formdata.password2:
            password=formdata.password
        
        if username and email and password:
            return OpenVpn().genClient(username, email, password)
        else:
            return False



class users(object):
    @thinfilter.common.islogged
    @thinfilter.common.isinrole('openvpn.users')
    @thinfilter.common.layout(body='', title='Configuración de usuarios VPN')
    def GET(self, options=None):
        openvpn_users=Users().get()
        return render.vpn_users(openvpn_users, 'Guardar')

    @thinfilter.common.islogged
    def POST(self):
        #FIXME
        return web.seeother('/vpn/users')



class adduser(object):
    @thinfilter.common.islogged
    @thinfilter.common.isinrole('openvpn.users')
    @thinfilter.common.layout(body='', title='Configuración de usuarios VPN')
    def GET(self, options=None):
        formdata=web.input()
        return render.vpn_newuser(formdata)

    @thinfilter.common.islogged
    @thinfilter.common.isinrole('openvpn.users')
    def POST(self):
        formdata=web.input()
        print formdata
        if Users().add(formdata):
            return web.seeother('/vpn/users')
        else:
            return web.seeother('/vpn/users/add?error=Datos%20incorrectos')



class download(object):
    @thinfilter.common.islogged
    @thinfilter.common.isinrole('openvpn.users')
    def GET(self, options=None):
        formdata=web.input()
        print formdata
        if not formdata.has_key('username'):
            return web.seeother('/vpn/users')
        
        username=thinfilter.db.clean(formdata.username)
        
        # create zip file
        out=thinfilter.common.run("%s/scripts/openvpn-create.zip '%s'"%(thinfilter.config.OPENVPN_DIR, username), verbose=True, _from=__name__)
        if len(out) != 1:
            return web.seeother('/vpn/users')
        
        if "error" in out[0] or not os.path.isfile(out[0]):
            return web.seeother('/vpn/users')
        
        sfile=out[0]
        filename="vpn-"+os.path.basename(sfile)
        
        
        f=open(os.path.join(sfile), 'rb')
        fs = os.fstat( f.fileno())
        print fs
        #web.header("Expires", thinfilter.common.date_time_string(time.time()+1)) # expires in 1 second
        #web.header("Last-Modified", thinfilter.common.date_time_string(fs.st_mtime))
        web.header("Content-Length", str(fs[6]))
        #web.header("Cache-Control", "max-age=3600, must-revalidate") 
        f.close()
        
        web.header('Content-Type', 'application/octet-stream')
        web.header('Content-Disposition', 'attachment; filename="%s"'%filename)
        web.header('Content-Transfer-Encoding', 'binary')
        
        return open(sfile).read()





def init():
    # nothing to check
    lg.debug("openvpn::init()", __name__)
    
    thinfilter.common.register_url('/vpn',    'thinfilter.modules.openvpn.vpn')
    thinfilter.common.register_url('/vpn/restart',  'thinfilter.modules.openvpn.restart')
    thinfilter.common.register_url('/vpn/reset',  'thinfilter.modules.openvpn.reset')
    thinfilter.common.register_url('/vpn/users',  'thinfilter.modules.openvpn.users')
    thinfilter.common.register_url('/vpn/users/add',  'thinfilter.modules.openvpn.adduser')
    thinfilter.common.register_url('/vpn/users/download',  'thinfilter.modules.openvpn.download')
    
    menu=thinfilter.common.Menu("", "VPN")
    menu.appendSubmenu("/vpn", "Configuración", role='openvpn.vpn')
    menu.appendSubmenu("/vpn/users", "Usuarios", role='openvpn.users')
    #menu.appendSubmenu("/vpn/remote", "Tunel", role='openvpn.restart')
    thinfilter.common.register_menu(menu)
    
    thinfilter.common.register_role_desc('openvpn.vpn', "Configurar servidor VPN")
    thinfilter.common.register_role_desc('openvpn.users', "Administrar usuarios VPN")
    thinfilter.common.register_role_desc('openvpn.restart', "Reiniciar servidor VPN")
    
    # copy server.conf.tpl => server.conf



