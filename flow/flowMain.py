# !/usr/bin/env python

# [Future imports]
# "print" function compatibility between Python 2.x and 3.x
from __future__ import print_function
# Use Python 3.x "/" for division in Pyhton 2.x
from __future__ import division

# [File header]     | Copy and edit for each file in this project!
# title             : flowMain.py
# description       : Microfluidic Control - Flow module - Main
# author            : Bjorn Harink
# credits           : Kurt Thorn, Huy Nguyen
# date              : 20160308
# version update    : 20161021
# version           : v0.4.0
# usage             : As module
# notes             : Do not quick fix functions for specific needs, keep them general!
# python_version    : 2.7

# [Modules]
# General Python
import warnings
import importlib
# GUI
import wx
# Project
import config
import flowGui

class Control(object):
    """"""
    def __init__(self, parent, config):
        self.config = config
        self.parent = parent

        var = self.config.hware['flowing']['hardware']
        self.flow_module = importlib.import_module("flow."+var+"Wrapper")
        self.control = self.flow_module.Load(self.config.hware['flowing']['config'])
        self.control.connect()
        if self.control.status is not None:
            self.gui = flowGui.MainWindow(self.parent, self.config, self.control)

    def __repr__(self):
        return repr([self.control])


