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

import thinfilter.statcreator
import thinfilter.config
import netifaces
import sys


if __name__ == "__main__":
    if "debug" in sys.argv:
        thinfilter.config.debug=True

    update=True
    graph=False
    if "graph" in sys.argv:
        graph=True
    
    for net in netifaces.interfaces():
        if net in thinfilter.config.HIDDEN_INTERFACES:
            continue
        app=thinfilter.statcreator.Net(iface=net)
        if update: app.update()
        if graph:  app.graph()
    
    
    app=thinfilter.statcreator.CPU()
    if update: app.update()
    if graph:  app.graph()
