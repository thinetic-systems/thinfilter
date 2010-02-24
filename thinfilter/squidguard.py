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

# squidGuard rules

import sys
import time
import traceback

sys.path.append("./")
import thinfilter.config

import thinfilter.common
import thinfilter.db
import thinfilter.logger as lg

SQUIDGUARD_CONF="/etc/squid3/squidGuard.conf"
SQUIDGUARD_PATH="/usr/share/squidGuard/db/"

def reloadSquid():
    if thinfilter.config.demo:
        time.sleep(2)
        return
    thinfilter.common.run("squidGuard -c %s -C all"%SQUIDGUARD_CONF, verbose=True, _from=__name__)
    thinfilter.common.run("squidGuard -c %s -u"%SQUIDGUARD_CONF, verbose=True, _from=__name__)
    thinfilter.common.run("chown -R proxy:proxy %s"%SQUIDGUARD_PATH, verbose=True, _from=__name__)
    thinfilter.common.run("chown -R proxy:proxy /var/log/squid3/*", verbose=True, _from=__name__)
    thinfilter.common.run("squid3 -k reconfigure || /etc/init.d/squid3 restart", verbose=True, _from=__name__)
        
class DB2files(object):
    def __init__(self):
        pass
    
    def save(self, mode):
        # read from SQL and generate files
        alllines=BlackTable()
        for line in alllines:
            line.toFile()





###############################################################################

TRANSLATE_STR={
            'urls':'Dirección URL',
            'domains':'Dominio',
            'expressions':'Expresión regular',
            
            'lista-negra':'Bloquear',
            'lista-blanca':'Permitir',
              }

class String(str):
    def __init__(self, txt):
        self.printable=self.__printable__()
        self=txt
    def __printable__(self):
        if self in TRANSLATE_STR:
            return TRANSLATE_STR[self]
        else:
            return self

###############################################################################


class Cat(thinfilter.common.Base):
    def __repr__(self):
        return 'Cat ' + dict.__repr__(self)
    def __init__(self, idcat=0, description='', text='', creator=''):
        self.id=int(idcat)
        self.description=description
        self.text=text.replace('<br/>', '\n')
        self.creator=creator
    
    def save(self, formdata):
        try:
            self._save(formdata)
        except Exception, err:
            lg.warning("Cat::save() Exception '%s'"%err, __name__)
            traceback.print_exc(file=sys.stderr)
            return "error"
        
        # change '\n' => <br/>
        self.text=self.text.replace('\r\n', '<br/>').replace('\n', '<br/>')
        
        if self.id == 0:
            sql="INSERT INTO filter (description,text,creator) VALUES('%s','%s','%s')"%(self.description, self.text, self.creator)
        else:
            sql="UPDATE filter set description='%s', text='%s', creator='%s' WHERE id='%s'"%(self.description, self.text, self.creator, self.id)
        lg.debug("Cat::save() sql=«%s»"%sql, __name__)
        thinfilter.db.query(sql)
        
        
    def _save(self, formdata):
        for key in self.keys():
            if key=='id':
                continue
            if formdata.has_key(key):
                lg.debug("   SAVE [%s] %s => %s"%(key, self[key], formdata[key]), __name__)
                self[key]=formdata[key]


class Categories(list):
    def __repr__(self):
        rep=''
        for item in self:
            rep+="   %s\n"%item
        
        return 'Categories \n' + rep
    
    def __init__(self):
        sql="SELECT id,description,text,creator FROM catfilter"
        data=thinfilter.db.query(sql)
        for line in data:
            self.append(Cat(idcat=line[0], description=line[1], text=line[2], creator=line[3]))
    
    def getid(self, catid):
        lg.debug("Categories()::getid(%s)"%catid, __name__)
        if int(catid) == 0:
            # new category
            return Cat()
        for line in self:
            if line.id == int(catid):
                return line

###############################################################################
class Row(thinfilter.common.Base):
    def __repr__(self):
        return 'Row ' + dict.__repr__(self)
    
    def __init__(self, idfilter=None, filtertype='url', mode='lista-negra', 
                 text='', description='', category='', creator='', 
                 catdescription='', cattext=''):
        self.id=idfilter
        self.filtertype=String(filtertype)
        self.mode=String(mode)
        self.text=text
        self.description=description
        self.category=category
        self.creator=creator
        self.catdescription=catdescription
        self.cattext=cattext
    
    def _delete(self):
        pass

    def save(self, formdata):
        try:
            self._save(formdata)
        except Exception, err:
            lg.warning("Row::save() Exception '%s'"%err, __name__)
            traceback.print_exc(file=sys.stderr)
            return "error"
        
        # save in database
        lg.error("Row::save() FIXME save in sqlite", __name__)
        sql="UPDATE filter set text='%s', filtertype='%s', mode='%s' WHERE id='%s'"%(self.text, self.filtertype, self.mode, self.id)
        lg.debug(sql, __name__)
        
        # generate files DB => squidGuard/db/*****
        lg.error("Row::save() FIXME save in files", __name__)
        a=DB2files()
        a.save(self.mode)
        
        
        # call to reload squid
        lg.error("Row::save() FIXME reload squid", __name__)
        reloadSquid()
        
        return "ok"

    def _save(self, formdata):
        for key in self.keys():
            if key=='id':
                continue
            if formdata.has_key(key):
                lg.debug("   SAVE [%s] %s => %s"%(key, self[key], formdata[key]), __name__)
                self[key]=formdata[key]
    
    def toFile(self):
        fname="%s%s/%s"%(SQUIDGUARD_PATH, self.mode, self.filtertype)
        lg.debug(" 2FILE %s => %s"%(fname, self.text), __name__)

###############################################################################
class Table(list):
    def __repr__(self):
        rep=''
        for item in self:
            rep+="   %s\n"%item
        
        return self._desc + ' \n' + rep
    
    def __init__(self):
        self._desc="Table"
        self._load()
    
    def _load(self, _filter):
        """
        SELECT * from filter INNER JOIN catfilter ON filter.category=catfilter.id;
        id|type|mode|text|description|category|creator|id|description|text|creator
         0  1    2    3        4         5       6      7    8          9    10
        """
        sql="SELECT * from filter INNER JOIN catfilter ON filter.category=catfilter.id %s"%(_filter)
        #sql="SELECT id,type,mode,text,description,category FROM filter %s"%(_filter)
        #lg.debug("Table::load() sql=«%s»"%sql, __name__)
        data=thinfilter.db.query(sql)
        if len(data) > 0:
            for line in data:
                self.append( Row(line[0], line[1], line[2], line[3], line[4], line[5], line[6], line[8], line[9]) )
    
    def add(self, line):
        if len(line) == 4:
            self.append(Row(line[0], line[1], line[2], line[3], line[4]))
        else:
            assert "Can't add data"

    def delete(self, **kwargs):
        toremove=[]
        
        for i in range(len(self)):
            obj=self[i]
            #print "  OBJ =>", obj
            for key in kwargs.keys():
                #print "   KEY =>", key
                if obj.has_key(key) and obj[key] == kwargs[key]:
                    toremove.append(i)
                    break
        
        toremove.reverse()
        for i in toremove:
            self.pop(i)
        if len(toremove) > 0:
            return True
        return False
    

###############################################################################

class BlackTable(Table):
    _desc="BlackTable"
    def __init__(self):
        self._desc="BlackTable"
        self._load("WHERE filter.mode='lista-negra'")

class WhiteTable(Table):
    def __init__(self):
        self._desc="WhiteTable"
        self._load("WHERE filter.mode='lista-blanca'")

###############################################################################

class squidGuard(thinfilter.common.Base):
    def __repr__(self):
        rep=''
        for item in [self.white, self.black]:
            rep+="   %s\n"%item
        
        return 'squidGuard: \n' + rep
    
    def __init__(self):
        self.white=WhiteTable()
        self.black=BlackTable()
        self.categories=Categories()
        self.all=self.white+self.black
    
    def getid(self, filterid):
        lg.debug("squidGuard()::getid(%s)"%filterid, __name__)
        for line in self.all:
            lg.debug("squidGuard()::getid()   ==> %s"%line.id, __name__)
            if line.id == int(filterid):
                return line

    def getargs(self, **kwargs):
        lg.debug("squidGuard::getargs() ==> %s"%kwargs, __name__)
        found=[]
        if len(kwargs) < 1:
            for line in self.all:
                line.catinfo=self.categories.getid(line.category)
                found.append(line)
            return found
        
        for line in self.all:
            foundcount=0
            for key in kwargs:
                if not line.has_key(key):
                    lg.warning("squidGuard::getargs() UPPSSSSSS key '%s' not found in object '%s'"%(key, line.keys()))
                    break
                elif line[key] == kwargs[key]:
                    foundcount+=1
                if len(kwargs) == foundcount:
                    line.catinfo=self.categories.getid(line.category)
                    found.append(line)
                
        return found


if __name__=='__main__':
    pass
    #a=squidGuard()
    #x=a.getid(1)
    #x.save(description='fooo', filtertype='url')
    #print a
    
    #w=a.getargs()
    #print w
    #print w[0].filtertype
    #print w[0].filtertype.printable
    #print w[0].mode
    #print w[0].mode.printable
    
    #s=String('url')
    #print s
    #print s.printable

    #a=Categories()
    #print a.getid(2)
