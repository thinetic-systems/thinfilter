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


import time
import thinfilter.config
import thinfilter.logger as lg
import thinfilter.common
import thinfilter.db
import traceback




import web
render = web.template.render(thinfilter.config.BASE + 'templates/')

signin_form = web.form.Form(web.form.Textbox('username',
                                     web.form.Validator('Unknown username.', 
                                                     lambda x: x in thinfilter.config.users.keys()),
                                     description='Usuario:'),
                            web.form.Password('password', description='Contraseña:'),
                            web.form.Button("Entrar", type="submit", description="Entrar"),
                            validators = [web.form.Validator("El usuario o la contraseña son incorrectos.",
                                          lambda x: thinfilter.config.users[x.username].check_password(x.password)) ]
                        )




class login(object):
    @thinfilter.common.layout(body='No logueado', title='ThinFilter')
    def GET(self):
        username=web.config._session.get('user', '')
        password=web.config._session.get('password', '')
        lg.debug("login::GET() user=%s password=%s"%(username,password), __name__)
        if not username:
            my_signin = signin_form()
            return render.login(my_signin)
        else:
            return render.main(thinfilter.common.get_buttons())
    
    #@thinfilter.common.layout(body='No logueado', title='ThinFilter Login')
    def POST(self):
        my_signin = signin_form()
        if not my_signin.validates():
            lg.debug("not login valid")
            return web.seeother('/')
        else:
            web.config._session.user=my_signin['username'].value
            web.config._session.roles=thinfilter.common.get_user_roles(my_signin['username'].value)
            web.config._session.timestamp=int(time.time())
            lg.debug("login OK set session.user to %s timestamp=%s"
                      %(my_signin['username'].value, web.config._session.timestamp), __name__)
            formdata=web.input()
            lg.debug(formdata, __name__)
            if formdata.has_key('redirect'):
                raise web.seeother(formdata.redirect)
            raise web.seeother('/')

class logout(object):
    def GET(self):
        web.config._session.user=''
        web.config._session.roles=''
        try:
            web.config._session.kill()
            formdata=web.input()
            if formdata.has_key('timeout'):
                return web.seeother("/403?timeout=1")
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

