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


import thinfilter.logger as lg
import thinfilter.config
import thinfilter.common

import web
render = web.template.render(thinfilter.config.BASE + 'templates/')

IPTABLES="/sbin/iptables"


class FireWall(thinfilter.common.Base):
    def __init__(self):
        pass





class firewall(object):
    @thinfilter.common.islogged
    @thinfilter.common.layout(body='', title='Configuración del Cortafuegos')
    def GET(self, options=None):
        firewall_vars=XXXXXXXXXXXXXXX
        return render.firewall(firewall_vars, 'Guardar')

    @thinfilter.common.islogged
    def POST(self):
        # FIXME guardar formulario
        return web.seeother('/firewall')




def init():
    # nothing to check
    lg.debug("firewall::init()", __name__)
    """
        '/firewall',       'firewall',
    """
    thinfilter.common.register_url('/firewall',    'thinfilter.modules.firewall.firewall')


if __name__ == "__main__":
    thinfilter.config.daemon=False
    thinfilter.config.debug=True
    
    print getUsers().get()



