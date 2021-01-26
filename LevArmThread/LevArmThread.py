'''
Created on Mar 3, 2015

@author: JFandino
'''
import multiprocessing
import math
import datetime as dt
# from itertools import izip
from itertools import chain
from decimal import Decimal
from LeverArmTrajectory import MyLevArmTraj
from LeverArmTrajectory import CoordFrames
from LevArmEncoder import MyLevArmEncoderDecoderClass

class myThreadProcess (multiprocessing.Process):
    '''
    Class that handles processing threads of file conversion
    from trajectory with no lever arm to trajectory with lever arm
    '''
    WEEK_SECONDS = Decimal(604800)
    MILLISECONDS_IN_SECONDS = Decimal(1000)
    MAX_SEPARATION = Decimal(0.01)
    MAX_ESTIMATED_STDDEV = Decimal(0.015)
    
    def __init__(self, ProcessID_, ProcessName_, params_):
        '''
        Thread constructor
        '''
        multiprocessing.Process.__init__(self)
        self._ProcessID = ProcessID_
        self._ProcessName = ProcessName_
        self._clMyLevArmEncoderDecoder = MyLevArmEncoderDecoderClass(params_[0:3])
        self._clMyLevArmTraj = MyLevArmTraj(list(chain.from_iterable([self._clMyLevArmEncoderDecoder.GetLeverArm(), [params_[3], params_[4]]])))
        self._INSFileName = params_[4]
        self._GNSSFileName = params_[5]
        self._MyLock = params_[6]
        self._MyQUEUE = params_[7]
        self._Datum = params_[8]
        self._Method = params_[9]
        self._SolStatus = params_[10]
        self._PosType = params_[11]
        self._INSInputFile = None
        self._GNSSInputFile = None
        self._CONInputFile = None
        self._dFitness = Decimal(100)
        self._dFitnessx = Decimal(100)
        self._dFitnessy = Decimal(100)
        self._dFitnessz = Decimal(100)
        
    def _ComputeGNSSStatistics(self):
        '''
        This function computes the RMS square
        of the differences between the GNSS file and the GNSS + INS
        file with lever arm
        '''
        # Report Start time of reading process
        starttime = dt.datetime.utcnow()
        print("Thread: " + self._ProcessName + " File read process start time: " + str(starttime))
        
        self._INSInputFile = open(self._INSFileName, "r")
        self._GNSSInputFile = open(self._GNSSFileName, "r")
        self._CONInputFile = open(self._clMyLevArmTraj.GetInputFileName(), "r")
        
        iNumSamples = Decimal(1)
        dLatRMSsqr = Decimal(0)
        dLngRMSsqr = Decimal(0)
        dHgtRMSsqr = Decimal(0)
        dxRMSsqr = Decimal(0)
        dyRMSsqr = Decimal(0)
        dzRMSsqr = Decimal(0)
        # Processing file
        for line1, line2, line3 in zip(self._INSInputFile, self._GNSSInputFile, self._CONInputFile):
            # Read INS File until finding a numeric value
            while (line1.split(',')[0].replace('.','',1).isdigit() == False):
                line1 = self._INSInputFile.next()
                line3 = self._CONInputFile.next()
            # Read GNSS File until finding a numeric value
            while (line2.split(',')[0].replace('.','',1).isdigit() == False):
                line2 = self._GNSSInputFile.next()
            dTime1 = (Decimal(line1.split(',')[0]) * self.WEEK_SECONDS + Decimal(line1.split(',')[1]))
            dTime2 = (Decimal(line2.split(',')[0]) * self.WEEK_SECONDS + Decimal(line2.split(',')[1]))
            # INS File starts before GNSS file
            while (dTime1 < dTime2):
                line1 = self._INSInputFile.next()
                line3 = self._CONInputFile.next()
                dTime1 = (Decimal(line1.split(',')[0]) * self.WEEK_SECONDS + Decimal(line1.split(',')[1]))
            # GNSS File starts before INS File
            while (dTime2 < dTime1):
                line2 = self._GNSSInputFile.next()
                dTime2 = (Decimal(line2.split(',')[0]) * self.WEEK_SECONDS + Decimal(line2.split(',')[1]))
            # Compute statistics only for the expected Solution Status and Position Type
            if ( (line2.split(',')[8] != self._SolStatus) and (line2.split(',')[9] != self._PosType) ):
                continue
            # Filter epochs where separation is higher than acceptable limit
            dseparation3D = pow(Decimal(line1.split(',')[22]), 2) + pow(Decimal(line1.split(',')[23]), 2) + pow(Decimal(line1.split(',')[24]), 2)
            dseparation3D = Decimal(math.sqrt(dseparation3D))
            if (dseparation3D > self.MAX_SEPARATION):
                continue
            # Filter epochs where the norm of standard deviations in GNSS position files exceed expected accuracy
            d3DStdDev = pow(Decimal(line2.split(',')[5]), 2) + pow(Decimal(line2.split(',')[6]), 2) + pow(Decimal(line2.split(',')[7]), 2)
            d3DStdDev = Decimal(math.sqrt(d3DStdDev))
            if (d3DStdDev > self.MAX_ESTIMATED_STDDEV):
                continue
            # Time Stamps aligned, Expected Solution Status and Expected Position Type
            if (dTime1 == dTime2):
                # Compute lever arm error in ECEF coordinates
                [dECEFX1, dECEFY1, dECEFZ1] = CoordFrames.GEOToECEFCoordinates([Decimal(line1.split(',')[2]), Decimal(line1.split(',')[3]), Decimal(line1.split(',')[4])], self._clMyLevArmTraj.GetEarthSemiMajorAxis(), self._clMyLevArmTraj.GetEarthEccentricity())
                [dECEFX2, dECEFY2, dECEFZ2] = CoordFrames.GEOToECEFCoordinates([Decimal(line2.split(',')[2]), Decimal(line2.split(',')[3]), Decimal(line2.split(',')[4])], self._clMyLevArmTraj.GetEarthSemiMajorAxis(), self._clMyLevArmTraj.GetEarthEccentricity())
                [dX, dY, dZ] = [dECEFX1 - dECEFX2, dECEFY1 - dECEFY2, dECEFZ1 - dECEFZ2]
                # Compute East, North and Up errors
                [dEastError, dNorthError, dUpError] = CoordFrames.TransformECEFToLLF([dX, dY, dZ], [Decimal(line3.split(',')[2]), Decimal(line3.split(',')[3]), Decimal(line3.split(',')[4])])
#                dEastError = (Decimal(line1.split(',')[3]) - Decimal(line2.split(',')[3])) * Decimal(math.pi)/Decimal(180) * Decimal(math.cos(Decimal(line1.split(',')[2]) * Decimal(math.pi) / Decimal(180))) * self._clMyLevArmTraj.GetEarthSemiMajorAxis()
#                dNorthError= (Decimal(line1.split(',')[2]) - Decimal(line2.split(',')[2])) * Decimal(math.pi)/Decimal(180) * self._clMyLevArmTraj.GetEarthSemiMajorAxis()
#                dUpError   = Decimal(line1.split(',')[4]) - Decimal(line2.split(',')[4])
                # Extract Roll, Pitch and Yaw information
                dRoll = Decimal(line1.split(',')[25]) * Decimal(math.pi) / Decimal(180)
                dPitch = Decimal(line1.split(',')[26]) * Decimal(math.pi) / Decimal(180)
                dHeading = Decimal(line1.split(',')[27]) * Decimal(math.pi) / Decimal(180)
                # Project errors onto body frame coordinates
                [dxError, dyError, dzError] = self._clMyLevArmTraj.TransformLLFToBody([dEastError, dNorthError, dUpError], [dPitch, dRoll, dHeading])
                dLatRMSsqr = (iNumSamples - 1) / iNumSamples * dLatRMSsqr + pow(dNorthError, 2) / iNumSamples
                dLngRMSsqr = (iNumSamples - 1) / iNumSamples * dLngRMSsqr + pow(dEastError, 2) / iNumSamples
                dHgtRMSsqr = (iNumSamples - 1) / iNumSamples * dHgtRMSsqr + pow(dUpError, 2) / iNumSamples
#                dLatRMSsqr = (iNumSamples - 1) / iNumSamples * dLatRMSsqr + pow((Decimal(line1.split(',')[2]) - Decimal(line2.split(',')[2])) * Decimal(math.pi)/Decimal(180) * self._clMyLevArmTraj.GetEarthSemiMajorAxis(), 2) / iNumSamples
#                dLngRMSsqr = (iNumSamples - 1) / iNumSamples * dLngRMSsqr + pow((Decimal(line1.split(',')[3]) - Decimal(line2.split(',')[3])) * Decimal(math.pi)/Decimal(180) * Decimal(math.cos(Decimal(line1.split(',')[2]) * Decimal(math.pi) / Decimal(180))) * self._clMyLevArmTraj.GetEarthSemiMajorAxis(), 2) / iNumSamples
#                dHgtRMSsqr = (iNumSamples - 1) / iNumSamples * dHgtRMSsqr + pow(Decimal(line1.split(',')[4]) - Decimal(line2.split(',')[4]), 2) / iNumSamples
                dxRMSsqr = (iNumSamples - 1) / iNumSamples * dxRMSsqr + pow(dxError, 2) / iNumSamples
                dyRMSsqr = (iNumSamples - 1) / iNumSamples * dyRMSsqr + pow(dyError, 2) / iNumSamples
                dzRMSsqr = (iNumSamples - 1) / iNumSamples * dzRMSsqr + pow(dzError, 2) / iNumSamples
                iNumSamples = iNumSamples + 1
        # Close Opened Files
        self._INSInputFile.close()
        self._GNSSInputFile.close()
        # Report elapsed time from reading process
        elapsedtime = (dt.datetime.utcnow() - starttime).total_seconds()
        print("Thread: " + self._ProcessName + " File read process elapsed time: {:.3f}".format(elapsedtime))
        
        return [dLatRMSsqr, dLngRMSsqr, dHgtRMSsqr, dxRMSsqr, dyRMSsqr, dzRMSsqr]
    
    def GetLevArmEncoderObject(self):
        '''
        Returns the Lever arm encoder object
        '''
        return self._clMyLevArmEncoderDecoder
    
    def GetLevArmTrajObject(self):
        '''
        Returns the lever arm trajectory object
        '''
        return self._clMyLevArmTraj
       
    def GetLeverArmFitness(self):
        '''
        Return lever arm fitness value
        '''
        return [self._dFitness, self._dFitnessx, self._dFitnessy, self._dFitnessz]
    
    def SetLeverArmFitness(self, adValue_):
        '''
        Set fitness value of lever arm
        '''
        self._dFitness = adValue_[0]
        self._dFitnessx = adValue_[1]
        self._dFitnessy = adValue_[2]
        self._dFitnessz = adValue_[3]
        
    def GetProcessName(self):
        '''
        Return the Process Name
        '''
        return self._ProcessName
    
    def GetProcessID(self):
        '''
        Return the Process ID
        '''
        return self._ProcessID
    
    def SerializedRun(self, Datum_='WGS84', Method_='GEOID'):
        '''
        Execute Serialized Processing Thread
        '''
        # Set Datum
        self._clMyLevArmTraj.SetDatum(Datum_)
        # Translate Vehicle's center of navigation to GNSS Antenna
        self._clMyLevArmTraj.TranslateFileToGNSSCoord(Method_, self._ProcessName)
        # Compute RMS Error statistics
        [dLatRMSsqr, dLngRMSsqr, dHgtRMSsqr, dxRMSsqr, dyRMSsqr, dzRMSsqr] = self._ComputeGNSSStatistics()
        # Objective is to minimize the RMS so the fitness is the inverse of the RMS error
        self._dFitness = Decimal(1) / (dLatRMSsqr + dLngRMSsqr + dHgtRMSsqr)
        self._dFitnessx = Decimal(1) / dxRMSsqr
        self._dFitnessy = Decimal(1) / dyRMSsqr
        self._dFitnessz = Decimal(1) / dzRMSsqr
        
    def run(self):
        '''
        Execute processing thread
        '''
        # Set Datum
        self._clMyLevArmTraj.SetDatum(self._Datum)
        # Translate Vehicle's center of navigation to GNSS Antenna
        self._clMyLevArmTraj.TranslateFileToGNSSCoord(self._Method, self._ProcessName)
        # Compute RMS Error statistics
        [dLatRMSsqr, dLngRMSsqr, dHgtRMSsqr, dxRMSsqr, dyRMSsqr, dzRMSsqr] = self._ComputeGNSSStatistics()
        # Objective is to minimize the RMS so the fitness is the inverse of the RMS error
        self._dFitness = Decimal(1) / (dLatRMSsqr + dLngRMSsqr + dHgtRMSsqr)
        self._dFitnessx = Decimal(1) / dxRMSsqr
        self._dFitnessy = Decimal(1) / dyRMSsqr
        self._dFitnessz = Decimal(1) / dzRMSsqr
        # Pass information back to Multiprocess calling stack
        self._MyLock.acquire()
        self._MyQUEUE.put([self.GetProcessID(), self.GetLeverArmFitness()])
        self._MyLock.release()
