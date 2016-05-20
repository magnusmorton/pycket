#!/usr/bin/env bash

if [ ! -d "pypy" ]; then
    hg clone https://bitbucket.org/pypy/pypy
fi
    
cd pypy
hg up release-5.1.2
cd -

