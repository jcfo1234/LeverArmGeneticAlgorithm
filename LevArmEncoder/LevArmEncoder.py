'''
Created on Mar 6, 2015

@author: JFandino
'''

from decimal import Decimal

class MyLevArmEncoder(object):
    '''
    This class encodes each component of the lever arm vector into a 
    binary value of a user defined number of bits
    '''

    def __init__(self):
        '''
        Constructor
        '''
        # Dimensions of the VAN in any direction
        self._MIN_LEV_ARM = -Decimal(5)
        self._MAX_LEV_ARM = Decimal(5)
        # Resolution supported by Inertial Explorer
        self._RESOLUTION = Decimal(0.001).quantize(Decimal(10) ** -3)
        # Build Dictionary
        self._ENCODEDDICT = {}
        self._DECODEDDICT = {}
        minvalue = self._MIN_LEV_ARM / self._RESOLUTION
        maxvalue = self._MAX_LEV_ARM / self._RESOLUTION
        i = minvalue.quantize(Decimal(10) ** 0)
        while i <= maxvalue.quantize(Decimal(10) ** 0):
            KeyValue = i / 1000
            # Encode with two's complement the negative decimal numbers
            if (i < 0):
                self._ENCODEDDICT[KeyValue] = bin(((1 << 16) - 1) & int(i))[2:].rjust(16,'0')
                self._DECODEDDICT[bin(((1 << 16) - 1) & int(i))[2:].rjust(16,'0')] = KeyValue
            # Encoding of positive numbers
            else:
                self._ENCODEDDICT[KeyValue] = bin(int(i))[2:].rjust(16,'0')
                self._DECODEDDICT[bin(int(i))[2:].rjust(16,'0')] = KeyValue
            i = i + 1
            
    def _GetKeyValueCoord(self, Value_):
        '''
        Computes Key value to return encoding sequence
        '''
        # Chop values of lever arm greater than operational range
        if (Decimal(Value_).quantize(Decimal(10) ** -3) > Decimal(5)):
            return Decimal(5).quantize(Decimal(10) ** -3)
        # Chop values of lever arm less than operational range
        elif (Decimal(Value_).quantize(Decimal(10) ** -3) < -Decimal(5)):
            return -Decimal(5).quantize(Decimal(10) ** -3)
        # Lever arm in operational range
        else:
            return Decimal(Value_).quantize(Decimal(10) ** -3)
               
    def GetEncodedLeverArm(self, params):
        '''
        Returns binary encoded version of Lever Arm
        params[0]: X coordinate of lever arm
        params[1]: Y coordinate of lever arm
        params[2]: Z coordinate of lever arm
        '''
        KeyValuex = self._GetKeyValueCoord(params[0])
        KeyValuey = self._GetKeyValueCoord(params[1])
        KeyValuez = self._GetKeyValueCoord(params[2])
        return [self._ENCODEDDICT[KeyValuex], self._ENCODEDDICT[KeyValuey], self._ENCODEDDICT[KeyValuez]]
    
    def GetMaxLeverArm(self):
        return self._MAX_LEV_ARM
    
    def GetfMaxLeverArm(self):
        return float(self._MAX_LEV_ARM)
    
    def GetMinLeverArm(self):
        return self._MIN_LEV_ARM
    
    def GetfMinLeverArm(self):
        return float(self._MIN_LEV_ARM)
    
    def GetResolutionInverse(self):
        return Decimal(1) / self._RESOLUTION
    
    def GetfResolutionInverse(self):
        return float(Decimal(1) / self._RESOLUTION)
    
    def GetResolution(self):
        return self._RESOLUTION
    
    def GetfResolution(self):
        return float(self._RESOLUTION)
    
    def GetEncodedLeverArmDict(self):
        return self._ENCODEDDICT
    
    def GetDecodedLeverArmDict(self):
        return self._DECODEDDICT
    
    def GetEncoderLength(self):
        return len(self._ENCODEDDICT)
