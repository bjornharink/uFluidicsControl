# !/usr/bin/env python
from __future__ import print_function   # "print" function compatibility between Python 2.x and 3.x
from __future__ import division
# Project | specific project modules

"""
Main script syntax for Valving module:

"""

## Script variables
# Identification
dateCreated = "2016-01-09"  # YYYY-MM-DD
chipSerial = "BS2.4-MBM-2016-01-09-M01-D01"

# Microscope (MMC) settings
polymerChannel = 'Polymerization'

# Valve and pressure settings
maxMfcsPressure = 14        # MFCS max absolute pressure [PSI]
maxPressure = 14            # MFCS max desired pressure [PSI]
oilMfcsCh = 1               # MFCS oil channel no.
oilPressure = 8             # MFCS oil pressure [PSI]
pushWaterMfcsCh = 2         # MFCS push water channel no.
pushWaterPressure = 12      # MFCS push water pressure [PSI]
lanthanideMfcsCh = [3, 5, 6, 7, 4]  # MFCS Lanthanide channel no. See Lanthanides variables

# Lanthanides
colors = np.array(['Sm', 'Dy', 'Tm', 'CeTb', 'Eu'])
numColors = colors.size
csvFile = 'SmTest_5Codes.csv'

# Timings [seconds]
mixerCleanTime = 10             # Mixer cleaning/flushing
mixingTime = 105                # Formulation mixing
dropStabilizationTime = 10      # Drop stabilization
dropPushStabilizationTime = 15  # Drop push stabilization
polymerTime = 150               # UV polymerization

## Script classes and definitions
# Correction factors and resistances
class mixData():
    # Mixer 1
    def M1():
        # Correction factors for input resistances
        c1 = 0.84           # RSm/REu = WidthEu/WidthSm
        c2 = 1.000          # RDy/REu = WidthEu/WidthDy
        c3 = 1.000          # RTm/REu = WidthEu/WidthTm
        c4 = 1.000          # RCeTb/REu = WidthEu/WidthCeTb
        c_mix = 1/25         # Rmix/REu = Pmix/(PEu - Pmix)
        # Input and mixer resistances
        r5 = maxPressure    # Eu
        r1 = c1*r5          # Sm
        r2 = c2*r5          # Dy
        r3 = c3*r5          # Tm
        r4 = c4*r5          # CeTb
        r_mix = Cmix*R5
        resistors = {'R1':r1, 'R2':r2, 'R3':r3, 'R4':r4, 'R5':r5, 'Rmix':r_mix}
        return Resistors
    # Mixer 2
    def M2():
        # Correction factors for input resistances
        c1 = 0.84           # RSm/REu = WidthEu/WidthSm
        c2 = 1.000          # RDy/REu = WidthEu/WidthDy
        c3 = 1.000          # RTm/REu = WidthEu/WidthTm
        c4 = 1.000          # RCeTb/REu = WidthEu/WidthCeTb
        c_mix = 1/25         # Rmix/REu = Pmix/(PEu - Pmix)
        # Input and mixer resistances
        r5 = maxPressure    # Eu
        r1 = c1*r5          # Sm
        r2 = c2*r5          # Dy
        r3 = c3*r5          # Tm
        r4 = c4*r5          # CeTb
        r_mix = Cmix*R5
        resistors = {'R1':r1, 'R2':r2, 'R3':r3, 'R4':r4, 'R5':r5, 'Rmix':r_mix}
        return Resistors

## Script initiation
class Load():
    """ 
    Script
    """
    ### Self instantiation
    def __init__(self, control):
        self.control = control
        self.start()

    def start(self):
        """Start procedure
        """
        self.control.valving.valve_on('Mx2Out')

    def loop(self):
        """Loop procedure"""
        self.control.valveOn('[Mx2Out]')
        self.control.valveOn('[Sieve]')
        self.control.valveOn('[Ro2]')
        self.control.delaySec(10)
        self.control.valveOff('[Mx2Out]')
        self.control.valveOff('[Sieve]')
        self.control.valveOff('[Ro2]')

    def pause(self):
        """Pause procedure"""
        self.control.valveCloseAll()
        self.control.valveOn('[Mx2Out]')
        self.control.valveOn('[Sieve]')
        self.control.valveOn('[Ro2]')
        self.control.delaySec(10)
        self.control.valveOff('[Mx2Out]')
        self.control.valveOff('[Sieve]')
        self.control.valveOff('[Ro2]')

    def stop(self):
        """Stop procedure
        """
        self.control.valveCloseAll()
        self.control.valveOn('[Mx2Out]')
        self.control.valveOn('[Sieve]')
        self.control.valveOn('[Ro2]')
        self.control.delaySec(10)
        self.control.valveOff('[Mx2Out]')
        self.control.valveOff('[Sieve]')
        self.control.valveOff('[Ro2]')

    def emergency(self):
        """Emergency procedure"""
        self.control.valveCloseAll()