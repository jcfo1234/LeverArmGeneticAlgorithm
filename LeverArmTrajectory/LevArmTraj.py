'''
Created on Mar 2, 2015

@author: JFandino
'''

import math
from decimal import Decimal
import datetime as dt

class MyLevArmTraj(object):
    '''
    classdocs
    '''
    # TO DO: Expand with other DATUMS
    DATUM_DICT = {'WGS84':(6378137.0,298.257223563)}
    
    def __init__(self, params_):
        '''
        Constructor
        This class will translate the vehicle's center of mass
        by an ammount specified in by the lever arm
        '''
        self._dlevx = Decimal(params_[0]) # Body frame lever arm vector x-axis
        self._dlevy = Decimal(params_[1]) # Body frame lever arm vector y-axis
        self._dlevz = Decimal(params_[2]) # Body frame lever arm vector z-axis
        self._szFullInputFileName = params_[3]
        self._szFullOutputFileName = params_[4]
        self._METHOD_DICT = {'GEOID': self._TranslateINSToGNSSCoord, 'ECEF': self._ECEFTranslation}
        
    def SetDatum(self, Datum_='WGS84'):
        '''
        Sets the ellipsoid datum values
        '''
        self._SEMI_MAJOR_AXIS = Decimal(self.DATUM_DICT[Datum_][0])
        self._FLATTENING = Decimal(1 / self.DATUM_DICT[Datum_][1])
        self._ECCENTRICITY = Decimal(math.sqrt(2 * self._FLATTENING - pow(self._FLATTENING, 2)))
        
    def _TransformLLFToECEF(self, vector, angles):
        '''
        Rotate vector from Local Level Frame coordinates to ECEF
        vector[0] -> E coordinate
        vector[1] -> N coordinate
        vector[2] -> U coordinate
        angles[0] -> Latitude
        angles[1] -> Longitude
        angles[2] -> Height
        '''
        R11 = -Decimal(math.sin(angles[1] * Decimal(math.pi) / 180))
        R12 = -Decimal(math.cos(angles[1] * Decimal(math.pi) / 180))*Decimal(math.sin(angles[0] * Decimal(math.pi) / 180))
        R13 = Decimal(math.cos(angles[0] * Decimal(math.pi) / 180))*Decimal(math.cos(angles[1] * Decimal(math.pi) / 180))
        R21 = Decimal(math.cos(angles[1] * Decimal(math.pi) / 180))
        R22 = -Decimal(math.sin(angles[0] * Decimal(math.pi) / 180))*Decimal(math.sin(angles[1] * Decimal(math.pi) / 180))
        R23 = Decimal(math.cos(angles[0] * Decimal(math.pi) / 180))*Decimal(math.sin(angles[1] * Decimal(math.pi) / 180))
        R31 = Decimal(0)
        R32 = Decimal(math.cos(angles[0] * Decimal(math.pi) / 180))
        R33 = Decimal(math.sin(angles[0] * Decimal(math.pi) / 180))
        # ECEF-X lever arm
        vReturnX = R11 * vector[0] + R12 * vector[1] + R13 * vector[2]
        # ECEF-Y lever arm
        vReturnY = R21 * vector[0] + R22 * vector[1] + R23 * vector[2]
        # ECEF-Z lever arm
        vReturnZ = R31 * vector[0] + R32 * vector[1] + R33 * vector[2]
        return [vReturnX,vReturnY,vReturnZ]
    
    def _TransformGEOToECEF(self, InsCoord_):
        '''
        Transform Geodetic coordinates to ECEF Coordinates
        InsCoord_[0] -> Latitude
        InsCoord_[1] -> Longitude
        InsCoord_[2] -> Height
        '''
        dN = self._SEMI_MAJOR_AXIS / pow(1 - pow(self._ECCENTRICITY,2)*pow(Decimal(math.sin(InsCoord_[0] * Decimal(math.pi) / 180)),2),Decimal(0.5))
        # ECEF-X position
        vReturnX = (InsCoord_[2] + dN) * Decimal(math.cos(InsCoord_[0] * Decimal(math.pi) / 180)) * Decimal(math.cos(InsCoord_[1] * Decimal(math.pi) / 180))
        # ECEF-Y position
        vReturnY = (InsCoord_[2] + dN) * Decimal(math.cos(InsCoord_[0] * Decimal(math.pi) / 180)) * Decimal(math.sin(InsCoord_[1] * Decimal(math.pi) / 180))
        # ECEF-Z position
        vReturnZ = (InsCoord_[2] + (1 - pow(self._ECCENTRICITY, Decimal(2))) * dN) * Decimal(math.sin(InsCoord_[0] * Decimal(math.pi) / 180))
        return [vReturnX, vReturnY, vReturnZ]
    
    def _TranslateECEFINSToECEFGNSS(self, InsECEF_, LevArmECEF_):
        '''
        Translates INS ECEF coordinates to GNSS ECEF coordinates
        '''
        # ECEF-X GNSS antenna position
        vReturnX = InsECEF_[0] + LevArmECEF_[0]
        # ECEF-Y GNSS antenna position
        vReturnY = InsECEF_[1] + LevArmECEF_[1]
        # ECEF-Z GNSS antenna position
        vReturnZ = InsECEF_[2] + LevArmECEF_[2]
        return [vReturnX, vReturnY, vReturnZ]
    
    def _TransformECEFToGEO(self, InsECEF_, CONVERGENCE_=0.000001):
        '''
        Transforms ECEF coordinates back into Geodetic Coordinates
        InsECEF_[0] -> ECEF X position
        InsECEF_[1] -> ECEF Y position
        InsECEF_[2] -> ECEF Z position
        '''
        # Longitude computation
        dLongitude = Decimal(math.atan2(InsECEF_[1], InsECEF_[0])) * Decimal(180) / Decimal(math.pi)
        # Distance from center of earth to projection of position vector to XY plane
        dp = Decimal(math.sqrt(pow(InsECEF_[0],2) + pow(InsECEF_[1],2)))
        dLatGeoc = Decimal(math.atan2(InsECEF_[2], dp))
        dLatitude = dLatGeoc
        dHeight = 0
        while 1:
            dN = self._SEMI_MAJOR_AXIS / pow(1 - pow(self._ECCENTRICITY,2)*pow(Decimal(math.sin(dLatitude)),2),Decimal(0.5))
            dL = InsECEF_[2] + pow(self._ECCENTRICITY,2) * dN * Decimal(math.sin(dLatitude))
            if (abs(dHeight - (Decimal(math.sqrt(pow(dL,2) + pow(dp,2))) - dN)) < CONVERGENCE_):
                break
            dHeight = Decimal(math.sqrt(pow(dL,2) + pow(dp,2))) - dN
            dLatitude = Decimal(math.atan2(InsECEF_[2] * (dN + dHeight), dp * (dN - dN * pow(self._ECCENTRICITY, 2) + dHeight)))
        return [dLatitude * Decimal(180) / Decimal(math.pi), dLongitude, dHeight]
    
    def TransformLLFToBody(self, vector, angles):
        '''
        Rotate vectro from Local Level frame to Body frame coordinates
        vector[0] -> E coordinate
        vector[1] -> N coordinate
        vector[2] -> U coordinate
        angles[0] -> Pitch
        angles[1] -> Roll
        angles[2] -> Azimuth
        '''
        R11 = -Decimal(math.sin(angles[0]))*Decimal(math.sin(angles[1]))*Decimal(math.sin(angles[2])) + Decimal(math.cos(angles[1]))*Decimal(math.cos(angles[2]))
        R12 = -Decimal(math.sin(angles[0]))*Decimal(math.sin(angles[1]))*Decimal(math.cos(angles[2])) - Decimal(math.cos(angles[1]))*Decimal(math.sin(angles[2]))
        R13 = -Decimal(math.cos(angles[0]))*Decimal(math.sin(angles[1]))
        R21 = Decimal(math.cos(angles[0]))*Decimal(math.sin(angles[2]))
        R22 = Decimal(math.cos(angles[0]))*Decimal(math.cos(angles[2]))
        R23 = -Decimal(math.sin(angles[0]))
        R31 = Decimal(math.sin(angles[0]))*Decimal(math.cos(angles[1]))*Decimal(math.sin(angles[2])) + Decimal(math.sin(angles[1]))*Decimal(math.cos(angles[2]))
        R32 = Decimal(math.sin(angles[0]))*Decimal(math.cos(angles[1]))*Decimal(math.cos(angles[2])) - Decimal(math.sin(angles[1]))*Decimal(math.sin(angles[2]))
        R33 = Decimal(math.cos(angles[0]))*Decimal(math.cos(angles[1]))
        # East Local level frame lever arm
        vReturnx = R11 * vector[0] + R12 * vector[1] + R13 * vector[2]
        # North Local level frame lever arm
        vReturny = R21 * vector[0] + R22 * vector[1] + R23 * vector[2]
        # Up Local level frame lever arm
        vReturnz = R31 * vector[0] + R32 * vector[1] + R33 * vector[2]
        return [vReturnx,vReturny,vReturnz]
        
    def _TransformBodyToLLF(self, vector, angles):
        '''
        Rotate vector from Body Frame coordinates to Local Level Frame
        vector[0] -> x coordinate
        vector[1] -> y coordinate
        vector[2] -> z coordinate
        angles[0] -> Pitch
        angles[1] -> Roll
        angles[2] -> Azimuth
        '''
        R11 = -Decimal(math.sin(angles[0]))*Decimal(math.sin(angles[1]))*Decimal(math.sin(angles[2])) + Decimal(math.cos(angles[1]))*Decimal(math.cos(angles[2]))
        R12 = Decimal(math.cos(angles[0]))*Decimal(math.sin(angles[2]))
        R13 = Decimal(math.sin(angles[0]))*Decimal(math.cos(angles[1]))*Decimal(math.sin(angles[2])) + Decimal(math.sin(angles[1]))*Decimal(math.cos(angles[2]))
        R21 = -Decimal(math.sin(angles[0]))*Decimal(math.sin(angles[1]))*Decimal(math.cos(angles[2])) - Decimal(math.cos(angles[1]))*Decimal(math.sin(angles[2]))
        R22 = Decimal(math.cos(angles[0]))*Decimal(math.cos(angles[2]))
        R23 = Decimal(math.sin(angles[0]))*Decimal(math.cos(angles[1]))*Decimal(math.cos(angles[2])) - Decimal(math.sin(angles[1]))*Decimal(math.sin(angles[2]))
        R31 = -Decimal(math.cos(angles[0]))*Decimal(math.sin(angles[1]))
        R32 = -Decimal(math.sin(angles[0]))
        R33 = Decimal(math.cos(angles[0]))*Decimal(math.cos(angles[1]))
        # East Local level frame lever arm
        vReturnE = R11 * vector[0] + R12 * vector[1] + R13 * vector[2]
        # North Local level frame lever arm
        vReturnN = R21 * vector[0] + R22 * vector[1] + R23 * vector[2]
        # Up Local level frame lever arm
        vReturnU = R31 * vector[0] + R32 * vector[1] + R33 * vector[2]
        return [vReturnE,vReturnN,vReturnU]
    
    def _TranslateINSToGNSSCoord(self, InsCoord_, LevArm_):
        '''
        Translates an single epoch INS position coordinates into GNSS antenna
        position coordinates using the lever arm vector
        '''
        dM = self._SEMI_MAJOR_AXIS * (1 - pow(self._ECCENTRICITY,2)) / pow(1 - pow(self._ECCENTRICITY,2) * pow(Decimal(math.sin(InsCoord_[0] * Decimal(math.pi) / 180)),2),Decimal(1.5))
        dN = self._SEMI_MAJOR_AXIS / pow(1 - pow(self._ECCENTRICITY,2)*pow(Decimal(math.sin(InsCoord_[0] * Decimal(math.pi) / 180)),2),Decimal(0.5))
        dLevArmLatitude =  (InsCoord_[0] * Decimal(math.pi) / 180 + LevArm_[1] / dM) * Decimal(180) / Decimal(math.pi)
        dLevArmLongitude = (InsCoord_[1] * Decimal(math.pi) / 180 + LevArm_[0] / (dN * Decimal(math.cos(InsCoord_[0] * Decimal(math.pi) / 180)))) * Decimal(180) / Decimal(math.pi)
        dHeight = InsCoord_[2] + LevArm_[2]
        return [dLevArmLatitude, dLevArmLongitude, dHeight]
    
    def _ECEFTranslation(self, InsCoord_, LevArm_):
        '''
        Translates a single epoch INS position coordinates into GNSS antenna
        position coordinates using the lever arm vector via the ECEF reference frame
        '''
        # Rotate lever arm from Local Level Frame to ECEF Frame
        [dLevX, dLevY, dLevZ] = self._TransformLLFToECEF(LevArm_, InsCoord_)
        # Compute INS position in ECEF Frame
        [dXINS, dYINS, dZINS] = self._TransformGEOToECEF(InsCoord_)
        # Translate the INS position coordinates into ECEF position coordinates via the Lever arm in ECEF reference frame
        [dXGNSS, dYGNSS, dZGNSS] = self._TranslateECEFINSToECEFGNSS([dXINS, dYINS, dZINS], [dLevX, dLevY, dLevZ])
        # Convert ECEF Coordinates back to Geodetic Coordinates
        [dGNSSLatitude, dGNSSLongitude, dGNSSHeight] = self._TransformECEFToGEO([dXGNSS, dYGNSS, dZGNSS])
        return [dGNSSLatitude, dGNSSLongitude, dGNSSHeight]
    
    def _AppendLineToFile(self, line_, GnssCoord_):
        '''
        Writes line to output file of INS position coordinates
        translated into GNSS antenna coordinates
        '''
        i = 0
        szNewLine = ''
        for item in line_.split(','):
            # Latitude Field
            if (i == 2):
                szNewLine = szNewLine + '{:.12f}'.format(GnssCoord_[0]) + ','
            # Longitude Field
            elif (i == 3):
                szNewLine = szNewLine + '{:.12f}'.format(GnssCoord_[1]) + ','
            # Height Field
            elif (i == 4):
                szNewLine = szNewLine + '{:.4f}'.format(GnssCoord_[2]) + ','
            else:
                szNewLine = szNewLine + item + ','
            i += 1
        # Remove last character ',' and feed new line
        szNewLine = szNewLine[:-1]
        self._OutputFile.write(szNewLine)
        
    def GetOutputFileName(self):
        return self._szFullOutputFileName
    
    def GetInputFileName(self):
        return self._szFullInputFileName
    
    def GetEarthEccentricity(self):
        return self._ECCENTRICITY
    
    def GetEarthFlattening(self):
        return self._FLATTENING
    
    def GetEarthSemiMajorAxis(self):
        return self._SEMI_MAJOR_AXIS
    
    def GetLeverArmBodyFrame(self):
        return [self._dlevx, self._dlevy, self._dlevz]
    
    def SetLeverArmBodyFrame(self, params):
        '''
        Sets lever arm parameters
        '''
        [self._dlevx, self._dlevy, self._dlevz] = params
    
    def TranslateFileToGNSSCoord(self, Method='GEOID', ThreadName_ = 'INSThread'):
        '''
        Translates the INS position coordinates into GNSS position coordinates
        using the lever arm vector
        '''
        starttime = dt.datetime.utcnow()
        print("Thread: " + ThreadName_ + " File creation start time: " + str(starttime))
        self._InputFile = open(self._szFullInputFileName, "r")
        self._OutputFile = open(self._szFullOutputFileName, "w")
        self._OutputFile.write('Week,GPSTime,Latitude,Longitude,H-Ell,Q,SDNorth,SDEast,SDHeigth,VEast,VNorth,VUp,SD-VE,SD-VN,SD-VH,COG,Cx11,Cx22,Cx33,Cx21,Cx31,Cx32,N-RMS,E-RMS,H-RMS\n')
        for line in self._InputFile:
            blineProcess = line.split(',')[0].replace('.','',1).isdigit()
            # Ignore non-numeric lines
            if (blineProcess == False):
                continue
            # Parse Values from Text file
            dNoLevArmLatitude = Decimal(line.split(',')[2])
            dNoLevArmLongitude = Decimal(line.split(',')[3])
            dNoLevArmHeight = Decimal(line.split(',')[4])
            dRoll = Decimal(line.split(',')[25]) * Decimal(math.pi) / 180
            dPitch = Decimal(line.split(',')[26]) * Decimal(math.pi) / 180
            dHeading = Decimal(line.split(',')[27]) * Decimal(math.pi) / 180
            # Rotate lever arm from body frame to local level frame
            [dLevE, dLevN, dLevU] = self._TransformBodyToLLF([self._dlevx, self._dlevy, self._dlevz], [dPitch, dRoll, dHeading])
            # Translate INS coordinates onto GNSS antenna in the Local Level Frame directly
            [dGNSSLatitude, dGNSSLongitude, dGNSSHeight] = self._METHOD_DICT[Method]([dNoLevArmLatitude,dNoLevArmLongitude,dNoLevArmHeight], [dLevE,dLevN,dLevU])
            self._AppendLineToFile(line, [dGNSSLatitude, dGNSSLongitude, dGNSSHeight])
        # Report the elapsed time consumed by the Thread
        elapsedtime = (dt.datetime.utcnow() - starttime).total_seconds()
        print("Thread: " + ThreadName_ + " File creation elapsed time: {:.3f}".format(elapsedtime))
        self._InputFile.close()
        self._OutputFile.close()
            
