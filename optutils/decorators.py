#!/usr/bin/env python
# -*- coding: utf-8 -*-
#Author: Tim Henderson
#Email: tim.tadh@gmail.com
#For licensing see the LICENSE file in the top level directory.

import os, sys, functools, subprocess
from getopt import getopt, GetoptError
import json, csv

from optutil.util import Util

commands = dict()

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
            log(err)
            util.usage(error_codes['option'])
        return opts, args
    return parse_args

def __command(main):
    def command(short_msg, long_message, short_opts, long_opts):
        util = Util(short_msg, long_message)
        parser = parse_args(short_opts, long_opts, usage)
        def command(f):
            @functools.wraps(f)
            def run_command(argv, *args, **kwargs):
                return f(argv, util, parser, *args, **kwargs)
            if not main:
                commands[f.func_name] = run_command
            return run_command
        return command
    return command

command = __command(False)
main = __command(True)

def run_command(argv, commands, util, *args, **kwargs):
    if len(argv) < 1:
        log("you must supply a command you gave:")
        log("    ", str(argv))
        util.usage(error_codes['option'])
    command_name = argv[0].replace('-', '_')

    if command_name in commands:
        commands[command_name](argv[1:], *args, **kwargs)
    else:
        log("no such command %s" % command_name)
        util.usage(error_codes['option'])

