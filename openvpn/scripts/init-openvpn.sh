#!/bin/sh

#echo "WARNING:"
#echo
#echo "All certificates and data will be erased "
#echo
#echo -n "    Continue [Ctrl+D] to quit"
#read cont


cd /etc/openvpn
. vars

/etc/init.d/openvpn stop

./clean-all

# delete crt and keys
rm -f *.crt *.key *.pem

if [ "$1" = "only" ]; then
  /etc/init.d/openvpn start
  exit 0
fi


./build-dh
./build-ca
./build-key-server server

/etc/init.d/openvpn restart
