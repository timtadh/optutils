#!/usr/bin/env python
# -*- coding: utf-8 -*-
#Author: Tim Henderson
#Email: tadh@case.edu
#Copyright (C) 2012 All Rights Reserved
#For licensing see the LICENSE file in the top level directory.

import sys, os, json, collections
import cStringIO as sio

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

def make_list_get(d, key):
    def get(self):
        return [
            Section(i) for i in d[key] if isinstance(i, dict)
        ] + [
            i for i in d[key] if not isinstance(i, dict)
        ]
    return get
def make_sec_get(d, key):
    def get(self):
        return Section(d[key])
    return get
def make_val_get(d, key):
    def get(self):
        return d[key]
    return get
def _set(self,k,v): raise RuntimeError, 'Operation Not Supported'
def _del(self): raise RuntimeError, 'Operation Not Supported'

class Section(collections.Mapping):

    def __init__(self, d):
        object.__setattr__(self, '_d', d)

        for k,v in d.iteritems():
            if not (isinstance(v, dict) or isinstance(v, list)):
                p = property(make_val_get(d, k),_set,_del,
                    'Property for interacting with "%s"' % k)
            elif isinstance(v, dict):
                p = property(make_sec_get(d, k),_set,_del,
                    'Property for interacting with "%s"' % k)
            elif isinstance(v, list):
                p = property(make_list_get(d, k),_set,_del,
                    'Property for interacting with "%s"' % k)
            object.__setattr__(self, k, p)

    def __repr__(self):
        l = list()
        for name in dir(self):
            a = object.__getattribute__(self, name)
            if type(a) == property: l.append((name, str(a.fget(self))))

        return str(dict(l))

    def __getattribute__(self, name):
        if type(object.__getattribute__(self, name)) == property:
            return object.__getattribute__(self, name).fget(self)
        return object.__getattribute__(self, name)

    def __contains__(self, name):
        return name in self._d

    def __iter__(self):
        return self._d.iterkeys()

    def __len__(self):
        return len(self._d)

    def __getitem__(self, name):
        return self.__getattribute__(name)

def json_parser(file_path):
    with open(file_path, 'rb') as f:
        try:
            return json.load(f, object_hook=encode)
        except ValueError, e:
            msg = (
                "The config file at '%s' appears to be corrupted." %
                file_path
            )
            raise ConfigError(msg)

class BaseConfig(object):

    def __new__(cls, schema, *paths, **kwargs):
        '''Base Config

        :param schema: the schema the files must match
        :param *paths: a list of paths to try to read from (and cascade)
        :param local_updates={}: a dictionary which matches the schema to apply
                                 after all paths. Useful for over-riding values
                                 from command line params.
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
        self.parser = kwargs.get('parser', json_parser)
        conf_dicts = self.__process_paths(paths)
        local_updates = kwargs.get('local_updates', None)
        if local_updates is not None:
            self._matches(local_updates)
            conf_dicts.append({'ok':True, 'path':'local_updates',
              'conf':local_updates})
        self._d = self._cascade(conf_dicts)
        if all(d['ok'] == False
              for d in conf_dicts
              if d['path'] is not 'skeleton'):
            raise ConfigError, 'no good configuration found'
        return self

    def __init__(self, schema, *paths, **kwargs):
        self._expose_dict()

    def __process_paths(self, paths):
        conf_dicts = [{'ok':True, 'path':'skeleton', 'conf':self._skeleton()}]
        for file_path in paths:
            if os.path.exists(file_path):
                d = self.parser(file_path)
                self._matches(d)
                conf_dicts.append({
                  'ok':True,
                  'path':file_path,
                  'conf':d
                })
            else:
                conf_dicts.append({
                  'ok':False,
                  'path':file_path,
                  'conf':self._skeleton()})
        return conf_dicts

    def __getattribute__(self, name):
        if name == '_d' or name == '_exposed':
            return object.__getattribute__(self, name)

        if name in self._d:
            return self._exposed.__getattribute__(name)
        return super(BaseConfig, self).__getattribute__(name)

    def __getitem__(self, name):
        return self._d[name]

    def keys(self):
        return self._d.keys()

    ## public methods ## ##
    def write_conf(self, file_path):
        self._matches(self._d)
        with open(file_path, 'wb') as f:
            json.dump(self._d, f, indent=4)

    def update(self, d):
        '''
        A localized configuration options specific to this run. Cascade them
        down onto the current configurator and re-expose.
        @param d : the dict of new configuration options
        '''
        self._matches(d)
        self._d = self._cascade([
          {'ok':True, 'path':'current', 'conf':self._d},
          {'ok':True, 'path':'new_mixin', 'conf':d}
        ])
        self._expose_dict()

    ## ## private methods ## ##
    def _expose_dict(self):
        self._exposed = Section(self._d)

    def _skeleton(self):
        '''
        produce a skeleton dictionary from the schema (with nones for values)
        '''
        def getdefault(s):
            '''transform a string into a type'''
            if   s == 'str'  : return str()
            elif s == 'int'  : return 0
            elif s == 'float': return 0.0
            elif s == 'bool' : return False
            raise Exception, 'Type %s unsupported' % s
        def proc(t):
            if   isinstance(t, dict):
                return procdict(t, dict())
            elif isinstance(t, list):
                return list()
            else:
                return getdefault(t)
        def procdict(t, d):
            if '__undefinedkeys__' in t:
                return dict()
            for k,v in t.iteritems():
                d[k] = proc(v)
            return d
        return procdict(self.schema, dict())

    def _matches(self, d, allow_none=False):
        '''
        Assert that d matches the schema
        @param d = the dictionary
        @param allow_none = allow Nones in d
        '''
        def gettype(s):
            '''transform a string into a type'''
            if   s == 'str'  : return str
            elif s == 'list' : return list
            elif s == 'dict' : return dict
            elif s == 'int'  : return int
            elif s == 'float': return float
            elif s == 'bool' : return bool
            raise Exception, 'Type %s unsupported' % s
        def proc(v1, v2):
            '''process 2 values assert they are of the same type'''
            #print 'proc>', v1, v2
            if   isinstance(v1, dict):
                procdict(v1, v2)
            elif isinstance(v1, list):
                proclist(v1, v2)
            else:
                if allow_none and v2 is None: return
                type_ = gettype(v1)
                try:
                    assert isinstance(v2, type_)
                except:
                    msg = ("%s must be of type %s, got type %s" %
                            (v2, type_, str(type(v2))))
                    raise AssertionError, msg
        def proclist(t, d):
            '''process a list type'''
            assert len(t) == 1
            if not isinstance(d, list):
                msg = ("Expected a <type 'list'> got %s" % type(d))
                raise AssertionError, msg
            v1 = t[0]
            for v2 in d:
                #print v1, v2
                proc(v1, v2)
        def procdict(t, d):
            '''process a dictionary type'''
            if not isinstance(d, dict):
              raise AssertionError, "Expected a <type 'dict'> got %s, '%s'\n %s %s"\
                                      % (type(d), str(d), str(t), str(d))
            tkeys = set(t.keys());
            dkeys = set(d.keys());
            if '__undefinedkeys__' in tkeys:
                v1 = t['__undefinedkeys__']
                for v2 in d.values():
                    proc(v1, v2)
            else:
                for k in dkeys:
                    try: assert k in tkeys
                    except:
                        msg = (
                          'Unexpected name, "%s". The name must be in %s'
                        ) % (k, str(tkeys))
                        raise AssertionError, msg
                for k in dkeys:
                    #print '> ', k
                    v1 = t[k]
                    v2 = d[k]
                    proc(v1, v2)
        proc(self.schema, d)

    def _cascade(self, dicts):
        '''
        cascades the configurations on top of one another.
        @param dicts = a sequence of dictionaries
        '''
        def aply(a,k,v):
            '''applys the key value to the collection a with the name name'''
            a[k] = v
        def proc(a,k,v):
            '''processes the item a'''
            if isinstance(v, dict):
                if k not in a or not isinstance(a[k], dict): a[k] = dict()
                procdict(a[k], v)
            else:
                aply(a,k,v)
        def procdict(a, d):
            for k,v in d.iteritems():
                proc(a,k,v)
        conf = dict()
        for d in dicts:
            if d['ok']:
                procdict(conf, d['conf'])
        return conf

