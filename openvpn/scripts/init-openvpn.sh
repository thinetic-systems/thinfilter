#!/bin/sh

#echo "WARNING:"
#echo
#echo "All certificates and data will be erased "
#echo
#echo -n "    Continue [Ctrl+D] to quit"
#read cont


cd /etc/openvpn
. vars

invoke-rc.d openvpn stop

./clean-all

rm -f server.conf
# delete crt and keys
#rm -f *.crt *.key *.pem

if [ "$1" = "only" ]; then
  invoke-rc.d openvpn start
  exit 0
fi


./build-dh
./build-ca
./build-key-server server

invoke-rc.d openvpn restart
