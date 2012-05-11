#!/usr/bin/env python
# -*- coding: utf-8 -*-
#Author: Tim Henderson
#Email: tim.tadh@hackthology.com
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

def version():
  '''Print version and exits'''
  log('fuzzbuzz version :', VERSION)
  sys.exit(error_codes['version'])

def usage(code=None):
  '''Prints the usage and exits with an error code specified by code. If code
  is not given it exits with error_codes['usage']'''
  log(short_usage_message)
  if code is None or code < 2:
    log(usage_message)
  if code is None:
    log(extended_message)
    code = error_codes['usage']
  sys.exit(code)

