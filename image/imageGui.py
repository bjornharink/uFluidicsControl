# !/usr/bin/env python

# [Future imports]
# "print" function compatibility between Python 2.x and 3.x
from __future__ import print_function
# Use Python 3.x "/" for division in Pyhton 2.x
from __future__ import division

# [File header]     | Copy and edit for each file in this project!
# title             : imageGui.py
# description       : Microfluidic Control - Image module - GUI
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
import time
import thread
import threading
# data
import numpy as np
# GUI
import wx
from wx.lib.masked import NumCtrl
# Project
import config

# [SETTINGS]


class MainWindow(wx.Frame):
    """This is the main window for the Image Module of the Microfluidic Control program.
    """
    def __init__(self, parent=None, config_handler=None, control=None):
        super(MainWindow, self).__init__(parent)
        self.SetTitle('Microfluidic Control - Image Module')
        # Parameters
        self.config = config_handler
        self.control = control
        self.current_chip = self.config.chip.name

        # Window Size/Postion Handler
        self.window_position = config.WindowPosition(self, self.config.main)

        self.init()

    def init(self):
        mainSizer = wx.BoxSizer(wx.HORIZONTAL)

        labelTube = wx.Button(self, name='labelTube', label='Go to tube #:', style=wx.TR_SINGLE)
        mainSizer.Add(labelTube, 1, wx.RIGHT|wx.ALIGN_CENTER, 5)
        self.tubeNo = NumCtrl(self, name = 'gotoTube', value = 1, integerWidth = 2, allowNegative = False, min = 1, max = 99, 
                                fractionWidth = 0, groupDigits = False, autoSize = False, style = wx.TR_SINGLE|wx.CENTER, size = (29,-1))
        mainSizer.Add(self.tubeNo, 1, wx.ALL|wx.ALIGN_CENTER, 5)

        self.SetSizer(mainSizer)

        # Bindings and updates
        self.window_position.update()
        self.Bind(wx.EVT_MOVE, self.update)
        self.Bind(wx.EVT_SIZING, self.update)
        self.Bind(wx.EVT_CLOSE, self.close)

        self.control.liveImage()

        #self.p_read = PressureRead(self, self.control)

    def __del__(self):
        self.Close()

    def close(self, event):
        self.Show(False)

    def show(self, event):
        self.Show(True)

    def update(self, event):
        self.window_position.update()

class ChannelSliders(wx.Panel):
    def __init__(self, parent=None, config=None, control=None):
        super(ChannelSliders, self).__init__(parent)
        # Parameters
        self.parent = parent
        self.control = control
        self.config = config