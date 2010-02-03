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

import glob

# DELETE me
sys.path.append('/home/mario/thinetic/git/thinfilter')


import thinfilter.logger as lg
import thinfilter.config
import thinfilter.common

import web
render = web.template.render(thinfilter.config.BASE + 'templates/')


class InfoScreen(thinfilter.common.Base):
    def __init__(self):
        pass


class stop(object):
    #@thinfilter.common.islogged
    #@thinfilter.common.layout(body='', title='Configuración de las pantallas de bloqueo')
    def GET(self, options=None):
        #fobj=FireWall()
        stop_vars={}
        formdata=web.input()
        formdata.info="Estas accediendo a una web social donde ...."
        if not formdata.has_key('url'):
            formdata.url='desconocida'
        #lg.debug("firewall::GET() firewall=%s" %firewall_vars, __name__)
        return render.stop(formdata, 'Guardar')


class admin(object):
    @thinfilter.common.islogged
    @thinfilter.common.isinrole('stop.admin')
    @thinfilter.common.layout(body='', title='Configuración de las pantallas de bloqueo')
    def GET(self, options=None):
        pass

    @thinfilter.common.islogged
    def POST(self):
        return web.seeother('/stop/admin')

def init():
    # nothing to check
    lg.debug("stop::init()", __name__)
    """
        '/stop',       'stop',
    """
    thinfilter.common.register_url('/stop',       'thinfilter.modules.stop.stop')
    thinfilter.common.register_url('/stop/admin', 'thinfilter.modules.stop.admin')
    
    
    
    menu=thinfilter.common.Menu("", "Pantallas", order=60)
    menu.appendSubmenu("/stop?url=http://url.de.ejemplo/index.html", "Ver pantalla")
    menu.appendSubmenu("/stop/admin", "Configurar pantalla", role='stop.admin')
    thinfilter.common.register_menu(menu)

if __name__ == "__main__":
    thinfilter.config.daemon=False
    thinfilter.config.debug=True
    
    app = FireWall()
    app.restart()
    



