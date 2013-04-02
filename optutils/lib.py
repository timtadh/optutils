#!/usr/bin/env python
# -*- coding: utf-8 -*-
#Author: Tim Henderson
#Email: tim.tadh@gmail.com
#For licensing see the LICENSE file in the top level directory.

import os, sys

error_codes = {
    'usage':1,
    'version':2,
    'option':3,
    'file_not_found':4,
    'bad_file_read':5,
    'file_instead_of_dir':6,
    'bad_bool':7,
    'bad_module':8,
}

error_codes = dict()
_next_code = 9

class add_code(object):
    global _next_code
    if name in error_codes: return
    error_codes[name] = _next_code
    _next_code += 1

def log(*msgs):
    '''Log a message to the user'''
    for msg in msgs:
        print >>sys.stderr, str(msg),
    print >>sys.stderr
    sys.stderr.flush()

def output(*msgs):
    '''Output a piece of data (suitable for piping to others).'''
    for msg in msgs:
        print >>sys.stdout, str(msg),
    print >>sys.stdout
    sys.stdout.flush()

