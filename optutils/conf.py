#!/usr/bin/env python
# -*- coding: utf-8 -*-
#Author: Tim Henderson
#Email: tadh@case.edu
#Copyright (C) 2012 All Rights Reserved
#For licensing see the LICENSE file in the top level directory.

import sys, os, json, collections
import cStringIO as sio

UNDEFINED_KEYS = '__undefinedkeys__'

class ConfigError(Exception): pass

def encode(d):
    new = dict()
    for k,v in d.iteritems():
        if isinstance(v, list):
            l = list()
            for i in v:
                if isinstance(i, unicode):
                    l.append(i.encode('utf-8'))
                else:
                    l.append(i)
            v = l
        if isinstance(k, unicode): k = k.encode('utf-8')
        if isinstance(v, unicode): v = v.encode('utf-8')
        new[k] = v
    return new

def json_parser(file_path):
    with open(file_path, 'rb') as f:
        return json.load(f, object_hook=encode)

def strbool(*args):
    if not args:
        return False
    arg = args[0]
    if isinstance(arg, bool):
        return arg
    arg = arg.lower()
    if arg == 'true':
        return True
    elif arg == 'false':
        return False
    raise Exception, '"%s" is not true or false' % arg

default_types = {
    'str': str,
    'bool': strbool,
    'int': int,
    'float': float,
}

class Section(collections.Mapping):

    def __init__(self, d):
        object.__setattr__(self, '_d', d)

    def __repr__(self):
        return str(self._d)

    def __getattribute__(self, name):
        if name == '_d':
            return super(Section, self).__getattribute__(name)
        if name in self._d:
            return self._d[name]
        return super(Section, self).__getattribute__(name)

    def __setattr__(self, name, value):
        if name in self._d:
            raise TypeError, "Section does not support item assignment"
        return super(Section, self).__setattr__(name, value)

    def __contains__(self, name):
        return name in self._d

    def __iter__(self):
        return self._d.iterkeys()

    def __len__(self):
        return len(self._d)

    def __getitem__(self, name):
        return self._d[name]

class BaseConfig(object):

    def __new__(cls, schema, *paths, **kwargs):
        '''Base Config

        :param schema: the schema the files must match
        :param *paths: a list of paths to try to read from (and cascade)
        :param local_updates={}: a dictionary which matches the schema to apply
                                 after all paths. Useful for over-riding values
                                 from command line params.
        :param types=default_types: a dictionary (string->type-func) which maps
                                    schema strings to the desired python type.
                                    These functions should take a string and
                                    parse it into a python type. If no argument
                                    is given they should provide a default
                                    value. If there is a parsing error it should
                                    simply raise an exception.
        :param parser=json_parser: a function file_path -> dict(). By default
                                   this speaks JSON. Using this you can
                                   override that with another language. Just
                                   make sure it outputs JSON compatible
                                   dictionaries.
        '''
        self = super(BaseConfig, cls).__new__(cls)
        self._d = dict()
        self.schema = schema
        self.paths = paths
        self.types = kwargs.get('types', default_types)
        self.parser = kwargs.get('parser', json_parser)
        local_updates = kwargs.get('local_updates', None)

        conf_dicts = self.__process_paths(paths)
        if local_updates is not None:
            self.__process_dict(conf_dicts, 'local_updates', local_updates, None)

        self._d = self._cascade(conf_dicts)

        self.errors = list()
        for d in conf_dicts:
            if d['err'] != None:
                if not isinstance(d['err'], list):
                    self.errors.append(d['path'] + ' - ' + d['err'])
                    continue
                for err in d['err']:
                    self.errors.append(d['path'] + ' - ' + err)


        no_good_conf = all(
            d['ok'] == False
            for d in conf_dicts
            if d['path'] is not 'skeleton'
        )

        if no_good_conf:
            raise ConfigError('no good configuration found', *self.errors)

        return self

    def __init__(self, schema, *paths, **kwargs):
        self._expose_dict()

    def __process_paths(self, paths):
        conf_dicts = [
          {'ok':True, 'path':'skeleton', 'conf':self._skeleton(), 'err':None},
        ]
        for file_path in paths:
            if os.path.exists(file_path):
                d = None
                err = None
                try:
                    d = self.parser(file_path)
                except Exception, e:
                    err = 'file did not parse. ' + ', '.join(e.args)
                self.__process_dict(conf_dicts, file_path, d, err)
            else:
                self.__process_dict(
                    conf_dicts, file_path, None,
                    'File %s did not exist' % file_path
                )
        return conf_dicts

    def __process_dict(self, conf_dicts, file_path, d, err):
          if err == None:
              err = self._validate(d)
          if err == None :
              conf_dicts.append({
                'ok':True,
                'path':file_path,
                'conf':d,
                'err':None,
              })
          else:
              conf_dicts.append({
                'ok':False,
                'path':file_path,
                'conf':dict(),
                'err':err,
              })

    def __getattribute__(self, name):
        if name == '_d' or name == '_exposed':
            return object.__getattribute__(self, name)

        if name in self._d:
            return self._exposed.__getattribute__(name)
        return super(BaseConfig, self).__getattribute__(name)

    def __getitem__(self, name):
        return self._exposed.__getattribute__(name)

    def __contains__(self, name):
        return name in self._exposed

    def __repr__(self):
        return str(self._d)

    def keys(self):
        return self._d.keys()

    def update(self, d):
        '''
        A localized configuration options specific to this run. Cascade them
        down onto the current configurator and re-expose.
        @param d : the dict of new configuration options
        '''
        err = self._validate(d)
        if err:
            raise ConfigError('update did not validate', *err)

        self._d = self._cascade([
          {'ok':True, 'path':'current', 'conf':self._d},
          {'ok':True, 'path':'new_mixin', 'conf':d}
        ])
        self._expose_dict()

    ## ## private methods ## ##
    def _expose_dict(self):

        def proc(v):
            if isinstance(v, dict):
                return procdict(v)
            elif isinstance(v, list):
                return proclist(v)
            else:
                return v

        def proclist(l):
            return tuple([
                proc(v)
                for v in l
            ])

        def procdict(d):
            a = dict(
                (k, proc(v))
                for k,v in d.iteritems()
            )
            return Section(a)

        self._exposed = procdict(self._d)

    def _skeleton(self):
        '''
        produce a skeleton dictionary from the schema (with nones for values)
        '''
        def proc(t):
            if   isinstance(t, dict):
                return procdict(t, dict())
            elif isinstance(t, list):
                return list()
            else:
                return self.gettype(t)()
        def procdict(t, d):
            if UNDEFINED_KEYS in t:
                return dict()
            for k,v in t.iteritems():
                d[k] = proc(v)
            return d
        return procdict(self.schema, dict())

    def gettype(self, s):
        '''transform a string into a type'''
        if s in self.types:
            return self.types[s]
        raise Exception, 'Type %s unsupported' % s

    def _validate(self, d, allow_none=False):
        '''
        Assert that d matches the schema

        :param d: the dictionary
        :param allow_none: allow Nones in d
        :returns: errors, which will be None if there were no errors.
        '''

        errors = list()

        def add_error(path, msg):
            errors.append("%s/ - %s" % (path, msg))

        def proc(v1, v2, path):
            '''process 2 values assert they are of the same type'''
            if   isinstance(v1, dict):
                procdict(v1, v2, path)
            elif isinstance(v1, list):
                proclist(v1, v2, path)
            else:
                try:
                    self.gettype(v1)(v2)
                except Exception, e:
                    add_error(path, ', '.join(e.args))

        def proclist(t, d, path):
            '''process a list type'''
            if len(t) != 1:
                msg = "A list schema should have only one item. Got " + str(t)
                add_error(path, msg)
            if not isinstance(d, list):
                msg = ("Expected a list got %s" % type(d))
                add_error(path, msg)
                return
            v1 = t[0]
            for i, v2 in enumerate(d):
                proc(v1, v2, os.path.join(path, str(i)))

        def procdict(t, d, path):
            '''process a dictionary type'''
            if not isinstance(d, dict):
              msg = (
                "Expected a dict got %s, '%s'\n %s %s" %
                (type(d), str(d), str(t), str(d))
              )
              add_error(path, msg)
              return
            tkeys = set(t.keys())
            dkeys = set(d.keys())
            if UNDEFINED_KEYS in tkeys:
                if len(tkeys) != 1:
                    msg = (
                        "A dict schema with __undefinedkeys__ should have "
                        "only one item. Got " + str(t)
                    )
                    add_error(path, msg)
                    return
                v1 = t[UNDEFINED_KEYS ]
                for k, v2 in d.iteritems():
                    proc(v1, v2, os.path.join(path, k))
            else:
                badkeys = set()
                for k in dkeys:
                    if k not in tkeys:
                        msg = (
                          "Unexpected name, '%s'. The name must be in %s"
                        ) % (k, str(list(tkeys)))
                        add_error(path, msg)
                        badkeys.add(k)
                for k in dkeys:
                    if k in badkeys:
                        continue
                    v1 = t[k]
                    v2 = d[k]
                    proc(v1, v2, os.path.join(path, k))

        proc(self.schema, d, '/')
        if len(errors) == 0:
            return None
        return errors

    def _cascade(self, dicts):
        '''
        cascades the configurations on top of one another.
        @param dicts = a sequence of dictionaries
        '''

        def template(t, k):
            if UNDEFINED_KEYS in t:
                return t[UNDEFINED_KEYS]
            return t[k]

        def gettype(item):
            if isinstance(item, dict):
                return dict
            elif isinstance(item, list):
                return list
            return self.gettype(item)

        def proc(t, a, v):
            if isinstance(v, dict):
                return procdict(t, a, v)
            elif isinstance(v, list):
                return proclist(t, a, v)
            else:
                return gettype(t)(v)

        def proclist(t, a, d):
            return [
                proc(t[0], gettype(t[0])(), v)
                for v in d
            ]

        def procdict(t, a, d):
            for k,v in d.iteritems():
                item = template(t, k)
                a[k] = proc(item, a.get(k, gettype(item)()), v)
            return a

        conf = dict()
        for d in dicts:
            if d['ok']:
                procdict(self.schema, conf, d['conf'])
        return conf

