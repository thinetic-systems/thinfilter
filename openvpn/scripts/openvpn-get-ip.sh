#!/bin/sh

NAME=$1

if [ "$NAME" = "all" ]; then
  grep "MULTI: primary virtual IP" /var/log/openvpn.log | \
     awk '{split($12, hostname, "/"); if ($7 == "MULTI:") print $13" "hostname[1]}'| sort | uniq
  exit 0
fi

if [ "$NAME" = "reverse" ]; then
  grep "MULTI: primary virtual IP" /var/log/openvpn.log | grep "${2}$" | tail -2 >&2
  grep 'MULTI: primary virtual IP' /var/log/openvpn.log | grep "${2}$" | awk '{split($12, hostname, "/"); if ($7 == "MULTI:") print hostname[1]}'| tail -1
  exit 0
fi


grep "MULTI: primary virtual IP" /var/log/openvpn.log | grep "$NAME" | tail -2 >&2
grep "MULTI: primary virtual IP" /var/log/openvpn.log | grep "$NAME" | awk '{print $NF}'| tail -1
