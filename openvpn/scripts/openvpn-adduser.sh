#!/bin/sh
set -e

VPNSERVER="thinetic.com"

DESTDIR=`pwd`

cd /etc/openvpn
. vars >/dev/null


_exit() {
  cat << EOF

   Uso:

      openvpn-adduser.sh EMAIL=aaa@aaa PASS=12345 NAME=nombre

EOF
  exit $1
}

for arg in $@; do
  export $arg
done

if [ "$EMAIL" = "" ]; then
  echo "EMAIL no puede estar vacío"
  _exit 1
fi

if [ "$PASS" = "" ]; then
  echo "PASS no puede estar vacío"
  _exit 1
fi

if [ "$NAME" = "" ]; then
  echo "NAME no puede estar vacío"
  _exit 1
fi


if [ -e /etc/openvpn/keys/${NAME}.crt ]; then
  echo
  echo "ERROR:"
  echo "  /etc/openvpn/keys/${NAME}.crt ya existe"
  exit 1
fi


# generar
FORCE_KEY_EMAIL=$EMAIL PASSIN=$PASS PASSOUT=$PASS ./build-key-pass $NAME >/dev/null 2>&1



# enlazar claves
#ln -s keys/${NAME}.crt ./
#ln -s keys/${NAME}.key ./

# generar archivo zip
TMP_DIR=$(mktemp -d /tmp/openvpnXXXXXXXX)

mkdir -p $TMP_DIR/keys

cp keys/ca.crt      $TMP_DIR/keys/
cp keys/${NAME}.crt $TMP_DIR/keys/
cp keys/${NAME}.key $TMP_DIR/keys/

# crear archivo vpn
cat << EOF > $TMP_DIR/thinetic.ovpn
client
dev tun
proto udp
remote $VPNSERVER
float
resolv-retry infinite
nobind
persist-key
persist-tun
ca "C:\\\\Archivos de Programa\\\\OpenVPN\\\\config\\\\ca.crt"
cert "C:\\\\Archivos de Programa\\\\OpenVPN\\\\config\\\\$NAME.crt"
key "C:\\\\Archivos de Programa\\\\OpenVPN\\\\config\\\\$NAME.key"
comp-lzo
verb 4

EOF


# comprimir en zip

cd $TMP_DIR/
zip -q -r $DESTDIR/$NAME.zip ./

cd /etc/openvpn
rm -rf $TMP_DIR

echo "Archivo zip creado en $DESTDIR/$NAME.zip"
