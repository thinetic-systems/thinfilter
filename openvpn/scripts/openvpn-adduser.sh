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

exit 0

