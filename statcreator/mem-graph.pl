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


# This create a database for monitoring the performance of a linux system
# For work it, you  need :
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

my $color_tags = "-c BACK#666699 -c CANVAS#FFFFFF -c FONT#FFFFFF";
my $yellow = "ffcc00";
my $red = "ff3300";
my $green = "66cc00";
my $blue = "333366";


sub generate_cpu_load_graph 
{
#cpu load
    local $cpuloadgraph = scalar($color_tags . " -v 'cpu load' -b 1000 "
				    . " DEF:cpuloadavg=$LIBDIR/loadavg.rrd:loadavg:AVERAGE"
				    . " AREA:cpuloadavg#$blue:\"Load Average one mesure each 5 minutes\"");

    system ("rrdtool graph $GRAPHDIR/avgload-day.png --start -86400 -t \"CPU LOAD AVERAGE BY DAY\" " . $cpuloadgraph);
    return if (defined $_[0]);
    system ("rrdtool graph $GRAPHDIR/avgload-week.png --start -604800 -t \"CPU LOAD AVERAGE BY WEEK\" " . $cpuloadgraph);
    system ("rrdtool graph $GRAPHDIR/avgload-month.png --start -2678400 -t \"CPU LOAD AVERAGE BY MONTH\" " . $cpuloadgraph);
    system ("rrdtool graph $GRAPHDIR/avgload-year.png --start -31622400 -t \"CPU LOAD AVERAGE BY YEAR\" " . $cpuloadgraph);
}


sub conv_debit
{
    $debit = $_[0];
    return int ($debit / 1024 /1024) . "Gbytes" if (length(int($debit)) > 6);
    return int ($debit /1024) . "Mbytes" if (length(int($debit)) > 3);
    return int ($debit) . "Kbytes" if (length(int($debit)) > 3);
    return int ($debit) ."bytes"
}

sub generate_net_traffic_graph
{
#net traffic
    $targetdir = $LIBDIR . "/net";
    opendir(DIR, $targetdir);
    @files = readdir (DIR);
    foreach $i (@files)
    {
	next if (defined $_[1] && !($i =~ /$_[1]/));
	print "processing file $i\n";
	local $nettrafficgraph = scalar($color_tags . " -v 'bytes/s' "
					. " DEF:inoctets=$targetdir/$i:input:AVERAGE "
					. "DEF:outoctets=$targetdir/$i:output:AVERAGE "
					. "DEF:maxinoctets=$targetdir/$i:input:MAX "
					. "DEF:maxoutoctets=$targetdir/$i:output:MAX "
					. "PRINT:inoctets:AVERAGE:\"%le\" "
					. "GPRINT:inoctets:AVERAGE:\"In  avg %4.0lf %sbytes/s,\" "
					. "GPRINT:maxinoctets:MAX:\"max %4.0lf %sbytes/s\\n\" "
					. "PRINT:outoctets:AVERAGE:\"%le\" "
					. "GPRINT:outoctets:AVERAGE:\"Out avg %4.0lf %sbytes/s,\" "
					. "GPRINT:maxoutoctets:MAX:\"max %4.0lf %sbytes/s\\n\" "
					. "AREA:inoctets#$green:\"In traffic\" "
					. "LINE1:outoctets#$blue:\"Out traffic\" ");
	if ($i =~ /(.*)\.rrd/) {
	    $interface = "\L$1";
	    local @result = `rrdtool graph $GRAPHDIR/$interface-hour.png --start -3600 -t \"INTERFACE $interface TRAFFIC BY HOUR\" $nettrafficgraph`;
	    local ($in, $out) = map {chomp;$_} @result[1..2];
	    $in = conv_debit ($in * (3600.0 / 1024.0));
	    $out = conv_debit ($out * (3600.0 / 1024.0));
	    system ("echo \"$in $out\" > $GRAPHDIR/\L$interface.vol");
	    next if (defined $_[0]);

	    local @result = `rrdtool graph $GRAPHDIR/$interface-day.png --start -86400 -t \"INTERFACE $interface TRAFFIC BY DAY\" $nettrafficgraph`;
	    local ($in, $out) = map {chomp;$_} @result[1..2];
	    $in = conv_debit ($in * (86400.0 / 1024.0));
	    $out = conv_debit ($out * (86400.0 / 1024.0));
	    system ("echo \"$in $out\" >> $GRAPHDIR/\L$interface.vol");

	    local @result = `rrdtool graph $GRAPHDIR/$interface-week.png --start -604800 -t \"INTERFACE $interface TRAFFIC BY WEEK\" $nettrafficgraph`;
	    local ($in, $out) = map {chomp;$_} @result[1..2];
	    $in = conv_debit ($in * (604800 / 1024));
	    $out = conv_debit ($out * (604800 / 1024));
	    system ("echo $in $out >> $GRAPHDIR/\L$interface.vol");

	    local @result = `rrdtool graph $GRAPHDIR/$interface-month.png --start -2678400 -t \"INTERFACE $interface TRAFFIC BY MONTH\" $nettrafficgraph`;
	    local ($in, $out) = map {chomp;$_} @result[1..2]; 
	    $in = conv_debit ($in * (2678400 / 1024));
	    $out = conv_debit ($out * (2678400 / 1024));
	    system ("echo $in $out >> $GRAPHDIR/\L$interface.vol");
	    
	    local @result = `rrdtool graph $GRAPHDIR/$interface-year.png --start -31622400 -t \"INTERFACE $interface TRAFFIC BY YEAR\" $nettrafficgraph`;
	    local ($in, $out) = map {chomp;$_} @result[1..2];
	    $in = conv_debit ($in * (31622400 / 1024));
	    $out = conv_debit ($out * (31622400 / 1024));
	    system ("echo $in $out >> $GRAPHDIR/\L$interface.vol");
	}
    }
}



sub generate_memusage_graph
{
#memusage ($memused, $cached, $memfreen, $swapused, $swapfree);
    local $memusagegraph = scalar ($color_tags . " -v 'mem size' --alt-autoscale-max -b 1024"
				   . " DEF:swapused=$LIBDIR/memusage.rrd:swapused:AVERAGE"
				   . " DEF:memused=$LIBDIR/memusage.rrd:memused:AVERAGE"
				   . " DEF:memfree=$LIBDIR/memusage.rrd:memfree:AVERAGE"
				   . " DEF:cached=$LIBDIR/memusage.rrd:cached:AVERAGE"
				   . " AREA:memused#$blue:\"Ram menory one mesure each 5 minutes\""
				   . " STACK:memfree#$green:\"Ram menory free one mesure each 5 minutes\""
				   . " LINE1:swapused#$red:\"Swap memory used one mesure each 5 minutes\""
				   . " LINE1:cached#$yellow:\"Memory used for cache one mesure each 5 minutes\"");

    system ("rrdtool graph $GRAPHDIR/memusage-day.png --start -86400 -t \"MEM USAGE BY DAY\" " . $memusagegraph);
    return if (defined $_[0]);
    system ("rrdtool graph $GRAPHDIR/memusage-week.png --start -604800 -t \"MEM USAGE BY WEEK\" " . $memusagegraph);
    system ("rrdtool graph $GRAPHDIR/memusage-month.png --start -2678400 -t \"MEM USAGE BY MONTH\" " . $memusagegraph);
    system ("rrdtool graph $GRAPHDIR/memusage-year.png --start -31622400 -t \"MEM USAGE BY YEAR\" " . $memusagegraph);
}

sub generate_net_type_graph
{  
#nettype ($inicmp, $outicmp, $inudp, $outudp, $intcp, $outtcp);
    local $inputgraph = scalar ($color_tags . " -v 'nb packet' "
				. "DEF:inicmp=$LIBDIR/nettype.rrd:inicmp:AVERAGE " 
				. "DEF:inudp=$LIBDIR/nettype.rrd:inudp:AVERAGE "
				. "DEF:intcp=$LIBDIR/nettype.rrd:intcp:AVERAGE "
				. "AREA:inicmp#$red:\"Icmp msg\" "
				. "STACK:inudp#$blue:\"Udp datagrame\" "
				. "STACK:intcp#$green:\"Tcp segment\"");
    local $outputgraph = scalar ($color_tags . " -v 'nb packet' "
				 . " DEF:inicmp=$LIBDIR/nettype.rrd:inicmp:AVERAGE"
				 . " DEF:inudp=$LIBDIR/nettype.rrd:inudp:AVERAGE"
				 . " DEF:intcp=$LIBDIR/nettype.rrd:intcp:AVERAGE"
				 . " AREA:inicmp#$red:\"Icmp msg\""
				 . " STACK:inudp#$blue:\"Udp datagrame\""
				 . " STACK:intcp#$green:\"Tcp segment\"");
    
#INPUT
    system ("rrdtool graph $GRAPHDIR/innettype-day.png --start -86400 -t \"INPUT PACKET BY DAY\" " . $inputgraph);
#OUTPUT
    system ("rrdtool graph $GRAPHDIR/outnettype-day.png --start -86400 -t \"OUTPUT PACKET BY DAY\" " . $outputgraph);
    return if (defined $_[0]);

#INPUT
    system ("rrdtool graph $GRAPHDIR/innettype-week.png --start -604800 -t \"INPUT PACKET BY WEEK\" " . $inputgraph);
    system ("rrdtool graph $GRAPHDIR/innettype-month.png --start -2678400 -t \"INPUT PACKET BY MONTH\" " . $inputgraph);
    system ("rrdtool graph $GRAPHDIR/innettype-year.png --start -31622400 -t \"INPUT PACKET BY YEAR\" " . $inputgraph);

#OUTPUT
    system ("rrdtool graph $GRAPHDIR/outnettype-week.png --start -604800 -t \"OUTPUT PACKET BY WEEK\" " . $outputgraph);
    system ("rrdtool graph $GRAPHDIR/outnettype-month.png --start -2678400 -t \"OUTPUT PACKET BY MONTH\" " . $outputgraph);
    system ("rrdtool graph $GRAPHDIR/outnettype-year.png --start -31622400 -t \"OUTPUT PACKET BY YEAR\" " . $outputgraph);
}

system("mkdir","-p",$GRAPHDIR);
my $arg = shift @ARGV if ($ARGV[0] =~ /-f/);

if (!defined $ARGV[0])
{
    generate_net_traffic_graph($arg);
    generate_cpu_load_graph($arg);
    generate_memusage_graph($arg);
    generate_net_type_graph($arg);
}
else {	
    if ($ARGV[0] =~ /--sys/)
    {
	generate_cpu_load_graph($arg);
	generate_memusage_graph($arg);
    }
    if ($ARGV[0] =~ /--net/)
    {
	generate_net_traffic_graph($arg, $ARGV[1]);
    }    
}
