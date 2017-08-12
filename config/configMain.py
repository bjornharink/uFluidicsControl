# !/usr/bin/env python

# [Future imports]
# "print" function compatibility between Python 2.x and 3.x
from __future__ import print_function
# Use Python 3.x "/" for division in Pyhton 2.x
from __future__ import division

# [File header]     | Copy and edit for each file in this project!
# title             : configMain.py
# description       : Microfluidic Control - Config module
# author            : Bjorn Harink
# credits           : Kurt Thorn, Huy Nguyen
# date              : 20150915
# version update    : 20160915
# version           : v0.4.0
# usage             : Use as main gui window
# notes             : 
# python_version    : 2.7


# [Modules]
# General Python
import warnings
import os
# Data
import glob
import json
from collections import OrderedDict
# GUI
import wx

# [SETTINGS]
CONFIG_FOLDER = "config"
CHIPS_FOLDER = "chips"
CHIPS_DEFAULT = "DEFAULT"
HARDWARE_FOLDER = "hware"

class ConfigHandler(object):
    def __init__(self, chip=None):
        self.main = FileLoad(CONFIG_FOLDER,'mainConfig.json')
        self.hware = FileLoad(HARDWARE_FOLDER,'hwareConfig.json')[self.main['profile']['hardware']]
        self.chip = Chip(chip)

class Chip(object):
    def __init__(self, chip=None):
        if chip is None:
            self._name = CHIPS_DEFAULT
        else:
            self._name = chip
        self._config = FileLoad(CHIPS_FOLDER+'//'+self._name,'chipConfig.json')

    def __repr__(self):
        return repr([self._config])

    def __getitem__(self, index):
        return self._config[index]

    def __setitem__(self, index, value):
        self._config[index] = value

    @property
    def name(self):
        return self._name
    @name.setter
    def name(self, value):
        self._name = value
        self._config = FileLoad(CHIPS_FOLDER+'//'+self._name,'chipConfig.json')
    
    @property
    def image(self):
        return FileLoad.newest_file(CHIPS_FOLDER +'//'+ self._name,'*.png')

    def update(self):
        self._config.update()

class FileLoad(object):
    def __init__(self, path, pattern):
        self._file_path = self.newest_file(path, pattern)
        self._data = self.json_load(self.file_path)

    def __getitem__(self, key):
        return self._data[key]

    def __setitem__(self, key, value):
        self._data[key] = value

    @property
    def all(self):
        return self._data.items()

    @property
    def keys(self):
        return self._data.keys()

    @property
    def file_path(self):
        return self._file_path

    @staticmethod
    def json_load(file_path):
        with open(file_path) as json_data_file:
            json_data = json.load(json_data_file, object_pairs_hook=OrderedDict)
        return json_data

    @staticmethod
    def newest_file(path, pattern):
        if os.path.exists(path):
            path = os.path.relpath(path)
        else:
            raise IOError('Path not found.')
        newest_file = max(glob.iglob('.\\' + path + '\\' + pattern), key=os.path.getctime)
        return newest_file

    @staticmethod
    def json_save(file_path, data):
        with open(file_path, 'w') as json_data_file:
            json.dump(data, json_data_file, indent=2, sort_keys=True)

    def update(self):
        self.json_save(self.file_path, self._data)

class WindowPosition(object):
    def __init__(self, window, config):
        self.window = window
        self.config = config
        self.name = self.window.GetTitle()
        self.check()

    @property
    def exist(self):
        return self._check

    def check(self):
        if self.name not in self.config['windows']:
            self.config['windows'][self.name] = {}
            self.config['windows'][self.name]['size'] = [100, 200]
            self.config['windows'][self.name]['position'] = [0, 0]
            self.config.update()
            self._check = False
        else:
            self.set()
            self._check = True

    def update(self):
        if not self._check:
            self.window.mainSizer.Fit(self.window)
            self._check = True
        self.config['windows'][self.name]['position'] = [self.window.GetPosition()[0], self.window.GetPosition()[1]]
        self.config['windows'][self.name]['size'] = [self.window.GetSize()[0], self.window.GetSize()[1]]
        self.config.update()

    def set(self):
        self.window.SetSize((self.config['windows'][self.name]['size']))
        self.window.SetPosition((self.config['windows'][self.name]['position']))