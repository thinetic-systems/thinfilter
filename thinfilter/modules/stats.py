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
# stats stuff
#

import sys
import os
import time

import thinfilter.logger as lg
import thinfilter.config

import thinfilter.common
import web
render = web.template.render(thinfilter.config.BASE + 'templates/')

SARG_DIR="/var/www/squid-reports/"

# from /usr/lib/python2.5/BaseHTTPServer.py
def date_time_string(timestamp=None):
    """Return the current date and time formatted for a message header."""
    weekdayname = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']

    monthname = [None,
                 'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
                 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    if timestamp is None:
        timestamp = time.time()
    year, month, day, hh, mm, ss, wd, y, z = time.gmtime(timestamp)
    s = "%s, %02d %3s %4d %02d:%02d:%02d GMT" % (
            weekdayname[wd],
            day, monthname[month], year,
            hh, mm, ss)
    return s


class stats_images:
    def GET(self, sfile, extension):
        #lg.debug("stats_images():GET() sfile=%s extension=%s"%(sfile, extension), __name__)
        absfile=os.path.join(SARG_DIR, "%s%s"%(sfile,extension) )
        #lg.debug("stats_images::GET() SARG_DIR=%s sfile=%s absfile=%s" %(SARG_DIR, sfile, absfile), __name__ )
        if not os.path.isfile( absfile ):
            # return 404
            lg.debug("stats_images() not found '%s'"%absfile, __name__)
            return web.notfound()

        # set headers (javascript, css, or images)
        extension = sfile.split('.')[-1]
        mode='r'
        if extension in thinfilter.config.IMAGE_EXTENSIONS:
            mode='rb'
        # set common headers
        f=open(absfile, mode)
        fs = os.fstat( f.fileno())
        web.header("Expires", date_time_string(time.time()+60*60*2)) # expires in 2 hours
        web.header("Last-Modified", date_time_string(fs.st_mtime))
        web.header("Content-Length", str(fs[6]))
        web.header("Cache-Control", "max-age=3600, must-revalidate") 
        f.close()
        
        web.header('Content-Type', 'image/%s' %(extension) )
        return open( absfile ).read()

class stats(object):
    @thinfilter.common.islogged
    @thinfilter.common.isinrole('stats.stats')
    @thinfilter.common.layout(body='', title='Estadísticas')
    def GET(self, path, extension):
        if path: path=str(path)
        if extension: extension=str(extension)
        lg.debug("stats::GET() path=%s extension=%s" %(path, extension), __name__)
        if extension and extension.replace('.','') in thinfilter.config.IMAGE_EXTENSIONS:
            image_name=path.split('/')[-1]
            return web.seeother("/stats-images/%s%s"%(path, extension) )
            #return web.seeother("/stats-images/images/%s%s"%(image_name, extension) )
            #return images().GET("images/graph.png")
            #return web.notfound()
        fname=None
        data=["<h1 class=\"clear\">Estadísticas</h1>\n"]
        data.append("<div id='menu2'><ul class='dropdown dropdown-horizontal'>")
        data.append("<li><a href='/stats/Daily/'>Diario</a></li>")
        data.append("<li><a href='/stats/Weekly/'>Semanal</a></li>")
        data.append("<li><a href='/stats/Monthly/'>Mensual</a></li>")
        data.append("</ul></div><br class='clear'/>")
        if path.startswith("Daily") or path.startswith("Weekly") or path.startswith("Monthly"):
            # FIXME i18n
            if "Daily" in path: periodo="diario"
            if "Weekly" in path: periodo="semanal"
            if "Monthly" in path: periodo="mensual"
            data.append("<h3 class='center-text'>Periodo %s</h3>"%periodo)
            
            fname="%s/%s/index.html"%(SARG_DIR, path)
            if extension:
                fname="%s/%s%s"%(SARG_DIR, path,extension)
        
        lg.debug("stats() fname=%s"%fname, __name__)
        
        if not fname or not os.path.isfile(fname):
            data.append("<h2 class='center'>404.- Periodo no encontrado</h2>")
            data.append("<small>%s</small>"%fname)
            return "".join(data)
        # read html and parse file
        f=open(fname,'r')
        read=False
        data2=False
        added_table=False
        closed_table=False
        
        for line in f.readlines():
            if line.startswith("<style>"):
                read=True
            elif line.startswith("</style>"):
                data.append(line)
                read=False
            elif line.startswith(".body"):
                continue
            elif "class=\"header\"" in line or "class=\"link\"" in line:
                if not added_table:
                    data.append("<table class='center'>\n")
                    added_table=True
                if "class=\"link\"" in line:
                    line=line.replace("href=\"","href=\"/stats/%s/"%path)
                data.append(line)
                continue
            elif "class=\"data2\"" in line or "class=\"data\"" in line:
                # rewrite link
                newline=line.replace('/index.html','').replace("href='","href='/").replace("href='","href='/stats/%s"%path)
                #lg.debug("stats() line=%s"%line, __name__)
                #lg.debug("stats() newline=%s"%newline, __name__)
                data.append( newline )
                data2=True
                continue
            if data2:
                if not closed_table:
                    data.append("\n</table>")
                    closed_table=True
            if read:
                data.append( line.replace('a:link,a:visited','') )
        
        data.append("<div id='sarg'>Informes generados con <a href='http://sarg.sourceforge.net'>sarg</a></div>")
        return "".join(data)

    @thinfilter.common.islogged
    def POST(self):
        return web.seeother('/stats')


def init():
    # nothing to check
    lg.debug("stats::init()", __name__)
    """
        '/stats/(.+?)(?:(\.[^.]*$)|$)$', 'stats'
        '/stats-images/(.+?)(?:(\.[^.]*$)|$)$', 'stats'
    """
    thinfilter.common.register_url('/stats/(.+?)(?:(\.[^.]*$)|$)$', 'thinfilter.modules.stats.stats')
    thinfilter.common.register_url('/stats-images/(.+?)(?:(\.[^.]*$)|$)$', 'thinfilter.modules.stats.stats_images')

    """
    <li><a href="/stats/Daily/">Accesos</a></li>
    """
    menu=thinfilter.common.Menu("/stats/Daily/", "Registros", order=80, role='stats.stats')
    thinfilter.common.register_menu(menu)
    
    """
    <a class="qbutton" href="/stats/Daily/"><img src="/data/stats.png" alt="Estadísticas"><br/>Estadísticas</a>
    """
    button=thinfilter.common.Button("/stats/Daily/", "Estadísticas", "/data/stats.png")
    thinfilter.common.register_button(button)



