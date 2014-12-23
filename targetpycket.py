#! /usr/bin/env python
# -*- coding: utf-8 -*-
#

from pycket.entry_point import target, get_additional_config_options, take_options
from rpython.jit.codewriter.policy import JitPolicy


if __name__ == '__main__':
    from pycket.__main__ import main
    main()

#
def jitpolicy(driver):
    return JitPolicy()
