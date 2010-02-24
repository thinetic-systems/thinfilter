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

class UserObj(web.Storage):
    def __repr__(self):
        return '<UserObj ' + dict.__repr__(self) + '>'
    def __init__(self, username='', password='', roles=''):
        self.username=username
        self.password=password
        self.roles=[]
        self.rolesobj=[]
        for role in roles.split():
            self.roles.append( role )
            self.rolesobj.append( {'role':role, 'desc':thinfilter.common.get_desc(role)})

    def save(self):
        # insert/edit in database
        
        exists=thinfilter.db.query("SELECT username,password FROM auth WHERE username='%s'"%(thinfilter.db.clean(self.username)))
        
        if len(exists) < 1:
            # insert
            passwd=thinfilter.common.PasswordHash(password_=self.password).get()
            ret=thinfilter.db.query("INSERT INTO auth (username, password, roles) VALUES ('%s', '%s', '%s')"
                                %(thinfilter.db.clean(self.username),
                                  passwd,
                                  " ".join(self.roles)
                                  )
                               )
        else:
            # edit username
            if self.password != '':
                passwd=thinfilter.common.PasswordHash(password_=self.password).get()
            else:
                passwd=exists[0][1]
            ret=thinfilter.db.query("UPDATE auth set password='%s', roles='%s' WHERE username='%s'"
                                %(passwd,
                                  " ".join(self.roles),
                                  thinfilter.db.clean(self.username)
                                  )
                               )

class Users(object):
    def __init__(self):
        # read all users
        self.users=[]

    def get_all(self):
        _users=thinfilter.db.query("SELECT username,roles FROM auth")
        for u in _users:
            self.users.append( UserObj( u[0], '', u[1]) )
        return self.users

    def get(self):
        return self.users

    def get_user(self, _username):
        sql="SELECT username,password,roles FROM auth WHERE username='%s'"%(thinfilter.db.clean(_username))
        _data=thinfilter.db.query(sql)
        if len(_data) < 1:
            return UserObj()
        user=UserObj( _data[0][0], _data[0][1], _data[0][2])
        return user

    def save_user(self, formdata):
        lg.debug("save_user() %s"%formdata, __name__)
        user=UserObj()
        # get username
        if formdata.has_key('new') and formdata.new == '0':
            user.username=formdata.usernameold
        else:
            user.username=formdata.username
        
        # compare password and save
        if formdata.password != '':
            if formdata.password == formdata.password2:
                user.password=formdata.password
            else:
                return False
        
        for role in thinfilter.common.get_roles_desc():
            if role in formdata.keys():
                user.roles.append(role)
        
        user.save()
        lg.debug("user=%s"%user, __name__)

    def edit(self, userobj):
        pass

    def delete(self, username):
        pass


class users(object):
    @thinfilter.common.islogged
    @thinfilter.common.isinrole('users.users')
    @thinfilter.common.layout(body='', title='Configuración de Usuarios')
    def GET(self):
        userlist=Users().get_all()
        return render.users(userlist, action='Guardar')

class edit(object):
    @thinfilter.common.islogged
    @thinfilter.common.isinrole('users.edit')
    @thinfilter.common.layout(body='', title='Configuración de Usuarios')
    def GET(self):
        new=False
        formdata=web.input()
        if formdata.has_key('new'):
            new=True
        elif not formdata.has_key('u'):
            raise web.seeother('/users')
        userdata=Users().get_user(formdata.u)
        return render.user_edit(userdata, new, thinfilter.common.get_roles_desc , action='Guardar')


    @thinfilter.common.islogged
    @thinfilter.common.isinrole('users.edit')
    def POST(self):
        formdata=web.input()
        #print formdata
        if not thinfilter.config.demo:
            Users().save_user(formdata)
        raise web.seeother('/users')


class delete(object):
    @thinfilter.common.islogged
    @thinfilter.common.isinrole('users.edit')
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
    thinfilter.common.register_url('/users/edit',     'thinfilter.modules.users.edit')
    thinfilter.common.register_url('/users/delete',  'thinfilter.modules.users.delete')

    # register menus
    menu=thinfilter.common.Menu("", "Usuarios", order=99)
    menu.appendSubmenu("/users", "Lista", role='users.users')
    menu.appendSubmenu("/users/edit?new=1&u=", "Añadir", role='users.edit')
    thinfilter.common.register_menu(menu)
    
    #button=thinfilter.common.Button("/usuarios", "Usuarios", "/data/network.png")
    #thinfilter.common.register_button(button)
    
    thinfilter.common.register_role_desc('users.users', "Ver usuarios")
    thinfilter.common.register_role_desc('users.edit', "Editar usuarios")



#if __name__ == "__main__":
#    thinfilter.config.daemon=False
#    thinfilter.config.debug=True
