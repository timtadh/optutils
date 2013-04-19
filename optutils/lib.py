#!/usr/bin/env python
# -*- coding: utf-8 -*-
#Author: Tim Henderson
#Email: tim.tadh@gmail.com
#For licensing see the LICENSE file in the top level directory.

import os, sys

error_codes = {
    'usage':1,
    'option':2,
    'file_not_found':3,
    'bad_file_read':4,
    'file_instead_of_dir':5,
    'bad_bool':6,
    'bad_module':7,
    'not_in_collection':8,
}
_next_code = 9

def add_code(name):
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

