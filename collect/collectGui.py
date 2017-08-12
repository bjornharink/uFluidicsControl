# !/usr/bin/env python

# [Future imports]
# "print" function compatibility between Python 2.x and 3.x
from __future__ import print_function
# Use Python 3.x "/" for division in Pyhton 2.x
from __future__ import division

# [File header]     | Copy and edit for each file in this project!
# title             : flowGui.py
# description       : Microfluidic Control - Collect module - GUI
# author            : Bjorn Harink
# credits           : Kurt Thorn, Huy Nguyen
# date              : 20160308
# version update    : 20161207
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
POS_READ_TIME = 0.5  # Refresh time in seconds for pressure read

class MainWindow(wx.Frame):
    """This is the main window for the Flow Module of the Microfluidic Control program.
    """
    def __init__(self, parent=None, config_handler=None, control=None):
        super(MainWindow, self).__init__(parent)
        self.SetTitle('Microfluidic Control - Collect Module')
        # Parameters
        self.config = config_handler
        self.control = control

        # Window Size/Postion Handler
        self.window_position = config.WindowPosition(self, self.config.main)

        self.init()

    def init(self):
        mainSizer = wx.BoxSizer(wx.VERTICAL)

        self.pos_param = PositionParameters(self)
        mainSizer.Add( self.pos_param, 0, wx.ALL|wx.ALIGN_CENTER|wx.EXPAND)

        self.dir_rose = DirectionRose(self)
        mainSizer.Add( self.dir_rose, 0, wx.ALL|wx.ALIGN_CENTER|wx.EXPAND)

        self.tubes = Tubes(self)
        mainSizer.Add(self.tubes, 0, wx.ALL|wx.ALIGN_CENTER|wx.EXPAND)

        self.SetSizer(mainSizer)
        self.Fit()
        self.Layout()

        # Bindings and updates
        self.window_position.update()
        self.Bind(wx.EVT_MOVE, self.update)
        self.Bind(wx.EVT_SIZING, self.update)
        self.Bind(wx.EVT_CLOSE, self.close)

        self.pos_read = PositionRead(self, self.control)

    def __del__(self):
        self.Close()

    def close(self, event):
        self.Show(False)

    def show(self, event):
        self.Show(True)

    def update(self, event):
        self.window_position.update()

class Tubes(wx.Panel):
    def __init__(self, parent=None):
        super(Tubes, self).__init__(parent)
        # Parameters
        self.parent = parent

        tubeBox = wx.StaticBox(self, -1, "Plate settings")

        mainSizer = wx.StaticBoxSizer(tubeBox, wx.VERTICAL)
        level1Sizer = wx.BoxSizer(wx.HORIZONTAL)
        level2Sizer = wx.BoxSizer(wx.HORIZONTAL)

        labelTube = wx.Button(self, name='labelTube', label='Go to tube #:', style=wx.TR_SINGLE)
        labelTube.Bind(wx.EVT_BUTTON, self.goto_tube)
        level1Sizer.Add(labelTube, 1, wx.RIGHT|wx.ALIGN_CENTER, 2)
        self.tubeNo = NumCtrl(self, name = 'gotoTube', value = 1, integerWidth = 2, allowNegative = False, min = 1, max = 99, 
                                fractionWidth = 0, groupDigits = False, autoSize = False, style = wx.TR_SINGLE|wx.CENTER, size = (29,-1))
        level1Sizer.Add(self.tubeNo, 1, wx.ALL|wx.ALIGN_CENTER, 2)
        mainSizer.Add(level1Sizer, 1, wx.ALL|wx.ALIGN_CENTER, 5)
        
        label_row = wx.StaticText(self, label='Rows', style=wx.TR_SINGLE)
        level2Sizer.Add(label_row, 2, wx.ALL|wx.ALIGN_CENTER, 2)
        self.tube_rows = NumCtrl(self, name = 'rowsTube', value = 12, integerWidth = 2, allowNegative = False, min = 1, max = 99, 
                                fractionWidth = 0, groupDigits = False, autoSize = False, style = wx.TR_SINGLE|wx.CENTER, size = (29,-1))
        level2Sizer.Add(self.tube_rows, 1, wx.ALL|wx.ALIGN_CENTER, 2)
        label_row = wx.StaticText(self, label='Columns', style=wx.TR_SINGLE)
        level2Sizer.Add(label_row, 2, wx.ALL|wx.ALIGN_CENTER, 2)
        self.tube_cols = NumCtrl(self, name = 'colsTube', value = 8, integerWidth = 2, allowNegative = False, min = 1, max = 99, 
                                fractionWidth = 0, groupDigits = False, autoSize = False, style = wx.TR_SINGLE|wx.CENTER, size = (29,-1))
        level2Sizer.Add(self.tube_cols, 1, wx.ALL|wx.ALIGN_CENTER, 2)
        mainSizer.Add(level2Sizer, 1, wx.ALL|wx.ALIGN_CENTER, 5)
        
        self.SetSizer(mainSizer)

    def goto_tube(self, event):
        rows = self.tube_rows.GetValue()
        cols = self.tube_cols.GetValue()
        tube = self.tubeNo.GetValue()-1
        if (tube+1 > rows*cols) or (tube < 0):
            return
        incX = self.parent.pos_param.setIncrementX.GetValue()
        incY = self.parent.pos_param.setIncrementY.GetValue()
        cols_step = int(tube/rows)
        rows_step = tube - (cols_step * rows)
        print(cols_step, rows_step)
        self.parent.control.move_abs(-rows_step*incX, cols_step*incY)
        

class PositionParameters(wx.Panel):
    def __init__(self, parent=None):
        super(PositionParameters, self).__init__(parent)
        # Parameters
        self.parent = parent

        self.SetSize((232,-1))
        self.SetSizeHints(232,-1)

        mainSizer = wx.BoxSizer(wx.VERTICAL)

        posBox = wx.StaticBox(self, -1, "Position  X, Y")
        posSizer = wx.StaticBoxSizer(posBox, wx.HORIZONTAL)
        self.positionX = wx.StaticText(self, label='0', style=wx.TR_SINGLE)
        posSizer.Add(self.positionX, 3, wx.ALL|wx.ALIGN_CENTER, 5)
        labelX = wx.StaticText(self, label='mm', style=wx.TR_SINGLE)
        posSizer.Add(labelX, 1, wx.ALL|wx.ALIGN_CENTER, 5)
        self.positionY = wx.StaticText(self, label='0', style=wx.TR_SINGLE)
        posSizer.Add(self.positionY, 3, wx.ALL|wx.ALIGN_CENTER, 5)
        labelY = wx.StaticText(self, label='mm', style=wx.TR_SINGLE)
        posSizer.Add(labelY, 1, wx.ALL|wx.ALIGN_CENTER, 5)
        self.setHome = wx.Button(self, name='setHome', label=u'Set \u2302', size=(50,25))
        self.setHome.Bind(wx.EVT_BUTTON, self.set_home)
        posSizer.Add(self.setHome, 1, wx.ALL|wx.ALIGN_CENTER, 5)
        mainSizer.Add(posSizer, 0, wx.ALL|wx.ALIGN_CENTER, 5)

        inBox = wx.StaticBox(self, -1, "Increment X, Y                  |  Speed")
        inSizer = wx.StaticBoxSizer(inBox, wx.HORIZONTAL)
        self.setIncrementX = NumCtrl(self, name = 'setIncrementX', value = 9, integerWidth = 2, allowNegative = False, min = 0.1, max = 99, 
                                     fractionWidth = 1, groupDigits = False, autoSize = False, style = wx.TR_SINGLE|wx.CENTER, size = (34,-1))
        inSizer.Add(self.setIncrementX, 2, wx.ALL|wx.ALIGN_CENTER, 2)
        labelIncX = wx.StaticText(self, label='mm', style=wx.TR_SINGLE)
        inSizer.Add(labelIncX, 1, wx.RIGHT|wx.ALIGN_CENTER, 2)
        self.setIncrementY = NumCtrl(self, name = 'setIncrementY', value = 9, integerWidth = 2, allowNegative = False, min = 0.1, max = 99, 
                                     fractionWidth = 1, groupDigits = False, autoSize = False, style = wx.TR_SINGLE|wx.CENTER, size = (34,-1))
        inSizer.Add(self.setIncrementY, 2, wx.ALL|wx.ALIGN_CENTER, 5)
        labelIncY = wx.StaticText(self, label='mm', style=wx.TR_SINGLE)
        inSizer.Add(labelIncY, 1, wx.RIGHT|wx.ALIGN_CENTER, 2)
        self.setSpeed = NumCtrl(self, name = 'setSpeed', value = self.parent.control.get_speed(), integerWidth = 2, allowNegative = False, min = 1, max = 99, 
                                fractionWidth = 1, groupDigits = False, autoSize = False, style = wx.TR_SINGLE|wx.CENTER, size = (34,-1))
        self.setSpeed.Bind(wx.EVT_TEXT, self.set_speed)
        inSizer.Add(self.setSpeed, 2, wx.ALL|wx.ALIGN_CENTER, 2)
        labelSpeed = wx.StaticText(self, label='mm/s', style=wx.TR_SINGLE)
        inSizer.Add(labelSpeed, 1, wx.RIGHT|wx.ALIGN_CENTER, 2)
        mainSizer.Add(inSizer, 0, wx.ALL|wx.ALIGN_CENTER, 5)

        self.SetSizer(mainSizer)
        mainSizer.Fit(self)

    def set_home(self, event):
        self.parent.control.set_home()

    def set_speed(self, event):
        o = event.GetEventObject()
        speed_set = float(o.GetValue())
        self.parent.control.set_speed(speed_set)
        speed_get = self.parent.control.get_speed()
        if ('%f0.1'%round(speed_get,1)) != ('%f0.1'%round(speed_set,1)):
            o.SetValue('%0.1f'%self.parent.control.get_speed())

class DirectionRose(wx.Panel):
    def __init__(self, parent=None):
        super(DirectionRose, self).__init__(parent, style=wx.RAISED_BORDER)
        # Parameters
        self.parent = parent

        self.SetSize((232,232))
        self.SetSizeHints(232,232)

        mainSizer = wx.BoxSizer(wx.HORIZONTAL)

        # Font and size
        roseFont = wx.Font(16, wx.SWISS, wx.NORMAL, wx.BOLD)
        roseSize = (75,75)

        roseSizer = wx.GridSizer( 3, 3, 1, 1 )

        # Control rose buttons
        self.luRose = wx.Button(self, name = "lu", label = u'\u21d6', size = roseSize)
        self.muRose = wx.Button(self, name = "mu", label = u'\u25b2', size = roseSize)
        self.ruRose = wx.Button(self, name = "ru", label = u'\u21d7', size = roseSize)
        self.llRose = wx.Button(self, name = "ll", label = u'\u25c4', size = roseSize)
        self.xxRose = wx.Button(self, name = "xx", label = u"\u2302", size = roseSize)
        self.rrRose = wx.Button(self, name = "rr", label = u'\u25ba', size = roseSize)
        self.ldRose = wx.Button(self, name = "ld", label = u'\u21d9', size = roseSize)
        self.mdRose = wx.Button(self, name = "md", label = u'\u25bc', size = roseSize)
        self.rdRose = wx.Button(self, name = "rd", label = u'\u21d8', size = roseSize)

        self.luRose.SetFont(roseFont)
        self.muRose.SetFont(roseFont)
        self.ruRose.SetFont(roseFont)
        self.llRose.SetFont(roseFont)
        self.xxRose.SetFont(roseFont)
        self.rrRose.SetFont(roseFont)
        self.ldRose.SetFont(roseFont)
        self.mdRose.SetFont(roseFont)
        self.rdRose.SetFont(roseFont)

        self.luRose.Bind(wx.EVT_BUTTON, self.move_stage)
        self.muRose.Bind(wx.EVT_BUTTON, self.move_stage)
        self.ruRose.Bind(wx.EVT_BUTTON, self.move_stage)
        self.llRose.Bind(wx.EVT_BUTTON, self.move_stage)
        self.xxRose.Bind(wx.EVT_BUTTON, self.move_stage)
        self.rrRose.Bind(wx.EVT_BUTTON, self.move_stage)
        self.ldRose.Bind(wx.EVT_BUTTON, self.move_stage)
        self.mdRose.Bind(wx.EVT_BUTTON, self.move_stage)
        self.rdRose.Bind(wx.EVT_BUTTON, self.move_stage)

        roseSizer.AddMany( [(self.luRose, 1), (self.muRose, 1), (self.ruRose, 1), 
                            (self.llRose, 1), (self.xxRose, 1), (self.rrRose, 1), 
                            (self.ldRose, 1), (self.mdRose, 1), (self.rdRose, 1)])
        mainSizer.Add(roseSizer, 0, wx.ALIGN_CENTER)
        self.SetSizer(mainSizer)
        mainSizer.Fit(self)

    def move_stage(self, event):
        incX = self.parent.pos_param.setIncrementX.GetValue()
        incY = self.parent.pos_param.setIncrementY.GetValue()
        o = event.GetEventObject()
        name = o.GetName()
        if name == "lu":
            self.parent.control.move_rel(-incX, -incY)
        elif name == "mu":
            self.parent.control.move_rel(-incX, 0)
        elif name == "ru":
            self.parent.control.move_rel(-incX, incY)
        elif name == "ll":
            self.parent.control.move_rel(0, -incY)
        elif name == "xx":
            self.parent.control.home()
        elif name == "rr":
            self.parent.control.move_rel(0, incY)
        elif name == "ld":
            self.parent.control.move_rel(incX, -incY)
        elif name == "md":
            self.parent.control.move_rel(incX, 0)
        elif name == "rd":
            self.parent.control.move_rel(incX, incY)
        

class PositionRead(threading.Thread):
    """Pressure read thread.
    """
    def __init__(self, parent, control):
        threading.Thread.__init__(self)
        self.parent = parent
        self.control = control
        self._stop = threading.Event()
        self.daemon = True
        self.halt = False
        self.start()

    def __del__(self):
        self.stop()
        return 0

    def stop(self):
        self.halt = True
        self._stop.set()

    @property
    def stopped(self):
        return self._stop.isSet()

    def run(self):
        """Overrides Thread.run. Don't call this directly its called internally when you call Thread.start()
        """
        while self.halt is False:
            self.control.update_position()
            time.sleep(POS_READ_TIME)
            try: 
                self.parent.pos_param.positionX.SetLabel("%.1f" %self.control.position['x'])
                self.parent.pos_param.positionY.SetLabel("%.1f" %self.control.position['y'])
            except: 
                warnings.warn("Collect position update failed.")
