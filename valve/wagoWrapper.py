# !/usr/bin/env python

# [Future imports]
# "print" function compatibility between Python 2.x and 3.x
from __future__ import print_function
# Use Python 3.x "/" for division in Pyhton 2.x
from __future__ import division

# [File header]     | Copy and edit for each file in this project!
# title             : wagoWrapper.py
# description       : Microfluidic Control - Wago Control
# author            : Bjorn Harink
# credits           : Kurt Thorn, Huy Nguyen
# date              : 20150901
# version update    : 20160808
# version           : v0.4.0
# usage             : Use as module
# notes             : General functions wrapper for flow control. Must be the same for all flow control hardware!
# python_version    : 2.7


# [Modules]
# General Python
import warnings
# IO
from pymodbus.client.sync import ModbusTcpClient as ModbusClient
from pymodbus.pdu import ModbusRequest

class Load(object):
    """Wago wrapper for Microfluidics Control

    Parameters
    ----------
    ip : str
        IP address of WAGO controller.

    valves : int
        Number valves controlled by WAGO controller.

    reg_addr : int
        Coil register address.
    """
    def __init__(self, config):
        self._config = config
        self._ip = self._config.hware['valving']['config'][0]
        self._valve_num = self._config.hware['valving']['config'][1]
        self._reg_addr = self._config.hware['valving']['config'][2]
        self._names = self._config.chip['valves']
        self._client = ModbusClient(self._ip)
        self._register = None

    def __repr__(self):
        """Returns Modbus client of the WAGO controller.
        """
        return repr([self._client])

    def __del__(self):
        self.close()

    @property
    def valve_num(self):
        return self._valve_num

    @property
    def ip(self):
        return self._ip

    @property
    def status(self):
        return self._register

    def connect(self):
        output = self._client.connect()
        if output is True:
            self.update()
            self.valve_set(False)
            print('Valve hardware connected to IP %s and initialized.' % self._ip)
        else:
            print('Could not connect to valve hardware: %s' % output)

    def close(self):
        try:
            wago_check = self._client.socket
            if wago_check is True:
                self._client.close()
                print('Valve hardware connection closed.')
            else:
                print('Valve hardware not initialized.')
        except IOError:
            print('Valve hardware connection error: %s' % self._client)

    # Base functions
    def _name2no(self, name):
        valve_name = name[1:-1]
        for valve_no in self._names:
            if valve_name in self.valves_data[valve_no]['name']:
                return int(valve_no)

    def _valve_func(self, num, state):
        if type(num) is str:
            num = self._name2no(num)
        self._client.write_coil(num, bool(state))

    def _reg_func(self):
        reg_read = self._client.read_coils(self._reg_addr, self._valve_num)
        return reg_read.bits

    # Minimum functions
    def update(self):
        self._register = self._reg_func()

    def valve_read(self, num=None):
        self.update()
        if type(num) is str:
            num = self._name2no(num)
        if num is None: 
            return self._register
        else: 
            return self._register[num]

    def valve_check(self, state, num=None):
        valve_read = self.valve_read(num)
        if state == valve_read:
            return True
        else:
            return False

    def valve_set(self, state=False, num=None):
        state = bool(state)
        if num is None:
            [self._valve_func(valve, state) for valve in xrange(self._valve_num)]
            state = [state] * self._valve_num
        else:
            self._valve_func(num, state)
        return self.valve_check(state, num)

    def valve_switch(self, num):
        wago_read = self.valve_read(num)
        if wago_read is True: valve_set(num, False)
        elif wago_read is False: valve_set(num, True)

    # Courtesy functions
    def valve_on(self, num=None):
        return self.valve_set(num, True)

    def valve_off(self, num=None):
        return self.valve_set(num, False)

