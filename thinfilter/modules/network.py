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
# network stuff
#

import os
import sys
import netifaces
import urllib
import time


import thinfilter.logger as lg
import thinfilter.config

import thinfilter.common
import web
render = web.template.render(thinfilter.config.BASE + 'templates/')




class network(object):
    @thinfilter.common.islogged
    @thinfilter.common.isinrole('network.network')
    @thinfilter.common.layout(body='', title='Configuración Red')
    def GET(self, options=None):
        lg.debug("network::GET() options=%s" %options, __name__)
        ifaces=thinfilter.common.Interfaces().get()
        return render.settings_net(ifaces, action='Guardar')

    @thinfilter.common.islogged
    @thinfilter.common.isinrole('network.network')
    def POST(self):
        ifaces=thinfilter.common.Interfaces().get()
        formdata=web.input()
        lg.debug("formdata=%s"%formdata, __name__)
        for i in range(len(ifaces)):
            iface=ifaces[i]['iface']
        #FIXME not finished
#        netdata=web.input()
#        lg.debug(netdata)
#        _debug = userdata.debug
#        _timeout = userdata.timeout
#        _concurrent = userdata.concurrent
#        lg.debug("debug=%s  timeout=%s  concurrent=%s"%(_debug, _timeout, _concurrent) )
#        try:
#            # set stop=2 to reload conf from daemon
#            #db.query("UPDATE config set debug='%s', timeout='%s', concurrent='%s', stop='2'" %(_debug, _timeout, _concurrent))
#        except Exception, err:
#            lg.error("Exception save config, error=%s"%err)
#            traceback.print_exc(file=sys.stderr)
        return web.seeother('/network')


class DnsMasq(object):
    def __init__(self):
        self.conf="/etc/dnsmasq.conf"
        f=open(self.conf, 'r')
        self.listen_address=""
        self.dhcp_range=""
        self.dhcp_option=""
        self.dns=""
        self.dnsfile=""
        self.rawdata=[]
        for _line in f.readlines():
            self.rawdata.append(_line)
            line=_line.strip()
            if not line == "" and not line.startswith("#"):
                lg.debug("DnsMasq() append line '%s'"%line, __name__)
                if line.startswith("listen-address="):
                    self.listen_address=line.split('=')[1]
                elif line.startswith("dhcp-range="):
                    self.dhcp_range=line.split('=')[1]
                elif line.startswith("dhcp-option="):
                    self.dhcp_option=line.split('=')[1]
                elif line.startswith("resolv-file="):
                    self.dnsfile=line.split('=')[1]
                    self.dns=",".join(self.__read_dns__())

    def __read_dns__(self):
        #resolv-file=/etc/resolv.conf.primary
        f=open(self.dnsfile, 'r')
        dns=[]
        for line in f.readlines():
            if line.startswith("nameserver"):
                dns.append(line.strip().split()[1])
        return dns

    def get(self):
        return {#'listen-address':self.listen_address, 
                'dhcp-range': self.dhcp_range,
                #'dhcp-option': self.dhcp_option,
                'dns': self.dns
                }
        
    def save(self, data):
        f=open(self.conf, 'w')
        for line in self.rawdata:
            if line.startswith("dhcp-range="):
                f.write("dhcp-range=%s\n"%(data['dhcp-range']) )
            #elif line.startswith("listen-address="):
            #    f.write("listen-address=%s\n"%(data['listen-address']) )
            #elif line.startswith("dhcp-option="):
            #    f.write("dhcp-option=%s\n"%(data['dhcp-option']) )
            else:
                f.write(line)
        f.close()
        # save DNS resolv-file=/etc/resolv.conf.primary
        f=open(self.dnsfile, 'w')
        for dns in self.dns.strip().split(','):
            f.write("nameserver %s\n" %(dns) )
        f.close()
        # save /etc/resolv.conf
        f=open("/etc/resolv.conf", 'w')
        f.write("nameserver %s\n"%(thinfilter.config.WEB_IP))
        for dns in self.dns.strip().split(','):
            f.write("nameserver %s\n" %(dns) )
        f.close()
        # restart dnsmasq
        os.system("/usr/sbin/invoke-rc.d dnsmasq restart")
        
class dhcp(object):
    @thinfilter.common.islogged
    @thinfilter.common.isinrole('network.dhcp')
    @thinfilter.common.layout(body='', title='Configuración DHCP')
    def GET(self, options=None):
        lg.debug("dhcp::GET() options=%s" %options, __name__)
        data=DnsMasq().get()
        lg.debug("dhcp::GET() dnsmasq=%s" %data, __name__)
        return render.settings_dhcp(data, action='Guardar')

    @thinfilter.common.islogged
    @thinfilter.common.isinrole('network.dhcp')
    def POST(self):
        dnsmasq=DnsMasq()
        data=dnsmasq.get()
        formdata=web.input()
        lg.debug("dhcp()::formdata=%s"%formdata, __name__)
        for param in data:
            lg.debug("dhcp::POST() param=%s old=%s"%(param, data[param]), __name__ )
            lg.debug("dhcp::POST() param=%s new=%s"%(param, getattr(formdata, param.replace('_','-')) ), __name__ )
            data[param]=getattr(formdata, param.replace('_','-'))
        lg.debug("dhcp::POST() data=%s"%data, __name__)
        if not thinfilter.config.demo:
            dnsmasq.save(data)
        return web.seeother('/network/dhcp')

class netStats(object):
    def __init__(self):
        self.ifaces=[]
        for dev in thinfilter.common.Interfaces().get():
            if not dev['iface'] in thinfilter.config.HIDDEN_INTERFACES:
                tx_and_rx=self.__get_data__(dev)
                
                self.ifaces.append(tx_and_rx)

    def __get_data__(self, _dev):
        #lg.debug("netStats::__get_data__() _dev=%s"%_dev, __name__)
        data={'iface':_dev['iface'], 'link':_dev['link'], 'gateway':_dev['gateway'], 'tx':0, 'rx':0}
        dev=_dev['iface']
        f=open("/proc/net/dev", 'r')
        for line in f.readlines():
            if "%s:"%dev in line:
                tx=int(line.split()[9]) or 0
                rx=line.split()[0].replace("%s:"%dev, "")
                if rx == "":
                    rx=int(line.split()[1])
                data['tx']="%.2f MiB" %( float(tx)/(1024*1024) )
                data['rx']="%.2f MiB" %( float(rx)/(1024*1024) )
        return data

    def get(self):
        #lg.debug("netStats::get() self.ifaces=%s"%self.ifaces, __name__)
        return self.ifaces




class extraStats(object):
    def __init__(self):
        raw=open("/proc/uptime", 'r').readline()
        self.uptime=self.fractSec(float(raw.split()[0]))
        self.public_ip=self.__get_public_ip__()

    def fractSec(self, s):
        years, s = divmod(s, 31556952)
        _min, s = divmod(s, 60)
        h, _min = divmod(_min, 60)
        d, h = divmod(h, 24)
        txtdate=""
        if int(years) > 0:
            txtdate+="%s años, "%int(years)
        txtdate+="%s días %s horas %s minutos %s segundos" %( int(d), int(h), int(_min), int(s))
        return txtdate

    def __get_public_ip__(self):
        try:
            raw = urllib.urlopen("http://thinetic.com/ip.php?id=thinfilter", proxies={})
            public_ip=raw.readline().strip()
            raw.close()
            return public_ip
        except:
            return "[no disponible]"
        

    def get(self):
        return [self.uptime, self.public_ip]




class netstats(object):
    @thinfilter.common.islogged
    @thinfilter.common.isinrole('network.netstats')
    @thinfilter.common.layout(body='', title='Estadísticas de red')
    def GET(self, options=None):
        data=netStats().get()
        extra=extraStats().get()
        lg.debug("netstats::GET() dnsmasq=%s" %data, __name__)
        lg.debug("netstats::GET() extra=%s" %extra, __name__)
        return render.net_stats(data, extra)

    @thinfilter.common.islogged
    def POST(self):
        return web.seeother('/network/stats')



class netgraph(object):
    #@thinfilter.common.islogged
    def GET(self, sfile):
        sfile=str(sfile)
        from thinfilter.statcreator import Net, CPU
        lg.debug("netgraph()::GET sfile=%s"%sfile, __name__)
        if "eth" in sfile or "br" in sfile or "tun" in sfile:
            app=Net(iface=str(sfile.split('.')[0]))
            app.graph()
        elif "cpu" in sfile:
            app=CPU()
            app.graph()
        else:
            return web.notfound()
        web.header("Expires", thinfilter.common.date_time_string(time.time()+60*5)) # expires in 5 minutes
        web.header("Cache-Control", "max-age=300, must-revalidate") 
        web.header('Content-Type', 'image/png')
        lg.debug("netgraph::GET() fname=%s.png" %app.fname, __name__)
        return open(str(app.fname + ".png") ).read()


def init():
    # nothing to check
    lg.debug("network::init()", __name__)
    """
        '/network', 'network',
        '/network/dhcp', 'dhcp',
        '/network/stats', 'netstats',
    """
    thinfilter.common.register_url('/network',      'thinfilter.modules.network.network')
    thinfilter.common.register_url('/network/dhcp',  'thinfilter.modules.network.dhcp')
    thinfilter.common.register_url('/network/stats', 'thinfilter.modules.network.netstats')
    thinfilter.common.register_url('/network/netgraph/([a-zA-Z0-9-:.]*)', 'thinfilter.modules.network.netgraph')

    # register menus
    """
    <li><span class="dir">Red</span>
        <ul>
            <li><a href="/network">Configuración</a></li>
            <li><a href="/network/dhcp">DHCP</a></li>
            <li><a href="/network/stats">Estadísticas</a></li>
        </ul>
    </li>
    """
    menu=thinfilter.common.Menu("", "Red", order=10)
    menu.appendSubmenu("/network", "Configuración", role='network.network')
    menu.appendSubmenu("/network/dhcp", "DHCP", role='network.dhcp')
    menu.appendSubmenu("/network/stats", "Estadísticas", role='network.netstats')
    thinfilter.common.register_menu(menu)
    
    thinfilter.common.register_role_desc('network.network', "Configurar parámetros de red")
    thinfilter.common.register_role_desc('network.dhcp', "Configurar servicio DHCP")
    thinfilter.common.register_role_desc('network.netstats', "Ver tráfico de red")
    
    """
    <a class="qbutton" href="/network"><img src="/data/network.png" alt="Red"><br/>Configuración de Red</a>
    """
    button=thinfilter.common.Button("/network", "Configuración de Red", "/data/network.png")
    thinfilter.common.register_button(button)



