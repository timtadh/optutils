#!/usr/bin/env python
# -*- coding: utf-8 -*-
#Author: Tim Henderson
#Email: tim.tadh@gmail.com
#For licensing see the LICENSE file in the top level directory.

import os, sys, functools
from getopt import getopt, GetoptError

from .lib import log, error_codes

def format_long(msg):
    def count_spaces(line):
        count = 0
        for c in line:
            if c == ' ': count += 1
            else: break
        return count
    def strip(line, count):
        start = 0
        for c in line:
            if start >= count: break
            elif c == ' ': start += 1
            else: break
        return line[start:]
    formatted = list()
    lines = msg.split('\n')
    n_spaces = count_spaces(lines[1])
    return '\n'.join(strip(line, n_spaces) for line in lines)


def parse_args(short_opts, long_opts, util):
    def parse_args(argv):
        try:
            opts, args = getopt(argv, short_opts, long_opts)
        except GetoptError, err:
            util.log(err)
            util.usage(error_codes['option'])
        return opts, args
    return parse_args

def make_command(commands, logf):
    def command(short_msg, long_message, short_opts, long_opts):
        util = Util(short_msg, format_long(long_message), logf)
        parser = parse_args(short_opts, long_opts, util)
        def command(f):
            @functools.wraps(f)
            def run_command(argv, *args, **kwargs):
                return f(argv, util, parser, *args, **kwargs)
            if commands is not None:
                commands[f.func_name] = run_command
            setattr(run_command, 'util', util)
            return run_command
        return command
    return command

main = make_command(None, log)
custom_log_main = lambda logf: make_command(None, logf)

class Util(object):

    def __init__(self, short_msg, long_msg, logf):
        self.log = logf
        self.short_msg = short_msg
        self.long_msg = long_msg
        self.commands = dict()
        self.command = make_command(self.commands, self.log)

    def run_command(self, argv, *args, **kwargs):
        if len(argv) < 1:
            self.log("you must supply a command you gave:", str(argv))
            self.log(str(self.commands.keys()))
            self.usage(error_codes['option'])
        command_name = argv[0].replace('-', '_')

        if command_name in self.commands:
            self.commands[command_name](argv[1:], *args, **kwargs)
        else:
            self.log("no such command %s" % command_name)
            self.log(str(self.commands.keys()))
            self.usage(error_codes['option'])

    def usage(self, code=None):
        '''Prints the usage and exits with an error code specified by code. If
        code is not given it exits with error_codes['usage']'''
        self.log(self.short_msg)
        if code is None:
            self.log(self.long_msg)

            if self.commands:
                self.log()
                self.log('Commands')
                for name, cmd in self.commands.iteritems():
                    self.log(' '*4, "%-15s" % name, ' '*12, cmd.util.short_msg[:50])
                self.log()
            code = error_codes['usage']
        sys.exit(code)

    def assert_file_exists(self, path):
        '''checks if the file exists. If it doesn't causes the program to exit.
        @param path : path to file
        @returns : the abs path to the file (an echo) [only on success]
        '''
        path = os.path.abspath(os.path.expanduser(path))
        if not os.path.exists(path):
            self.log('No file found. "%(path)s"' % locals())
            self.usage(error_codes['file_not_found'])
        return path

    def assert_dir_exists(self, path, nocreate=False):
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
            self.log('No directory exists at location "%(path)s"' % locals())
            self.usage(error_codes['file_not_found'])
        elif not os.path.exists(path):
            os.mkdir(path)
        elif not os.path.isdir(path):
            self.log('Expected a directory found a file. "%(path)s"' % locals())
            self.usage(error_codes['file_instead_of_dir'])
        return path

    def assert_in(self, obj, collection):
        '''checks if the obj in in the collection. dies if not.
        @param obj : an object
        @param collection : must support the "in" operator
        @returns : the obj
        '''
        if obj not in collection:
            self.log("obj '%s' not in %s" % (str(obj), str(collection)))
            self.usage(error_codes['not_in_collection'])
        return obj

    def read_file_or_die(self, path):
        '''Reads the file, if there is an error it kills the program.
        @param path : the path to the file
        @returns string : the contents of the file
        '''
        path = self.assert_file_exists(path)
        try:
            f = open(path, 'r')
            s = f.read()
            f.close()
        except Exception:
            self.log('Error reading file at "%s".' % path)
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
            self.log(e.message)
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

