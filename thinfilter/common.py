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

# common functions

import time
import os
import copy
from subprocess import Popen, PIPE, STDOUT

import thinfilter.logger as lg
import thinfilter.config

import web
triggers={
        'netip-change':[],
        'localip-change':[],
        'dnsmasq-change':[]
        }


class SessionData(object):
    def __init__(self, **kwargs):
        for _var in kwargs:
            setattr(self, _var, kwargs[_var])


#
# decorator for protected methods
#
def islogged(function):
    def new_function(*args, **kwargs):
        username = web.config._session.get('user', '')
        #lg.debug("islogged() username=%s"%username, __name__)
        if username:
            # check for timestamp
            timestamp=web.config._session.get('timestamp', 0)
            #lg.debug("islogged() timestamp=%s"%timestamp, __name__)
            if int(time.time()) - timestamp > thinfilter.config.sessiontimeout:
                lg.debug("islogged() timestamp=%s seconds => timeout force logout"%(int(time.time()) - timestamp), __name__)
                # session expired
                raise web.seeother("/logout?timeout=1")
            
            # update timestamp
            #lg.debug("islogged() timestamp=%s UPDATED"%( int(time.time()) ), __name__)
            web.config._session.timestamp=int(time.time())
            
            return function(*args, **kwargs)
        else:
            raise web.seeother('/login')

    return new_function

#
# decorator for template layout methods
#
def layout(body='', title='ThinFilter', session=None ):
    render = web.template.render(thinfilter.config.BASE + 'templates/')
    def new_deco(function):
        def new_function(*args, **kwargs):
            body = function(*args, **kwargs)
            if web.config._session:
                session=web.config._session
            #lg.debug("layout() session=%s"%(session), __name__)
            layout = render.layout(title=title, body=body, session=session, menus=get_menus(), config=thinfilter.config)
            return layout
        
        return new_function

    return new_deco

#
# decorator for access rights
#
def isinrole(role='', session=None):
    def new_deco(function):
        def new_function(*args, **kwargs):
            if web.config._session:
                session=web.config._session
            ROLES=web.config._session.get('roles','')
            #lg.debug("isinole() USER ROLES='%s' needed role='%s'"%(ROLES, role), __name__)
            
            if "admin" in ROLES:
                #lg.debug("isinrole() user is admin, return True", __name__)
                return function(*args, **kwargs)
                
            elif role in ROLES:
                #lg.debug("isinrole() role found in ROLES, return True", __name__)
                return function(*args, **kwargs)
            else:
                #lg.debug("isinrole() role not found, return False", __name__)
                raise web.seeother('/403?role=%s'%(role))
            
        return new_function
    return new_deco


def get_user_roles(username):
    roles=[]
    _roles=thinfilter.db.query("SELECT roles FROM auth WHERE username='%s'"%username)
    for r in _roles[0][0].split():
        roles.append(r)
    return roles

################################################################################
# from /usr/lib/python2.5/BaseHTTPServer.py
def date_time_string(timestamp=None):
    """Return the current date and time formatted for a message header."""
    weekdayname = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']

    monthname = [None,
                 'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
                 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    if timestamp is None:
        timestamp = time.time()
    year, month, day, hh, mm, ss, wd, y, z = time.gmtime(timestamp)
    s = "%s, %02d %3s %4d %02d:%02d:%02d GMT" % (
            weekdayname[wd],
            day, monthname[month], year,
            hh, mm, ss)
    return s

################################################################################

def run(cmd, verbose=True, canfail=False, _from=__name__):
    if verbose: lg.debug("run: %s" %cmd, __name__)
    
    result=[]
    running=True
    p = Popen(cmd, shell=True, bufsize=4096, stdout=PIPE, stderr=STDOUT, close_fds=True)
    for _line in p.stdout.readlines():
        line=_line.replace('\n','')
        if line.strip() == '': continue
        if verbose:
            lg.debug( line.replace('\n', '') , _from)
        result.append( line.replace('\n','') )

    if canfail:
        if p.returncode == 2:
            lg.error("ERROR: Command return code 2 and canfail is True", _from)
            #sys.exit(1)
    return result

################################################################################


def init_modules(base):
    """
    launch init() method in every loaded module
    """
    for mod in dir(base):
        if mod.startswith("__"): continue
        
        obj=getattr(base, mod)
        #print dir(obj)
        if hasattr(obj, 'init'):
            # call init() in module
            getattr(obj, 'init')()
        else:
            lg.error("Module '%s' don't have init() method"%mod, __name__)


################################################################################
def register_url(url, classname):
    #lg.debug("register_url() url='%s' classname='%s'"%(url, classname), __name__)
    thinfilter.config.urls.append( url )
    thinfilter.config.urls.append( classname )

def geturls():
    # return a tuple
    for i in range(len(thinfilter.config.urls)/2):
        lg.debug("REGISTERED url '%s'  =>   '%s'"%(thinfilter.config.urls[i*2], thinfilter.config.urls[i*2+1]) , __name__)
    return tuple(thinfilter.config.urls)

################################################################################
class Base(dict):
    """
    base class expanding dict object, based on web.Storage object
    """
    def __getattr__(self, key):
        try:
            return self[key]
        except KeyError, k:
            raise AttributeError, k

    def __setattr__(self, key, value):
        self[key] = value

    def __delattr__(self, key):
        try:
            del self[key]
        except KeyError, k:
            raise AttributeError, k

    def __repr__(self):
        return '<Base ' + dict.__repr__(self) + '>'

################################################################################

class Menu(Base):
    """
    Menu object with submenus
    """
    def __init__(self, path="/", name="unknow", submenus=[], order=50, role=''):
        self.name=name
        self.path=path
        # froms 0 to 100
        self.order=order
        self.role=role
        self.submenus=[]
        
    def __repr__(self):
        return '<Menu ' + dict.__repr__(self) + '>'
    
    def appendSubmenu(self, path="/", name="unknow", role=''):
        sub=Menu()
        sub.name=name
        sub.path=path
        sub.role=role
        del(sub.submenus)
        self.submenus.append(sub)

def register_menu(menu):
    #lg.debug("register_menu() menu=%s"%menu, __name__)
    thinfilter.config.menus.append(menu)

def _sort_menu(menu1, menu2):
    if menu1.order > menu2.order:
        return 1
    elif menu1.order == menu2.order:
        return 0
    else:
        return -1

def showMenu(role, roles, menu):
    #lg.debug("role='%s' roles='%s' menu=%s\n" %(role, roles, menu), __name__)
    if "admin" in roles:
        #lg.debug("showMenu() admin user, return True", __name__)
        return True
    if role == '':
        #lg.debug("showMenu() role empty, not protected, return True", __name__)
        return True
    elif role in roles:
        #lg.debug("showMenu() role found in roles, retrurn True", __name__)
        return True
        
    #lg.debug("NOT SHOW role='%s' roles='%s'" %(role, roles))
    return False

def get_menus():
    clonedmenus=[]
    # clone menus (don't work with original objects)
    for menu in thinfilter.config.menus:
        clonedmenus.append( copy.copy(menu) )
    
    # sort by order attr
    clonedmenus.sort(_sort_menu)
    
    roles=tuple()
    if web.config._session:
        roles=web.config._session.get('roles', '')
    
    newmenu=[]
    # remove not allowed items
    for menu in clonedmenus:
        if len(menu.submenus) > 0:
            newmenu.append(menu)
            submenus=menu.submenus
            newmenu[-1].submenus=[]
            for submenu in submenus:
                if showMenu(submenu.role, roles, submenu):
                    newmenu[-1].submenus.append(submenu)
            
        else:
            # no submenus
            if showMenu(menu.role, roles, menu):
                newmenu.append(menu)
    new=[]
    for i in range(len(newmenu)):
        menu=newmenu[i]
        if menu.path == '' and len(menu.submenus) < 1:
            pass
        else:
            new.append(menu)
    return new

################################################################################

class Button(Base):
    def __init__(self, path="/", name="unknow", img="/"):
        self.name=name
        self.path=path
        self.img=img
    def __repr__(self):
        return '<Button ' + dict.__repr__(self) + '>'

def register_button(button):
    #lg.debug("register_button() button=%s"%button, __name__)
    thinfilter.config.buttons.append(button)

def get_buttons():
    return thinfilter.config.buttons

################################################################################

def register_trigger(triggername, triggeraction):
    lg.debug("register_trigger() name=%s action=%s"%(triggername,triggeraction), __name__ )
    if not triggers.has_key(triggername):
        triggers[triggername]=[]
    triggers[triggername].append(triggeraction)

class ThinFilterException(Exception):
    def __str__(self):
        return repr(self)
    def __init__(self, errcode, errmsg):
        self.errcode = errcode
        self.errmsg = errmsg
    def __repr__(self):
        return (
            "<ThinFilterException %s msg: %s>" %
            (self.errcode, self.errmsg)
            )

################################################################################

def register_role_desc(role, desc):
    thinfilter.config.role_desc.append([role,desc])

def get_roles_desc(rol=None):
    if rol:
        return get_desc(rol)
    roles=[]
    for role in thinfilter.config.role_desc:
        roles.append(role[0])
    return roles

def get_desc(role):
    for r in thinfilter.config.role_desc:
        if role == r[0]:
            return r[1]
    return "desconocido"

################################################################################
from hashlib import sha1
import random
# A simple user object that doesn't store passwords in plain text
# see http://en.wikipedia.org/wiki/Salt_(cryptography)

class PasswordHash(object):
    """
    Compare/generate password with hashed
    """
    def __init__(self, password_=None, hash_=None):
        if password_:
            self.hash=sha1(password_).hexdigest()
        elif hash_:
            self.hash=hash_
        else:
            raise "PasswordHash not passed password or hash"
    def check_password(self, password_):
        """checks if the password is correct"""
        return self.hash == sha1(password_).hexdigest()
    
    def get(self):
        return self.hash

################################################################################
import netifaces

class Interfaces(object):
    def __init__(self, **kwargs):
        self.__GetAllNetworkInterfaces__()

    def get_ip_address(self, ifname):
        lg.debug("get_ip_address() ifname=%s" %(ifname) , __name__)
        if not ifname in netifaces.interfaces():
            return None
        ip=netifaces.ifaddresses(ifname)
        if ip.has_key(netifaces.AF_INET):
            return ip[netifaces.AF_INET][0]['addr']
        return None

    def __getLink__(self, iface):
        try:
            f=open("/sys/class/net/%s/carrier"%iface, 'r')
        except:
            lg.error("Can't read /sys/class/net/%s/carrier"%iface, __name__)
            return False
        try:
            link=f.readline().strip()
        except:
            lg.error("Can't read /sys/class/net/%s/carrier"%iface, __name__)
            link=0
        f.close()
        if link == "1":
            return True
        else:
            return False

    def __getGateway__(self, iface):
        data=[]
        try:
            f=open("/proc/net/route", 'r')
        except:
            lg.error("/proc/net/route is not readable", __name__)
            return None
        for l in f.readlines():
            if l.startswith(iface):
                tmp=l.strip().split()
                if tmp[1] == "00000000":
                    data.append(self.__hex2dec__(tmp[2]))
                    break
        f.close()
        if len(data) < 1:
            lg.warning("WARNING: iface='%s' no gateway"%iface, __name__)
            return None
        else:
            return data[0]

    def __hex2dec__(self, s):
        out=[]
        for i in range(len(s)/2):
            out.append( str(int(s[i*2:(i*2)+2],16)) )
        # data in /proc/net/route is reversed
        out.reverse()
        return ".".join(out)

    def __GetAllNetworkInterfaces__(self):
        self.allnetworkinterfaces=[]
        for dev in netifaces.interfaces():
            if not dev in thinfilter.config.HIDDEN_INTERFACES:
                ip=netifaces.ifaddresses(dev)
                if ip.has_key(netifaces.AF_INET):
                    data=ip[netifaces.AF_INET][0]
                    data['iface']=dev
                    data['gateway']=self.__getGateway__(dev)
                    if not data['gateway']:
                        data['readonly']="readonly"
                    else:
                        data['readonly']=""
                    data['link']=self.__getLink__(dev)
                    self.allnetworkinterfaces.append(data)
        #lg.debug ( "Interfaces::GetAllNetworkInterfaces() %s" %( self.allnetworkinterfaces ), __name__ )
        return self.allnetworkinterfaces

    def get(self):
        lg.debug ( "Interfaces::get() %s" %( self.allnetworkinterfaces ), __name__ )
        return self.allnetworkinterfaces

################################################################################

def FirstRun(do='0'):
    if do == '0':
        return
    lg.debug("FirstRun()", __name__)

# from /usr/lib/python2.5/BaseHTTPServer.py
def date_time_string(timestamp=None):
    """Return the current date and time formatted for a message header."""
    weekdayname = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']

    monthname = [None,
                 'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
                 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    if timestamp is None:
        timestamp = time.time()
    year, month, day, hh, mm, ss, wd, y, z = time.gmtime(timestamp)
    s = "%s, %02d %3s %4d %02d:%02d:%02d GMT" % (
            weekdayname[wd],
            day, monthname[month], year,
            hh, mm, ss)
    return s





