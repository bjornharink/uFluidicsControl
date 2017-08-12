# !/usr/bin/env python

# [Future imports]
# "print" function compatibility between Python 2.x and 3.x
from __future__ import print_function
# Use Python 3.x "/" for division in Pyhton 2.x
from __future__ import division

# [File header]     | Copy and edit for each file in this project!
# title             : mfcs-ezWrapper.py
# description       : Microfluidic Control - Fluigent MFCS-EZ Control
# author            : Bjorn Harink
# credits           : Kurt Thorn, Huy Nguyen
# date              : 20150901
# version update    : 20161019
# version           : v0.4.0
# usage             : Use as module
# notes             : General functions wrapper for flow control. Must be the same for all flow control hardware!
# python_version    : 2.7


# [Modules]
# General Python
import sys
import warnings
import time
# IO
import ctypes  # Used for variable definition types
from ctypes import cdll  # Used to load dynamic linked libraries
mfcs_lib = cdll.LoadLibrary('flow/mfcs_64.dll')  # mfcs x64 library

# [CONSTANTS]
MBA2PSI = 0.0145037738007
MBA2KPA = 0.1
CHANNELS = 4
ALPHA = 5
P_LIMITS = {'mba':1034, 'psi':15, 'kpa':103.4}
P_FACTORS = {'mba':1, 'psi':MBA2PSI, 'kpa':MBA2KPA}

class Load(object):
    """Fluigent MFCS-EZ wrapper for Microfluidics Control

    Parameters
    ----------
    serials : str, list (of str)
        Serial(s) of MFCS-EZ controller(s) in strings (or list of strings).
    """

    def __init__(self, serials, unit='mba'):
        if type(serials) is list:
            self._serials = serials
        else:
            self._serials = [serials]
        self._status = [None] * len(self._serials)
        self._unit = unit
        ## Handle variables
        self._serial_check = ctypes.c_ushort(0)  # Serial number handler
        self._status_check = ctypes.c_char()  # Status handler
        self._c_error = ctypes.c_char()  # Error handler

    def __repr__(self):
        """Returns client of the MFCS-EZ controller.
        """
        return repr([self._client])

    def __del__(self):
        self.close()

    @property
    def channel_num(self):
        return len(self._client) * CHANNELS

    @property
    def status(self):
        return self._status

    @property
    def serials(self):
        return self._serials

    @property
    def error(self):
        return self._c_error

    @property
    def unit(self):
        return self._unit
    @unit.setter
    def unit(self, unit):
        self._unit = unit.lower()

    @property
    def limit(self):
        return P_LIMITS[self._unit]

    @property
    def factor(self):
        return P_FACTORS[self._unit]

    def connect(self):
        self._client = [None] * len(self._serials)
        print ('Initializng MFCS-EZ units')
        for idx, serial in enumerate(self._serials):
            self._client[idx] = mfcs_lib.mfcsez_initialisation(serial)
        time.sleep(1)
        # Check status
        for idx, handle in enumerate(self._client):
            self._c_error = mfcs_lib.mfcs_get_status(handle, ctypes.byref(self._status_check))
            if ord(self._status_check.value) == 1:
                self._status[idx] = True
            if (handle != 0) & (self._status[idx] == 1):
                self._c_error = mfcs_lib.mfcs_get_serial(handle, ctypes.byref(self._serial_check))
                print('MFCS-EZ initialized: %s' % self._serial_check.value)
                self._c_error = mfcs_lib.mfcs_set_alpha(handle, 0, ALPHA);   # Sends channel configuration
            elif self._c_error == 0 and ord(self._status_check.value) == 0:
                print('MFCS-EZ not primed. Push green button and restart.')
            else:
                print('Error on MFCS-EZ initialisation: %s Status: %s' % (self._c_error, ord(self._status_check.value)) )

    def close(self):
        print("closing flow")
        try:
            for idx, handle in enumerate(self._client):
                B_OK = bool(False)
                self._c_error = mfcs_lib.mfcs_get_serial(handle, byref(self._serial_check))
                # Close communication port 
                B_OK = mfcs_lib.mfcs_close(handle)
                if (B_OK == True):
                    print ('Connection closed to serial: %s' % self._serial_check.value)
                if (B_OK == False):
                    print ('Failed to close connection %s' % self._serial_check.value)
        except IOError:
            print('Flow hardware connection error: %s' % self._c_error)
        finally:
            # Release the DLL
            ctypes.windll.kernel32.FreeLibrary(mfcs_lib._handle)
            del mfcs_lib
            print ('MFCS library unloaded')

    # Base functions
    def _handle_select(self, num):
        handle_no = (int(num) - 1) // CHANNELS
        channel_no = int(num) - (CHANNELS * (handle_no) )
        return self._client[handle_no], int(channel_no)

    def _pressure_func(self, num, value):
        h, c = self._handle_select(num)
        self._c_error = mfcs_lib.mfcs_set_auto(h, c, ctypes.c_float(value) )

    def _read_func(self, num):
        pressure = ctypes.c_float()
        timer = ctypes.c_ushort()
        h, c = self._handle_select(num)
        self._c_error = mfcs_lib.mfcs_read_chan(h, c, ctypes.pointer(pressure), ctypes.pointer(timer))
        return pressure.value

    def _unit_conv(self, pressure, set=False, unit=None):
        if unit is None:
            unit = self._unit
        if unit == 'kpa':
            unit_factor = MBA2KPA
        elif unit == 'psi':
            unit_factor = MBA2PSI
        elif unit == 'mba':
            unit_factor = 1
        else:
            raise AttributeError("Available units: millibar: 'mba'; kilopascal: 'kpa'; and pounds-per-sqaure-inch: 'psi'. %s" % sys.exc_info()[0])
        if set is True:
            if type(pressure) is list:
                return [p/unit_factor for p in pressure]
            else:
                return pressure/unit_factor
        else:
            if type(pressure) is list:
                return [p*unit_factor for p in pressure]
            else:
                return pressure*unit_factor

    # Minimum functions
    def set_pressure(self, pressure=0, channel=None, unit=None):
        if unit is None:
            unit = self._unit
        if channel is None:
            [self._pressure_func(channel, self._unit_conv(pressure, set=True, unit=unit)) for channel in xrange(self.channel_num)]
        else:
            self._pressure_func(channel, self._unit_conv(pressure, set=True, unit=unit))

    def read_pressure(self, channel=None, unit=None):
        if unit is None:
            unit = self._unit
        if channel is None:
            pressure = [self._read_func(channel) for channel in xrange(1,self.channel_num+1)]
        else:
            pressure = self._read_func(channel)
        return self._unit_conv(pressure, unit=unit)