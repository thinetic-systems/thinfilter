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

import os
import sys
import time
import datetime
import traceback

sys.path.append("./")
import thinfilter.config

import thinfilter.common
import thinfilter.db
import thinfilter.logger as lg


def reloadSquid():
    if thinfilter.config.demo:
        lg.debug("reloadSquid() demo mode, doing nothing", __name__)
        time.sleep(2)
        return
    
    # delete all editable files
    sq=squidGuard()
    sq.resetAllTables()
    
    # regenerate lista-negra lista-blanca and servidor/domains files
    for row in sq.all:
        row.toFile()
    
    #save IP in squidGuard.conf
    #FIXME
    
    thinfilter.common.run("squidGuard -c %s -C all"%thinfilter.config.SQUIDGUARD_CONF, verbose=True, _from=__name__)
    #thinfilter.common.run("squidGuard -c %s -u"%thinfilter.config.SQUIDGUARD_CONF, verbose=True, _from=__name__)
    thinfilter.common.run("chown -R proxy:proxy %s"%thinfilter.config.SQUIDGUARD_PATH, verbose=True, _from=__name__)
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


class Expire(str):
    def __init__(self, txt):
        self.printable=self.__printable__()
        self.expired=self.__expired__()
        self=txt
        
    def __printable__(self):
        #print "expire => human %s"%self
        if self != '':
            diff=int(self)-int(time.time())
            a=datetime.timedelta(seconds=diff)
            if a.days > 0:
                return "%s días, %s" %(a.days ,datetime.timedelta(seconds=a.seconds))
            return a
    
    def __expired__(self):
        if self == '':
            return False
        diff=int(self)-int(time.time())
        if diff < 0:
            return True
        return False

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
                 text='', description='', category='1', creator='', 
                 catdescription='', cattext='', expire=''):
        self.id=idfilter
        self.filtertype=String(filtertype)
        self.mode=String(mode)
        self.text=text
        self.description=description
        self.category=category
        self.creator=creator
        self.catdescription=catdescription
        self.cattext=cattext
        self.expire=Expire(expire)


    def delete(self, restart=False):
        sql="DELETE FROM filter WHERE id='%s'"%self.id
        lg.debug("Row:delete() sql='%s'"%sql, __name__)
        try:
            result=thinfilter.db.query(sql)
            lg.debug("Row:new() result=%s"%result)
        except:
            return False
        
        # call to reload squid
        if restart:
            reloadSquid()
        return True

    def save(self, formdata, restart=True):
        try:
            self._save(formdata)
        except Exception, err:
            lg.warning("Row::save() Exception '%s'"%err, __name__)
            traceback.print_exc(file=sys.stderr)
            return "error"
        
        # save in database
        lg.error("Row::save() FIXME save in sqlite", __name__)
        sql="UPDATE filter set text='%s', type='%s', mode='%s', category='%s' WHERE id='%s'"%(self.text, self.filtertype, self.mode, self.category, self.id)
        lg.debug("Row:save() sql='%s'"%sql, __name__)
        result=thinfilter.db.query(sql)
        lg.debug("Row:save() result=%s"%result)
        
        if restart:
            # call to reload squid
            lg.debug("Row::save() reload squid", __name__)
            reloadSquid()
        
        return "ok"

    def new(self, formdata, restart=False):
        """
        <Storage {'domain': u'de.ejemplo', 
                  'url': u'http://url.de.ejemplo/index.html', 
                  'unblock': u'domain', 
                  'timeout': u'1800', 
                  'rulename': u'porn', 
                  'subdomain': u'url.de.ejemplo', 
                  'expression': u''}>
        
        # type =>        urls|domains|expressions
        # mode =>        lista-blanca|lista-negra
        # text =>        the filter
        # description => additional description of filter
        # category =>    id of catfilter, default 1
        """
        if formdata.has_key('unblock'):
            self.filtertype=formdata.unblock
            if formdata.has_key(formdata.unblock):
                self.text=formdata[formdata.unblock]
            if self.filtertype in ['domain','subdomain']:
                self.filtertype='domain'
        # calculate expire
        try:
            if formdata.has_key('timeout'):
                self.expire=int(formdata.timeout)+int(time.time())
        except:
            self.expire=""
        sql="INSERT INTO filter (type,mode,text,category,expire) VALUES ('%s','%s','%s','%s','%s')"%(self.filtertype, self.mode, self.text, self.category, self.expire)
        lg.debug("Row:new() sql='%s'"%sql, __name__)
        try:
            result=thinfilter.db.query(sql)
            lg.debug("Row:new() result=%s"%result)
        except:
            return False
        
        # call to reload squid
        if restart:
            reloadSquid()
        return True

    def _save(self, formdata):
        for key in self.keys():
            if key=='id':
                continue
            if formdata.has_key(key):
                lg.debug("   SAVE [%s] %s => %s"%(key, self[key], formdata[key]), __name__)
                self[key]=formdata[key]
    
    def toFile(self, restart=False):
        fname="%s%s/%s"%(thinfilter.config.SQUIDGUARD_PATH, self.mode, self.filtertype)
        lg.debug("%s => %s"%(self.text, fname), __name__)
        f=open(fname, 'a')
        f.write("%s\n"%self.text)
        f.close()
        
        if restart:
            reloadSquid()

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
        def __init__(self, idfilter=None, filtertype='url', mode='lista-negra', 
             text='', description='', category='', creator='', 
             catdescription='', cattext='', expire=''):
        
        SELECT * from filter INNER JOIN catfilter ON filter.category=catfilter.id;
        id|type|mode|text|description|category|expire|creator|id|description|text|creator
         0  1    2    3        4         5       6      7    8          9    10     11
        """
        sql="SELECT * from filter INNER JOIN catfilter ON filter.category=catfilter.id %s"%(_filter)
        #sql="SELECT id,type,mode,text,description,category FROM filter %s"%(_filter)
        #lg.debug("Table::load() sql=«%s»"%sql, __name__)
        data=thinfilter.db.query(sql)
        if len(data) > 0:
            for line in data:
                self.append( Row(idfilter=line[0], filtertype=line[1], mode=line[2], 
                                 text=line[3], description=line[4], category=line[5], 
                                 expire=line[6], creator=line[8], catdescription=line[9], 
                                 cattext=line[10]) )
    
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

    def getProxyUID(self):
        import pwd
        for user in pwd.getpwall():
            if "proxy" in user:
                return user[2]
        # never here
        return 0

    def getProxyGID(self):
        import pwd
        for user in pwd.getpwall():
            if "proxy" in user:
                return user[3]
        # never here
        return 0

    def __resetFile(self, fname):
        """
        Remove file (and *.db)
        Create and change owner
        """
        #lg.debug("squidGuard::__resetFile => %s"%fname, __name__)
        if os.path.exists(fname):
            os.unlink(fname)
        if os.path.exists(fname + ".db"):
            os.unlink(fname + ".db")
        # create empty
        open(fname, 'w').close()
        # change owner
        os.chown(fname, self.getProxyUID(), self.getProxyGID())

    def resetAllTables(self):
        """
        Clean lista-negra lista-blanca rules
        """
        for rule in thinfilter.config.SQUIDGUARD_EDIT_RULES:
            for sfile in thinfilter.config.SQUIDGUARD_FILES:
                fname="%s/%s/%s"%(thinfilter.config.SQUIDGUARD_PATH, rule, sfile)
                try:
                    self.__resetFile(fname)
                except Exception, err:
                    lg.error("Exception cleaning file %s, error=%s"%(fname, err))
        # set WEB_IP in server
        try:
            fname="%s/servidor/domains"%(thinfilter.config.SQUIDGUARD_PATH)
            f=open(fname, 'w')
            f.write("%s\n"%thinfilter.config.WEB_IP)
            f.close()
        except Exception,err:
            lg.debug("resetAllTables() set server IP as allowed, error %s"%err, __name__)


    def saveAndReload(self):
        # delete all editable files
        self.resetAllTables()
        
        # regenerate lista-negra lista-blanca and servidor/domains files
        for row in self.all:
            row.toFile()
        
        #save IP in squidGuard.conf
        #FIXME
        
        reloadSquid()

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
