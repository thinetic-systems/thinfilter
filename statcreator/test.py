#!/usr/bin/env python

import rrdtool , time , random

stime = int(time.time()) - 5 * 86400
dpoints = 1000
etime = stime + (dpoints * 300)
fname = 'test.rrd'
gfname = 'test.png'

rrdtool.create('test.rrd' ,
        '--start' , str(stime) ,
        'DS:speed:COUNTER:600:U:U' ,
        'RRA:AVERAGE:0.5:1:576' ,
        'RRA:AVERAGE:0.5:6:336'
)

ctime = stime
cmiles = 0
for i in xrange(dpoints):
    bump = random.randint(1 , 20)
    cmiles += bump
    ctime += 300
    rrdtool.update(fname , '%d:%d' % (ctime , cmiles))

rrdtool.graph(gfname ,
        '--start' , str(etime - (24 * 3600)) ,
        '--end' , str(etime) ,
        '--vertical-label' , 'Speed m/h' ,
        '--imgformat' , 'PNG' ,
        '--title' , 'Speeds' ,
        '--lower-limit' , '0' ,
        'DEF:myspeed=%s:speed:AVERAGE' % fname ,
        'CDEF:mph=myspeed,3600,*' ,
        'VDEF:msmax=mph,MAXIMUM' ,
        'VDEF:msavg=mph,AVERAGE' ,
        'VDEF:msmin=mph,MINIMUM' ,
        'VDEF:mspct=mph,95,PERCENT' ,
        'LINE1:mph#FF0000:My Speed' ,
        r'GPRINT:msmax:Max\: %6.1lf mph' ,
        r'GPRINT:msavg:Avg\: %6.1lf mph' ,
        r'GPRINT:msmin:Min\: %6.1lf mph\l' ,
        r'GPRINT:mspct:95th Perc\: %6.1lf mph\l'
)


