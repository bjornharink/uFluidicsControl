# !/usr/bin/env python

# [Future imports]
# "print" function compatibility between Python 2.x and 3.x
from __future__ import print_function
# Use Python 3.x "/" for division in Pyhton 2.x
from __future__ import division

# [File header]     | Copy and edit for each file in this project!
# title             : baseMain.py
# description       : Microfluidic Control - Base - Main
# author            : Bjorn Harink
# credits           : Kurt Thorn, Huy Nguyen
# date              : 20150901
# version update    : 20160808
# version           : v0.4.0
# usage             : Start program with this file
# notes             : 
# python_version    : 2.7

# [Main header with project metadata] | Only in the main file!
# Copyright and credits
__copyright__   = ("Copyright University of California 2016 - "
                   "The Encoded Beads Project - "
                   "ThornLab@UCSF and "
                   "FordyceLab@Stanford")
# Original author(s) of this Python project, like: ("...", 
__author__      = ("Bjorn Harink")  #               "name")
# People who contributed to this Python project, like: ["...",
__credits__     = ["Kurt Thorn",  #                     "name"] 
                   "Huy Nguyen", 
                   "Brain Baxter"]
# Maintainer contact information
__maintainer__  = "Bjorn Harink" 
__email__       = "bjorn@harink.info" 
# Software information
__license__     = "MIT" 
__version__     = "v1.0.0"
__status__      = "Development"

# [TO-DO]

# [Modules]
# General Python
import sys
import os
import types
import warnings
import time
#import thread
#from threading import Thread as thread
# GUI
import wx
# Project | specific project modules
import baseGui
import valve
import flow
import config as cfg
import hware
import collect
import image

#import win32com.client
#win32com.client.pythoncom.CoInitialize()

# [SETTINGS]
STATUS_ON = wx.Colour(138,212,153)
STATUS_OFF = wx.Colour(238,208,208)
DEFAULT_CHIP = "DEFAULT"

class ModuleHandler(object):
    def __init__(self, parent, config):
        self.parent = parent
        self.config = config

        self.valving = valve.Control(self.parent, self.config)
        if self.valving.control.status is not None:
            self.parent.hPanel.checkValve.SetBackgroundColour(STATUS_ON)
            self.parent.hPanel.checkValve.Bind(wx.EVT_BUTTON, self.valving.gui.show)
        else:
            self.parent.hPanel.checkValve.SetBackgroundColour(STATUS_OFF)

        self.flowing = flow.Control(self.parent, self.config)
        if all(self.flowing.control.status) is True:
            self.parent.hPanel.checkFlow.SetBackgroundColour(STATUS_ON)
            self.parent.hPanel.checkFlow.Bind(wx.EVT_BUTTON, self.flowing.gui.show)
        else:
            self.parent.hPanel.checkFlow.SetBackgroundColour(STATUS_OFF)

        self.collecting = collect.Control(self.parent, self.config)
        if self.collecting.control.status is True:
            self.parent.hPanel.checkCollect.SetBackgroundColour(STATUS_ON)
            self.parent.hPanel.checkCollect.Bind(wx.EVT_BUTTON, self.collecting.gui.show)
        else:
            self.parent.hPanel.checkCollect.SetBackgroundColour(STATUS_OFF)

        #self.imaging = image.Control(self.parent, self.config)
        #if self.collect.control.status is True:
        #    self.parent.hPanel.checkCollect.SetBackgroundColour(STATUS_ON)
        #self.parent.hPanel.checkImage.Bind(wx.EVT_BUTTON, self.imaging.gui.show)
        #else:
        #    self.parent.hPanel.checkCollect.SetBackgroundColour(STATUS_OFF)

def main():
    print(__copyright__)

    config_handler = cfg.ConfigHandler(DEFAULT_CHIP)

    wxapp = wx.App()
    locale = wx.Locale(wx.LANGUAGE_ENGLISH)

    main_gui = baseGui.MainWindow(None, config_handler)

    module_handler = ModuleHandler(main_gui, config_handler)

    main_gui.Show(True)

    wxapp.MainLoop()
    
    return 0

# Main loop
if __name__ == '__main__':
    status = main()
    sys.exit(status)
