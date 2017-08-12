# !/usr/bin/env python

# [Future imports]
# "print" function compatibility between Python 2.x and 3.x
from __future__ import print_function
# Use Python 3.x "/" for division in Pyhton 2.x
from __future__ import division

# [File header]     | Copy and edit for each file in this project!
# title             : imageMain.py
# description       : Microfluidic Control - Image module - Main
# author            : Bjorn Harink
# credits           : Kurt Thorn, Huy Nguyen
# date              : 20160308
# version update    : 20161212
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
import imageGui

class Control(object):
    """"""
    def __init__(self, parent, config):
        self.config = config
        self.parent = parent

        var = self.config.hware['imaging']['hardware']
        self.image_module = importlib.import_module("image."+var+"Wrapper")
        self.control = self.image_module.Load(*self.config.hware['imaging']['config'])
        self.control.connect()
        if self.control.status is not None:
            self.gui = imageGui.MainWindow(self.parent, self.config, self.control)

    def __repr__(self):
        return repr([self.control])


