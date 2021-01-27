'''
Created on Feb 26, 2015

@author: JFandino
'''

import array
import binascii
import struct

class MyNHeader(object):
    '''
    classdocs
    NovAtel Header
    '''
    
    HEADER_BUFFER_SIZE = 28
    
    def __init__(self):
        '''
        Constructor
        NovAtel Header structure
        '''
        self._headbuff = array.array('B', [0]*self.HEADER_BUFFER_SIZE)
        # Useful Header information fields
        self._usmsgID   = 0
        self._cmsgType = 0
        self._ucPortAdd = 0
        self._usmsgLgth = 0
        self._ussequence = 0
        self._ucidletime = 0
        self._uctimestatus = 0
        self._usweek = 0
        self._fmilliseconds = 0
        self._ulRxStatus = 0
        self._usReserved = 0
        self._usSWVersion = 0
        
        
    def SetHeadBuff(self, params):
        '''
        Sets Header Binary Buffer from Array
        '''
        i = 0
        for Bytes in params:
            self._headbuff[i] = Bytes
            i = i+1
        self._SetusMsgID()
        self._SetcmsgType()
        self._SetucPortAdd()
        self._SetusmsgLgth()
        self._Setussequence()
        self._SetucIdletime()
        self._SetucTimeStatus()
        self._SetusWeek()
        self._Setfmilliseconds()
        self._SetulRxStatus()
        self._SetusReserved()
        self._SetusSWVersion()
   
    def _SetusMsgID(self):
        '''
        Sets Message ID
        '''
        self._usmsgID = (self._headbuff[5] << 8) | self._headbuff[4]
        
    def GetusMsgID(self):
        return self._usmsgID
        
    def _SetcmsgType(self):
        '''
        Sets Message Type
        '''
        self._cmsgType = self._headbuff[6]
        
    def GetcmsgType(self):
        return self._cmsgType
        
    def _SetucPortAdd(self):
        '''
        Sets Port Address
        '''
        self._ucPortAdd = self._headbuff[7]
        
    def GetucPortAdd(self):
        return self._ucPortAdd
        
    def _SetusmsgLgth(self):
        '''
        Sets Message Length
        '''
        self._usmsgLgth = (self._headbuff[9] << 8) | self._headbuff[8]
        
    def GetusmsgLgth(self):
        return self._usmsgLgth
        
    def _Setussequence(self):
        '''
        Set Log Sequence
        '''
        self._ussequence = (self._headbuff[11] << 8) | self._headbuff[10]
        
    def Getussequence(self):
        return self._ussequence
        
    def _SetucIdletime(self):
        '''
        Set Log Idle time
        '''
        self._ucidletime = self._headbuff[12]
        
    def GetucIdletime(self):
        return self._ucidletime
        
    def _SetucTimeStatus(self):
        '''
        Set Log Time status
        '''
        self._uctimestatus = self._headbuff[13]
        
    def GetucTimeStatus(self):
        return self._uctimestatus
        
    def _SetusWeek(self):
        '''
        Set Log Week Number
        '''
        self._usweek = (self._headbuff[15] << 8) | self._headbuff[14]
        
    def GetusWeek(self):
        return self._usweek
    
    def _Setfmilliseconds(self):
        '''
        Set GNSS Week milliseconds
        '''
        self._fmilliseconds = float((self._headbuff[19] << 24) | (self._headbuff[18] << 16) | (self._headbuff[17] << 8) | self._headbuff[16]) / 1000.0
        
    def Getfmilliseconds(self):
        return self._fmilliseconds
        
    def _SetulRxStatus(self):
        '''
        Set Log Receiver STATUS
        '''
        self._ulRxStatus = (self._headbuff[23] << 24) | (self._headbuff[22] << 16) | (self._headbuff[21] << 8) | self._headbuff[20]
        
    def GetulRxStatus(self):
        return self._ulRxStatus
        
    def _SetusReserved(self):
        '''
        Set Log reserved field
        '''
        self._usReserved = (self._headbuff[25] << 8) | self._headbuff[24]
        
    def GetusReserved(self):
        return self._usReserved
        
    def _SetusSWVersion(self):
        '''
        Set Log reserved field
        '''
        self._usSWVersion = (self._headbuff[27] << 8) | self._headbuff[26]
        
    def GetusSWVersion(self):
        return self._usSWVersion


class MyNPosition(MyNHeader):
    '''
    NovAtel Position logs structure
    '''
    # Size of position Logs
    POSITION_LOGS_BUFFER_SIZE = 72
    
    # Solution status of position logs
    SOLUTIONSTATUS = {0 : 'SOL_COMPUTED', 1 : 'INSUFFICIENT_OBS', 2 : 'NO_CONVERGENCE', 3 : 'SINGULARITY', 4 : 'COV_TRACE', 5 : 'TEST_DIST',
                      6 : 'COLD_START', 7 : 'V_H_LIMIT', 8 : 'VARIANCE', 9 : 'RESIDUALS', 10 : 'DELTA_POS', 11 : 'NEGATIVE_VAR', 12 : 'OLD_SOLUTION',
                      13 : 'INTEGRITY_WARNING', 14 : 'INS_INACTIVE', 15 : 'INS_ALIGNING', 16 : 'INS_BAD', 17 : 'IMU_UNPLUGGED', 18 : 'PENDING',
                      19 : 'INVALID_FIX', 20 : 'UNAUTHORIZED', 21 : 'ANTENNA_WARNING', 22 : 'INVALID_RATE', 23 : 'INS_AIDED'}
    
    # Position type status
    POSITIONTYPE = {0 : 'NONE', 1 : 'FIXEDPOS', 2 : 'FIXEDHEIGHT', 3 : 'FIXEDVEL', 4 : 'FLOATCONV', 5 : 'WIDELANE', 6 : 'NARROWLANE',
                    7 : 'DOPPLER_VELOCITY', 8 : 'SINGLE', 16 : 'SINGLE', 17 : 'PSRDIFF', 18 : 'WAAS', 19 : 'PROPAGATED', 20 : 'OMNISTAR',
                    32 : 'L1_FLOAT', 33 : 'IONOFREE_FLOAT', 34 : 'NARROW_FLOAT', 35 : 'L1L2_FLOAT', 46 : 'L1L2_INT', 47 : 'L1L2_INT_VERIFIED',
                    48 : 'L1_INT', 49 : 'WIDE_INT', 50 : 'NARROW_INT', 51 : 'RTK_DIRECT_INS', 52 : 'INS_SBAS', 53 : 'INS_PSRSP', 54 : 'INS_PSRDIFF',
                    55 : 'INS_RTKFLOAT', 56 : 'INS_RTKFIXED', 57 : 'INS_OMNISTAR', 58 : 'INS_OMNISTAR_HP', 59 : 'INS_OMNISTAR_XP', 
                    64 : 'OMNISTAR_HP', 65 : 'OMNISTAR_XP', 66 : 'CDGPS', 67 : 'EXT_CONSTRAINED', 68 : 'PPP_CONVERGING', 69 : 'PPP',
                    70 : 'OPERATIONAL', 71 : 'WARNING', 72 : 'OUT_OF_BOUNDS', 73 : 'INS_PPP_CONVERGING', 74 : 'INS_PPP', 75 : 'PPP_PLUS',
                    76 : 'INS_PPP_PLUS'}
    
    # Datum Type
    DATUM_TYPE = {1 : 'ADIND', 2 : 'ARC50', 3 : 'ARC60', 4 : 'AGD66', 5 : 'AGD84', 6 : 'BUKIT',  7 : 'ASTRO', 8 : 'CHATM', 9 : 'CARTH', 10 : 'CAPE', 
                  11 : 'DJAKA', 12 : 'EGYPT', 13 : 'ED50', 14 : 'ED79', 15 : 'GUNSG', 16 : 'GEO49', 17 : 'GRB36', 18 : 'GUAM', 19 : 'HAWAII', 
                  20 : 'KAUAI', 21 : 'MAUI',  22 : 'OAHU', 23 : 'HERAT', 24 : 'HJORS', 25 : 'HONGK', 26 : 'HUTZU', 27 : 'INDIA', 28 : 'IRE65', 
                  29 : 'KERTA', 30 : 'KANDA', 31 : 'LIBER', 32 : 'LUZON', 33 : 'MINDA', 34 : 'MERCH', 35 : 'NAHR', 36 : 'NAD83', 37 : 'CANADA', 
                  38 : 'ALASKA', 39 : 'NAD27', 40 : 'CARIBB', 41 : 'MEXICO', 42 : 'CAMER', 43 : 'MINNA', 44 : 'OMAN', 45 : 'PUERTO', 46 : 'QORNO', 
                  47 : 'ROME', 48 : 'CHUA', 49 : 'SAM56', 50 : 'SAM69', 51 : 'CAMPO', 52 : 'SACOR', 53 : 'YACAR', 54 : 'TANAN', 55 : 'TIMBA', 
                  56 : 'TOKYO', 57 : 'TRIST', 58 : 'VITI', 59 : 'WAK60', 60 : 'WGS72', 61 : 'WGS84', 62 : 'ZANDE', 63 : 'USER', 64 : 'CSRS', 
                  65 : 'ADIM', 66 : 'ARSM', 67 : 'ENW', 68 : 'HTN', 69 : 'INDB', 70 : 'INDI', 71 : 'IRL', 72 : 'LUZA', 73 : 'LUZB',  74 : 'NAHC', 
                  75 : 'NASP', 76 : 'OGBM', 77 : 'OHAA', 78 : 'OHAB', 79 : 'OHAC', 80 : 'OHAD', 81 : 'OHIA', 82 : 'OHIB', 83 : 'OHIC', 84 : 'OHID', 
                  85 : 'TIL', 86 : 'TOYM', 87 : 'NAD83OMNI', 88 : 'PE90'}
    
    def __init__(self):
        '''
        Constructor of NovAtel Position Logs
        '''
        self._posbuff = array.array('B', [0]*self.POSITION_LOGS_BUFFER_SIZE)
        super(MyNPosition, self).__init__()
        # Useful information fields
        self._eMyPositionStatus = self.SOLUTIONSTATUS[1]
        self._eMyPositionType = self.POSITIONTYPE[0]
        self._dMyLatitude = 0
        self._dMyLongitude = 0
        self._dMyHeight = 0
        self._fMyUndulation = 0
        self._eMyDatumType = self.DATUM_TYPE[61]
        self._fMyLatStdDev = 0
        self._fMyLongStdDev = 0
        self._fMyHgtStdDev = 0
        self._acMyBaseID = ""
        self._fMyDifferentialLag = 0
        self._fMySolutionAge = 0
        self._ucMyNumTracked = 0
        self._ucMyNumInSolution = 0
        self._ucMyNumInSolutionSingleFreq = 0
        self._ucMyNumInSolutionDualFreq = 0
        self._ucMyMeasurementSource = 0
        self._ucMyExtendedSolutionStatus = 0
        self._ucMyGALandBDSSignals = 0
        self._ucMyGPSandGLOSignals = 0
        
    def SetLogBuffer(self, params):
        '''
        Populate Position Log Buffer
        '''
        # Populate Header Buffer
        self.SetHeadBuff(params[0:MyNHeader.HEADER_BUFFER_SIZE])
        i = 0
        for Bytes in params[self.HEADER_BUFFER_SIZE:]:
            self._posbuff[i] = Bytes
            i = i + 1
        self._SetePositionStatus()
        self._SetePositionType()
        self._SetdLatitude()
        self._SetdLongitude()
        self._SetdHeight()
        self._SetfUndulation()
        self._SeteDatumType()
        self._SetfLatStdDev()
        self._SetfLongStdDev()
        self._SetfHgtStdDev()
        self._SetacStationID()
        self._SetfDifferentialLag()
        self._SetfSolutionAge()
        self._SetucNumTracked()
        self._SetucNumInSolution()
        self._SetucNumInSolutionSingleFreq()
        self._SetucNumInSolutionDualFreq()
        self._SetucMeasurementSource()
        self._SetucExtendedSolutionStatus()
        self._SetucGALandBDSSignals()
        self._SetucGPSandGLOSignals()
            
    def _SetePositionStatus(self):
        '''
        Sets Log position status
        '''
        Keyvalue = (self._posbuff[3] << 24) | (self._posbuff[2] << 16) | (self._posbuff[1] << 8) | self._posbuff[0]
        self._eMyPositionStatus = self.SOLUTIONSTATUS[Keyvalue]
        
    def GetePositionStatus(self):
        return self._eMyPositionStatus
        
    def _SetePositionType(self):
        '''
        Sets Log position type
        '''
        Keyvalue = (self._posbuff[7] << 24) | (self._posbuff[6] << 16) | (self._posbuff[5] << 8) | self._posbuff[4]
        self._eMyPositionType = self.POSITIONTYPE[Keyvalue]
        
    def GetePositionType(self):
        return self._eMyPositionType
        
    def _SetdLatitude(self):
        '''
        Sets Log position latitude
        '''
        self._dMyLatitude = struct.unpack('!d', bytearray(reversed(self._posbuff[8:16])))[0]
        
    def GetdLatitude(self):
        return self._dMyLatitude
        
    def _SetdLongitude(self):
        '''
        Sets Log position longitude
        '''
        self._dMyLongitude = struct.unpack('!d', bytearray(reversed(self._posbuff[16:24])))[0]
        
    def GetdLongitude(self):
        return self._dMyLongitude
        
    def _SetdHeight(self):
        '''
        Sets Log position Height
        '''
        self._dMyHeight = struct.unpack('!d', bytearray(reversed(self._posbuff[24:32])))[0]
        
    def GetdHeight(self):
        return self._dMyHeight
        
    def _SetfUndulation(self):
        '''
        Sets Log position Undulation
        '''
        self._fMyUndulation = struct.unpack('!f', bytearray(reversed(self._posbuff[32:36])))[0]
        
    def GetfUndulation(self):
        return self._fMyUndulation
        
    def _SeteDatumType(self):
        '''
        Sets Log position Datum
        '''
        Keyvalue = (self._posbuff[39] << 24) | (self._posbuff[38] << 16) | (self._posbuff[37] << 8) | self._posbuff[36]
        self._eMyDatumType = self.DATUM_TYPE[Keyvalue]
        
    def GeteDatymType(self):
        return self._eMyDatumType
        
    def _SetfLatStdDev(self):
        '''
        Sets Log position latitude standard deviation
        '''
        self._fMyLatStdDev = struct.unpack('!f', bytearray(reversed(self._posbuff[40:44])))[0]
        
    def GetfLatStdDev(self):
        return self._fMyLatStdDev
        
    def _SetfLongStdDev(self):
        '''
        Sets Log position longitude standard deviation
        '''
        self._fMyLongStdDev = struct.unpack('!f', bytearray(reversed(self._posbuff[44:48])))[0]
        
    def GetfLongStdDev(self):
        return self._fMyLongStdDev
        
    def _SetfHgtStdDev(self):
        '''
        Sets Log position Height standard deviation
        '''
        self._fMyHgtStdDev = struct.unpack('!f', bytearray(reversed(self._posbuff[48:52])))[0]
        
    def GetfHgtStdDev(self):
        return self._fMyHgtStdDev
        
    def _SetacStationID(self):
        '''
        Sets Log position station ID
        '''
        self._acMyBaseID = binascii.hexlify(bytearray(reversed(self._posbuff[52:56])))
        
    def GetacStationID(self):
        return self._acMyBaseID
        
    def _SetfDifferentialLag(self):
        '''
        Sets Log position differential lag
        '''
        self._fMyDifferentialLag = struct.unpack('!f', bytearray(reversed(self._posbuff[56:60])))[0]
        
    def GetfDifferentialLag(self):
        return self._fMyDifferentialLag
        
    def _SetfSolutionAge(self):
        '''
        Sets Log position solution age
        '''
        self._fMySolutionAge = struct.unpack('!f', bytearray(reversed(self._posbuff[60:64])))[0]
        
    def GetfSolutionAge(self):
        return self._fMySolutionAge
        
    def _SetucNumTracked(self):
        '''
        Sets Log position number of satellites tracked
        '''
        self._ucMyNumTracked = self._posbuff[64]
        
    def GetucNumTracked(self):
        return self._ucMyNumTracked
        
    def _SetucNumInSolution(self):
        '''
        Sets Log position number of satellites used in solution
        '''
        self._ucMyNumInSolution = self._posbuff[65]
        
    def GetucNumInSolution(self):
        return self._ucMyNumInSolution
        
    def _SetucNumInSolutionSingleFreq(self):
        '''
        Sets Log position number of satellites used in solution L1
        '''
        self._ucMyNumInSolutionSingleFreq = self._posbuff[66]
        
    def GetucNumInSolutionSingleFreq(self):
        return self._ucMyNumInSolutionSingleFreq
        
    def _SetucNumInSolutionDualFreq(self):
        '''
        Sets Log position number of satellites used in solution L1/L2
        '''
        self._ucMyNumInSolutionDualFreq = self._posbuff[67]
        
    def GetucNumInSolutionDualFreq(self):
        return self._ucMyNumInSolutionDualFreq
        
    def _SetucMeasurementSource(self):
        '''
        Sets Log position measurement SOURCE
        '''
        self._ucMyMeasurementSource = self._posbuff[68]
        
    def GetucMeasurementSource(self):
        return self._ucMyMeasurementSource
        
    def _SetucExtendedSolutionStatus(self):
        '''
        Sets Log position extended solution status
        '''
        self._ucMyExtendedSolutionStatus = self._posbuff[69]
        
    def GetucExtendedSolutionStatus(self):
        return self._ucMyExtendedSolutionStatus
        
    def _SetucGALandBDSSignals(self):
        '''
        Sets Log position Galileo and BDS signals
        '''
        self._ucMyGALandBDSSignals = self._posbuff[70]
        
    def GetucGALandBDSSignals(self):
        return self._ucMyGALandBDSSignals
        
    def _SetucGPSandGLOSignals(self):
        '''
        Sets Log position GPS and GLONASS signal
        '''
        self._ucMyGPSandGLOSignals = self._posbuff[71]
        
    def GetucGPSandGLOSignals(self):
        return self._ucMyGPSandGLOSignals

class MyNCRC32():
    '''
    Class that Computes the CRC32 checksum of a binary array
    '''
    CRC32_POLYNOMIAL = 0xEDB88320
    def __init__(self):
        self._ulCRC32 = 0
        
    def CRC32Value(self, iVALUE):
        '''
        Computes per byte CRC32 value
        '''
        ulCRC = iVALUE
        j = 8
        while (j > 0):
            if (ulCRC & 1):
                ulCRC = (ulCRC >> 1) ^ self.CRC32_POLYNOMIAL
            else:
                ulCRC >>= 1
            j = j - 1
        return ulCRC
    
    def CalculateBlockCRC32(self, ulCOUNT, ucBUFFER):
        '''
        Computes Block CRC32 of binary array
        '''
        i = 0
        while (ulCOUNT != 0):
            ulTemp1 = (self._ulCRC32 >> 8) & 0x00FFFFFF
            ulTemp2 = self.CRC32Value((self._ulCRC32 ^ ucBUFFER[i]) & 0xFF)
            self._ulCRC32 = ulTemp1 ^ ulTemp2
            i = i + 1
            ulCOUNT = ulCOUNT - 1
        return self._ulCRC32
            