#!/bin/bash
#instructions from http://www.tc.umn.edu/~brams006/selfsign.html

BITCOUNT=512
TIMEOUT=3650 #ten yrs

echo Generate your own Certificate Authority
openssl genrsa -out ca.key $BITCOUNT
openssl req -new -x509 -days $TIMEOUT -key ca.key -out ca.crt

echo Generate a server key and request for signing
openssl genrsa -out ca.key $BITCOUNT
openssl req -new -x509 -days $TIMEOUT -key ca.key -out ca.crt

echo Generate a server key and request for signing
openssl genrsa -out server.key $BITCOUNT
openssl req -new -key server.key -out server.csr

echo Sign the certificate signing request with the self-created certificate authority
openssl x509 -req -days $TIMEOUT -in server.csr -CA ca.crt -CAkey ca.key -set_serial 01 -out server.crt

echo Make a server.key which doesnt cause apache to prompt for a password
openssl rsa -in server.key -out server.key.insecure
mv server.key server.key.secure
mv server.key.insecure server.key

#echo Copy the files into position
#cp server.key /etc/apache2/ssl.key
#cp server.crt /etc/apache2/ssl.crt
#cp server.csr /etc/apache2/ssl.csr

echo All Done

