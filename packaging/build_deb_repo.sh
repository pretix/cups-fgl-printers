#!/bin/bash

pushd dist

if [ ! -f cups-fgl-printers.deb ]; then
    echo "Create cups-fgl-printers.deb first!"
    exit 1
fi

APTARCHIVE=apt-ftparchive
DEBDIR=$(pwd)
if ! hash APTARCHIVE 2>/dev/null
then
    APTARCHIVE="docker run --rm --entrypoint /usr/bin/apt-ftparchive -v $(pwd):/tmp/deb -w /tmp/deb -it raphaelm/ci-pretixdesk-apt"
    DEBDIR=/tmp/deb
fi
$APTARCHIVE packages . > Packages
gzip -k9 Packages
$APTARCHIVE release . > Release
gpg --output Release.gpg -u support-executables@pretix.eu -ba Release

popd
