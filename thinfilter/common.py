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


import thinfilter.logger as lg
import thinfilter.config

import web


class SessionData(object):
    def __init__(self, **kwargs):
        for _var in kwargs:
            setattr(self, _var, kwargs[_var])



def islogged(function):
    def new_function(*args, **kwargs):
        username = web.config._session.get('user', '')
        lg.debug("islogged() username=%s"%username, __name__)
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
            lg.debug("layout() session=%s"%(session), __name__)
            layout = render.layout(title=title, body=body, session=session)
            return layout
        
        return new_function

    return new_deco



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



def register_url(url, classname):
    lg.debug("register_url() url='%s' classname='%s'"%(url, classname), __name__)
    thinfilter.config.urls.append( url )
    thinfilter.config.urls.append( classname )

def geturls():
    # return a tuple
    for i in range(len(thinfilter.config.urls)/2):
        lg.debug("REGISTERED url '%s'  =>   '%s'"%(thinfilter.config.urls[i*2], thinfilter.config.urls[i*2+1]) )
    return tuple(thinfilter.config.urls)


class Menu(dict):
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
        return '<Menu ' + dict.__repr__(self) + '>'


def register_menu(menu):
    lg.debug("register_menu() menu=%s"%menu, __name__)
