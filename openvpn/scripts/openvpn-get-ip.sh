#!/bin/sh

NAME=$1

if [ "$NAME" = "all" ]; then
  HOSTS=$(grep "VERIFY OK" /var/log/openvpn.log | awk '{print $NF}' | \
     awk -F "/" '{where=match($6, /CN/); if(where) print $6; where2=match($7, /CN/); if(where2) print $7}' | \
     grep -v "ThineticSystems" | sort | uniq| awk -F"=" '{print $2}')
  for host in $HOSTS; do
     IP=$(openvpn-get-ip.sh $host 2>/dev/null)
     echo "$IP $host"
  done

  #grep "MULTI: primary virtual IP" /var/log/openvpn.log | \
  #   awk '{split($12, hostname, "/"); if ($7 == "MULTI:") print $13" "hostname[1]}'| sort | uniq
  exit 0
fi

if [ "$NAME" = "reverse" ]; then
  grep "MULTI: primary virtual IP" /var/log/openvpn.log | grep "${2}$" | tail -2 >&2
  IP=$(grep 'MULTI: primary virtual IP' /var/log/openvpn.log | grep "${2}$" | awk '{split($12, hostname, "/"); if ($7 == "MULTI:") print hostname[1]}'| tail -1)
  if [ "$IP" = "" ]; then
    grep "$2" /var/log/ipp.txt | awk -F"," '{print $1}'
  else
    grep "MULTI: primary virtual IP" /var/log/openvpn.log | grep "${2}$" | tail -2 >&2
    echo $IP
  fi
  exit 0
fi

if [ "$NAME" = "public" ]; then
  grep "$2" /var/log/openvpn.log| grep "Peer Connection Initiated"| tail -2 >&2
  grep "$2" /var/log/openvpn.log| grep "Peer Connection Initiated"| tail -1| awk '{split($NF, A,":"); print A[1]}'
  exit 0
fi

IP=$(grep "MULTI: primary virtual IP" /var/log/openvpn.log | grep "$NAME" | awk '{print $NF}'| tail -1)
if [ "$IP" = "" ]; then
  echo " from /var/log/ipp.txt" >&2
  grep "$NAME" /var/log/ipp.txt | awk -F"," '{print $2}'
else
  grep "MULTI: primary virtual IP" /var/log/openvpn.log | grep "$NAME" | tail -2 >&2
  echo $IP
fi


