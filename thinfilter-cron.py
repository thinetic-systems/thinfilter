#!/usr/bin/env python
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

import sys
import thinfilter
import thinfilter.config
if "debug" in sys.argv:
    thinfilter.config.debug=True
    thinfilter.config.daemon=False

import thinfilter.statcreator
import netifaces
import thinfilter.squidguard
import thinfilter.logger as lg

class Cron(object):
    def __init__(self):
        pass


    def update_net(self):
        for net in netifaces.interfaces():
            if net in thinfilter.config.HIDDEN_INTERFACES:
                continue
            app=thinfilter.statcreator.Net(iface=net)
            app.update()

    def update_cpu(self):
        app=thinfilter.statcreator.CPU()
        app.update()


    def expireRules(self):
        needReload=False
        sq=thinfilter.squidguard.squidGuard()
        for rule in sq.all:
            #print "%s %s" %(rule.id, rule.expire)
            if rule.expire.expired:
                lg.info("expireRules() id=%s expired, deleting ..."%(rule.id), "thinfilter-cron")
                rule.delete()
                needReload=True
        
        if needReload:
            thinfilter.squidguard.reloadSquid()
        else:
            lg.info("expireRules() no rules expired", "thinfilter-cron")



if __name__ == "__main__":
    app=Cron()
    app.update_net()
    app.update_cpu()
    app.expireRules()
