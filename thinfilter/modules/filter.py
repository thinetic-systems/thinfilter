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
import re
import base64
import pickle

import thinfilter.logger as lg
import thinfilter.config
import thinfilter.common
import thinfilter.squidguard


import web
render = web.template.render(thinfilter.config.BASE + 'templates/')

EDIT_RULES=['lista-blanca', 'lista-negra']
FILES=['domains', 'urls', 'expressions']
PATH="/usr/share/squidGuard/db/"
SQUIDGUARD_CONF="/etc/squid3/squidGuard.conf"
SQUIDGUARD_ALLRULES=["servidor", "lista-blanca", "!lista-negra", 
                     "!drugs", "!aggressive", "!hacking", "!proxy",
                     "!mail", "!warez","!violence","!porn","!audio-video",
                     "!ads","gambling","all"]

class Reason(thinfilter.common.Base):
    def __repr__(self):
        return '<Reason ' + dict.__repr__(self) + '>'
    def __init__(self, domains='', subdomains='', expressions=''):
        self.domains=domains
        self.subdomains=subdomains
        self.expressions=expressions

def encode(obj):
    return base64.urlsafe_b64encode(pickle.dumps(obj))

def decode(txt):
    return pickle.loads(base64.urlsafe_b64decode(str(txt)))

class InfoScreen(thinfilter.common.Base):
    def __init__(self, formdata):
        """
        redirect stop?url=%u&addr=%a&clientname=%n&clientident=%i&srcclass=%s&targetclass=%t
        """
        self.formdata=formdata
        self.info=None
        if formdata.has_key('url'):
            self.url=formdata.url
        elif formdata.has_key('urlbase64'):
            self.url=base64.urlsafe_b64decode(str(formdata.urlbase64))
        self.clientname=''
        self.clientident=''
        self.srcclass=''
        self.targetclass=''
        self.src=''
        self.reason=Reason()
        
        self.__set('clientname')
        self.__set('clientident')
        self.__set('srclass')
        self.__set('targetclass')
        self.__set('src')
        
        try:
            # encode && decode to safe base64 encoding
            self.urlbase64=base64.urlsafe_b64encode(unicode(self.url).encode("utf-8")).encode("utf-8")
        except:
            pass
        
        del(self.formdata)
        
        try:
            self.__load()
        except Exception, err:
            lg.debug("InfoScreen exception err=%s"%err)
        
        # convert reason object => pickle => base64
        self.reason=encode(self.reason)
        #print decode(self.reason)

    def __set(self, varname):
        if self.formdata.has_key(varname):
            setattr(self, varname, getattr(self.formdata, varname))

    def __load(self):
        subdomain=self.url.split('/')[2]
        sql="SELECT type,text,description,category FROM filter WHERE mode='lista-negra' and text LIKE '%%%s%%'"%(subdomain)
        #lg.debug("__load()::subdomain sql=%s"%sql, __name__)
        data=thinfilter.db.query(sql)
        if len(data) > 0:
            # subdomain found
            lg.debug("subdomain '%s' found"%subdomain, __name__)
            self.info=self.get_catdesc(data[0][3], data[0][2])
            self.reason.subdomains=subdomain
            return
        
        domain=".".join(self.url.split('/')[2].split('.')[-2:])
        sql="SELECT type,text,description,category FROM filter WHERE mode='lista-negra' and text LIKE '%%%s%%'"%(domain)
        #lg.debug("__load()::domain sql=%s"%sql, __name__)
        data=thinfilter.db.query(sql)
        if len(data) > 0:
            # domain found
            lg.debug("domain '%s' found"%domain, __name__)
            self.info=self.get_catdesc(data[0][3], data[0][2])
            self.reason.domains=domain
            return
        
        # search in regexp
        #re.search('(tuent)', url).group()
        sql="SELECT type,text,description,category FROM filter WHERE mode='lista-negra' and type='expressions'"
        lg.debug("__load()::regexp sql=%s"%sql, __name__)
        data=thinfilter.db.query(sql)
        if len(data)>0:
            for line in data:
                #print line
                #print re.search(line[1], self.url)
                if re.search(line[1], self.url):
                    # FOUND
                    self.info=self.get_catdesc(line[3])
                    self.reason.expressions=line[1]
                    return
        
        self.info=self.get_default_desc()
        #print data

    def get_catdesc(self, catid, desc=''):
        if desc != '':
            return desc
        sql="SELECT text FROM catfilter WHERE id='%s'"%(catid)
        lg.debug("get_catdesc() sql=%s"%sql, __name__)
        data=thinfilter.db.query(sql)
        if len(data) > 0:
            return data[0][0]
        return self.get_default_desc()

    def get_default_desc(self):
        sql="SELECT text FROM catfilter WHERE description='default'"
        data=thinfilter.db.query(sql)
        if len(data) > 0:
            return data[0][0]
        return ""

class FormData(thinfilter.common.Base):
    def __repr__(self):
        return '<Formdata ' + dict.__repr__(self) + '>'
        
    def __init__(self, data):
        self.url='desconocida'
        self.src='10.0.0.1:9090'
        try:
            self.__load(data)
        except:
            pass

    def __load(self, data):
        __data=data['src'].split()
        self.src=__data[0]
        self.addr=__data[1].split('=')[1]
        self.clientname=__data[2].split('=')[1]
        self.clientident=__data[3].split('=')[1]
        self.srcclass=__data[4].split('=')[1]
        self.targetclass=__data[5].split('=')[1]
        self.url=__data[6].split('=',1)[1]
        for key in data:
            if key != 'src':
                if not data[key]:
                    continue
                self.url+="&%s=%s"%(key, data[key])


class stop(object):
    def GET(self, options=None):
        formdata=web.input()
        # redirect http://10.0.0.1:9090/stop?src=10.0.0.1:9090+addr=%a+clientname=%n+clientident=%i+srcclass=%s+targetclass=%t+url=%u
        # <Storage {'src': u'10.0.0.1:9090 addr=10.0.0.2 clientname= clientident= srcclass=default targetclass=lista-negra url=http://images.google.es/images?hl=es', 'aq': u'f', 'btnG': None, 'gbv': u'1', 'source': u'hp', 'q': u'porn', 'ie': u'ISO-8859-1', 'oq': u''}>
        data=FormData(formdata)
        
        #print formdata
        #if not formdata.has_key('url'):
        #    formdata.url='desconocida'
        screen=InfoScreen(data)
        #print screen
        return render.stop(screen, 'Guardar')

################################################################################

class Rules(thinfilter.common.Base):
    def __repr__(self):
        return '<Filter::Rules ' + dict.__repr__(self) + '>'
    
    def __init__(self, formdata=None):
        self.editable=EDIT_RULES
        self.rules=[]
        self.rulecontent={}
        self.rulename=''
        self.squidguard=self.__load_squidGuard()
        for path in glob.glob(PATH + "*"):
            if os.path.isdir(path):
                if not os.path.basename(path) in EDIT_RULES and not os.path.basename(path) == 'servidor':
                    self.rules.append( os.path.basename(path) )
        #print self.rules
        if formdata and formdata.has_key('rule'):
            self.__load(formdata.rule)
            self.rules=[]
            self.rulename=formdata.rule
        
    def __load(self, rule):
        path=os.path.join(PATH, rule)
        # load domains expressions and urls
        self.rulecontent[rule]={}
        for f in FILES:
            self.rulecontent[rule][f]=self.__load_file(os.path.join(path, f))

    def __load_file(self, fname):
        if not os.path.isfile(fname):
            return ""
        data=[]
        f=open(fname, 'r')
        for line in f.readlines():
            if line.strip() != '' and not line.startswith('#'):
                data.append(line.strip())
        f.close()
        return "\n".join(data)



    def save(self, formdata):
        path=os.path.join(PATH, formdata.rulename)
        for f in FILES:
            self.__save_file(os.path.join(path, f), formdata[f])


    def __save_file(self, fname, data):
        f=open(fname, 'w')
        for line in data.split('\n'):
            f.write(line + "\n")
        f.close()

    def reloadSquid(self):
        thinfilter.common.run("squidGuard -c %s -C all"%SQUIDGUARD_CONF, verbose=True, _from=__name__)
        thinfilter.common.run("squidGuard -c %s -u"%SQUIDGUARD_CONF, verbose=True, _from=__name__)
        thinfilter.common.run("chown -R proxy:proxy %s"%PATH, verbose=True, _from=__name__)
        thinfilter.common.run("chown -R proxy:proxy /var/log/squid3/*", verbose=True, _from=__name__)
        thinfilter.common.run("squid3 -k reconfigure || /etc/init.d/squid3 restart", verbose=True, _from=__name__)
        
    def __load_squidGuard(self):
        """
        >>> a="pass servidor lista-blanca !lista-negra !drugs !aggressive !hacking !proxy !mail !warez !violence !porn !audio-video !ads !gambling all"
        >>> a.split()
        ['pass', 'servidor', 'lista-blanca', '!lista-negra', '!drugs', '!aggressive', '!hacking', '!proxy', '!mail', '!warez', '!violence', '!porn', '!audio-video', '!ads', '!gambling', 'all']
        """
        data=""
        rules={'blocked':[], 'pass':[]}
        if not os.path.isfile(SQUIDGUARD_CONF):
            return rules
        f=open(SQUIDGUARD_CONF, 'r')
        for line in f.readlines():
            if line.strip().startswith('pass '):
                data=line.strip().split()
        f.close()
        for rule in data:
            if rule in ['pass', 'all']: continue
            if rule.startswith('!'):
                rules['blocked'].append(rule.replace('!',''))
            else:
                rules['pass'].append(rule)
        return rules

    def saveSquidGuard(self, formdata):
        newblocked=[]
        for rule in self.squidguard['blocked']:
            lg.debug(rule, __name__)
            if formdata.has_key(rule):
                newblocked.append(rule)
        self.squidguard['blocked']

class admin(object):
    @thinfilter.common.islogged
    @thinfilter.common.isinrole('filter.admin')
    @thinfilter.common.layout(body='', title='Configuración de reglas de filtrado')
    def GET(self):
        rules=Rules()
        return render.filter_admin(rules, 'Guardar')

    @thinfilter.common.islogged
    @thinfilter.common.isinrole('filter.admin')
    def POST(self):
        formdata=web.input()
        if not thinfilter.config.demo:
            rules=Rules().saveSquidGuard(formdata)
        return web.seeother('/stop/admin')

################################################################################


class edit(object):
    @thinfilter.common.islogged
    @thinfilter.common.isinrole('filter.admin')
    @thinfilter.common.layout(body='', title='Configuración de las pantallas de bloqueo')
    def GET(self):
        formdata=web.input()
        sg=thinfilter.squidguard.squidGuard()
        if not formdata.has_key('rule'):
            rules=sg.getargs()
            formdata['rule']=""
        else:
            rules=sg.getargs(mode=formdata.rule)
        categories=thinfilter.squidguard.Categories()
        return render.filter_edit(rules, formdata.rule, categories, 'Guardar')

    @thinfilter.common.islogged
    @thinfilter.common.isinrole('filter.admin')
    def POST(self):
        formdata=web.input()
        a=thinfilter.squidguard.squidGuard()
        x=a.getid(formdata.id)
        if not thinfilter.config.demo:
            result=x.save(formdata)
        else:
            result="error, modo demo"
        return result
################################################################################

class TestFilter(thinfilter.common.Base):
    def __repr__(self):
        return '<TestFilter ' + dict.__repr__(self) + '>'
    def __init__(self, formdata):
        self.url=formdata.url
        self.blocked=False
        self.reason=''
        out=thinfilter.common.run("echo '%s 10.0.0.1 - GET' | squidGuard -c %s 2>&1" %(self.url, SQUIDGUARD_CONF), verbose=True, _from=__name__)
        for line in out:
            if "stop?src" in line:
                self.blocked=True
                for varname in line.split('+'):
                    if "targetclass" in varname:
                        self.reason=varname.split('=')[1]

class test(object):
    @thinfilter.common.islogged
    @thinfilter.common.isinrole('filter.admin')
    @thinfilter.common.layout(body='', title='Configuración de las pantallas de bloqueo')
    def GET(self):
        return render.filter_test()

    @thinfilter.common.islogged
    @thinfilter.common.isinrole('filter.admin')
    def POST(self):
        """
        call this command
        echo "$URL 10.0.0.1 - GET" | squidGuard -c /etc/squid3/squidGuard.conf
        
        @result = empty no blocked
                = not empty retunr 2 line, redirect ULR and original call
        """
        formdata=web.input()
        testobj=TestFilter(formdata)
        return render.filter_test_result(testobj)


class UnblockFilter(thinfilter.common.Base):
    def __repr__(self):
        return '<UnblockFilter ' + dict.__repr__(self) + '>'
    def __init__(self, formdata):
        if formdata.has_key('urlbase64'):
            self.url=base64.urlsafe_b64decode(str(formdata.urlbase64))
        else:
            self.url=formdata.url
        self.htmlurl=self.url
        self.rule=formdata.rule
        self.done=0
        if formdata.has_key('done'):
            self.done=formdata.done
        
        self.reason=Reason()
        if formdata.has_key('reason'):
            self.reason=decode(formdata.reason)
        
        if self.reason.expressions != '':
            c=re.search(self.reason.expressions, self.url)
            self.htmlurl=self.url[:c.start()]+ "<span class='match'>" +self.url[c.start():c.end()] + "</span>" + self.url[c.end():]
        elif self.reason.domains != '':
            c=re.search(self.reason.domains, self.url)
            self.htmlurl=self.url[:c.start()]+ "<span class='match'>" +self.url[c.start():c.end()] + "</span>" + self.url[c.end():]
        elif self.reason.subdomains != '':
            c=re.search(self.reason.subdomains, self.url)
            self.htmlurl=self.url[:c.start()]+ "<span class='match'>" +self.url[c.start():c.end()] + "</span>" + self.url[c.end():]
        
        # search for subdomain and domain
        self.subdomain=self.url.split('/')[2]
        self.domain=".".join(self.url.split('/')[2].split('.')[-2:])
        if self.subdomain == self.domain:
            self.subdomain=None

class unblock(object):
    @thinfilter.common.islogged
    @thinfilter.common.isinrole('filter.unblock')
    @thinfilter.common.layout(body='', title='Configuración de las pantallas de bloqueo')
    def GET(self):
        formdata=web.input()
        lg.debug(formdata, __name__)
        data=UnblockFilter(formdata)
        lg.debug(data, __name__)
        # formdata have url and rule vars
        return render.filter_unblock(data, 'Desbloquear')

    @thinfilter.common.islogged
    @thinfilter.common.isinrole('filter.unblock')
    def POST(self):
        formdata=web.input()
        lg.debug(formdata, __name__)
        #FIXME
        return web.seeother('/stop/admin/unblock?done=1&rule=%s&url=%s'%(formdata.rulename, formdata.url))

################################################################################

class Categories(list):
    def __init__(self, formdata):
        self.edit=False
        if formdata.has_key('id'):
            if int(formdata.id) == 0:
                self.edit=True
                self.append(thinfilter.squidguard.Cat())
            for cat in thinfilter.squidguard.Categories():
                if cat.id == int(formdata.id):
                    self.append(cat)
                    self.edit=True
                    return
        else:
            for cat in thinfilter.squidguard.Categories():
                self.append(cat)

class categories(object):
    @thinfilter.common.islogged
    @thinfilter.common.isinrole('filter.admin')
    @thinfilter.common.layout(body='', title='Configuración de las pantallas de bloqueo')
    def GET(self):
        formdata=web.input()
        data=Categories(formdata)
        #print data
        if data.edit:
            return render.filter_cat_edit(data[0])
        return render.filter_cat(data)

    @thinfilter.common.islogged
    @thinfilter.common.isinrole('filter.admin')
    def POST(self):
        formdata=web.input()
        lg.debug(formdata, __name__)
        data=thinfilter.squidguard.Categories().getid(formdata.id)
        if not thinfilter.config.demo:
            data.save(formdata)
        #FIXME
        return web.seeother('/stop/admin/categories')


def init():
    # nothing to check
    lg.debug("filter::init()", __name__)
    
    thinfilter.common.register_url('/stop',            'thinfilter.modules.filter.stop')
    thinfilter.common.register_url('/stop/admin',      'thinfilter.modules.filter.admin')
    thinfilter.common.register_url('/stop/admin/edit', 'thinfilter.modules.filter.edit')
    thinfilter.common.register_url('/stop/admin/test', 'thinfilter.modules.filter.test')
    thinfilter.common.register_url('/stop/admin/unblock', 'thinfilter.modules.filter.unblock')
    thinfilter.common.register_url('/stop/admin/categories',      'thinfilter.modules.filter.categories')
    
    
    
    menu=thinfilter.common.Menu("", "Filtros", order=60)
    menu.appendSubmenu("/stop?src=10.0.0.1:9090+addr=+clientname=+clientident=+srcclass=+targetclass=lista-negra+url=http://url.de.ejemplo/index.html", "Ver pantalla", role='filter.admin')
    menu.appendSubmenu("/stop/admin", "Configurar filtros", role='filter.admin')
    menu.appendSubmenu("/stop/admin/categories", "Categorías", role='filter.admin')
    menu.appendSubmenu("/stop/admin/test", "Probar filtros", role='filter.admin')
    thinfilter.common.register_menu(menu)
    
    thinfilter.common.register_role_desc('filter.admin', "Configurar pantalla de bloqueo")
    thinfilter.common.register_role_desc('filter.unblock', "Añadir/desbloquear reglas")
    #FIXME in init() generate/load rules to/from squidGuard/db files
    app=Rules()


