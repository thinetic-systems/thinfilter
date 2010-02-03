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
# login stuff
#

import random
from hashlib import sha1
import thinfilter.config
import thinfilter.logger as lg
import thinfilter.common
import thinfilter.db
import traceback

# A simple user object that doesn't store passwords in plain text
# see http://en.wikipedia.org/wiki/Salt_(cryptography)
class PasswordHash(object):
    def __init__(self, password_):
        self.salt = "".join(chr(random.randint(33,127)) for x in xrange(64))
        self.saltedpw = sha1(password_ + self.salt).hexdigest()
    def check_password(self, password_):
        """checks if the password is correct"""
        return self.saltedpw == sha1(password_ + self.salt).hexdigest()

# users and password are stored in sqlite3 database
users={}
for _auth in thinfilter.db.query("SELECT username,password from auth"):
    users[_auth[0]]=PasswordHash(_auth[1])




import web
render = web.template.render(thinfilter.config.BASE + 'templates/')

signin_form = web.form.Form(web.form.Textbox('username',
                                     web.form.Validator('Unknown username.', 
                                                     lambda x: x in users.keys()),
                                     description='Usuario:'),
                        web.form.Password('password', description='Contraseña:'),
                        web.form.Button("submit", type="submit", description="Entrar"),
                        validators = [web.form.Validator("El usuario o la contraseña son incorrectos.",
                                      lambda x: users[x.username].check_password(x.password)) ]
                        )



class login(object):
    @thinfilter.common.layout(body='No logueado', title='ThinFilter Login')
    def GET(self):
        username=web.config._session.get('user', '')
        lg.debug("login::GET() user=%s"%username, __name__)
        if not username:
            my_signin = signin_form()
            return render.login(my_signin)
        else:
            return render.main(thinfilter.common.get_buttons())
    
    @thinfilter.common.layout(body='No logueado', title='ThinFilter Login')
    def POST(self):
        my_signin = signin_form()
        if not my_signin.validates():
            lg.debug("not login valid")
            return web.seeother('/')
        else:
            web.config._session.user=my_signin['username'].value
            web.config._session.roles=thinfilter.db.query("SELECT roles FROM auth WHERE username='%s'"%my_signin['username'].value)[0]
            lg.debug("login OK set session.user to %s" %my_signin['username'].value, __name__)
            return render.main(thinfilter.common.get_buttons())

class logout(object):
    def GET(self):
        web.config._session.user=''
        web.config._session.roles=''
        try:
            web.config._session.kill()
        except Exception, err:
            lg.debug("Exception logout, error=%s"%err, __name__)
            traceback.print_exc(file=sys.stderr)
            pass
        raise web.seeother('/')



def init():
    # nothing to check
    lg.debug("login::init()", __name__)
    """
        '/', 'login', 
        '/login', 'login',
        '/logout', 'logout',
    """
    thinfilter.common.register_url('/',      'thinfilter.modules.login.login')
    thinfilter.common.register_url('/login', 'thinfilter.modules.login.login')
    thinfilter.common.register_url('/logout', 'thinfilter.modules.login.logout')

