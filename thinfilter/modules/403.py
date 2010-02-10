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
# access denied stuff
#



import thinfilter.logger as lg
import thinfilter.common


import web
render = web.template.render(thinfilter.config.BASE + 'templates/')

class denied(object):
    @thinfilter.common.layout(body='Permiso denegado', title='ThinFilter Login')
    def GET(self):
        formdata=web.input()
        if formdata.has_key('role'):
            return render.denied(formdata.role)
        
        elif formdata.has_key('timeout'):
            return render.timeout()
        
        else:
            return render.denied('Error desconocido')




def init():
    # nothing to check
    lg.debug("403::init()", __name__)
    
    thinfilter.common.register_url('/403',      'thinfilter.modules.403.denied')

