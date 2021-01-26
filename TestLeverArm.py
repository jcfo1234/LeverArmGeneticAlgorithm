'''
Created on Feb 27, 2015

@author: JFandino
'''

#import sys
import shutil
import multiprocessing
import os
from FileInterpreter.FileParser import MyPositionFileParser
import sys, getopt
# from LeverArmTrajectory import MyLevArmTraj
from GA import GAOperations
from decimal import Decimal

FITNESS_THRESHOLD = Decimal(0.0004)

def MultipleFileCopies(source_, iPopulation_):
    '''
    Creates multiple copies of the same file to avoid race conditions
    '''
    Filelist = []
    for i in range(iPopulation_):
        destination = source_.split('.')[0] + '_' + str(i) + '.' + source_.split('.')[1]
        shutil.copy2(source_, destination)
        Filelist.append(destination)
    return Filelist

def ListOutputFiles(source_, iPopulation_):
    '''
    File list Output
    '''
    Filelist = []
    for i in range(iPopulation_):
        destination = source_.split('.')[0] + '_' + str(i) + '.' + source_.split('.')[1]
        Filelist.append(destination)
    return Filelist

def ParseArguments(argv):
    try:
        opts, args = getopt.getopt(argv, "hr:l:t:g:p:x:y:z:a:b:c:",["reffile=","levfile=","gnssbinfile=","gnssoutfile=","popsize=","levx=","levy=","levz=","solstatus=","postype=","poslog="])
    except getopt.GetoptError:
        print('TestLeverArm.py \n-r <Reference Trajectory file full path(In)> \n-l <Lever arm trajectory file full path (Out)> \n-t <UUT trajectory binary file (In)> \n-g <UUT trajectory file (Out)> \n-p <Population size> \n-x <Lever arm x> \n-y <Lever arm y> \n-z <Lever arm z> \n-a <Expected Solution Status> \n-b <Expected position type> \n-c <Expected position log>')
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print('TestLeverArm.py \n-r <Reference Trajectory file full path(In)> \n-l <Lever arm trajectory file full path (Out)> \n-t <UUT trajectory binary file (In)> \n-g <UUT trajectory file (Out)> \n-p <Population size> \n-x <Lever arm x> \n-y <Lever arm y> \n-z <Lever arm z> \n-a <Expected Solution Status> \n-b <Expected position type> \n-c <Expected position log>')
            sys.exit()
        elif opt in ("-r", "--reffile"):
            szRefTrajFullPath = arg
        elif opt in ("-l", "--levfile"):
            szLevTrajFullPath = arg
        elif opt in ("-t", "--gnssbinfile"):
            szTstGNSSFullPath = arg
        elif opt in ("-g", "--gnssoutfile"):
            szGNSSTrajFullPath = arg
        elif opt in ("-p", "--popsize"):
            iPopulationSize = int(arg)
        elif opt in ("-x", "--levx"):
            x = float(arg)
        elif opt in ("-y", "--levy"):
            y = float(arg)
        elif opt in ("-z", "--levz"):
            z = float(arg)
        elif opt in ("-a", "--solstatus"):
            szExpectedSolutionStatus = arg
        elif opt in ("-b", "--postype"):
            szExpectedPositionType = arg
        elif opt in ("-c", "--poslog"):
            szExpectedPositionLog = arg
    return [szRefTrajFullPath, szLevTrajFullPath, szTstGNSSFullPath, szGNSSTrajFullPath, iPopulationSize, [x, y, z], szExpectedSolutionStatus, szExpectedPositionType, szExpectedPositionLog]

if __name__ == '__main__':
    [szRefTrajFullPath, szLevTrajFullPath, szTstGNSSFullPath, szGNSSTrajFullPath, iPopulationSize, LeverArm, szExpectedSolutionStatus, szExpectedPositionType, szExpectedPositionLog] = ParseArguments(sys.argv[1:])

    # Convert to comma separated Text encoded file
    TestFile = MyPositionFileParser([szTstGNSSFullPath, szGNSSTrajFullPath])
    TestFile.ConvertBinaryToText(szExpectedPositionLog)
    
    # Generate copies of files the same size as population size
    GNSSFiles = MultipleFileCopies(szGNSSTrajFullPath, iPopulationSize)
    INSFiles = MultipleFileCopies(szRefTrajFullPath, iPopulationSize)
    INSLevArmFiles = ListOutputFiles(szLevTrajFullPath, iPopulationSize)
    
    # Generate Population
    iGeneration = 0
    lock = multiprocessing.Lock()
    queue = multiprocessing.Queue(0)
    aclGAPopulationThread = GAOperations.GenerateGAPopulation(iPopulationSize, INSFiles, GNSSFiles, INSLevArmFiles, LeverArm, lock, queue, szExpectedSolutionStatus, szExpectedPositionType)
    aclGAPopulationThread = GAOperations.TestGAChromosomes(aclGAPopulationThread, queue)
    [dFitnessAvg, dFitnessStdDev, dFittestFitness, aclGAPopulationThread] = GAOperations.TestGAFitness(aclGAPopulationThread)
    # Search for optimal through generations. Ideally convergence should be obtained in less iterations than when using brute force
    while (iGeneration < aclGAPopulationThread[0].GetLevArmEncoderObject().MYLEVERARMENCODER.GetEncoderLength()) and (dFittestFitness > FITNESS_THRESHOLD):
        [GenRoulettex,GenFitnessPiex] = GAOperations.GARouletteWheel(aclGAPopulationThread, 1)
        [GenRoulettey,GenFitnessPiey] = GAOperations.GARouletteWheel(aclGAPopulationThread, 2)
        [GenRoulettez,GenFitnessPiez] = GAOperations.GARouletteWheel(aclGAPopulationThread, 3)
        nextGenListx = GAOperations.GASelectParentIndexes(GenRoulettex, GenFitnessPiex)
        nextGenListy = GAOperations.GASelectParentIndexes(GenRoulettey, GenFitnessPiey)
        nextGenListz = GAOperations.GASelectParentIndexes(GenRoulettez, GenFitnessPiez)
        # List of Chosen parents for each coordinate
        nextGenList = [nextGenListx, nextGenListy, nextGenListz]
        nextGenEncoded = GAOperations.NextGenerationEncoded(nextGenList, aclGAPopulationThread, [dFitnessAvg, dFitnessStdDev, FITNESS_THRESHOLD, iPopulationSize])
        # New population initialization since Python is unable to start a process multiple times
        del aclGAPopulationThread
        aclGAPopulationThread = GAOperations.GenerateGAPopulation(iPopulationSize, INSFiles, GNSSFiles, INSLevArmFiles, LeverArm, lock, queue, szExpectedSolutionStatus, szExpectedPositionType)
        # Set New Population
        aclGAPopulationThread = GAOperations.SetNextGeneration(aclGAPopulationThread, nextGenEncoded)
        # Evaluate fitness of new population
        aclGAPopulationThread = GAOperations.TestGAChromosomes(aclGAPopulationThread, queue)
        # Compute standard deviations of Fitnesses for stopping algorithm
        [dFitnessAvg, dFitnessStdDev, dFittestFitness, aclGAPopulationThread] = GAOperations.TestGAFitness(aclGAPopulationThread)
        iGeneration += 1
        # Debug Information
        szPath = '\\'.join(szTstGNSSFullPath.split('\\')[:-1])
        szListInfo = 'ECHO '
        for items in nextGenList:
            szListInfo = szListInfo + '[' + ','.join(map(str, items)) + '],'
        FittestLeverArm = aclGAPopulationThread[GAOperations.GAGetFittestByFitness(aclGAPopulationThread)].GetLevArmTrajObject().GetLeverArmBodyFrame()
        FitnessOfFittest = aclGAPopulationThread[GAOperations.GAGetFittestByFitness(aclGAPopulationThread)].GetLeverArmFitness()
        szLevArmInfo = 'ECHO Lever Arm is: [{:.3f},{:.3f},{:.3f},{:d}]'.format(FittestLeverArm[0], FittestLeverArm[1], FittestLeverArm[2], GAOperations.GAGetFittestByFitness(aclGAPopulationThread))
        szLevArmFit = 'ECHO Lever Arm Fitness is: [{:.3f}, {:.3f}, {:.3f}]'.format(FitnessOfFittest[1], FitnessOfFittest[2], FitnessOfFittest[3])        
        szGenInfo = 'ECHO Generation, Fittest, Average and StdDev Fitness are: [{:d}, {:.5f}, {:.5f}, {:.5f}]'.format(iGeneration, dFittestFitness, dFitnessAvg, dFitnessStdDev)
        os.system(szListInfo + ' >> ' + szPath + '\\GAFile.txt')
        os.system(szLevArmInfo + ' >> ' + szPath + '\\GAFile.txt')
        os.system(szLevArmFit + ' >> ' + szPath + '\\GAFile.txt')
        os.system(szGenInfo + ' >> ' + szPath + '\\GAFile.txt')
    
    # Pick the fittest element in the last generation
    FittestLeverArm = aclGAPopulationThread[GAOperations.GAGetFittestByFitness(aclGAPopulationThread)].GetLevArmTrajObject().GetLeverArmBodyFrame()
    print('Lever Arm is: [{:.3f},{:.3f},{:.3f}]'.format(FittestLeverArm[0], FittestLeverArm[1], FittestLeverArm[2]))
    print('Average and StdDev Fitness is: {:.3f}, {:.3f}'.format(dFitnessAvg, dFitnessStdDev))
    pass