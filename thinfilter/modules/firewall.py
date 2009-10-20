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

# delete me
sys.path.append('/home/mario/thinetic/git/thinfilter')


import thinfilter.logger as lg
import thinfilter.config
import thinfilter.common

import web
render = web.template.render(thinfilter.config.BASE + 'templates/')



FW_CONF="/etc/thinfilter/firewall.conf"
FW_SCRIPT="/usr/sbin/fw.proxy"

#delete this
FW_CONF="firewall/firewall.conf"
FW_SCRIPT="firewall/fw.proxy"

VARS=[
      'VPN_ENABLE',
      'ONLY_WEB',
      'ICMP_ENABLE',
      'NTP_ENABLE',
      'PORTS',
      'NOPROXY',
      'NOPROXY_PORTS',
      'ALL_OPEN_PORTS',
      ]

FW_PORTS={
        'https':[443],
        'ftp':['ftp'],
        'ssh':[22],
        'correo':[25,465,110,995,143,993],
        }

class FireWall(thinfilter.common.Base):
    def __init__(self):
        self.vars={}
        self.varsobj=thinfilter.common.Base()
        f=open(FW_CONF, 'r')
        data=f.readlines()
        f.close()
        
        self.formvars={'VPN_ENABLE': '',
                       'ONLY_WEB': '',
                       'ICMP_ENABLE':'',
                       'NTP_ENABLE':'',
                       'ports':FW_PORTS,
                        }
        
        for line in data:
            l=line.split('=')[0]
            if l in VARS:
                #self.vars[l]=[VARSTXT[VARS.index(l)], self._clean(line.strip().split('=')[1])]
                self.vars[l]=self._clean(line.strip().split('=')[1])
                self.varsobj[l]=self._clean(line.strip().split('=')[1])
                if l in self.formvars.keys():
                    if self.vars.has_key(l):
                        value=self.vars[l]
                    if value == "1":
                        lg.debug("%s enabled"%(l), __name__)
                        self.formvars[l]=' checked'
                    else:
                        lg.debug("%s disabled '%s'"%(l, value), __name__)
        self.vars['form']=self.formvars

    def save(self, newdata):
        for l in newdata:
            self.varsobj[l]=newdata[l]
        
        f=open(FW_CONF, 'r')
        data=f.readlines()
        f.close()
        
        f=open(FW_CONF, 'w')
        for line in data:
            l=line.split('=')[0]
            if l in VARS:
                f.write("%s=\"%s\"\n" %(l, self.varsobj[l]) )
            else:
                f.write(line)
        f.close()

    def _clean(self, txt):
        txt=txt.replace('"', '')
        txt=txt.replace("'", '')
        return txt

    def restart(self):
        thinfilter.common.run(FW_SCRIPT, _from=__name__)


class firewall(object):
    @thinfilter.common.islogged
    @thinfilter.common.layout(body='', title='Configuración del Cortafuegos')
    def GET(self, options=None):
        fobj=FireWall()
        firewall_vars=fobj.vars
        lg.debug("firewall::GET() firewall=%s" %firewall_vars, __name__)
        return render.firewall(firewall_vars, 'Guardar')

    @thinfilter.common.islogged
    def POST(self):
        fobj=FireWall()
        data=fobj.vars
        formdata=web.input()
        lg.debug("firewall()::formdata=%s"%formdata, __name__)
        #for param in data:
            #lg.debug("firewall::POST() param=%s old=%s"%(param, data[param]), __name__ )
            #lg.debug("firewall::POST() param=%s new=%s"%(param, getattr(formdata, param) ), __name__ )
            #data[param]=getattr(formdata, param)
        #lg.debug("firewall::POST() data=%s"%data, __name__)
        #fobj.save(data)
        #fobj.restart()
        return web.seeother('/firewall')




def init():
    # nothing to check
    lg.debug("firewall::init()", __name__)
    """
        '/firewall',       'firewall',
    """
    thinfilter.common.register_url('/firewall',    'thinfilter.modules.firewall.firewall')
    """
    <li><span class="dir">Cortafuegos</span>
        <ul>
            <li><a href="/firewall">Configuración</a></li>
        </ul>
    </li>
    """
    menu=thinfilter.common.Menu("/firewall", "Cortafuegos")
    thinfilter.common.register_menu(menu)

if __name__ == "__main__":
    thinfilter.config.daemon=False
    thinfilter.config.debug=True
    
    app = FireWall()
    app.restart()
    



