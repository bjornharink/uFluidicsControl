# !/usr/bin/env python

# [Future imports]
# "print" function compatibility between Python 2.x and 3.x
from __future__ import print_function
# Use Python 3.x "/" for division in Pyhton 2.x
from __future__ import division

# [File header]     | Copy and edit for each file in this project!
# title             : valveGui.py
# description       : Microfluidic Control - Valve module - Gui
# author            : Bjorn Harink
# credits           : Kurt Thorn, Huy Nguyen
# date              : 20160308
# version update    : 20160901
# version           : v0.4.0
# usage             : As module
# notes             : Do not quick fix functions for specific needs, keep them general!
# python_version    : 2.7

# [Modules]
# General Python
import warnings
import thread
# GUI
import wx
import wx.lib.scrolledpanel
# Project
import config

# [SETTINGS]
VALVE_CLOSED_COLOR = wx.Colour(128,255,0)
VALVE_OPENED_COLOR = wx.Colour(160,160,160)
DEFAULT_CHIP_SIZE = 800
DEFAULT_CHIP = "DEFAULT"

### TO-DO ###
# Change HACK in Toggle Add

class MainWindow(wx.Frame):
    """This is the main window for the Valve Module of the Microfluidic Control program.
    """
    def __init__(self, parent=None, config_handler=None, control=None):
        super(MainWindow, self).__init__(parent)
        self.SetTitle('Microfluidic Control - Valve Module')
        
        # Parameters
        self.config = config_handler
        self.control = control

        self.current_chip = self.config.chip.name

        # Window Size/Postion Handler
        self.window_position = config.WindowPosition(self, self.config.main)
        if self.window_position.exist:
            self.chip_size = self.config.main['windows'][self.GetTitle()]['size'][1]-141
        else:
            self.chip_size = DEFAULT_CHIP_SIZE

        self.init()

    def init(self):
        # MainSizer and Tabs
        self.mainSizer = wx.BoxSizer(wx.HORIZONTAL)
        valveTabs = wx.Notebook(self)

        # Chip Tab
        if self.config.chip.name != DEFAULT_CHIP:
            self.chipImageTab = ChipTab(valveTabs, self.chip_size, self.config.chip)
            valveTabs.AddPage(self.chipImageTab, u"Chip", False)
            valveTabs.Bind(wx.EVT_NOTEBOOK_PAGE_CHANGED, self.chipImageTab.update_names)

        # Valve Tab
        self.valveTab = ValveTab(valveTabs, self.config.chip)
        valveTabs.AddPage(self.valveTab, u"Valves", False)

        # Add Tabs to mainSizer
        self.mainSizer.Add(valveTabs, 1, wx.EXPAND|wx.ALL, 5)

        # Custom Control Tab
        self.cControl = CustomChipControl(self, self.config.chip)
        self.mainSizer.Add(self.cControl, 0, wx.EXPAND|wx.RIGHT|wx.TOP|wx.BOTTOM, 5)

        self.SetSizer(self.mainSizer)

        # Bindings and updates
        self.window_position.update()
        self.Bind(wx.EVT_MOVE, self.update)
        self.Bind(wx.EVT_CLOSE, self.close)

        thread.start_new_thread(self.toggle_check, ())

    def __del__(self):
        self.Close()

    def close(self, event):
        self.Show(False)

    def show(self, event):
        if self.current_chip != self.config.chip.name:
            self.Show(False)
            self.DestroyChildren()
            self.current_chip = self.config.chip.name
            self.init()
            self.Layout()
        self.Show(True)

    def update(self, event):
        self.window_position.update()

    def toggle(self, event):
        valve_closed_color = VALVE_CLOSED_COLOR
        valve_opened_color = VALVE_OPENED_COLOR
        o = event.GetEventObject()
        valve_no = filter( str.isdigit, str(o.GetLabel()) )
        state = o.GetValue()
        self.control.valve_set(state, int(valve_no))
        thread.start_new_thread(self.toggle_check, ())

    def toggle_checker(self, valve_no):
        name_c = "chipBtn%02d" % valve_no
        try:
            btn_id_chip = self.chipImageTab.FindWindowByName( name_c )
            if self.control.status[valve_no] == True:
                btn_id_chip.SetValue(True)
                btn_id_chip.SetBackgroundColour(VALVE_OPENED_COLOR)
            else:
                btn_id_chip.SetValue(False)
                btn_id_chip.SetBackgroundColour(VALVE_CLOSED_COLOR)
        except AttributeError:
            pass
        name_v = "valveBtn%02d" % valve_no
        btn_id_valve = self.valveTab.FindWindowByName( name_v )
        if self.control.status[valve_no] == True:
            btn_id_valve.SetValue(True)
            btn_id_valve.SetBackgroundColour(VALVE_OPENED_COLOR)
        else:
            btn_id_valve.SetValue(False)
            btn_id_valve.SetBackgroundColour(VALVE_CLOSED_COLOR)

    def toggle_check(self):
        self.control.update()
        valves = xrange(self.control.valve_num)
        map(self.toggle_checker, valves)

class ChipTab(wx.Panel):
    def __init__(self, parent=None, size=None, chip_config=None):
        super(ChipTab, self).__init__(parent)
        # Parameters
        self.size = size
        self.chip_config = chip_config

        # mainSizer
        mainSizer = wx.BoxSizer(wx.HORIZONTAL)
        
        # chipSizer
        chipImageSizer = wx.BoxSizer(wx.VERTICAL)
        self.chip_image = self.resize_image(self.chip_config.image, self.size)
        self.chipImage = wx.StaticBitmap(self, bitmap=self.chip_image, pos=(0, 0))
        self.chipImage.Bind(wx.EVT_SIZE, self.update)
        chipImageSizer.Add(self.chipImage, 1, wx.EXPAND|wx.ALL|wx.SHAPED, 0)
        chipImageSizer.Fit(self)
        mainSizer.Add(chipImageSizer, 1, wx.EXPAND|wx.ALL|wx.SHAPED, 0)

        # Button Handler and Dynamic Widgets
        self.buttonHandler = ButtonHandler(self, self.chip_config)
        self.add_chip_toggles()

        # Set sizer
        self.SetSizer(mainSizer)

    def resize_image(self, image_path, max_size):
        image = wx.Image(image_path, wx.BITMAP_TYPE_PNG)
        max_size = max_size
        W = image.GetWidth()
        H = image.GetHeight()
        if W > H:
            new_W = max_size
            new_H = max_size * H / W
        else:
            new_H = max_size
            new_W = max_size * W / H
        image = wx.BitmapFromImage(image.Rescale(new_W,new_H, wx.IMAGE_QUALITY_HIGH))
        return image

    def update(self, event):
        self.chip_image = self.resize_image(self.chip_config.image, min(self.Size))
        self.chipImage.SetBitmap(self.chip_image)
        self.Fit()
        self.Parent.Parent.update(event)
        self.update_pos()

    def add_chip_toggles(self):
        valve_closed_color = VALVE_CLOSED_COLOR
        valves = self.chip_config['valves']
        for valve_step, valve_no in enumerate(valves):
            if valve_step >= self.Parent.Parent.control.valve_num:
                break
            label = "V%02d" % valve_step
            name = "chipBtn%02d" % valve_step
            im_size = self.GetSize()
            new_button = wx.ToggleButton( self.chipImage, label = label, name = name, size = (30,30), pos = (int(valves[valve_no]['position'][0]*im_size[0]), int(valves[valve_no]['position'][1]*im_size[1])))
            text = valves[valve_no]['name']
            name_t = "chipTxt%02d" % valve_step
            text_valve = wx.ToolTip(text)
            new_button.SetToolTip(text_valve)
            new_button.SetToolTipString(tip = valves[valve_no]['name'])
            new_button.SetBackgroundColour(valve_closed_color)
                
            new_button.Bind(wx.EVT_RIGHT_DOWN, self.buttonHandler.mouse_down)
            new_button.Bind(wx.EVT_MOTION, self.buttonHandler.mouse_move)
            new_button.Bind(wx.EVT_RIGHT_UP, self.buttonHandler.mouse_up)
            new_button.Bind(wx.EVT_TOGGLEBUTTON, self.Parent.Parent.toggle)

    def update_pos(self):
        valve_closed_color = VALVE_CLOSED_COLOR
        valves = self.chip_config['valves']
        for valve_step, valve_no in enumerate(valves):
            ### HACK ###
            if valve_step >= self.Parent.Parent.control.valve_num:
                break
            ### HACK ###
            name = "chipBtn%02d" % valve_step
            btn_id_chip = self.FindWindowByName(name)
            im_size = self.GetSize()
            btn_id_chip.SetPosition((int(valves[valve_no]['position'][0]*(im_size[0])), int(valves[valve_no]['position'][1]*(im_size[1]))))

    def update_names(self, event):
        valves = self.chip_config['valves']
        for valve_step, valve_no in enumerate(valves):
            name = "chipBtn%02d" % valve_step
            btn_id_chip = self.FindWindowByName(name)
            text = valves[valve_no]['name']
            text_valve = wx.ToolTip(text)
            btn_id_chip.SetToolTip(text_valve)            

    def toggle(self, event):
        valve_closed_color = VALVE_CLOSED_COLOR
        valve_opened_color = VALVE_OPENED_COLOR
        o = event.GetEventObject()
        valve_no = filter( str.isdigit, str(o.GetLabel()) )
        state = o.GetValue()
        if state == True:
            self.valveControl.valveOn(int(valve_no))
        else:
            self.valveControl.valveOff(int(valve_no))

class CustomChipControl(wx.Panel):
    def __init__(self, parent=None, chip=None):
        super(CustomChipControl, self).__init__(parent, style=wx.RAISED_BORDER) 
        self.chip = chip
        self.SetMinSize((309, -1))

        statusBox = wx.StaticBox(self, 1, "Custom Control")
        self.mainSizer = wx.StaticBoxSizer(statusBox, wx.VERTICAL)

        self.addButton = wx.Button(self, label = 'Add Control')
        self.addButton.Bind(wx.EVT_BUTTON, self.add_control)
        self.mainSizer.Add(self.addButton, 0, wx.EXPAND|wx.RIGHT, 18)

        static_line = wx.StaticLine(self)
        self.mainSizer.Add(static_line, 0, wx.EXPAND|wx.TOP|wx.BOTTOM, 15)

        self.scrollSizer = wx.BoxSizer(wx.VERTICAL)
        self.scroll = wx.lib.scrolledpanel.ScrolledPanel(self, style=wx.SIMPLE_BORDER)
        self.scroll.SetupScrolling(scroll_x=False)
        self.scroll.SetSizer(self.scrollSizer)
        self.mainSizer.Add(self.scroll, 1, wx.EXPAND)
        self.mainSizer.Fit(self)
        self.SetSizer(self.mainSizer)

    def add_control(self, event):
        name = "test"
        sizer = wx.BoxSizer(wx.VERTICAL)
        panel = wx.Panel(self.scroll)
        
        textCtrl = wx.TextCtrl(panel,value=name)
        sizer.Add(textCtrl, 1, wx.EXPAND|wx.ALL, 2)

        sizerV1 = wx.BoxSizer(wx.HORIZONTAL)
        btnStart = wx.Button(panel, label="Start")
        sizerV1.Add(btnStart, 1, wx.EXPAND|wx.ALL, 2)
        btnStop = wx.Button(panel, label="Stop")
        sizerV1.Add(btnStop, 1, wx.EXPAND|wx.ALL, 2)
        btnDel = wx.Button(panel, label="Remove")
        btnDel.Bind(wx.EVT_BUTTON, self.remove_control)
        sizerV1.Add(btnDel, 1, wx.EXPAND|wx.ALL, 2)
        sizer.Add(sizerV1, 1)

        sizerV2 = wx.BoxSizer(wx.HORIZONTAL)        
        cmbCtrl = wx.ComboBox(panel, style=wx.CB_READONLY)
        sizerV2.Add(cmbCtrl, 2, wx.EXPAND|wx.ALL, 2)
        btnEdit = wx.Button(panel, label="Edit")
        sizerV2.Add(btnEdit, 1, wx.ALL, 2)
        sizer.Add(sizerV2, 1)

        static_line = wx.StaticLine(panel)
        sizer.Add(static_line, 0, wx.EXPAND|wx.ALL, 3)

        self.scrollSizer.Add(panel, 0, wx.EXPAND|wx.RIGHT, 18)
        panel.SetSizer(sizer)
        self.scroll.Fit()
        self.Parent.Layout()

    def remove_control(self, event):
        btn_object = event.GetEventObject()
        parent_panel = btn_object.GetParent()
        parent_panel.Hide()
        parent_panel.Destroy()
        self.Parent.Layout()

class ButtonHandler(object):
    """Button Handler
    """
    def __init__(self, panel, valve_config):
        super(ButtonHandler, self).__init__()
        self.valve_config = valve_config
        self.d = {}
        self.panel = panel

    def mouse_down(self, event):
        o           = event.GetEventObject()
        sx,sy       = self.panel.ScreenToClient(o.GetPositionTuple())
        dx,dy       = self.panel.ScreenToClient(wx.GetMousePosition())
        o._x,o._y   = (sx-dx, sy-dy)
        self.d['d'] = o

    def mouse_move(self, event):
        try:
            if 'd' in self.d:
                o = self.d['d']
                x, y = wx.GetMousePosition()
                o.SetPosition(wx.Point(x+o._x,y+o._y))                
        except: pass

    def mouse_up(self, event):
        try:
            if 'd' in self.d: 
                o = self.d['d']
                valve_no = filter( str.isdigit, str(o.GetLabel()) )
                del self.d['d']
                try:
                    update = o.GetPositionTuple()
                    im_size = self.panel.GetSize()
                    self.valve_config['valves'][valve_no]['position'] = [update[0]/(im_size[0]), update[1]/(im_size[1])]
                    self.valve_config.update()
                except: pass
        except: pass

class ValveTab(wx.ScrolledWindow):
    def __init__(self, parent=None, chip=None):
        super(ValveTab, self).__init__(parent, style=wx.VSCROLL) 
        self.chip = chip
        self.SetScrollRate(10, 10)

        mainSizer = wx.BoxSizer(wx.HORIZONTAL)

        self.valveSizer = wx.BoxSizer(wx.VERTICAL)
        self.add_valve_toggles(parent.Parent.control.valve_num)

    def add_valve_toggles(self, num):
        valve_closed_color = VALVE_CLOSED_COLOR
        valve_opened_color = VALVE_OPENED_COLOR
        if self.chip is None: 
            valves = list(range(num))
        else:
            valves = self.chip['valves']
        for valve_step, valve_no in enumerate(valves):
            ### HACK ###
            if valve_step >= num:
                break
            ### HACK ###
            label = "V%02d" % valve_step
            name = "valveBtn%02d" % valve_step
            name_t = "valveTxt%02d" % valve_step
            try:
                text = valves[valve_no]['name']
            except:
                text = "NA"
            hsizer = wx.BoxSizer(wx.HORIZONTAL)
            new_button = wx.ToggleButton(self, label = label, name = name, size = (50,50))
            new_button.SetBackgroundColour(valve_closed_color)
            new_button.Bind(wx.EVT_TOGGLEBUTTON, self.Parent.Parent.toggle)
            new_text = wx.TextCtrl(self, value=text, name = name_t)
            new_text.Bind(wx.EVT_KEY_UP, self.update_text)
            hsizer.Add(new_button, 0, wx.ALL, 5)
            hsizer.Add(new_text, 0, wx.ALL, 5)
            self.valveSizer.Add(hsizer, 0, wx.ALL, 5 )
        self.SetSizer(self.valveSizer)

    def toggle(self, event):
        valve_closed_color = VALVE_CLOSED_COLOR
        valve_opened_color = VALVE_OPENED_COLOR
        o = event.GetEventObject()
        valve_no = filter( str.isdigit, str(o.GetLabel()) )
        state = o.GetValue()
        if state == True:
            self.valveControl.valveOn(int(valve_no))
        else:
            self.valveControl.valveOff(int(valve_no))

    def update_text(self, event):
        o = event.GetEventObject()
        valve_no = filter( str.isdigit, str(o.GetName()) )
        value = o.GetValue()
        self.chip['valves'][valve_no]['name'] = value
        self.chip.update()




