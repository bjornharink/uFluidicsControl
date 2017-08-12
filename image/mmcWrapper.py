# !/usr/bin/env python

# [Future imports]
# "print" function compatibility between Python 2.x and 3.x
from __future__ import print_function
# Use Python 3.x "/" for division in Pyhton 2.x
from __future__ import division

# [File header]     | Copy and edit for each file in this project!
# title             : mmcWrapper.py
# description       : Microfluidic Control - MicroManager Control (MMC)
# author            : Bjorn Harink
# credits           : Kurt Thorn, Huy Nguyen
# date              : 20150901
# version update    : 20161212
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
import cv2
import MMCorePy  # Micro Manager

# [CONSTANTS]
VIDEO_BUFFER_SIZE = 2048 # MB
EXPOSURE = 10

class Load(object):
    """Fluigent MFCS-EZ wrapper for Microfluidics Control

    Parameters
    ----------
    serials : str, list (of str)
        Serial(s) of MFCS-EZ controller(s) in strings (or list of strings).
    """

    def __init__(self, config_file):
        self._config_file = config_file
        self._status = None

        # Init Micro Manager core
        self._client = MMCorePy.CMMCore()
        

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

    def connect(self):
        print("Initializing Micro-Manager Control")
        print("Micro Manager: %s initialized" % self._client.getVersionInfo())
        # Load Micro Manager devices
        #self._client.loadSystemConfiguration("C:/Program Files/Micro-Manager-1.4/MMConfig_demo.cfg")
        self._client.loadSystemConfiguration("C:/Program Files/Micro-Manager-1.4/MMConfig_demo.cfg")
        self._status = True
        # Config settings
        self._client.enableStderrLog(False)
        self._client.enableDebugLog(False)
        self._client.setCircularBufferMemoryFootprint(VIDEO_BUFFER_SIZE)
        self._client.setAutoShutter(True)
        #self.mmc.setConfig("Channel", "BF")
        #self.mmc.setProperty("Andor", "Binning", "2")
        #self.mmc.setProperty("Andor", "Exposure", "25")

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
    def snapImage(self):
        self._client.snapImage()
        img = self._client.getImage()
        return img

    def liveImage(self):
        cv2.namedWindow('Video')
        self._client.startContinuousSequenceAcquisition(EXPOSURE)
        while True:
            #img = self._client.getLastImage()
            if self._client.getRemainingImageCount() > 0:
                img = self._client.popNextImage()
                #img = self._client.getLastImage()
                cv2.imshow('Video', img)
            else:
                print('No frame')
            if cv2.waitKey(20) >= 0:
                break
        cv2.destroyAllWindows()
        self._client.stopSequenceAcquisition()
        self._client.reset()


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