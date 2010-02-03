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

class settings(object):
    @thinfilter.common.islogged
    @thinfilter.common.isinrole('settings')
    @thinfilter.common.layout(body='', title='Configuración')
    def GET(self, options=None):
        
        import thinfilter.rules
        lg.debug("config::GET() options=%s" %options, __name__)
        
        if options == "cache":
            conf=thinfilter.rules.squid().getdata()
        
        elif options == "network":
            conf=thinfilter.rules.ips().getdata()
        
        elif options == "stats":
            conf=thinfilter.rules.squid().mgrinfo()
        
        else:
            conf=[
              thinfilter.rules.DataObj(itype="checkbox", varname="var1", value=1, varnamechecked="checked"),
              thinfilter.rules.DataObj(itype="checkbox", varname="var2", value=2, varnamechecked=""),
              thinfilter.rules.DataObj(itype="checkbox", varname="var3", value=3, varnamechecked="checked"),
              thinfilter.rules.DataObj(itype="text", varname="var4", value="prueba"),
                ]
        
        return render.config(conf)

    @thinfilter.common.islogged
    def POST(self):
        return web.seeother('/')


def init():
    # nothing to check
    lg.debug("settings::init()", __name__)
    """
        '/settings/(.*)', 'settings',
    """
    thinfilter.common.register_url('/settings/(.*)',      'thinfilter.modules.settings.settings')

