# !/usr/bin/env python

# [Future imports]
# "print" function compatibility between Python 2.x and 3.x
from __future__ import print_function
# Use Python 3.x "/" for division in Pyhton 2.x
from __future__ import division

# [File header]     | Copy and edit for each file in this project!
# title             : baseMain.py
# description       : Microfluidic Control - Base - Gui
# author            : Bjorn Harink
# credits           : Kurt Thorn, Huy Nguyen
# date              : 20150901
# version update    : 20160901
# version           : v0.4.0
# usage             : Use as main gui window
# notes             : 
# python_version    : 2.7


# [Modules]
# General Python
import warnings
import os
# GUI
import wx
from baseMain import __version__ as version
from baseMain import __copyright__ as copyright
# Project
import config

class MainWindow(wx.Frame):
    """This is the main window for the base of the Microfluidic Control program.
    """
    def __init__(self, parent, config_handler):
        super(MainWindow, self).__init__(parent)
        self.SetTitle('Microfluidic Control - Main - %s' % version)
        
        # Load config
        self.config = config_handler
        
        # Window Size/Postion Handler
        self.window_position = config.WindowPosition(self, self.config.main)

        # Add Menu Bar
        self.menu_bar()

        self.mainSizer = wx.BoxSizer(wx.HORIZONTAL)
        self.mainPanel = wx.Panel(self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL)

        panelSizer = wx.BoxSizer(wx.VERTICAL)
        self.hPanel = StatusPanel(self.mainPanel)
        panelSizer.Add(self.hPanel, 0, wx.ALIGN_RIGHT|wx.EXPAND|wx.ALL, 5)
        static_line = wx.StaticLine(self.mainPanel)
        panelSizer.Add(static_line, 0, wx.ALIGN_RIGHT|wx.EXPAND|wx.ALL, 5)
        self.cPanel = ChipPanel(self.mainPanel)
        panelSizer.Add(self.cPanel, 0, wx.ALIGN_RIGHT|wx.EXPAND|wx.ALL, 5)
        static_line = wx.StaticLine(self.mainPanel)
        panelSizer.Add(static_line, 0, wx.ALIGN_RIGHT|wx.EXPAND|wx.ALL, 5)
        self.sPanel = ScriptPanel(self.mainPanel)
        panelSizer.Add(self.sPanel, 1, wx.ALIGN_RIGHT|wx.EXPAND|wx.ALL, 5)
        
        self.mainPanel.SetSizerAndFit(panelSizer)
        self.mainSizer.Add(self.mainPanel, 1, wx.EXPAND, 5)

        #self.mainSizer.Fit(self)
        self.SetSizer(self.mainSizer)
        self.Layout()

        # Bindings and updates
        self.window_position.update()
        self.Bind(wx.EVT_MOVE, self.update)
        self.Bind(wx.EVT_SIZE, self.update)

    def update(self, event):
        self.Layout()
        self.window_position.update()

    def menu_bar(self):
        """Setting up menu bar.
        """
        menubar = wx.MenuBar()
        
        # File menu items
        fileMenu = wx.Menu()
        self.fileItem = fileMenu.Append(wx.ID_EXIT, 'Quit', 'Quit application')
        self.Bind(wx.EVT_MENU, self.on_close, self.fileItem)
        
        # Edit menu items
        editMenu = wx.Menu()
        self.editItem = editMenu.Append(wx.ID_EDIT, 'Config', 'Config application')
        self.Bind(wx.EVT_MENU, self.show_config, self.editItem)
        
        # About menu items
        aboutMenu = wx.Menu()
        self.aboutItem = aboutMenu.Append(wx.ID_HELP, 'About', 'About application')
        self.Bind(wx.EVT_MENU, self.show_about, self.aboutItem)

        # Init menu
        menubar.Append(fileMenu, '&File')
        menubar.Append(editMenu, '&Edit')
        menubar.Append(aboutMenu, '&Help')  
        self.SetMenuBar(menubar)

    def on_close(self, event):
        self.Close()

    def show_about(self, event):
        wx.MessageBox(copyright, 'About', wx.OK | wx.ICON_INFORMATION)

    def show_config(self, event):
        wx.MessageBox('Configuration Menu', 'Config', wx.OK | wx.ICON_INFORMATION)

class ScriptPanel(wx.Panel):
    """Script Panel
    """
    def __init__(self, parent): 
        super(ScriptPanel, self).__init__(parent) 
        statusBox = wx.StaticBox(self, -1, "Script")
        mainSizer = wx.StaticBoxSizer(statusBox, wx.VERTICAL)

        btnSizer = wx.BoxSizer(wx.HORIZONTAL)
        self.btnStart = wx.Button(self, label=u"Start")
        self.btnPause = wx.ToggleButton(self, label=u"Pause")
        self.btnStop  = wx.Button(self, label=u"Stop")
        self.btnEdit  = wx.Button(self, label=u"Update")
        btnSizer.AddMany([(self.btnStart, 1, wx.EXPAND|wx.ALL, 2),
                          (self.btnPause, 1, wx.EXPAND|wx.ALL, 2), 
                          (self.btnStop,  1, wx.EXPAND|wx.ALL, 2), 
                          (self.btnEdit,  1, wx.EXPAND|wx.ALL, 2)])
        btnSizer.Fit(self)
        mainSizer.Add(btnSizer, 0, wx.EXPAND|wx.ALL, 5)

        self.comboScript = wx.ComboBox(self, style=wx.CB_READONLY, size=(-1,25))
        self.comboScript.Bind(wx.EVT_COMBOBOX_DROPDOWN, self.update_script_combo)
        mainSizer.Add(self.comboScript, 0, wx.EXPAND|wx.ALL, 7)
        
        self.scriptEdit = wx.ListCtrl(self)
        self.scriptEdit.SetMinSize((300,300))
        mainSizer.Add(self.scriptEdit, 1, wx.EXPAND|wx.ALL, 7)
 
        self.SetSizerAndFit(mainSizer)

    def update_script_combo(self, event):
        chip = self.Parent.Parent.config.chip.name
        scripts = next(os.walk('chips/' + chip + '/scripts'))[2]
        self.comboScript.Clear()
        self.comboScript.AppendItems(scripts)

class ChipPanel(wx.Panel):
    """Script Panel
    """
    def __init__(self, parent): 
        super(ChipPanel, self).__init__(parent) 
        statusBox = wx.StaticBox(self, -1, "Chip")
        mainSizer = wx.StaticBoxSizer(statusBox, wx.VERTICAL)

        chipChoiceSizer = wx.BoxSizer(wx.HORIZONTAL)
        self.comboChip = wx.ComboBox(self, style=wx.CB_READONLY, size=(-1,25))
        self.comboChip.Bind(wx.EVT_COMBOBOX_DROPDOWN, self.update_chip_combo)
        self.comboChip.Bind(wx.EVT_COMBOBOX_CLOSEUP, self.chip_change)
        chipChoiceSizer.Add(self.comboChip, 3, wx.EXPAND|wx.ALL, 2)
        self.launchChip = wx.Button(self, label=u"Launch")
        chipChoiceSizer.Add(self.launchChip, 1, wx.EXPAND|wx.ALL, 2)
        chipChoiceSizer.Fit(self)
        mainSizer.Add(chipChoiceSizer, 0, wx.EXPAND|wx.ALL, 5)
        
        self.SetSizerAndFit(mainSizer)

    def update_chip_combo(self, event):
        chips = next(os.walk('chips'))[1]
        self.comboChip.Clear()
        self.comboChip.AppendItems(chips)
        self.Parent.Parent.sPanel.update_script_combo(event)

    def chip_change(self, event):
        self.Parent.Parent.config.chip.name = self.comboChip.GetValue()   

class StatusPanel(wx.Panel):
    """Status Panel
    """
    def __init__(self, parent): 
        super(StatusPanel, self).__init__(parent)
        statusBox = wx.StaticBox(self, -1, "Status")
        mainSizer = wx.StaticBoxSizer(statusBox, wx.VERTICAL)

        statusSizer = wx.BoxSizer(wx.HORIZONTAL)
        self.checkCollect = wx.Button(self, label=u"Collect")
        self.checkFlow = wx.Button(self, label=u"Flow")
        self.checkImage = wx.Button(self, label=u"Image")
        self.checkValve = wx.Button(self, label=u"Valve")
        statusSizer.AddMany([(self.checkCollect, 1, wx.EXPAND|wx.ALL, 2), 
                           (self.checkFlow, 1, wx.EXPAND|wx.ALL, 2), 
                           (self.checkImage, 1, wx.EXPAND|wx.ALL, 2), 
                           (self.checkValve, 1, wx.EXPAND|wx.ALL, 2)])
        statusSizer.Fit(self)
        mainSizer.Add(statusSizer, 0, wx.EXPAND|wx.ALL, 5)
        
        self.SetSizerAndFit(mainSizer)