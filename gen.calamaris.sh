#!/bin/bash
# Script for calamaris 3 to generate reports for squid 
#
# "Usage: calam_rep.sh [today|yesterday|week|month]"
#
# Pavel Malakhov 28.03.05 
#       12.05.05 fixed yesterday date format, new vars

CALAM_DIR='/etc/calamaris';                    # where calamaris is
SQUID_LOG_DIR='/var/log/squid3/';              # where the squid logs are
 # where to store reports. Root dir, all the other will be created by this script
REP_PATH_PREFIX='/var/www/calamaris';
CACHE_DIR='/etc/calamaris/cache';              # where to store cache files for every week
YESTD=`date -d yesterday +%d`;               # yesterday's day of month
YESTW=`date -d yesterday +%V`;               # yesterday's week of year
YESTM=`date -d yesterday +%m_%B`;            # yesterday's month number and name

# ------------ You don't need to edit anything below ---------------------------
# ------------------ [but welcome to analyze!] ---------------------------------

# Check for dir for report.Create, if does not exist.
function checkdir {
     if [ ! -e "$REPPATH" ];then
       echo -n `date +%c` "Dir \"$REPPATH\" is not created. Creating...   ";   
       mkdir -p $REPPATH;   
       echo "Done.";
     fi;
}

# Check for parameter
if [ "$1" = "" ]; then
  echo "Usage: calam_rep.sh [today|yesterday|week|month]"
  exit 1
fi

# check for cache dir
if [ ! -e "$CACHE_DIR" ];then                              
   echo -n `date +%c` "Cache dir \"$CACHE_DIR\" is not created. Creating...   ";
   mkdir -p $CACHE_DIR;   
   echo "Done.";
fi;


case "$1" in
  "today" )
     REPPATH=$REP_PATH_PREFIX'/today';
     checkdir;
     cd $CALAM_DIR;
     echo -n `date +%c` "Processing data for today...   ";
     cat $SQUID_LOG_DIR/access.log | calamaris --config-file /etc/calamaris/calamaris.conf -F html,graph --output-path $REPPATH;
     ;;
  "yesterday" )
     REPPATH=$REP_PATH_PREFIX'/days/'$YESTD;
     checkdir;
     cd $CALAM_DIR;
     echo -n `date +%c` "Processing data for yesterday...   ";
     cat $SQUID_LOG_DIR/access.log.0 | calamaris --config-file /etc/calamaris/calamaris.conf --output-path $REPPATH --cache-output-file $CACHE_DIR/day.$YESTD;
     ;;
  "week" )
     REPPATH=$REP_PATH_PREFIX'/weeks/'$YESTW;
     checkdir;
     cd $SQUID_LOG_DIR;
     echo -n `date +%c` "Processing data for week...   ";
     cat access.log.6 access.log.5 access.log.4 access.log.3 access.log.2 access.log.1 access.log.0  | calamaris --config-file $CALAM_DIR/calamaris.conf --output-path $REPPATH  --cache-output-file $CACHE_DIR/week.$YESTW;
     ;;
  "month" )
     REPPATH=$REP_PATH_PREFIX'/months/'$YESTM;
     checkdir;
     cd $CACHE_DIR;
     CACHEFILES="";
     for ((i=1; i<=31; i++)); do
       FILE='day.'$i;
       if [ -e "$FILE" ]; then 
	 if ["$CACHEFILES" = ""]; then 
	   CACHEFILES=$FILE;
         else
	   CACHEFILES=$CACHEFILES':'$FILE;
         fi
       fi    
     done 
     echo 'files to process '$CACHEFILES;
     echo -n `date +%c` "Processing data for month...   ";
     calamaris --config-file $CALAM_DIR/calamaris.conf --cache-input-file $CACHEFILES --no-input --output-path $REPPATH;
     echo "Done";
     # clean up cache directory at the start of a month
     # delete only cached days, leave cached weeks 
     DD=`date +%d`;
     if [ "$DD" = "01" ]; then 
       echo -n `date +%c` "Cleaning up cache dir...   ";
       rm -f $CACHE_DIR/day.*;
     fi
     ;;
esac
echo "Done";
echo `date +%c` "---Everything is done" 
exit 0
-----------------------------------------------------

Everyone who really uses <Squidmaster@Cord.de> while testing has to send me a
	postcard!
-----------------------------------------------------------------------



Version of the EXAMPLES.v3
--------------------------

$Id: EXAMPLES.v3,v 3.1 2006-03-19 17:59:03 cord Exp $
