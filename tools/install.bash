#!/bin/bash

#install Python3
#brew install python3
which python3
if [ $? -ne 0 ]
then
    echo "ERROR: not installed python3, please install python3 ver3.10 using pyenv"
    exit 1
fi

#MKDIRS
HAKO_LIBDIR=/usr/local/lib/hakoniwa
HAKO_BINDIR=/usr/local/bin/hakoniwa
if [ -d ${HAKO_LIBDIR} ]
then
    :
else
sudo    mkdir ${HAKO_LIBDIR}
fi

if [ -d ${HAKO_BINDIR} ]
then
    :
else
sudo    mkdir ${HAKO_BINDIR}
fi

#install libshakoc.dylib
OS_TYPE=`uname`
ARCH=`arch`
VERSION="1.0.4"

if [ "$OS_TYPE" = "Darwin" ]
then
    EXT="dylib"
else
    EXT="so"
fi

LIBNAME=libshakoc.${ARCH}.${EXT}
CMDNAME=hako-cmd.${ARCH}.${OS_TYPE}
wget https://github.com/toppers/hakoniwa-core-cpp-client/releases/download/${VERSION}/${LIBNAME}
wget https://github.com/toppers/hakoniwa-core-cpp-client/releases/download/${VERSION}/${CMDNAME}

sudo cp ${LIBNAME} ${HAKO_LIBDIR}/hakoc.so
sudo mv ${LIBNAME} ${HAKO_LIBDIR}/libshakoc.${EXT}
sudo mv ${CMDNAME} ${HAKO_BINDIR}/hako-cmd
sudo chmod +x ${HAKO_BINDIR}/hako-cmd
