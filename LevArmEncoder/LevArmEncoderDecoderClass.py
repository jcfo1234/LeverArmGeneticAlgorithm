'''
Created on Mar 7, 2015

@author: JFandino
'''

import random
from decimal import Decimal
from LevArmEncoder import MyLevArmEncoder

class MyLevArmEncoderDecoderClass(object):
    '''
    classdocs
    '''
    # Static encoder, instanced once ONLY
    MYLEVERARMENCODER = MyLevArmEncoder()

    def __init__(self, params):
        '''
        Constructor
        '''
        # Lever arm Vector in Body frame coordinates
        # X-coordinate
        self._blevx = ''
        if (Decimal(params[0]) < self.MYLEVERARMENCODER.GetMaxLeverArm() and Decimal(params[0]) > self.MYLEVERARMENCODER.GetMinLeverArm()):
            self._levx = Decimal(random.triangular(self.MYLEVERARMENCODER.GetfMinLeverArm(), self.MYLEVERARMENCODER.GetfMaxLeverArm(), params[0])).quantize(Decimal(10) ** -3)
        else:
            self._levx = Decimal(random.triangular(self.MYLEVERARMENCODER.GetfMinLeverArm(), self.MYLEVERARMENCODER.GetfMaxLeverArm())).quantize(Decimal(10) ** -3)
        # Y-coordinate
        self._blevy = ''
        if (Decimal(params[1]) < self.MYLEVERARMENCODER.GetMaxLeverArm() and Decimal(params[1]) > self.MYLEVERARMENCODER.GetMinLeverArm()):
            self._levy = Decimal(random.triangular(self.MYLEVERARMENCODER.GetfMinLeverArm(), self.MYLEVERARMENCODER.GetfMaxLeverArm(), params[1])).quantize(Decimal(10) ** -3)
        else:
            self._levy = Decimal(random.triangular(self.MYLEVERARMENCODER.GetfMinLeverArm(), self.MYLEVERARMENCODER.GetfMaxLeverArm())).quantize(Decimal(10) ** -3)
        # Z-coordinate
        self._blevz = ''
        if (Decimal(params[2]) < self.MYLEVERARMENCODER.GetMaxLeverArm() and Decimal(params[2]) > self.MYLEVERARMENCODER.GetMinLeverArm()):
            self._levz = Decimal(random.triangular(self.MYLEVERARMENCODER.GetfMinLeverArm(), self.MYLEVERARMENCODER.GetfMaxLeverArm(), params[2])).quantize(Decimal(10) ** -3)
        else:
            self._levz = Decimal(random.triangular(self.MYLEVERARMENCODER.GetfMinLeverArm(), self.MYLEVERARMENCODER.GetfMaxLeverArm())).quantize(Decimal(10) ** -3)
        self._SetBinaryEncodedLeverArm()
        
    def GetLeverArm(self):
        '''
        Returns object's lever arm
        '''
        return [self._levx, self._levy, self._levz]
    
    def GetBinaryEncodedLeverArm(self):
        return [self._blevx, self._blevy, self._blevz]
    
    def _SetBinaryEncodedLeverArm(self):
        [self._blevx, self._blevy, self._blevz] = self.MYLEVERARMENCODER.GetEncodedLeverArm([self._levx, self._levy, self._levz])

    def SetLeverArm(self, szBinary_, ordinate_):
        '''
        Sets lever arm coordinate
        '''
        # Any value obtained not between -5000 and +5000 will get chopped
        if (Decimal(int(szBinary_,2)) > self.MYLEVERARMENCODER.GetMaxLeverArm() * self.MYLEVERARMENCODER.GetResolutionInverse() and Decimal(int(szBinary_,2)) < (Decimal(1 << 16) + self.MYLEVERARMENCODER.GetMinLeverArm() * self.MYLEVERARMENCODER.GetResolutionInverse())):
            # Positive lever arm
            if (int(szBinary_, 2) < (1 << 15)):
                dValue = Decimal(5)
            # Negative Lever arm
            else:
                dValue = -Decimal(5)
        # Lever arm within valid range
        else:
            # Positive lever arm
            if (int(szBinary_, 2) < (1 << 15)):
                dValue = self.MYLEVERARMENCODER.GetDecodedLeverArmDict()[szBinary_]
            else:
                dValue = self.MYLEVERARMENCODER.GetDecodedLeverArmDict()[bin(((1 << 16) - 1) & int(szBinary_, 2))[2:]]
        # x-coordinate
        if (ordinate_ == 0):
            self._levx = dValue
        # y-coordinate
        elif (ordinate_ == 1):
            self._levy = dValue
        # z-coordinate
        elif (ordinate_ == 2):
            self._levz = dValue
        self._SetBinaryEncodedLeverArm()
