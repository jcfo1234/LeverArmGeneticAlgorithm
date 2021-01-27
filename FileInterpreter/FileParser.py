'''
Created on Feb 27, 2015

@author: JFandino
'''

import os
import sys
import binascii
import PositionInterpreter

class MyPositionFileParser(object):
    '''
    classdocs
    '''

    # Available Position Logs to decode
    POSITION_LOGS_ID = {'BESTPOS' : 42, 'PSRPOS' : 47, 'RTKPOS' : 141, 'PPPPOS' : 1538, 'PDPPOS' : 469}

    def __init__(self, params):
        '''
        Constructor
        params[0]: Full path and name of Binary input file
        params[1]: Full path and name of Text output file
        '''
        self._szFullInputFileName = params[0]
        self._szFullOutputFileName = params[1]
        self._InputFile = None
        self._OutputFile = None
        self._clPositionLog = None
        self._clLogCRC32 = None
        
    def _CompareSynchBytes(self, BinaryArray, SynchString):
        '''
        Synch Bytes Comparison
        '''
        szSynch = binascii.hexlify(bytearray(BinaryArray)).decode('utf-8')
        # Compare UPPERCASE Strings
        if (szSynch.upper() == SynchString.upper()):
            return True
        else:
            return False
           
    def _AssembleULONG(self, BinaryArray):
        '''
        Transforms 4 Bytes into unsigned short
        BinaryArray must be of length 4
        '''
        return (BinaryArray[3] << 24) | (BinaryArray[2] << 16) | (BinaryArray[1] << 8) | BinaryArray[0]

    def _AssembleUSHORT(self, BinaryArray):
        '''
        Transforms 2 Bytes into unsigned short
        BinaryArray must be of length 2
        '''
        return (BinaryArray[1] << 8) | BinaryArray[0]

    def _IsPositionLog(self, BinaryArray_, PositionLogKey_):
        '''
        Determines if the Message ID corresponds to a position Log
        '''
        ulMsgId = self._AssembleUSHORT(BinaryArray_)
        bPosLog = False
        if (self.POSITION_LOGS_ID[PositionLogKey_] == ulMsgId):
            bPosLog = True
        return bPosLog
    
    def _AppendToBuffer(self, NumBytes_, LogBuffer_, ulFileSize_, ulCurrentPos_):
        '''
        Append Bytes to Buffer array
        '''
        if ((ulCurrentPos_ + NumBytes_) > ulFileSize_):
            return False
        bytes_read = self._InputFile.read(NumBytes_)
        for byte_write in bytes_read:
            LogBuffer_.append(byte_write)
        if (len(bytes_read) > 0):
            return True
        else:
            return False
    
    def _WriteLinetoTextFile(self):
        '''
        Write Line to Text File
        '''
        usWeek = self._clPositionLog.GetusWeek()
        fWeekSeconds = self._clPositionLog.Getfmilliseconds()
        dLatitude = self._clPositionLog.GetdLatitude()
        dLongitude = self._clPositionLog.GetdLongitude()
        dHeight = self._clPositionLog.GetdHeight() + self._clPositionLog.GetfUndulation()
        dLatStdDev = self._clPositionLog.GetfLatStdDev()
        dLngStdDev = self._clPositionLog.GetfLongStdDev()
        dHgtStdDev = self._clPositionLog.GetfHgtStdDev()
        szPositionStatus = self._clPositionLog.GetePositionStatus()
        szPositionType = self._clPositionLog.GetePositionType()
        self._OutputFile.write("{:d},{:.3f},{:.12f},{:.12f},{:.4f},{:.4f},{:.4f},{:.4f},{:s},{:s}\n".format(usWeek,fWeekSeconds,dLatitude,dLongitude,dHeight,dLatStdDev,dLngStdDev,dHgtStdDev,szPositionStatus,szPositionType))
    
    def GetSolutionStatusDict(self):
        '''
        Get definition of solution status dictionary
        '''
        return self._clPositionLog.SOLUTIONSTATUS
    
    def GetPositionTypeDict(self):
        '''
        Get definition of Position type dictionary
        '''
        return self._clPositionLog.POSITIONTYPE
    
    def ConvertBinaryToText(self, PositionLogKey):
        '''
        Converts Binary position logs to text
        '''
        self._InputFile = open(self._szFullInputFileName, "rb")
        self._OutputFile = open(self._szFullOutputFileName, "w")
        self._OutputFile.write('Week,GPSTime,Latitude,Longitude,Height,Position Status,Position Type\n')
        ulInputFileSize = os.path.getsize(self._szFullInputFileName)
        ulCurrFilePos = self._InputFile.tell()
        LogBuffer = []
        # Read data from Input Binary File
        try:
            print('Percentage file read is: ')
            bytes_read = True
            while bytes_read:
                # Tell current status of file read
                fPercentageRead = float(ulCurrFilePos) / float(ulInputFileSize) * 100
                sys.stdout.write("\b"*8 + "{:.3f}%".format(fPercentageRead))
                sys.stdout.flush()
                bytes_read = self._AppendToBuffer(1, LogBuffer, ulInputFileSize, self._InputFile.tell())
                # Stop processing if no more bytes can be read
                if (bytes_read == False):
                    LogBuffer = []
                    break
                # Check for Synch Bytes. Discard Bytes wihout Synchronization Bytes
                if (not self._CompareSynchBytes(LogBuffer, 'aa44121c')):
                    # Discard what had been assembled
                    if (len(LogBuffer) >= 4):
                        ulValueBytes1 = self._AssembleULONG(LogBuffer) & 0xFF000000
                        ulValueBytes2 = self._AssembleULONG(LogBuffer) & 0xFFFF0000
                        ulValueBytes3 = self._AssembleULONG(LogBuffer) & 0xFFFFFF00
                        # 3 Synch bytes accumulated
                        if (ulValueBytes3 == 0x1244AA00):
                            LogBuffer = LogBuffer[1:]
                        # 2 Synch bytes accumulated
                        elif (ulValueBytes2 == 0x44AA0000):
                            LogBuffer = LogBuffer[2:]
                        # 1 Synch byte accumulated
                        elif (ulValueBytes1 == 0xAA000000):
                            LogBuffer = LogBuffer[3:]
                        else:
                            LogBuffer = []
                    # Tell Current positin in file
                    ulCurrFilePos = self._InputFile.tell()
                    continue
                # Once Synch bytes of header are found, read rest of header
                bytes_read = self._AppendToBuffer(24, LogBuffer, ulInputFileSize, self._InputFile.tell())
                # Stop reading if Header Buffer is not completely filled
                if (len(LogBuffer) != 28):
                    LogBuffer = []
                    break
                # Copy The rest of the Message onto LogBuffer
                usMsgSize = self._AssembleUSHORT(LogBuffer[8:10])
                bytes_read = self._AppendToBuffer(usMsgSize + 4, LogBuffer, ulInputFileSize, self._InputFile.tell())
                # Discard Buffer if Log is not a Position Log
                if (not self._IsPositionLog(LogBuffer[4:6], PositionLogKey)):
                    LogBuffer = []
                    # Tell Current positin in file
                    ulCurrFilePos = self._InputFile.tell()
                    continue
                # Stop processing if length of Buffer is not as expected
                if (len(LogBuffer) != 104):
                    LogBuffer = []
                    break
                ulLogCRC32 = self._AssembleULONG(LogBuffer[usMsgSize + 28:usMsgSize + 32])
                self._clLogCRC32 = PositionInterpreter.MyNCRC32()
                ulComputedLogCRC32 = self._clLogCRC32.CalculateBlockCRC32(28 + usMsgSize, LogBuffer[:28 + usMsgSize])
                # Discard Log if the CRC32 Fails
                if (ulLogCRC32 != ulComputedLogCRC32):
                    LogBuffer = []
                    # Tell Current positin in file
                    ulCurrFilePos = self._InputFile.tell()
                    continue
                # Set The Log Object decoder
                self._clPositionLog = PositionInterpreter.MyNPosition()
                self._clPositionLog.SetLogBuffer(LogBuffer[0:28 + usMsgSize])
                # Write line to text file
                self._WriteLinetoTextFile()
                # Erase Decoders and Containers
                self._clLogCRC32 = None
                self._clPositionLog = None
                LogBuffer = []
                # Tell Current positin in file
                ulCurrFilePos = self._InputFile.tell()
            # Close File Handles
            self._InputFile.close()
            self._OutputFile.close()
        # Close File Handles
        finally:
            self._InputFile.close()
            self._OutputFile.close()

