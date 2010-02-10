#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import sys
import os


SQUID_PATH="/usr/share/squidGuard/db/"
#SQUID_PATH = "../squidGuard/db/"
BLANCA = SQUID_PATH + "/lista-blanca/"
NEGRA = SQUID_PATH  + "/lista-negra/"

DEBUG = True
ERROR = 0

def debug(txt):
    if DEBUG:
        print >> sys.stderr, "DEBUG: " , txt

def exe(cmd, _exit = False):
    ret = os.system(cmd)
    if ret != 0:
        ERROR += 1
        if _exit:
            sys.exit(1)

def restart_squid():
    if ERROR > 0:
        print "Ocurrieron errores no se reinicia Squid"
        sys.exit(1)
    
    exe("squidGuard -d -c /etc/squid3/squidGuard.conf -C all", True)
    exe("squidGuard -d -c /etc/squid3/squidGuard.conf -u", True)
    exe("chown -R proxy:proxy %s" % SQUID_PATH)
    exe("squid3 -k reconfigure || /etc/init.d/squid3 restart", True)
    if ERROR == 0:
        print "proxy reiniciado"
    else:
        print "\n\n\nUPSSSSS !!! \nocurrieron errores"

def file_exists(_file):
    if not os.path.isfile(_file):
        print "El archivo %s no existe" % _file
        sys.exit(1)
    else:
        print "Usando archivo %s" % _file


def append_line(_file, line):
    f = open(_file, 'r')
    data = f.readlines()
    f.close()
    for l in data:
        if l.replace('\n','') == line:
            print("no añadiendo línea '%s' (ya estaba)" %line )
            return
    f = open(_file, 'w')
    for l in data:
        f.write(l)
    f.write(line + "\n")
    print("añadiendo línea '%s'" %line )
    f.close()

def delete_line(_file, line):
    f = open(_file, 'r')
    data = f.readlines()
    f.close()
    newdata = []
    for i in range(len(data)):
        l = data[i]
        if l.replace('\n','') == line:
            print( "linea '%s' encontrada y borrada" %line )
        else:
            newdata.append(l)
    
    f = open(_file, 'w')
    for l in newdata:
        f.write(l)
    f.close()

if sys.argv[1] == "--restart-squid":
    restart_squid()
    sys.exit(0)

if len(sys.argv) < 4:
    print "No se han pasado suficientes opciones"
    sys.exit(0)

if sys.argv[1] == "--add-blanca":
    file_exists( BLANCA +"/" + sys.argv[2])
    append_line( BLANCA +"/" + sys.argv[2] , sys.argv[3] )
    restart_squid()

elif sys.argv[1] == "--add-negra":
    file_exists( NEGRA +"/" + sys.argv[2])
    append_line( NEGRA +"/" + sys.argv[2] , sys.argv[3] )
    restart_squid()

elif sys.argv[1] == "--delete-blanca":
    file_exists( BLANCA +"/" + sys.argv[2])
    delete_line( BLANCA +"/" + sys.argv[2] , sys.argv[3] )
    restart_squid()

elif sys.argv[1] == "--delete-negra":
    file_exists( NEGRA +"/" + sys.argv[2])
    delete_line( NEGRA +"/" + sys.argv[2] , sys.argv[3] )
    restart_squid()

else:
    print "parametros incorrectos"



