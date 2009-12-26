#!/bin/sh

echo "WARNING:"
echo 
echo "All certificates and data will be erased "
echo
echo -n "    Continue [Ctrl+D] to quit"
read cont


cd /etc/openvpn
. vars

./clean-all

# delete crt and keys
rm -f *.crt *.key *.pem

if [ "$1" = "only" ]; then
  exit 0
fi


./build-dh
#ln -s keys/dh1024.pem ./

./build-ca
#ln -s keys/ca.crt ./ 
#ln -s keys/ca.key ./

./build-key-server server
#ln -s keys/server.crt ./
#ln -s keys/server.key ./

/etc/init.d/openvpn restart
