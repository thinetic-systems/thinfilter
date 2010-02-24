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

import os
import sys
import re
import thinfilter.logger as lg
import thinfilter.config
import thinfilter.common
import time

from pysqlite2 import dbapi2 as sqlite3
sqlite3.enable_callback_tracebacks(True)

import threading
mutex = threading.Lock()


class Sqlite3(object):
    def __init__(self, db=None):
        #lg.debug("Sqlite3():: init dbname=%s"%db, __name__)
        self.db=db
    def run(self, sql, exe=False):
        if self.db is None:
            return
        con = sqlite3.connect(self.db)
        con.isolation_level = None
        cursor = con.cursor()
        cursor.execute(sql)
        result=[]
        if not exe:
            for row in cursor: result.append(row)
        
        # lock
        mutex.acquire()
        con.commit()
        # unlock
        mutex.release()
        
        cursor.close()
        con.close()
        return result
    
    def select(self, sql):
        return self.run(sql)
    
    def execute(self, sql):
        self.run(sql, exe=True)

    def close(self, *args):
        lg.debug("    close called", __name__)




__sql__=Sqlite3(thinfilter.config.DBNAME)



def connect():
    raise "connect() called and not needed"

def query(_sql, silent=True):
    if not silent: lg.debug("query() sql=%s" %_sql, __name__)
    lg.debug("query() sql=%s" %_sql, __name__)
    if "SELECT" in _sql or "select" in _sql:
        _res=__sql__.select(_sql)
    else:
        _res=__sql__.execute(_sql)
    result=[]
    if _res:
        for f in _res:
            result.append(f)
    if not silent: lg.debug("query() sql='%s' result='%s'" %(_sql, result) , __name__)
    return result

def clean(value):
    sanitized =re.sub(r'[^A-Za-z0-9_. ñÑáéíóúÁÉÍÓÚ$€]+|^\.|\.$|^ | $|^$', '', value)
    if value != sanitized:
        lg.warning("UNSANITIZED data=#%s#"%value, __name__)
    return sanitized

def create_db():
    lg.debug("Creating tables...", __name__)
    query("""CREATE TABLE filter (id INTEGER PRIMARY KEY AUTOINCREMENT,
                                 type TEXT, 
                                 mode TEXT, 
                                 text TEXT, 
                                 description TEXT,
                                 category INT,
                                 creator TEXT) """)
    # type urls|domains|expressions
    # mode lista-blanca|lista-negra
    # text the filter
    # description additional description of filter
    # category
    #
    query("INSERT INTO filter VALUES (1, 'domains', 'lista-negra', 'tuenti.es', '', 2, 'thinfilter')")
    query("INSERT INTO filter VALUES (2, 'expressions', 'lista-negra', '(sex)', '', 3, 'thinfilter')")
    
    
    query("""CREATE TABLE catfilter (id INTEGER PRIMARY KEY AUTOINCREMENT,
                                     description TEXT,
                                     text TEXT,
                                     creator TEXT) """)
    query("INSERT INTO catfilter VALUES (1, 'default', 'Estás en un ordenador de un Centro Educativo.\n<br/>La página que pretendes ver ha sido considerada por el Colegio como no adecuada de visitar en horario lectivo.\n<br/>Si deseas información de porqué ha sido así, pídesela a tu profesor.', 'thinfilter')""")
    query("INSERT INTO catfilter VALUES (2, 'redes sociales', 'Cuando te conectes a Internet siempre has de tener claro cuando hacerlo para el estudio o el trabajo, y cuando para el ocio personal.\n<br/><br/>La página que pretendes ver es para el ocio personal, y no es momento de hacerlo cuando estés en clase.\n<br/><br/>No olvides que en las Redes Sociales hay que ser prudente con a quién otorgas la categoría de «amigo» y muy cuidadoso con la cantidad y el tipo de fotos que cuelgues: siempre dicen mucho de ti', 'thinfilter')""")
    query("INSERT INTO catfilter VALUES (3, 'contenido adulto', 'La página que se pretende visualizar no es aconsejable verla sin supervisión de un adulto.\n<br/>Ten en cuenta que estos contenidos está realizados por actores y actrices profesionales...\n<br/>Si has entrado para «aprender algo», mejor que lo hables con un adulto de confianza que te enseñará mejor cualquier tema relacionado con la vida sexual.', 'thinfilter')""")
    
    ##############################################
    query("""CREATE TABLE config (varname TEXT, 
                                  value TEXT) """)
    
    query("""CREATE TABLE auth (username TEXT, 
                                password TEXT,
                                roles TEXT) """)
    #
    #
    # insert default data
    query("INSERT into auth (username, password, roles) VALUES ('admin', '%s', 'admin')" %(thinfilter.common.PasswordHash(password_='admin').get()) )
    query("INSERT into auth (username, password, roles) VALUES ('demo', '%s', 'livestats.livestats')"%(thinfilter.common.PasswordHash(password_='admin').get()) )
    return



def close():
    global __sql__
    lg.debug("close()", __name__)
    __sql__.close()



def load_users():
    # users and password are stored in sqlite3 database
    thinfilter.config.users={}
    for _auth in query("SELECT username,password from auth"):
        thinfilter.config.users[_auth[0]]=thinfilter.common.PasswordHash(hash_=_auth[1])
    lg.debug("load_users() loaded %s users"%( len(thinfilter.config.users) ), __name__)

def start():
    if not os.path.isfile(thinfilter.config.DBNAME):
        # create database
        create_db()
    load_users()






