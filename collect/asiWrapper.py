# !/usr/bin/env python

# [Future imports]
# "print" function compatibility between Python 2.x and 3.x
from __future__ import print_function
# Use Python 3.x "/" for division in Pyhton 2.x
from __future__ import division

# [File header]     | Copy and edit for each file in this project!
# title             : asiWrapper.py
# description       : Microfluidic Control - ASI fraction collector control
# author            : Bjorn Harink
# credits           : Kurt Thorn, Huy Nguyen, Scott Longwell
# date              : 20170808
# version update    : 20170808
# version           : v0.1.0
# usage             : Use as module
# notes             : General functions wrapper for collect control. Must be the same for all collect control hardware!
# python_version    : 2.7


# [Modules]
# General Python
import sys
import warnings
import time
import thread
import re
# IO
from IPy import IP
#import gclib
from serial import Serial

# [CONSTANTS]
# Galil counts to mm conversion --> Move into function
X_MM = 10000   # counts to mm
Y_MM = 10000   # counts to mm
MAX_SPEED = 8.6

CONTROLLER = "ASI MS-2000"
BAUD_RATE = 115200
TEMRINATOR = "\r"

class Load(object):
    """ASI Fraction Collector wrapper for Microfluidics Control

    Parameters
    ----------
    port : str
        Communication port for collect control.
    """

    def __init__(self, port):
        self._port = port
        self._status = None
        self._output = None
        self._position = None
        self._client = Serial()

    def __repr__(self):
        """Returns client of the collect controller.
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
            com = self._port
            #try:
            self._client.baudrate = BAUD_RATE
            self._client.port = self._port
            self._client.open()
            self._status = True
            print("ASI Connected: %s"%self._port)
            #except:
                #print("Could not load %s: %s" % (CONTROLLER, self._output))
                #self._status = False
        else:
            IOError('Incorrect connection settings for collect module: %s' % self._port)
        if self._status is True:
            self._command('2H MC X+ Y+')

    def close(self):
        try:
            self._output = self._client.close()
            print('Collect hardware connection closed.')
        except IOError:
            print('Collect hardware connection error: %s' % self._output)

    # Base functions
    def _write(self, send_string):
        #try:
        output = self._client.write(bytes(send_string+TEMRINATOR))
        self._output = output
        #except IOError:
        #   print("Colector returned error: %s " % self._output)

    def _read(self):
        time.sleep(0.05)
        buffer_bytes = self._client.inWaiting()
        buffer_string = self._client.read(buffer_bytes).decode('utf-8')
        #print("ASI out: %s"%buffer_string)
        return buffer_string

    def _busy(self):
        self._write('2H STATUS')
        if 'B' in self._read():
            return True
        else:
            return False

    def _command(self, string, wait=True):
        #try:
        busy=True
        while (self._busy() is True) and (wait is True):
            if busy is True:
                print("Fraction collector busy...")
                busy=False
            time.sleep(0.1)
        self._client.flush()
        self._write(string)
        #time.sleep(0.05)
        self._output = self._read()
        return self._output
        #except IOError:
        #    print("Colector returned error: %s " % self._output)

    def _error_code(self, code):
        """Error code handler
        """
        if code == 22:
            print('Limit switch tripped. Move other direction.')
        else:
            print('Code:' + code + ' unknown.')

    # Minimum functions
    def stop(self):
        print('HALT')
        self._command('2H HALT', wait=False)

    def homing(self):
        """Stage homing.
        """
        self._command('2H HOME X Y')
        print('Homing ...')

    def update_position(self):
        """Update current position.
        """
        out = self._command('2H W X')        
        try:
            outx = float(re.search(r"\d+.\d{1}", out).group())
            x_conv = float(outx)/X_MM    
        except:
            x_conv = 0
        out = self._command('2H W Y')
        try:
            outy = float(re.search(r"\d+.\d{1}", out).group())
            y_conv = float(outy)/Y_MM
        except:
            y_conv = 0
        #print( 'Current position is: ' + str(x_conv) + ' mm, ' + str(y_conv) + ' mm')
        self._position =  {'x':x_conv, 'y':y_conv}

    def set_home(self):
        """Set current position as home position.
        """
        print("Setting home position.")
        self._command('2H HERE X Y')

    def move_abs(self, x, y):
        """Move absolute in mm.
        """
        if x != 0:
            x_conv = str(float(x)* X_MM)
        else:
            x_conv = str(0)
        if y != 0:
            y_conv = str(float(y)* Y_MM)
        else:
            y_conv = str(0)
        self._command('2H M X='+x_conv+' Y='+y_conv)
        while self._busy() is True:
            time.sleep(0.2)
        self.update_position()
        print("Moved absolute position: %0.1f, %0.1f" % (self._position['x'],self._position['y']))

    def home(self):
        """Go to home position.
        """
        out = self.move_abs(0,0)
        while self._busy() is True:
            time.sleep(0.2)
        self.update_position()
        print("Moved home position: %0.1f mm, %0.1f mm" % (self._position['x'],self._position['y']))

    def move_rel(self, x, y):
        """Move relative in mm.
        """
        x_conv = str(float(x)* X_MM)
        y_conv = str(float(y)* Y_MM)
        self._command('2H R X='+x_conv+' Y=' + y_conv)
        while self._busy() is True:
            time.sleep(0.2)
        self.update_position()
        print("Moved relative position: %0.1f mm, %0.1f mm" % (self._position['x'],self._position['y']))

    def set_speed(self, speed):
        """Set speed in mm/s.
        """
        if speed > MAX_SPEED:
            speed = MAX_SPEED
        out = self._command('2H S X=%0.1f Y=%0.1f' % (speed, speed))
        self.get_speed()

    def get_speed(self):
        """Get surrent speed setting in mm/s.
        """
        out = self._command('2H S X?')
        try:
            outx = float(re.search(r"\d.\d{6}", out).group())
        except:
            outx = float(0)
        out = self._command('2H S Y?')
        try:
            outy = float(re.search(r"\d.\d{6}", out).group())
        except:
            outy = float(0)
        print("Current speed: X %0.1f Y %0.1f mm/s" % (outx, outy))
        return outx
