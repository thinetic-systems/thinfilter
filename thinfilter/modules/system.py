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
# settings stuff
#

import thinfilter.config
import thinfilter.logger as lg
import thinfilter.common

import web
render = web.template.render(thinfilter.config.BASE + 'templates/')

class system(object):
    @thinfilter.common.islogged
    @thinfilter.common.isinrole('system.system')
    @thinfilter.common.layout(body='', title='Sistema')
    def GET(self):
        return render.system()

    @thinfilter.common.islogged
    @thinfilter.common.isinrole('system.system')
    def POST(self):
        return web.seeother('/system')


def init():
    lg.debug("system::init()", __name__)
    
    thinfilter.common.register_url('/system',      'thinfilter.modules.system.system')
    
    
    menu=thinfilter.common.Menu("/system", "Sistema", order=95)
    #menu.appendSubmenu("/system", "Sistema", role='system.system')
    #menu.appendSubmenu("/shares/share/new", "Nuevo recurso", role='samba.shares')
    #menu.appendSubmenu("/shares/user/new", "Nuevo usuario", role='samba.shares')
    thinfilter.common.register_menu(menu)
    
    thinfilter.common.register_role_desc('system.system', "Apagar o reiniciar servidor")

