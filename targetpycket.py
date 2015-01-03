#! /usr/bin/env python
# -*- coding: utf-8 -*-
#

from rpython.jit.codewriter.policy import JitPolicy

from pycket.entry_point import target, get_additional_config_options, take_options
from pycket.hooks import PycketJitInterface

if __name__ == '__main__':
    from pycket.__main__ import main
    main()


def jitpolicy(driver):
    """Defines a JitPolicy for pycket"""
    return JitPolicy(PycketJitInterface())
#
