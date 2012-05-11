#!/usr/bin/env python
# -*- coding: utf-8 -*-
#Author: Tim Henderson
#Email: tim.tadh@hackthology.com
#For licensing see the LICENSE file in the top level directory.

import os, sys

# TODO: figure out how to supply:
# - log
# - output
# - usage
# - error_codes
# in a generic independent manner such that the client can override them (and
# doesn't have to supply the explicity everytime).

def assert_file_exists(path):
  '''checks if the file exists. If it doesn't causes the program to exit.
  @param path : path to file
  @returns : the abs path to the file (an echo) [only on success]
  '''
  path = os.path.abspath(os.path.expanduser(path))
  if not os.path.exists(path):
    log('No file found. "%(path)s"' % locals())
    usage(error_codes['file_not_found'])
  return path

def assert_dir_exists(path, nocreate=False):
  '''checks if a directory exists. if not it creates it. if something exists
  and it is not a directory it exits with an error.
  @param path : path to file
  @param nocreate : boolean flag, if false will create the directory (if it
                    doesn't exist) if true will not create the directory
  @returns : the abs path to the directory
  '''
  path = os.path.abspath(path)
  if not os.path.exists(path) and nocreate:
    log('No directory exists at location "%(path)s"' % locals())
    usage(error_codes['file_not_found'])
  elif not os.path.exists(path):
    os.mkdir(path)
  elif not os.path.isdir(path):
    log('Expected a directory found a file. "%(path)s"' % locals())
    usage(error_codes['file_instead_of_dir'])
  return path

def read_file_or_die(path):
  '''Reads the file, if there is an error it kills the program.
  @param path : the path to the file
  @returns string : the contents of the file
  '''
  path = assert_file_exists(path)
  try:
    f = open(path, 'r')
    s = f.read()
    f.close()
  except Exception:
    log('Error reading file at "%s".' % path)
    usage(error_codes['bad_file_read'])
  return s


