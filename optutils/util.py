#!/usr/bin/env python
# -*- coding: utf-8 -*-
#Author: Tim Henderson
#Email: tim.tadh@gmail.com
#For licensing see the LICENSE file in the top level directory.

import os, sys

from optutils.lib import log, error_codes

def make_usage(short, long_msg):
    return usage

class Util(object):

    def __init__(self, short_msg, long_msg):
        self.short_msg = short_msg
        self.long_msg = long_msg
        self.usage = make_usage(short, long_msg)

    def usage(self, code=None):
        '''Prints the usage and exits with an error code specified by code. If
        code is not given it exits with error_codes['usage']'''
        log(self.short_msg)
        if code is None:
            log(self.long_msg)
            code = error_codes['usage']
        sys.exit(code)

    def assert_file_exists(path):
        '''checks if the file exists. If it doesn't causes the program to exit.
        @param path : path to file
        @returns : the abs path to the file (an echo) [only on success]
        '''
        path = os.path.abspath(os.path.expanduser(path))
        if not os.path.exists(path):
            log('No file found. "%(path)s"' % locals())
            self.usage(error_codes['file_not_found'])
        return path

    def assert_dir_exists(path, nocreate=False):
        '''checks if a directory exists. if not it creates it. if something
        exists and it is not a directory it exits with an error.
        @param path : path to file
        @param nocreate : boolean flag, if false will create the directory (if
                          it doesn't exist) if true will not create the
                          directory
        @returns : the abs path to the directory
        '''
        path = os.path.abspath(path)
        if not os.path.exists(path) and nocreate:
            log('No directory exists at location "%(path)s"' % locals())
            self.usage(error_codes['file_not_found'])
        elif not os.path.exists(path):
            os.mkdir(path)
        elif not os.path.isdir(path):
            log('Expected a directory found a file. "%(path)s"' % locals())
            self.usage(error_codes['file_instead_of_dir'])
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
            self.usage(error_codes['bad_file_read'])
        return s

    def parse_int(self, s):
        '''Try and parse and int. die on failure.
        @param s : a string
        @returns int
        '''
        try:
            return int(s)
        except ValueError, e:
            log(e.message)
            self.usage(error_codes['bad_int'])

    def getfile(self, path, mode, default):
        '''Get a file from either a path + mode or return a default file. If
        path is None it uses the default. This is useful if you want to either
        use the standard in or read from a file. This will not validate the path
        so do that first.

        ex.
            path = None
            if len(argv) > 1:
                path = argv[1]

            with getfile(path, "r", sys.stdin) as f:
                data = parse_my_file(f)

        @param path : either None or a valid path.
        @param mode : the open mode
        @param default : a file like object
        @returns a file like object
        '''
        if path is None:
            return default
        else:
            return open(path, mode)

