#!/usr/bin/perl 


#   * Copyright (C) 2000 Vince (Vincent Saugey), MandrakeSoft <vince@mandrakesoft.com>
#   *
#   * This program is free software; you can redistribute it and/or modify
#   * it under the terms of the GNU General Public License as published by
#   * the Free Software Foundation; either version 2, or (at your option)
#   * any later version.
#   *
#   * This program is distributed in the hope that it will be useful,
#   * but WITHOUT ANY WARRANTY; without even the implied warranty of
#   * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   * GNU General Public License for more details.
#   *
#   * You should have received a copy of the GNU General Public License
#   * along with this program; if not, write to the Free Software
#   * Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA 02111-1307, USA.


# This create a database for monitoring the performance and use of a linux system
# For work it need :
#    1) rrdtool (round robin database installing and in the path of the user
#    2) A mounted proc file system from linux kernel at least 2.2.17
#    3) Add a entry in our cron table to launch this script each 5min 
#          (like this one : "0-59/5 * * * * root /usr/bin/monitor_script.pl")
#    4) God declaration of the two next variables

# Libdir is the base repertorie where is stocked the rrd file. 
# /var/lib seem to be a good space for this (In point of view of FHS).
#$LIBDIR="/var/lib/monitoring/";
$LIBDIR="./";

# Graphdir is the directory where the image will be generated
# You can use many values like one subdir of our html server.
# you have to create this directories
#$GRAPHDIR="/var/www/html/monitoring";
$GRAPHDIR="./";


# Update the cpu load rrdb
sub cpu_load()
{
    my $cpuloadFile="$LIBDIR/loadavg.rrd";
    if (! -f $cpuloadFile ) {
	system ("rrdtool create $cpuloadFile DS:loadavg:GAUGE:600:U:U"
		. " RRA:AVERAGE:0.5:1:600 RRA:AVERAGE:0.5:6:700 RRA:AVERAGE:0.5:24:775 RRA:AVERAGE:0.5:288:797"
		. " RRA:MAX:0.5:1:600 RRA:MAX:0.5:6:700 RRA:MAX:0.5:24:775 RRA:MAX:0.5:288:79");
    }
    my $load_avg = `cat /proc/loadavg`;
# using the second 
    $load_avg =~ /^\d+\.\d+ (\d+\.\d+)/;
    system ("rrdtool update $cpuloadFile N:$1");	
}


# update the network interfaces taffic rrdbs
sub net_traffic()
{
    if (! -d "$LIBDIR/net")
    {
	system ("mkdir -p $LIBDIR/net") or die;
    }
    open (FILE, "</proc/net/dev");
    while (<FILE>) {
	if ( $_ =~ /(\w+)\:\s*(.*)/ ) {
	    my $interface = $1;
	    if ( $interface ne "lo" )  {
		@stat = split (/\s+/, $2);
		my ($inBytes, $inPackets, $inErrs, $inDrops, $inFifo, $inFrame, $inCompressed, $inMaulticast, 
		 $outBytes, $outPackets, $outErrs, $outDrops, $outFifo, $outFrame, $outCompressed, $outMaulticast) = @stat;
		$interfaceFile = $LIBDIR . "/net/" . $interface . ".rrd";
		if ( ! -f $interfaceFile ) {
		    system ("rrdtool create $interfaceFile DS:input:COUNTER:600:U:U DS:output:COUNTER:600:U:U"
			    . " RRA:AVERAGE:0.5:1:600 RRA:AVERAGE:0.5:6:700 RRA:AVERAGE:0.5:24:775 RRA:AVERAGE:0.5:288:797"
			    . " RRA:MAX:0.5:1:600 RRA:MAX:0.5:6:700 RRA:MAX:0.5:24:775 RRA:MAX:0.5:288:79");
		}
		else
		{
		    system ("rrdtool update $interfaceFile N:$inBytes:$outBytes");
		}
	    }
	}
    }
}


sub mem_usage()
{
    $memusageFile="$LIBDIR/memusage.rrd";
    if (! -f $memusageFile ) {
	system ("rrdtool create $memusageFile DS:memused:GAUGE:600:U:U DS:cached:GAUGE:600:U:U  DS:memfree:GAUGE:600:U:U DS:swapused:GAUGE:600:U:U DS:swapfree:GAUGE:600:U:U "
		. " RRA:AVERAGE:0.5:1:600 RRA:AVERAGE:0.5:6:700 RRA:AVERAGE:0.5:24:775 RRA:AVERAGE:0.5:288:797"
		. " RRA:MAX:0.5:1:600 RRA:MAX:0.5:6:700 RRA:MAX:0.5:24:775 RRA:MAX:0.5:288:79 ");
    }
    my ($memused, $cached, $memfree, $swapused, $swapfree);
    open (FILE, "</proc/meminfo");
    while (<FILE>) {
	($memused, $cached, $memfreen) = ($1,$3,$2) if (/^Mem:\s*\d+\s+(\d+)\s+(\d+)\s+\d+\s+\d+\s+(\d+)\s*$/);
	($swapused, $swapfree) = ($1, $2) if (/^Swap:\s*\d+\s+(\d+)\s+(\d+)\s*$/);
    }
    system ("rrdtool update $memusageFile N:$memused:$cached:$memfreen:$swapused:$swapfree");	
}


sub traffic_type()
{
    $nettypeFile="$LIBDIR/nettype.rrd";
    if (! -f $nettypeFile ) {
	system ("rrdtool create $nettypeFile DS:inicmp:COUNTER:600:U:U DS:outicmp:COUNTER:600:U:U  DS:inudp:COUNTER:600:U:U DS:outudp:COUNTER:600:U:U DS:intcp:COUNTER:600:U:U DS:outtcp:COUNTER:600:U:U"
		. " RRA:AVERAGE:0.5:1:600 RRA:AVERAGE:0.5:6:700 RRA:AVERAGE:0.5:24:775 RRA:AVERAGE:0.5:288:797"
		. " RRA:MAX:0.5:1:600 RRA:MAX:0.5:6:700 RRA:MAX:0.5:24:775 RRA:MAX:0.5:288:79 ");
    }
    my ($inicmp, $outicmp, $inudp, $outudp, $intcp, $outtcp);
    open (FILE, "</proc/net/snmp");
    while (<FILE>) {
	($inicmp, $outicmp) = ($1,$3) if (/^Icmp:\s*(\d+)(\s+\d+){12,12}\s+(\d+)(\s+\d+){12,12}\s*$/);
	($inudp, $outudp) = ($1, $2) if (/^Udp:\s*(\d+)[\s\d]+\s(\d+)\s*$/);
	($intcp, $outtcp) = ($2, $3) if (/^Tcp:\s*(\d+\s+){9,9}(\d+)\s+(\d+)(\s+\d+){3,3}\s*$/);
    }
    system ("rrdtool update $nettypeFile N:$inicmp:$outicmp:$inudp:$outudp:$intcp:$outtcp");	
}


#Begin of main procedure !!!

if (scalar (@ARGV) == 0) 
{
    #create libdir if it doesn't existe.
    system ("mkdir -p $LIBDIR") if (! -d "$LIBDIR");
    #update the rrd database, you can remove one or more section if you want.
    &cpu_load();
    &mem_usage();
    &net_traffic();
    &traffic_type();
    exit (0);
}


if (@ARGV[0] eq "--graph")
{
    
    my $color_tags = "-c BACK#666699 -c CANVAS#FFFFFF -c FONT#FFFFFF";
    my $yellow = "ffcc00";
    my $red = "ff3300";
    my $green = "66cc00";
    my $blue = "333366";
	

    #cpu load
#      system ("rrdtool graph $GRAPHDIR/avgload-day.png --start -86400 DEF:cpuloadavg=$targetdir/$LIBDIR/loadavg.rrd:loadavg:AVERAGE DEF:cpuloadmax=$targetdir/$LIBDIR/loadavg.rrd:loadavg:MAX AREA:cpuloadavg#00FF00:\"Load Average\" LINE1:cpuloadmax#0000FF:\"Max cpu load\"");
    system ("rrdtool graph $GRAPHDIR/avgload-day.png --start -86400 -t \"CPU LOAD AVERAGE BY DAY\" "
	    . $color_tags . " -v 'cpu load' -b 1000 "
	    . " DEF:cpuloadavg=$LIBDIR/loadavg.rrd:loadavg:AVERAGE"
	    . " AREA:cpuloadavg#$green:\"Load Average one mesure each 5 minutes\"");
    system ("rrdtool graph $GRAPHDIR/avgload-week.png --start -604800 -t \"CPU LOAD AVERAGE BY WEEK\" "
	    . $color_tags . " -v 'cpu load' -b 1000"
	    . " DEF:cpuloadavg=$LIBDIR/loadavg.rrd:loadavg:AVERAGE" 
	    . " AREA:cpuloadavg#$green:\"Load Average one mesure each 5 minutes\"");
    system ("rrdtool graph $GRAPHDIR/avgload-month.png --start -2678400 -t \"CPU LOAD AVERAGE BY MONTH\" "
	    . $color_tags . " -v 'cpu load' -b 1000"
	    . " DEF:cpuloadavg=$LIBDIR/loadavg.rrd:loadavg:AVERAGE" 
	    . " AREA:cpuloadavg#$green:\"Load Average one mesure each 5 minutes\"");
    system ("rrdtool graph $GRAPHDIR/avgload-year.png --start -31622400 -t \"CPU LOAD AVERAGE BY YEAR\" "
	    . $color_tags . " -v 'cpu load' -b 1000 "
	    . " DEF:cpuloadavg=$LIBDIR/loadavg.rrd:loadavg:AVERAGE"
	    . " AREA:cpuloadavg#$green:\"Load Average one mesure each 5 minutes\"");
    
    #net traffic
    $targetdir = $LIBDIR . "/net";
    opendir(DIR, $targetdir);
    @files = readdir (DIR);
    foreach $i (@files)
    {
	print "processing file $i\n";
	if ($i =~ /(.*)\.rrd/) {
	    $interface = $1;
	    system ("rrdtool graph $GRAPHDIR/$interface-day.png --start -86400 -t \"INTERFACE \U$interface\U TRAFFIC BY DAY\" "
		    . $color_tags
		    . " DEF:inoctets=$targetdir/$i:input:AVERAGE"
		    . " DEF:outoctets=$targetdir/$i:output:AVERAGE" 
		    . " AREA:inoctets#$green:\"In traffic\"" 
		    . " LINE1:outoctets#$blue:\"Out traffic\"");
	    system ("rrdtool graph $GRAPHDIR/$interface-week.png --start -604800 -t \"INTERFACE \U$interface\U TRAFFIC BY WEEK\" "
		    . $color_tags
		    . " DEF:inoctets=$targetdir/$i:input:AVERAGE"
		    . " DEF:outoctets=$targetdir/$i:output:AVERAGE"
		    . " AREA:inoctets#$green:\"In traffic\""
		    . " LINE1:outoctets#$blue:\"Out traffic\"");
	    system ("rrdtool graph $GRAPHDIR/$interface-month.png --start -2678400 -t \"INTERFACE \U$interface\U TRAFFIC BY MONTH\" "
		    . $color_tags
		    . " DEF:inoctets=$targetdir/$i:input:AVERAGE"
		    . " DEF:outoctets=$targetdir/$i:output:AVERAGE"
		    . " AREA:inoctets#$green:\"In traffic\""
		    . " LINE1:outoctets#$blue:\"Out traffic\"");
	    system ("rrdtool graph $GRAPHDIR/$interface-year.png --start -31622400 -t \"INTERFACE \U$interface\U TRAFFIC BY YEAR\" "
		    . $color_tags
		    . " DEF:inoctets=$targetdir/$i:input:AVERAGE"
		    . " DEF:outoctets=$targetdir/$i:output:AVERAGE"
		    . " AREA:inoctets#$green:\"In traffic\""
		    . " LINE1:outoctets#$blue:\"Out traffic\"");
	}
    }
    
    #memusage ($memused, $cached, $memfreen, $swapused, $swapfree);
    system ("rrdtool graph $GRAPHDIR/memusage-day.png --start -86400 -t \"MEM USAGE BY DAY\" "
	    . $color_tags . " -v 'mem size' --alt-autoscale-max -b 1024"
	    . " DEF:swapused=$LIBDIR/memusage.rrd:swapused:AVERAGE"
	    . " DEF:memused=$LIBDIR/memusage.rrd:memused:AVERAGE"
	    . " DEF:memfree=$LIBDIR/memusage.rrd:memfree:AVERAGE"
	    . " DEF:cached=$LIBDIR/memusage.rrd:cached:AVERAGE"
	    . " AREA:memused#$red:\"Ram menory one mesure each 5 minutes\""
	    . " STACK:memfree#$blue:\"Ram menory free one mesure each 5 minutes\""
	    . " LINE1:swapused#$green:\"Swap memory used one mesure each 5 minutes\""
	    . " LINE1:cached#$yellow:\"Memory used for cache one mesure each 5 minutes\"");
    system ("rrdtool graph $GRAPHDIR/memusage-week.png --start -604800 -t \"MEM USAGE BY WEEK\" "
	    . $color_tags . " -v 'mem size' --alt-autoscale"
	    . " DEF:swapused=$LIBDIR/memusage.rrd:swapused:AVERAGE"
	    . " DEF:memused=$LIBDIR/memusage.rrd:memused:AVERAGE"
	    . " DEF:memfree=$LIBDIR/memusage.rrd:memfree:AVERAGE"
	    . " DEF:cached=$LIBDIR/memusage.rrd:cached:AVERAGE"
	    . " AREA:memused#$red:\"Total menory used\""
	    . " STACK:memfree#$blue:\"Total menory free\""
	    . " LINE1:swapused#$green:\"Swap memory used\""
	    . " LINE1:cached#$yellow:\"Memory used for cache\"");
    system ("rrdtool graph $GRAPHDIR/memusage-month.png --start -2678400 -t \"MEM USAGE BY MONTH\" "
	    . $color_tags . " -v 'mem size' --alt-autoscale"
	    . " DEF:swapused=$LIBDIR/memusage.rrd:swapused:AVERAGE"
	    . " DEF:memused=$LIBDIR/memusage.rrd:memused:AVERAGE"
	    . " DEF:memfree=$LIBDIR/memusage.rrd:memfree:AVERAGE"
	    . " DEF:cached=$LIBDIR/memusage.rrd:cached:AVERAGE"
	    . " AREA:memused#$red:\"Total menory used\""
	    . " STACK:memfree#$blue:\"Total menory free\""
	    . " LINE1:swapused#$green:\"Swap memory used\""
	    . " LINE1:cached#$yellow:\"Memory used for cache\"");
    system ("rrdtool graph $GRAPHDIR/memusage-year.png --start -31622400 -t \"MEM USAGE BY YEAR\" "
	    . $color_tags . " -v 'mem size' --alt-autoscale-max"
	    . " DEF:swapused=$LIBDIR/memusage.rrd:swapused:AVERAGE"
	    . " DEF:memused=$LIBDIR/memusage.rrd:memused:AVERAGE"
	    . " DEF:memfree=$LIBDIR/memusage.rrd:memfree:AVERAGE"
	    . " DEF:cached=$LIBDIR/memusage.rrd:cached:AVERAGE"
	    . " AREA:memused#$red:\"Total menory used\""
	    . " STACK:memfree#$blue:\"Total menory free\""
	    . " LINE1:swapused#$green:\"Swap memory used\""
	    . " LINE1:cached#$yellow:\"Memory used for cache\"");

    #nettype ($inicmp, $outicmp, $inudp, $outudp, $intcp, $outtcp);
    #INPUT
	print "make net traffic type graph\n";
    system ("rrdtool graph $GRAPHDIR/innettype-day.png --start -86400 -t \"INPUT PACKET BY DAY\" "
	    . $color_tags . " -v 'nb packet'"
	    . " DEF:inicmp=$LIBDIR/nettype.rrd:inicmp:AVERAGE"
	    . " DEF:inudp=$LIBDIR/nettype.rrd:inudp:AVERAGE"
	    . " DEF:intcp=$LIBDIR/nettype.rrd:intcp:AVERAGE"
	    . " AREA:inicmp#$red:\"Icmp msg\""
	    . " STACK:inudp#$blue:\"Udp datagrame\""
	    . " STACK:intcp#$green:\"Tcp segment\"");
    system ("rrdtool graph $GRAPHDIR/innettype-week.png --start -604800 -t \"INPUT PACKET BY WEEK\" "
	    . $color_tags . " -v 'nb packet'"
	    . " DEF:inicmp=$LIBDIR/nettype.rrd:inicmp:AVERAGE"
	    . " DEF:inudp=$LIBDIR/nettype.rrd:inudp:AVERAGE"
	    . " DEF:intcp=$LIBDIR/nettype.rrd:intcp:AVERAGE"
	    . " AREA:inicmp#$red:\"Icmp msg\""
	    . " STACK:inudp#$blue:\"Udp datagrame\""
	    . " STACK:intcp#$green:\"Tcp segment\"");
    system ("rrdtool graph $GRAPHDIR/innettype-month.png --start -2678400 -t \"INPUT PACKET BY MONTH\" "
	    . $color_tags . " -v 'nb packet'"
	    . " DEF:inicmp=$LIBDIR/nettype.rrd:inicmp:AVERAGE"
	    . " DEF:inudp=$LIBDIR/nettype.rrd:inudp:AVERAGE"
	    . " DEF:intcp=$LIBDIR/nettype.rrd:intcp:AVERAGE"
	    . " AREA:inicmp#$red:\"Icmp msg\""
	    . " STACK:inudp#$blue:\"Udp datagrame\""
	    . " STACK:intcp#$green:\"Tcp segment\"");
    system ("rrdtool graph $GRAPHDIR/innettype-year.png --start -31622400 -t \"INPUT PACKET BY YEAR\" "
	    . $color_tags . " -v 'nb packet'"
	    . " DEF:inicmp=$LIBDIR/nettype.rrd:inicmp:AVERAGE"
	    . " DEF:inudp=$LIBDIR/nettype.rrd:inudp:AVERAGE"
	    . " DEF:intcp=$LIBDIR/nettype.rrd:intcp:AVERAGE"
	    . " AREA:inicmp#$red:\"Icmp msg\""
	    . " STACK:inudp#$blue:\"Udp datagrame\""
	    . " STACK:intcp#$green:\"Tcp segment\"");
    #OUTPUT
    system ("rrdtool graph $GRAPHDIR/outnettype-day.png --start -86400 -t \"OUTPUT PACKET BY DAY\" "
	    . $color_tags . " -v 'nb packet'"
	    . " DEF:outicmp=$LIBDIR/nettype.rrd:outicmp:AVERAGE"
	    . " DEF:outudp=$LIBDIR/nettype.rrd:outudp:AVERAGE"
	    . " DEF:outtcp=$LIBDIR/nettype.rrd:outtcp:AVERAGE"
	    . " AREA:outicmp#$red:\"Icmp msg\""
	    . " STACK:outudp#$blue:\"Udp datagrame\""
	    . " STACK:outtcp#$green:\"Tcp segment\"");
    system ("rrdtool graph $GRAPHDIR/outnettype-week.png --start -604800 -t \"OUTPUT PACKET BY WEEK\" "
	    . $color_tags . " -v 'nb packet'"
	    . " DEF:outicmp=$LIBDIR/nettype.rrd:outicmp:AVERAGE"
	    . " DEF:outudp=$LIBDIR/nettype.rrd:outudp:AVERAGE"
	    . " DEF:outtcp=$LIBDIR/nettype.rrd:outtcp:AVERAGE"
	    . " AREA:outicmp#$red:\"Icmp msg\""
	    . " STACK:outudp#$blue:\"Udp datagrame\""
	    . " STACK:outtcp#$green:\"Tcp segment\"");
    system ("rrdtool graph $GRAPHDIR/outnettype-month.png --start -2678400 -t \"OUTPUT PACKET BY MONTH\" "
	    . $color_tags . " -v 'nb packet'"
	    . " DEF:outicmp=$LIBDIR/nettype.rrd:outicmp:AVERAGE"
	    . " DEF:outudp=$LIBDIR/nettype.rrd:outudp:AVERAGE"
	    . " DEF:outtcp=$LIBDIR/nettype.rrd:outtcp:AVERAGE"
	    . " AREA:outicmp#$red:\"Icmp msg\""
	    . " STACK:outudp#$blue:\"Udp datagrame\""
	    . " STACK:outtcp#$green:\"Tcp segment\"");
    system ("rrdtool graph $GRAPHDIR/outnettype-year.png --start -31622400 -t \"OUTPUT PACKET BY YEAR\" "
	    . $color_tags . " -v 'nb packet'"
	    . " DEF:outicmp=$LIBDIR/nettype.rrd:outicmp:AVERAGE"
	    . " DEF:outudp=$LIBDIR/nettype.rrd:outudp:AVERAGE"
	    . " DEF:outtcp=$LIBDIR/nettype.rrd:outtcp:AVERAGE"
	    . " AREA:outicmp#$red:\"Icmp msg\""
	    . " STACK:outudp#$blue:\"Udp datagrame\""
	    . " STACK:outtcp#$green:\"Tcp segment\"");
    exit(0);
}

print STDERR "Usage : monitoring-script <--graph>\n";
