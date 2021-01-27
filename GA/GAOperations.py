'''
Created on Mar 9, 2015

@author: JFandino
'''

import random
import math
import copy
from LevArmThread import myThreadProcess
from decimal import Decimal

GA_CROSS_OVER_RATE = Decimal(0.7)
GA_MUTATION_RATE = Decimal(0.1)

def GASetMutation(szBinary_, Index_):
    '''
    This function mutates a binary string
    '''
    Mutation = list(szBinary_)
    # Start search from scratch at zero
    if Index_ == len(Mutation):
        Mutation = list('0'*len(szBinary_))
    # Flip one bit in chromosome to emulate Mutation
    elif (szBinary_[Index_] == '1'):
        Mutation[Index_] = '0'
    else:
        Mutation[Index_] = '1'
    return ''.join(Mutation)

def GACrossOverIndex(xorlist_):
    '''
    This function determines the starting point of crossover
    '''
    Index = 0
    for xorbit in xorlist_:
        if xorbit == '1':
            break
        Index += 1
    return Index
    
def GASetCrossOverOffspring(szBinary1_, szBinary2_):
    '''
    This function Mixes two binary strings to create offspring
    '''
    Fenotype1 = list(szBinary1_)
    Fenotype2 = list(szBinary2_)
    InitIndex = GACrossOverIndex(list('{0:016b}'.format(int(szBinary1_,2) ^ int(szBinary2_,2))))
    # Fenotypes producing two different offsprings
    if (InitIndex < len(Fenotype1)):
        # Pick two random indexes
        Index1 = random.randint(InitIndex, len(Fenotype1) - 1)
        Index2 = random.randint(InitIndex, len(Fenotype2) - 1)
        Temp1 = Fenotype1[Index1:]
        Temp2 = Fenotype2[Index2:]
        Fenotype1[Index2:] = Temp2
        Fenotype2[Index1:] = Temp1
    return [''.join(Fenotype1), ''.join(Fenotype2)]

def GAGetFittestByFitness(aclGAPopulationThread_):
    '''
    Get the Fittest Lever Arm object
    '''
    Index = 0
    Value = Decimal(0)
    for clGAThread in aclGAPopulationThread_:
        if clGAThread.GetLeverArmFitness()[0] > Value:
            Value = clGAThread.GetLeverArmFitness()[0]
    for clGAThread in aclGAPopulationThread_:
        if clGAThread.GetLeverArmFitness()[0] == Value:
            break
        Index += 1
    return Index

def GAFittestInFitnessPie(FitnessPie_):
    '''
    This function finds the fittest element in the population set
    '''
    iFittest = 0
    dFittest = Decimal(0)
    for Key in FitnessPie_:
        # Find the Fittest element
        if FitnessPie_[Key] > dFittest:
            dFittest = FitnessPie_[Key]
            iFittest = Key
    return iFittest

def GenerateGAPopulation(iPopulationSize_, INSFiles_, GNSSFiles_, INSLevArmFiles_, LevArmSeed_, lock, queue, SolutionStatus_, PositionType_, Datum_='WGS84', Method_='GEOID'):
    '''
    Generates Genetic Algorithm Population
    '''
    aclGAPopulationThread = []
    # Generate Population for Genetic Algorithm
    for i in range(iPopulationSize_):
        clGAThread = myThreadProcess(i, 'GAThread' + str(i), [LevArmSeed_[0], LevArmSeed_[1], LevArmSeed_[2], INSFiles_[i], INSLevArmFiles_[i], GNSSFiles_[i], lock, queue, Datum_, Method_, SolutionStatus_, PositionType_])
        aclGAPopulationThread.append(clGAThread)
    return aclGAPopulationThread

def GABuildRouletteIntervals(FitnessPie_):
    '''
    This Function Builds a Weighted Roulette Wheel
    '''
    lastFitness = 0
    Roulette = {}
    for Key in FitnessPie_:
        Roulette[Key] = [lastFitness, lastFitness + FitnessPie_[Key]]
        lastFitness = lastFitness + FitnessPie_[Key]
    return Roulette

def GARouletteNewFitness(Roulette_):
    '''
    Re-computes the Roulette distribution once a member of the list
    is removed
    '''
    sumoffitness = 0
    FitnessPie = {}
    for Key in Roulette_:
        FitnessPie[Key] = Roulette_[Key][1] - Roulette_[Key][0]
        sumoffitness += Roulette_[Key][1] - Roulette_[Key][0]
    for Key in FitnessPie:
        FitnessPie[Key] = FitnessPie[Key] / sumoffitness
    NewRoulette = GABuildRouletteIntervals(FitnessPie)
    return NewRoulette

def GASelectOffspringPairs(Roulette_, CrossOver_):
    '''
    This function selects a pair of parents to pass their offspring
    to the next generation
    '''
    # First Parent Selection
    Value = Decimal(random.random())
    MyRoulette = copy.copy(Roulette_)
    Index1 = 0
    Index2 = 0
    for Key in MyRoulette:
        if (Value >= MyRoulette[Key][0] and Value < MyRoulette[Key][1]):
            Index1 = Key
            break
    # Second Parent Selection if Cross Over is enabled
    if (CrossOver_ > (1 - GA_CROSS_OVER_RATE)):
        del MyRoulette[Index1]
        MyRoulette = GARouletteNewFitness(MyRoulette)
        Value = Decimal(random.random())
        for Key in MyRoulette:
            if (Value >= MyRoulette[Key][0] and Value < MyRoulette[Key][1]):
                Index2 = Key
                break
    # Second Parent Selection if Cross Over is disabled
    else:
        Index2 = Index1
    return [Index1, Index2]

def GASelectParentIndexes(Roulette_, FitnessPie_):
    '''
    This function builds a list of parent pairs for next generation
    '''
    # If population is odd Select the Fittest to offspring with itself
    if (len(Roulette_) % 2 != 0):
        FittestElement = GAFittestInFitnessPie(FitnessPie_)
        nextGenList = [FittestElement, FittestElement]
    # Generate list of parents for next generation
    else:
        nextGenList = []
    # Generate list of parents
    while (len(nextGenList) < len(Roulette_) / 2):
        ParentList = GASelectOffspringPairs(Roulette_, Decimal(random.random()))
        nextGenList.append(ParentList)
    return nextGenList

def GAParentOffspring(ParentPair_, aclGAPopulationThread_, iCoord_):
    '''
    This function returns two binary strings representing the offspring from two parents
    '''
    vect1 = aclGAPopulationThread_[ParentPair_[0]].GetLevArmEncoderObject().GetBinaryEncodedLeverArm()
    vect2 = aclGAPopulationThread_[ParentPair_[1]].GetLevArmEncoderObject().GetBinaryEncodedLeverArm()
    [vect1[iCoord_], vect2[iCoord_]] = GASetCrossOverOffspring(vect1[iCoord_], vect2[iCoord_])
    return [vect1[iCoord_], vect2[iCoord_]]
#    [szEncoder1x, szEncoder1y, szEncoder1z] = aclGAPopulationThread_[ParentPair_[0]].GetLevArmEncoderObject().GetBinaryEncodedLeverArm()
#    [szEncoder2x, szEncoder2y, szEncoder2z] = aclGAPopulationThread_[ParentPair_[1]].GetLevArmEncoderObject().GetBinaryEncodedLeverArm()
#    # X-coordinate offspring encoding
#    [szEncoder1x, szEncoder2x] = GASetCrossOverOffspring(szEncoder1x, szEncoder2x)
#    # Y-coordinate offspring encoding
#    [szEncoder1y, szEncoder2y] = GASetCrossOverOffspring(szEncoder1y, szEncoder2y)
#    # Z-coordinate offspring encoding
#    [szEncoder1z, szEncoder2z] = GASetCrossOverOffspring(szEncoder1z, szEncoder2z)
#    return [[szEncoder1x, szEncoder1y, szEncoder1z],[szEncoder2x, szEncoder2y, szEncoder2z]]

def GAOffspringMutation(nextGenItem_, MutationRate_, MutationParams_):
    '''
    This function mutates one gene of a binary string
    '''
    # RMS error greater than Accuracy Threshold
    if (MutationParams_[0] > MutationParams_[2]):
        GA_MUTATION_RATE = Decimal(1) - Decimal(math.exp(-MutationParams_[1]))
    # Do mutation if enabled
    if (MutationRate_ > (1 - GA_MUTATION_RATE)):
        BinMutString = GASetMutation(nextGenItem_, random.randint(3,len(nextGenItem_)))
    # Object does not mutate if disabled
    else:
        BinMutString = copy.copy(nextGenItem_)
    return BinMutString

def OrderNextGenerationEncoded(List1_, List2_):
    '''
    Order the encoded vector values as follows:
    [[[vx11, vy11, vz11],[vx12, vy12, vz12]], [[vx21, vy21, vz21],[vx22, vy22, vz22]], ..., [[vxn1, vyn1, vzn1],[vxn2, vyn2, vzn2]]]
    '''
    nextEncoded = []
    for i in range(len(List1_) / 3):
        Vect1 = [List1_[i], List1_[i + len(List1_) / 3], List1_[i + 2 * len(List1_) / 3]]
        Vect2 = [List2_[i], List2_[i + len(List2_) / 3], List2_[i + 2 * len(List2_) / 3]]
        nextEncoded.append([Vect1, Vect2])
        i += 1
    return nextEncoded

def NextGenerationEncoded(nextGenList_, aclGAPopulationThread_, MutationParams_):
    '''
    This function generates the next population generation
    MutationParams_[0]: Average RMS position error
    MutationParams_[1]: Standard Deviation of RMS position error
    MutationParams_[2]: Accuracy Threshold to achieve
    '''
    iCoord = 0
    List1 = []
    List2 = []
    # Iterate over every coordinate
    for nextGenListCoord in nextGenList_:
        MyMutationParams = copy.copy(MutationParams_)
        # List of parents per coordinate
        for ParentPair in nextGenListCoord:
            nextGenCoordItem = GAParentOffspring(ParentPair, aclGAPopulationThread_, iCoord)
            MyMutationParams[1] = Decimal(1) / aclGAPopulationThread_[ParentPair[0]].GetLeverArmFitness()[iCoord + 1]
            TempEncoded1 = GAOffspringMutation(nextGenCoordItem[0], random.random(), MyMutationParams)
            MyMutationParams[1] = Decimal(1) / aclGAPopulationThread_[ParentPair[1]].GetLeverArmFitness()[iCoord + 1]
            TempEncoded2 = GAOffspringMutation(nextGenCoordItem[1], random.random(), MyMutationParams)
            List1.append(TempEncoded1)
            List2.append(TempEncoded2)
        del MyMutationParams
        iCoord += 1
    nextGenEncoded = OrderNextGenerationEncoded(List1, List2)
    return nextGenEncoded
#    for ParentPair in nextGenList_:
#        nextGenItem = GAParentOffspring(ParentPair, aclGAPopulationThread_)
#        # Set Mutations in next generation chromosomes
#        TempEncoded = []
#        for MyOffspringList in nextGenItem:
#            TempEncoded.append(GAOffspringMutation(MyOffspringList, random.random(), MutationParams_))
#        nextGenEncoded.append(TempEncoded)
#    return nextGenEncoded

def GAFitnessPie(aclGAPopulationThread_, FitnessIndex_):
    '''
    This function generates a fitness pie of the items of the present generation
    '''
    sumoffitness = Decimal(0)
    i = 0
    FitnessPie = {}
    # Build the fitness Pie
    for clGAThread in aclGAPopulationThread_:
        FitnessPie[i] = clGAThread.GetLeverArmFitness()[FitnessIndex_]
        sumoffitness = sumoffitness + clGAThread.GetLeverArmFitness()[FitnessIndex_]
        i = i + 1
    # Normalize fitness pie
    for key in FitnessPie:
        FitnessPie[key] = FitnessPie[key] / sumoffitness
    return FitnessPie

def GARouletteWheel(aclGAPopulationThread_, FitnessIndex_):
    '''
    This function Builds a Roulette Wheel to select the items of next generation
    '''
    FitnessPie = GAFitnessPie(aclGAPopulationThread_, FitnessIndex_)
    # Generate Roulette
    Roulette = GABuildRouletteIntervals(FitnessPie)
    return [Roulette, FitnessPie]

def GAElitist(aclGAPopulationThread_):
    '''
    Turn weakest object into fittest
    '''
    aclMyPopulationThread = copy.copy(aclGAPopulationThread_)
    WeakestFitness = Decimal(999999)
    # Individual Fitness
    dFittestx = Decimal(0)
    dFittesty = Decimal(0)
    dFittestz = Decimal(0)
    iNumSamples = 1
    for clGAThread in aclMyPopulationThread:
        # Save the Weakest Object
        if (clGAThread.GetLeverArmFitness()[0] < WeakestFitness):
            WeakestFitness = clGAThread.GetLeverArmFitness()[0]
            iWeakestIndex = iNumSamples - 1
        # Fittest lever arm x-coordinate
        if (clGAThread.GetLeverArmFitness()[1] > dFittestx):
            dFittestx = clGAThread.GetLeverArmFitness()[1]
            iIndexFitx = iNumSamples - 1
        # Fittest lever arm y-coordinates
        if (clGAThread.GetLeverArmFitness()[2] > dFittesty):
            dFittesty = clGAThread.GetLeverArmFitness()[2]
            iIndexFity = iNumSamples - 1
        # Fittest lever arm z-coordinates
        if (clGAThread.GetLeverArmFitness()[3] > dFittestz):
            dFittestz = clGAThread.GetLeverArmFitness()[3]
            iIndexFitz = iNumSamples - 1
        iNumSamples += 1
    # Pick the fittest lever arm per coordinate and set it to the weakest lever arm object
    levx = aclMyPopulationThread[iIndexFitx].GetLevArmEncoderObject().GetLeverArm()[0] + Decimal(random.triangular(-0.05, 0.05, 0)).quantize(Decimal(10) ** -3)
    levy = aclMyPopulationThread[iIndexFity].GetLevArmEncoderObject().GetLeverArm()[1] + Decimal(random.triangular(-0.05, 0.05, 0)).quantize(Decimal(10) ** -3)
    levz = aclMyPopulationThread[iIndexFitz].GetLevArmEncoderObject().GetLeverArm()[2] + Decimal(random.triangular(-0.05, 0.05, 0)).quantize(Decimal(10) ** -3)
    # Set weakest trajectory object with new lever arm
    aclMyPopulationThread[iWeakestIndex].GetLevArmTrajObject().SetLeverArmBodyFrame([levx, levy, levz])
    [blevx, blevy, blevz] = aclMyPopulationThread[iWeakestIndex].GetLevArmEncoderObject().MYLEVERARMENCODER.GetEncodedLeverArm([levx, levy, levz])
    aclMyPopulationThread[iWeakestIndex].GetLevArmEncoderObject().SetLeverArm(blevx, 0)
    aclMyPopulationThread[iWeakestIndex].GetLevArmEncoderObject().SetLeverArm(blevy, 1)
    aclMyPopulationThread[iWeakestIndex].GetLevArmEncoderObject().SetLeverArm(blevz, 2)
    # Compute new Fitness of Weakest object
    aclMyPopulationThread[iWeakestIndex].SerializedRun()
    del aclGAPopulationThread_
    return aclMyPopulationThread

def TestGAFitness(aclGAPopulationThread_):
    aclMyPopulationThread = GAElitist(aclGAPopulationThread_)
    # Population Fitness
    FitnessAverage = Decimal(0)
    FitnessVarianc = Decimal(0)
    FittestFitness = Decimal(0)
    iNumSamples = Decimal(1)
    for clGAThread in aclMyPopulationThread:
        # Save the fittest lever arm result
        if (clGAThread.GetLeverArmFitness()[0] > FittestFitness):
            FittestFitness = clGAThread.GetLeverArmFitness()[0]
        # Compute Fitness Variance
        if (iNumSamples > 1):
            FitnessVarianc = (iNumSamples - 2) / (iNumSamples - 1) * FitnessVarianc + 1 / iNumSamples * pow(1 / clGAThread.GetLeverArmFitness()[0] - FitnessAverage, 2)
        FitnessAverage = (iNumSamples - 1) / iNumSamples * FitnessAverage + 1 / iNumSamples * 1 / clGAThread.GetLeverArmFitness()[0]
        iNumSamples = iNumSamples + 1
    del aclGAPopulationThread_
    return [Decimal(FitnessAverage), Decimal(math.sqrt(FitnessVarianc)), Decimal(1) / FittestFitness, aclMyPopulationThread]

def SetNextGeneration(aclGAPopulationThread_, nextGenEncoded_):
    '''
    Set lever arm values for next generation
    '''
    aclGAMyPopulationThread = copy.copy(aclGAPopulationThread_)
    i = 0
    for EncodedSequence in nextGenEncoded_:
        for Sequence in EncodedSequence:
            # Conserve the population size
            if (i < len(aclGAMyPopulationThread)):
                # New X-coordinate
                aclGAMyPopulationThread[i].GetLevArmEncoderObject().SetLeverArm(Sequence[0], 0)
                # New Y-coordinate
                aclGAMyPopulationThread[i].GetLevArmEncoderObject().SetLeverArm(Sequence[1], 1)
                # New Z-coordinate
                aclGAMyPopulationThread[i].GetLevArmEncoderObject().SetLeverArm(Sequence[2], 2)
                # Trajectory object
                aclGAMyPopulationThread[i].GetLevArmTrajObject().SetLeverArmBodyFrame(aclGAMyPopulationThread[i].GetLevArmEncoderObject().GetLeverArm())
            i = i + 1
    del aclGAPopulationThread_
    return aclGAMyPopulationThread

def TestGAChromeSerial(aclGAPopulationThread_):
    '''
    This function evaluates the fitness of each chromosome to solve the problem
    of minimizing the RMS error between the GNSS and the INS + Lever Arm trajectories
    Each population member (or chromosome) is executed on the main thread
    '''
    # Need to return the modified object and by design python when returning does not modify argument
    aclGAMyPopulationThread = copy.copy(aclGAPopulationThread_)
    del aclGAPopulationThread_
    for clGAThread in aclGAMyPopulationThread:
        # Start Processing Threads
        clGAThread.SerializedRun()
    return aclGAMyPopulationThread    

def TestGAChromosomes(aclGAPopulationProcess_, Queue_):
    '''
    This function evaluates the fitness of each chromosome to solve the problem
    of minimizing the RMS error between the GNSS and the INS + Lever Arm trajectories
    Each population member (or chromosome) is executed in its own Thread context
    '''
    # Need to return the modified object and by design python when returning does not modify argument
    aclGAMyPopulationProcess = copy.copy(aclGAPopulationProcess_)
    del aclGAPopulationProcess_
    for clGAProcess in aclGAMyPopulationProcess:
        # Start Processing Threads
        clGAProcess.start()
        
    # Wait for all threads to finish computing the fitness of each chromosome
    FITNESS_DICT = {}
    while 1:
        for clGAProcess in aclGAMyPopulationProcess:
            # Wait for processing to finish
            if (clGAProcess.is_alive()):
                continue
            # Read Queue until we finish
            if (not Queue_.empty()):
                # [Process ID, Fitness]
                TempInfo = Queue_.get()
                # Modify dictionary
                if (TempInfo[0] not in FITNESS_DICT):
                    FITNESS_DICT[TempInfo[0]] = TempInfo[1]
        # Finish when all threads created are finished
        if (len(FITNESS_DICT) == len(aclGAMyPopulationProcess)):
            break
    
    # Save Fitness of each chromosome
    for key in FITNESS_DICT:
        aclGAMyPopulationProcess[key].SetLeverArmFitness(FITNESS_DICT[key])
    
    return aclGAMyPopulationProcess
