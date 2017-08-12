# !/usr/bin/env python

# [Future imports]
# "print" function compatibility between Python 2.x and 3.x
from __future__ import print_function
# Use Python 3.x "/" for division in Pyhton 2.x
from __future__ import division

# [File header]     | Copy and edit for each file in this project!
# title             : mfcs-ezWrapper.py
# description       : Microfluidic Control - Gallil craction collector control
# author            : Bjorn Harink
# credits           : Kurt Thorn, Huy Nguyen
# date              : 20150901
# version update    : 20161208
# version           : v0.4.0
# usage             : Use as module
# notes             : General functions wrapper for flow control. Must be the same for all flow control hardware!
# python_version    : 2.7


# [Modules]
# General Python
import sys
import warnings
import time
import thread
# IO
from IPy import IP
import gclib

# [CONSTANTS]
# Galil counts to mm conversion --> Move into function
X_MM = 2012.072  # counts to mm
Y_MM = 402.317   # counts to mm

class Load(object):
    """Gallil Fraction Collector wrapper for Microfluidics Control

    Parameters
    ----------
    port : str
        Communication port for Gallil control.
    """

    def __init__(self, port):
        self._port = port
        self._status = None
        self._output = None
        self._position = None
        self._client = gclib.py()

    def __repr__(self):
        """Returns client of the Gallil controller.
        """
        return repr([self._client])

    def __del__(self):
        self.close()

    @property
    def port(self):
        return self._port

    @property
    def status(self):
        return self._status

    @property
    def output(self):
        return self._output
    
    @property
    def position(self, value=None):
        if value is not None:
            return self._position[value]
        else:
            return self._position

    def connect(self):
        if 'COM' in self._port:
            com = self._port + ' --direct'
            try: 
                self._output = self._client.GOpen(com)  # COM/Serial connection default 115200 baud
                self._status = True
            except:
                print("Could not load Galil: %s" % self._output)
                self._status = False
        elif IP(self._port):
            try:
                self._output = self._client.GOpen(self._port, '--direct')  # TCP/IP connection
                self._status = True
            except:
                print("Could not load Galil: %s" % self._output)
                self._status = False
        else:
            IOError('Incorrect connection settings for collect module: %s' % self._port)
        if self._status is True:
            print(self._client.GInfo())
            self._command('EO 0')     # Turn off comand echo
            self._command('CN 1, 1')  # Switch on X/Y limit switches high

    def close(self):
        try:
            self._output = self._client.GClose()
            print('Collect hardware connection closed.')
        except IOError:
            print('Collect hardware connection error: %s' % self._output)

    # Base functions
    def _command(self, string):
        try:
            output = self._client.GCommand(string)
            self._output = output
            return output
        except gclib.GclibError:
            if self.output == '?':
                print("Gallil busy...")
            else:
                print("Gallil returned error: %s " % self.output)

    def _error_code(self, code):
        """Error code handler
        """
        if code == 22:
            print('Limit switch tripped. Move other direction.')
        else:
            print('Code:' + code + ' unknown.')

    # Minimum functions
    def stop(self):
        print('STOP')
        self._command('ST')

    def check_limits(self):
        self._command('TC')
        if self._ouput == 22: 
            self._error_code(self._output)

    def homing(self):
        """Stage homing.
        """
        self._command('HM')
        print('Homing X-axis...')
        self._command('BGA')
        sleep(5)
        print('Homing X-axis')
        self._command('BGB')

    def update_position(self):
        """Update current position.
        """
        outx = self._command('TPA')
        x_conv = float(outx)/X_MM
        outy = self._command('TPB')
        y_conv = float(outy)/Y_MM
        #print( 'Current position is: ' + str(x_conv) + ' mm, ' + str(y_conv) + ' mm')
        self._position =  {'x':x_conv, 'y':y_conv}

    def set_home(self):
        """Set current position as home position.
        """
        print("Setting home position.")
        self._command('DP 0,0')

    def move_abs(self, x, y):
        """Move absolute in mm.
        """
        x_conv = str(float(x)* X_MM)
        y_conv = str(float(y)* Y_MM)
        self._command('PA ' + x_conv + ',' + y_conv)
        self._command('BG X,Y')
        out = self._command('PA ?,?')
        print("Moved to absolute position: %s" % out)

    def home(self):
        """Go to home position.
        """
        self._command('PA 0,0')
        self._command('BG X,Y')
        out = self._command('PA ?,?')
        print("Moved to absolute position: %s" % out)

    def move_rel(self, x, y):
        """Move relative in mm.
        """
        x_conv = str(float(x)* X_MM)
        y_conv = str(float(y)* Y_MM)
        self._command('PR ' + x_conv + ',' + y_conv)
        self._command('BG X,Y')
        out = self._command('PA ?,?')
        print("Moved to position: %s" % out)

    def set_speed(self, speed):
        """Set speed in mm/s.
        """
        if speed <= 1:
            speed = 1
        x_conv = str(speed*X_MM)
        y_conv = str(speed*Y_MM)
        out = self._command('SP' + x_conv + ',' + y_conv)
        self.get_speed()

    def get_speed(self):
        """Get surrent speed setting in mm/s.
        """
        out = self._command('SP ?, ?')
        out = out.split(',')
        outx = float(out[0])/X_MM
        outy = float(out[1])/Y_MM
        print("Current speed: X %0.1f Y %0.1f mm/s" % (outx, outy))
        return outx
