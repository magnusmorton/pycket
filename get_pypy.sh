#!/usr/bin/env bash

if [ ! -d "pypy" ]; then
    hg clone https://bitbucket.org/pypy/pypy
fi
    
cd pypy
hg up -r release-5.1.2
patch < ../counters_workaround.patch -p1
cd -

