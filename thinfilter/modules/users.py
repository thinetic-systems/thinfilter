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
# users stuff
#


import thinfilter.logger as lg
import thinfilter.config
import thinfilter.db

import thinfilter.common
import web
render = web.template.render(thinfilter.config.BASE + 'templates/')

class Users(object):
    def __init__(self):
        # read all users
        self.users=thinfilter.db.query("SELECT * from auth")

    def get(self):
        return self.users

    def edit(self, userobj):
        pass

    def delete(self, username):
        pass


class users(object):
    @thinfilter.common.islogged
    @thinfilter.common.isinrole('admin')
    @thinfilter.common.layout(body='', title='Configuración de Usarios')
    def GET(self):
        userlist=Users().get()
        return render.users(userlist, action='Guardar')

class add(object):
    @thinfilter.common.islogged
    @thinfilter.common.isinrole('admin')
    @thinfilter.common.layout(body='', title='Configuración de Usarios')
    def GET(self):
        #FIXME
        #userlist=Users().get()
        #return render.users(userlist, action='Guardar')
        raise web.seeother('/users')

class delete(object):
    @thinfilter.common.islogged
    @thinfilter.common.isinrole('admin')
    @thinfilter.common.layout(body='', title='Configuración de Usarios')
    def GET(self):
        #FIXME
        #userlist=Users().get()
        #return render.users(userlist, action='Guardar')
        raise web.seeother('/users')


def init():
    # nothing to check
    lg.debug("users::init()", __name__)
    
    thinfilter.common.register_url('/users',         'thinfilter.modules.users.users')
    thinfilter.common.register_url('/users/add',     'thinfilter.modules.users.add')
    thinfilter.common.register_url('/users/delete',  'thinfilter.modules.users.delete')

    # register menus
    menu=thinfilter.common.Menu("", "Usuarios", order=99)
    menu.appendSubmenu("/users", "Lista", role='admin')
    menu.appendSubmenu("/users/add", "Añadir", role='admin')
    thinfilter.common.register_menu(menu)
    
    button=thinfilter.common.Button("/usuarios", "Usuarios", "/data/network.png")
    thinfilter.common.register_button(button)



if __name__ == "__main__":
    thinfilter.config.daemon=False
    thinfilter.config.debug=True
