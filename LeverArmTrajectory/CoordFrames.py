'''
Created on May 8, 2015

@author: JFandino

Module used to transform vectors and coordinates
to ECEF, Local Level Frame (LLF) and Body Frame 
coordinate systems
'''

import math
from decimal import Decimal

def GEOToECEFCoordinates(InsCoord_, SEMI_MAJOR_AXIS_, ECCENTRICITY_):
    '''
    Transform Geodetic coordinates to ECEF Coordinates
    InsCoord_[0] -> Latitude [Degrees]
    InsCoord_[1] -> Longitude [Degrees]
    InsCoord_[2] -> Height [meters]
    '''
    dN = SEMI_MAJOR_AXIS_ / pow(1 - pow(ECCENTRICITY_,2)*pow(Decimal(math.sin(InsCoord_[0] * Decimal(math.pi) / 180)),2),Decimal(0.5))
    # ECEF-X position
    vReturnX = (InsCoord_[2] + dN) * Decimal(math.cos(InsCoord_[0] * Decimal(math.pi) / 180)) * Decimal(math.cos(InsCoord_[1] * Decimal(math.pi) / 180))
    # ECEF-Y position
    vReturnY = (InsCoord_[2] + dN) * Decimal(math.cos(InsCoord_[0] * Decimal(math.pi) / 180)) * Decimal(math.sin(InsCoord_[1] * Decimal(math.pi) / 180))
    # ECEF-Z position
    vReturnZ = (InsCoord_[2] + (1 - pow(ECCENTRICITY_, Decimal(2))) * dN) * Decimal(math.sin(InsCoord_[0] * Decimal(math.pi) / 180))
    return [vReturnX, vReturnY, vReturnZ]

def ECEFToGEOCoordinates(InsECEF_, SEMI_MAJOR_AXIS_, ECCENTRICITY_, CONVERGENCE_=0.000001):
    '''
    Transforms ECEF coordinates back into Geodetic Coordinates
    InsECEF_[0] -> ECEF X position [meters]
    InsECEF_[1] -> ECEF Y position [meters]
    InsECEF_[2] -> ECEF Z position [meters]
    '''
    # Longitude computation
    dLongitude = Decimal(math.atan2(InsECEF_[1], InsECEF_[0])) * Decimal(180) / Decimal(math.pi)
    # Distance from center of earth to projection of position vector to XY plane
    dp = Decimal(math.sqrt(pow(InsECEF_[0],2) + pow(InsECEF_[1],2)))
    dLatGeoc = Decimal(math.atan2(InsECEF_[2], dp))
    dLatitude = dLatGeoc
    dHeight = 0
    while 1:
        dN = SEMI_MAJOR_AXIS_ / pow(1 - pow(ECCENTRICITY_,2)*pow(Decimal(math.sin(dLatitude)),2),Decimal(0.5))
        dL = InsECEF_[2] + pow(ECCENTRICITY_,2) * dN * Decimal(math.sin(dLatitude))
        if (abs(dHeight - (Decimal(math.sqrt(pow(dL,2) + pow(dp,2))) - dN)) < CONVERGENCE_):
            break
        dHeight = Decimal(math.sqrt(pow(dL,2) + pow(dp,2))) - dN
        dLatitude = Decimal(math.atan2(InsECEF_[2] * (dN + dHeight), dp * (dN - dN * pow(ECCENTRICITY_, 2) + dHeight)))
    return [dLatitude * Decimal(180) / Decimal(math.pi), dLongitude, dHeight]

def TransformLLFToECEF(vLLF_, InsCoord_):
    '''
    Rotate vector from Local Level Frame coordinates to ECEF
    vLLF_[0] -> E coordinate [meters]
    vLLF_[1] -> N coordinate [meters]
    vLLF_[2] -> U coordinate [meters]
    InsCoord_[0] -> Latitude [Degrees]
    InsCoord_[1] -> Longitude [Degrees]
    InsCoord_[2] -> Height [meters]
    '''
    R11 = -Decimal(math.sin(InsCoord_[1] * Decimal(math.pi) / 180))
    R12 = -Decimal(math.cos(InsCoord_[1] * Decimal(math.pi) / 180))*Decimal(math.sin(InsCoord_[0] * Decimal(math.pi) / 180))
    R13 = Decimal(math.cos(InsCoord_[0] * Decimal(math.pi) / 180))*Decimal(math.cos(InsCoord_[1] * Decimal(math.pi) / 180))
    R21 = Decimal(math.cos(InsCoord_[1] * Decimal(math.pi) / 180))
    R22 = -Decimal(math.sin(InsCoord_[0] * Decimal(math.pi) / 180))*Decimal(math.sin(InsCoord_[1] * Decimal(math.pi) / 180))
    R23 = Decimal(math.cos(InsCoord_[0] * Decimal(math.pi) / 180))*Decimal(math.sin(InsCoord_[1] * Decimal(math.pi) / 180))
    R31 = Decimal(0)
    R32 = Decimal(math.cos(InsCoord_[0] * Decimal(math.pi) / 180))
    R33 = Decimal(math.sin(InsCoord_[0] * Decimal(math.pi) / 180))
    # ECEF-X lever arm
    vReturnX = R11 * vLLF_[0] + R12 * vLLF_[1] + R13 * vLLF_[2]
    # ECEF-Y lever arm
    vReturnY = R21 * vLLF_[0] + R22 * vLLF_[1] + R23 * vLLF_[2]
    # ECEF-Z lever arm
    vReturnZ = R31 * vLLF_[0] + R32 * vLLF_[1] + R33 * vLLF_[2]
    return [vReturnX,vReturnY,vReturnZ]

def TransformECEFToLLF(vECEF_, INSCoord_):
    '''
    Rotate vector from ECEF coordinates to LLF coordinates
    vECEF_[0] -> X coordinate
    vECEF_[1] -> Y coordinate
    vECEF_[2] -> Z coordinate
    INSCoord_[0] -> Latitude [Degrees]
    INSCoord_[1] -> Longitude [Degrees]
    INSCoord_[2] -> Height [meters]
    '''
    R11 = -Decimal(math.sin(INSCoord_[1] * Decimal(math.pi) / 180))
    R12 = Decimal(math.cos(INSCoord_[1] * Decimal(math.pi) / 180))
    R13 = Decimal(0)
    R21 = -Decimal(math.cos(INSCoord_[1] * Decimal(math.pi) / 180))*Decimal(math.sin(INSCoord_[0] * Decimal(math.pi) / 180))
    R22 = -Decimal(math.sin(INSCoord_[0] * Decimal(math.pi) / 180))*Decimal(math.sin(INSCoord_[1] * Decimal(math.pi) / 180))
    R23 = Decimal(math.cos(INSCoord_[0] * Decimal(math.pi) / 180))
    R31 = Decimal(math.cos(INSCoord_[0] * Decimal(math.pi) / 180))*Decimal(math.cos(INSCoord_[1] * Decimal(math.pi) / 180))
    R32 = Decimal(math.cos(INSCoord_[0] * Decimal(math.pi) / 180))*Decimal(math.sin(INSCoord_[1] * Decimal(math.pi) / 180))
    R33 = Decimal(math.sin(INSCoord_[0] * Decimal(math.pi) / 180))
    # ECEF-X lever arm
    vReturnE = R11 * vECEF_[0] + R12 * vECEF_[1] + R13 * vECEF_[2]
    # ECEF-Y lever arm
    vReturnN = R21 * vECEF_[0] + R22 * vECEF_[1] + R23 * vECEF_[2]
    # ECEF-Z lever arm
    vReturnU = R31 * vECEF_[0] + R32 * vECEF_[1] + R33 * vECEF_[2]
    return [vReturnE,vReturnN,vReturnU]
    