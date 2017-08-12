# !/usr/bin/env python

# [Future imports]
# "print" function compatibility between Python 2.x and 3.x
from __future__ import print_function
# Use Python 3.x "/" for division in Pyhton 2.x
from __future__ import division

# [File header]     | Copy and edit for each file in this project!
# title             : flowGui.py
# description       : Microfluidic Control - Flow module - GUI
# author            : Bjorn Harink
# credits           : Kurt Thorn, Huy Nguyen
# date              : 20160308
# version update    : 20161024
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
P_READ_TIME = 0.3  # Refresh time in seconds for pressure read
RING_BUFFER_SIZE = 3  # Moving average
FRACTION_WIDTH = {'mba':0, 'kpa':1, 'psi':2}
INTEGER_WIDTH = {'mba':4, 'kpa':3, 'psi':2}
UNITS = ['mBa', 'kPa', 'PSI']
UNITS_LOW = ['mba', 'kpa', 'psi']

class MainWindow(wx.Frame):
    """This is the main window for the Flow Module of the Microfluidic Control program.
    """
    def __init__(self, parent=None, config_handler=None, control=None):
        super(MainWindow, self).__init__(parent)
        self.SetTitle('Microfluidic Control - Flow Module')
        # Parameters
        self.config = config_handler
        self.control = control
        self.current_chip = self.config.chip.name

        # Window Size/Postion Handler
        self.window_position = config.WindowPosition(self, self.config.main)

        self.init()

    def init(self):
        mainSizer = wx.BoxSizer(wx.HORIZONTAL)

        self.p_control = ChannelSliders(self, self.config, self.control)

        mainSizer.Add( self.p_control, 1, wx.ALIGN_CENTER_HORIZONTAL|wx.ALL|wx.EXPAND, 5  )

        # All ZERO button
        sideSizer = wx.BoxSizer(wx.VERTICAL)
        sidePanel = wx.Panel(self)
        self.allZeroBtn = wx.Button( sidePanel, wx.ID_ANY, u"All\nZero", size = (50, 35))
        self.allZeroBtn.Bind(wx.EVT_BUTTON, self.p_control.set_all_zero)
        sideSizer.Add(self.allZeroBtn, 0, wx.ALIGN_TOP|wx.ALL, 5)
        sidePanel.SetSizer(sideSizer)

        # Unit change
        self.unitBtn = wx.RadioBox(sidePanel, wx.ID_ANY, u"P units", wx.DefaultPosition, wx.DefaultSize, UNITS, 1, wx.RA_SPECIFY_COLS)
        self.unitBtn.Bind(wx.EVT_RADIOBOX, self.unit_change)
        self.unitBtn.SetSelection(UNITS_LOW.index(self.control.unit))
        sideSizer.Add(self.unitBtn, 0, wx.ALIGN_TOP|wx.ALL, 5)

        mainSizer.Add(sidePanel, 0, wx.EXPAND|wx.ALIGN_CENTER_HORIZONTAL|wx.TOP|wx.BOTTOM|wx.RIGHT, 5)

        self.SetSizer(mainSizer)

        # Bindings and updates
        self.window_position.update()
        self.Bind(wx.EVT_MOVE, self.update)
        self.Bind(wx.EVT_SIZING, self.update)
        self.Bind(wx.EVT_CLOSE, self.close)

        self.p_read = PressureRead(self, self.control)

    def __del__(self):
        self.Close()

    def close(self, event):
        self.Show(False)

    def show(self, event):
        if self.current_chip != self.config.chip.name:
            self.Show(False)
            del self.p_read
            self.DestroyChildren()
            self.current_chip = self.config.chip.name
            self.init()
            self.Layout()
            self.p_read = PressureRead(self, self.control)
        self.Show(True)

    def update(self, event):
        self.window_position.update()

    def unit_change(self, event):
        unit = event.GetSelection()
        self.control.unit = str(UNITS[unit])
        print(self.control.unit)

        for channel_num in xrange(1, self.control.channel_num+1):
            slider = "pSldr%s" % channel_num
            nctrl = "pCtrl%s" % channel_num
            slider_id = self.p_control.FindWindowByName(slider)    
            nctrl_id = self.p_control.FindWindowByName(nctrl)
            if unit == 0:
                nctrl_id.SetIntegerWidth(INTEGER_WIDTH[self.control.unit])
                nctrl_id.SetFractionWidth(FRACTION_WIDTH['mba'])
                print(self.control.limit)
                nctrl_id.SetMax(self.control.limit)
            if unit == 1:
                nctrl_id.SetIntegerWidth(INTEGER_WIDTH[self.control.unit])
                nctrl_id.SetFractionWidth(FRACTION_WIDTH['kpa'])
                print(self.control.limit)
                nctrl_id.SetMax(self.control.limit)
            if unit == 2:
                nctrl_id.SetIntegerWidth(INTEGER_WIDTH[self.control.unit])
                nctrl_id.SetFractionWidth(FRACTION_WIDTH['psi'])
                print(self.control.limit)
                nctrl_id.SetMax(self.control.limit)
            nctrl_id.SetValue(0)

class ChannelSliders(wx.Panel):
    def __init__(self, parent=None, config=None, control=None):
        super(ChannelSliders, self).__init__(parent)
        # Parameters
        self.parent = parent
        self.control = control
        self.config = config

        pSizer = wx.BoxSizer( wx.HORIZONTAL )
        numFont = wx.Font(9, wx.DEFAULT, wx.NORMAL, wx.NORMAL)
        for channel_no in xrange(1, self.control.channel_num+1):
            slideSizer = wx.BoxSizer( wx.VERTICAL )
            name_n = "nTxt%s" % channel_no
            name_s = "pSldr%s" % channel_no
            name_t = "pTxt%s" % channel_no
            name_c = "pCtrl%s" % channel_no
            name_z = "zBtn%s" % channel_no
            try:
                self.parent.config.chip["flows"][str(channel_no)]["name"]
            except:
                self.parent.config.chip["flows"][str(channel_no)] = {}
                self.parent.config.chip["flows"][str(channel_no)]["name"] = "NA"
                self.parent.config.chip.update()
            channel_name = wx.TextCtrl( self, wx.ID_ANY, value = self.parent.config.chip["flows"][str(channel_no)]["name"], name = name_n , size = (52, -1) )
            channel_name.Bind( wx.EVT_TEXT, self.name_change )
            slideSizer.Add( channel_name, 0, wx.ALIGN_CENTER_HORIZONTAL|wx.EXPAND, 5 )
            pressure_slider = wx.Slider( self, wx.ID_ANY, 0, 0, 1034, name = name_s, size = (-1,300), style = wx.SL_VERTICAL|wx.SL_INVERSE|wx.SL_AUTOTICKS)
            slideSizer.Add( pressure_slider, 1, wx.ALL|wx.EXPAND, 5 )
            pressure_slider.Bind( wx.EVT_COMMAND_SCROLL_CHANGED, self.set_control )
            pressure_info = wx.StaticText( self, wx.ID_ANY, name = name_t, label='0 %s' % self.control.unit)
            slideSizer.Add( pressure_info, 0, wx.ALIGN_CENTER_HORIZONTAL, 5 )
            pressure_set = NumCtrl(self, wx.ID_ANY, name = name_c, value = 0, integerWidth = INTEGER_WIDTH[self.control.unit], allowNegative = False, min = 0, max = self.control.limit, 
                                   fractionWidth = FRACTION_WIDTH[self.control.unit], groupDigits = False, autoSize = False, style = wx.TR_SINGLE|wx.CENTER, size = (50,-1))
            pressure_set.Bind( wx.EVT_TEXT, self.set_pressure )
            pressure_set.SetFont( numFont )
            slideSizer.Add( pressure_set, 0, wx.ALIGN_CENTER_HORIZONTAL|wx.EXPAND, 5 )
            pressure_zero = wx.Button( self, wx.ID_ANY, label = u"Zero", name = name_z, size = ( 52,25 ) )
            pressure_zero.Bind(wx.EVT_BUTTON, self.set_zero)
            slideSizer.Add( pressure_zero, 0, wx.ALIGN_CENTER_HORIZONTAL|wx.EXPAND, 5 )
            pSizer.Add(slideSizer, 1, wx.ALIGN_CENTER_HORIZONTAL|wx.ALL|wx.EXPAND, 5 )
        # Set sizer
        self.SetSizer(pSizer)

    def name_change(self, event):
        o = event.GetEventObject()
        flow_no = filter( str.isdigit, str(o.GetName()) )
        self.config.chip['flows'][flow_no]['name'] = o.GetValue()
        self.config.chip.update()

    def set_zero(self, event):
        self.set_control(event, value=0)

    def set_all_zero(self, event):
        [self.set_control(event, value=0, channel=ch) for ch in xrange(1, self.control.channel_num+1)]

    def set_pressure(self, event):
        o = event.GetEventObject()
        channel_num = filter( str.isdigit, str(o.GetName()) )
        self.set_control(event)
        self.control.set_pressure(o.GetValue(), channel_num)
        print("Set pressure %s to %4.1f" % (channel_num, o.GetValue()) )

    def set_control(self, event, value=0, channel=None):
        o = event.GetEventObject()
        if channel is not None:
            channel_num = channel
        else:
            channel_num = filter( str.isdigit, str(o.GetName()) )
        slider = "pSldr%s" % channel_num
        nctrl = "pCtrl%s" % channel_num
        slider_id = self.Parent.FindWindowByName(slider)
        nctrl_id = self.Parent.FindWindowByName(nctrl)
        if "Sldr" in o.GetName():
            value_conv = self.control._unit_conv(o.GetValue())
            nctrl_id.SetValue(value_conv)
        elif "Ctrl" in o.GetName():
            value_conv = o.GetValue()/self.control.factor
            slider_id.SetValue(value_conv)
        else:
            nctrl_id.SetValue(value)
            slider_id.SetValue(value)
        

class RingBuffer:
    def __init__(self, size, value):
        self.data = [value for i in xrange(size)]

    def append(self, x):
        self.data.pop(0)
        self.data.append(x)

    @property
    def get(self):
        return np.mean(self.data, axis=0).tolist()

class PressureRead(threading.Thread):
    """Pressure read thread.
    """
    def __init__(self, parent, control):
        threading.Thread.__init__(self)
        self.parent = parent
        self.control = control
        self.buffer = RingBuffer(RING_BUFFER_SIZE, [0]*self.control.channel_num)
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
            time.sleep(P_READ_TIME)
            p_chan = self.control.read_pressure()
            p_chan = np.array(p_chan).clip(min=0).tolist()
            self.buffer.append(p_chan)
            for idx, p in enumerate(self.buffer.get):
                label = "%3.1f %s" % (p, self.control.unit)
                i_gui = "pTxt%s" % str(idx+1)
                try: 
                    i_gui_id = self.parent.p_control.FindWindowByName(i_gui)
                    i_gui_id.SetLabel(label)
                except: pass