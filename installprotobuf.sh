#!/bin/bash
PYVERSION=`python3 --version 2>&1 | cut -d' ' -f2 | cut -d. -f1-2`
PREFIX=/usr/local
if [ `whoami` != root ] ; then
    echo 'Must run as root!'
    exit 1
fi
cd /tmp
version="3.0.0-beta-2"
archive="protoc-$version-linux-x86_$(getconf LONG_BIT).zip"
wget "https://github.com/google/protobuf/releases/download/v$version/$archive"
unzip "$archive"
mkdir -p /usr/local/bin
mkdir -p /usr/local/include
cp protoc /usr/local/bin
chmod 755 /usr/local/bin/protoc
cp -r google /usr/local/include
find /usr/local/include/google -type d | xargs chmod 755
find /usr/local/include/google -type f | xargs chmod 644
rm -rf protoc google readme.txt "$archive"

archive="protobuf-python-$version.tar.gz"
wget "https://github.com/google/protobuf/releases/download/v$version/$archive"
tar -xf "$archive"
cd "protobuf-$version/python"
python3 setup.py build
python3 setup.py install
find /usr/local/include/google -name '*.proto' \
    | xargs protoc "--proto_path=$PREFIX/include" "--python_out=$PREFIX/lib/python$PYVERSION/dist-packages"
cd ../..
rm -rf "protobuf-$version" "$archive"
