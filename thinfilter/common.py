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



def islogged(function):
    def new_function(*args, **kwargs):
        username = web.config._session.get('user', '')
        #lg.debug("islogged() username=%s"%username, __name__)
        if username:
            return function(*args, **kwargs)
        else:
            raise web.seeother('/login')

    return new_function


def layout(body='', title='ThinFilter', session=None ):
    render = web.template.render(thinfilter.config.BASE + 'templates/')
    def new_deco(function):
        def new_function(*args, **kwargs):
            body = function(*args, **kwargs)
            if web.config._session:
                session=web.config._session
            #lg.debug("layout() session=%s"%(session), __name__)
            layout = render.layout(title=title, body=body, session=session, menus=get_menus())
            return layout
        
        return new_function

    return new_deco


def isinrole(role='', session=None):
    def new_deco(function):
        def new_function(*args, **kwargs):
            if web.config._session:
                session=web.config._session
            ROLES=web.config._session.get('roles','')
            lg.debug("ROLES='%s' role='%s'"%(ROLES, role), __name__)
            
            if "admin" in ROLES:
                return function(*args, **kwargs)
                
            if role == 'admin':
                return function(*args, **kwargs)
            elif role in ROLES:
                return function(*args, **kwargs)
            else:
                raise web.seeother('/403?role=%s'%(role))
            
        return new_function
    return new_deco

#    
#    def new_role(function):
#        # search in roles
#        try:
#            roles=web.config._session.get('roles','')
#            lg.debug("ROLES='%s' role='%s'"%(roles, role), __name__)
#        except:
#            pass
#        return function(*args, **kwargs)

#    return new_role

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
#    
#    while running:
#        #print p
#        if p.poll() != None: running=False
#        line=p.stdout.readline()
#        if line.strip() == '': continue
#        if verbose:
#            lg.debug( line.replace('\n', '') , _from)
#        result.append( line.replace('\n','') )
#    p.wait()

    if canfail:
        if p.returncode == 2:
            lg.error("ERROR: Command return code 2 and canfail is True", _from)
            #sys.exit(1)
    return result


def init_modules(base):
    for mod in dir(base):
        if mod.startswith("__"): continue
        
        obj=getattr(base, mod)
        #print dir(obj)
        if hasattr(obj, 'init'):
            # call init() in module
            getattr(obj, 'init')()
        else:
            lg.error("Module '%s' don't have init() method"%mod, __name__)
            print dir(obj)


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

class Menu(web.Storage):
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

def showMenu(role, roles):
    #lg.debug("role='%s' roles='%s'" %(role, roles))
    if "admin" in roles:
        return True
    if role == '':
        return True
    elif role in roles:
        return True
        
    lg.debug("NOT SHOW role='%s' roles='%s'" %(role, roles))
    return False

def get_menus():
    #lg.debug("get_menus() antes=%s" %thinfilter.config.menus, __name__)
    thinfilter.config.menus.sort(_sort_menu)
    #lg.debug("get_menus() despues=%s" %thinfilter.config.menus, __name__)
    from pprint import pprint
    roles=tuple()
    if web.config._session:
        roles=web.config._session.get('roles', '')
    #print "user roles='%s'"%(roles)
    newmenu=[]
    # remove not allowed items
    for menu in thinfilter.config.menus:
        #print "\n"
        #print "menu %s" %menu
        
        if len(menu.submenus) > 0:
            newmenu.append(menu)
            submenus=menu.submenus
            menu.submenus=[]
            for submenu in submenus:
                #print "  submenu %s\n"%submenu
                if showMenu(submenu.role, roles):
                    newmenu[-1].submenus.append(submenu)
            
        else:
            # no submenus
            if showMenu(menu.role, roles):
                newmenu.append(menu)
        
        #print "\n"
    
    new=[]
    for i in range(len(newmenu)):
        menu=newmenu[i]
        if menu.path == '' and len(menu.submenus) < 1:
            pass
        else:
            new.append(menu)
    #return thinfilter.config.menus
    return new

################################################################################

class Button(web.Storage):
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

