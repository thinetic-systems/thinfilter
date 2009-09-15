#!/bin/bash
# ------------------------------------------------------------------------------------
# See URL: http://www.cyberciti.biz/tips/linux-setup-transparent-proxy-squid-howto.html
# (c) 2006, nixCraft under GNU/GPL v2.0+
# -------------------------------------------------------------------------------------

set -e

. /etc/thinfilter/firewall.conf

# DANSGUARDIAN server IP
DANSGUARDIAN_SERVER=$(awk -F"," '/router,/ {print $2}' /etc/dnsmasq/dnsmasq.conf)

# Interface connected to Internet
INTERNET="eth0"

# Interface connected to LAN
LAN_IN="eth1"

VPN_LAN=$(awk '/server / {print $2"/24"}' /etc/openvpn/server.conf)


# DansGuardian port
DANSGUARDIAN_PORT="8080"

# Clean old firewall
iptables -F
iptables -X
iptables -t nat -F
iptables -t nat -X
iptables -t mangle -F
iptables -t mangle -X

if [ "$1" = "off" ]; then
  echo "iptables clean."
  exit 0
fi

# Load IPTABLES modules for NAT and IP conntrack support
modprobe ip_conntrack
modprobe ip_conntrack_ftp

# For win xp ftp client
modprobe ip_nat_ftp

echo 1 > /proc/sys/net/ipv4/ip_forward

# Setting default filter policy
iptables -P INPUT DROP
iptables -P OUTPUT ACCEPT

# Unlimited access to loop back
iptables -A INPUT -i lo -j ACCEPT
iptables -A OUTPUT -o lo -j ACCEPT

# Allow UDP, DNS and Passive FTP
iptables -A INPUT -i $INTERNET -m state --state ESTABLISHED,RELATED -j ACCEPT

# set this system as a router for Rest of LAN
iptables --table nat --append POSTROUTING --out-interface $INTERNET -j MASQUERADE
iptables --append FORWARD --in-interface $LAN_IN -j ACCEPT

# unlimited access to LAN
iptables -A INPUT -i $LAN_IN -j ACCEPT
iptables -A OUTPUT -o $LAN_IN -j ACCEPT

PORTS="2022 443 4949 1194"

for port in $PORTS; do
    iptables -A INPUT -i $INTERNET -j ACCEPT -p tcp --dport $port
    iptables -A OUTPUT -o $INTERNET -j ACCEPT -p tcp --dport $port
done

# openVPN 
iptables -t nat -A POSTROUTING -s $VPN_LAN -o $LAN_IN -j MASQUERADE
iptables -A INPUT -i tun0 -j ACCEPT
iptables -A OUTPUT -o tun0 -j ACCEPT
iptables -A FORWARD -i tun0 -j ACCEPT



# DNAT port 80 request comming from LAN systems to DANSGUARDIAN ($DANSGUARDIAN_PORT) aka transparent proxy
iptables -t nat -A PREROUTING -i $LAN_IN -p tcp --dport 80 -j DNAT --to $DANSGUARDIAN_SERVER:$DANSGUARDIAN_PORT

# if it is same system
iptables -t nat -A PREROUTING -i $INTERNET -p tcp --dport 80 -j REDIRECT --to-port $DANSGUARDIAN_PORT

# DROP everything and Log it
iptables -A INPUT -j LOG
iptables -A INPUT -j DROP


