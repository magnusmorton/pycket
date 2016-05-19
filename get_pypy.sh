#!/usr/bin/env bash

if [ -d "pypy" ]; then
    cd pypy
    hg up
    cd -
else
   hg clone https://bitbucket.org/pypy/pypy
fi
