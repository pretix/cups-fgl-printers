#!/bin/bash
VERSION=0.1.0

mkdir -p dist
mkdir deb.tmp
pushd deb.tmp

mkdir -p debian
mkdir -p debian/DEBIAN

# Write control files
cat <<END > debian/DEBIAN/control
Package: cups-fgl-printers
Version: $VERSION
Section: web
Priority: optional
Architecture: any
Maintainer: Raphael Michel
License: GPL-3
Depends: python3, python3-pillow
Description: CUPS driver for FGL-based ticket printers
 .
 CUPS driver for FGL-based ticket printers
 .
END

mkdir -p debian/usr/lib/cups/filter
mkdir -p debian/usr/share/cups/model/custom

cd ..
make ppds
cd deb.tmp

cp -r ../ppd debian/usr/share/cups/model/custom/fgl
install -Dm 755 ../rastertofgl.py debian/usr/lib/cups/filter/rastertofgl

DPKG=dpkg
DEBDIR=$(pwd)
if ! hash $DPKG 2>/dev/null
then
    DPKG="docker run --rm --entrypoint /usr/bin/dpkg -v $(pwd):/tmp/deb -it raphaelm/ci-pretixdesk-apt"
    DEBDIR=/tmp/deb
fi

mkdir -p ../dist
$DPKG --build $DEBDIR/debian

mv -f debian.deb ../dist/cups-fgl-printers.deb

popd
#rm -rf deb.tmp
