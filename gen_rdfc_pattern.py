# coding: utf-8
"""Tool to generate rdFC pattern corresponding to a 5-minute EEG epoch of an electrode triplet and the resultant pattern's match score with the three reference patterns"""

# Copyright (c) Siddharth Panwar
# Distributed under the terms of the BSD-3-Clause License.

import argparse
import numpy as np
import pandas as pd

from scipy import signal


# Text file containing first reference pattern
FIRST_REFERENCE_PATTERN_FILE = 'refPatterns/firstRefPattern.txt'

# Text file containing second reference pattern
SECOND_REFERENCE_PATTERN_FILE = 'refPatterns/secondRefPattern.txt'

# Text file containing third reference pattern
THIRD_REFERENCE_PATTERN_FILE = 'refPatterns/thirdRefPattern.txt'

# Frequency to apply the notch filter at
NOTCH_FREQUENCY = 50.0

# Duration of EEG to process: 5 minutes
EEG_DURATION_SECS = 5 * 60 

# Number of orders of correlation coefficents to compute
NUM_ORDERS = 5


def filterSignalList(signalArr, sampleRate):
    """Filter the input signals. LowPass: 70, HighPass: 0.5, Notch: As specified by NOTCH_FREQUENCY"""
    
    #Design Bandpass filter
    lp_wp = (2.0 * 70) / sampleRate
    lp_ws = (2.0 * 90) / sampleRate
    hp_wp = (2.0 * 0.5) / sampleRate
    hp_ws = (2.0 * 0.01) / sampleRate
    wp = [hp_wp, lp_wp]
    ws = [hp_ws, lp_ws]
    gpass = 0.1
    gstop = 20
    b,a = signal.iirdesign(wp, ws, gpass, gstop, analog=False, ftype='ellip', output='ba')
    
    #Design notch filter
    f0 = NOTCH_FREQUENCY
    Q = 30.0
    b_n, a_n = signal.iirnotch((2 * f0)/sampleRate, Q)
    
    numSignals = signalArr.shape[0]
    filtered_signalArr = np.zeros(signalArr.shape)
    for i in range(numSignals):
        filtered_signal = signal.filtfilt(b, a, signalArr[i], method="gust")
        notch_filtered_signal = signal.filtfilt(b_n, a_n, filtered_signal, method="gust")
        filtered_signalArr[i] = notch_filtered_signal
        
    return filtered_signalArr


def getPattern(signals, sampleRate):
    """Get the rdFC pattern for the signals"""
    
    assert signals.shape[0] == 3
    numSamples = signals.shape[1]
         
    pattern = np.zeros((3, NUM_ORDERS))
    vals = signals
    for order in range(NUM_ORDERS):
        vals_pd = pd.DataFrame(vals.transpose())
        corrCoefficient = vals_pd.corr().values
        pattern[0, order] = corrCoefficient[0, 1]
        pattern[1, order] = corrCoefficient[1, 2]
        pattern[2, order] = corrCoefficient[0, 2]
        
        #Compute next set of values
        if order != NUM_ORDERS - 1:
            numFrames = vals.shape[1] - sampleRate + 1
            vals_rw = vals_pd.rolling(window=sampleRate)
            vals_corr = vals_rw.corr().values.reshape(-1, 3, 3)
            
            vals_next = np.zeros((3, numFrames))
            vals_next[0] = vals_corr[-numFrames:, 0, 1]
            vals_next[1] = vals_corr[-numFrames:, 1, 2]
            vals_next[2] = vals_corr[-numFrames:, 0, 2]
            
            vals = vals_next
            
    return pattern 


def getNormalizedVector(vec):
    diffVector = np.diff(vec)
    numCols = diffVector.shape[1]
    normalizedVector = np.zeros(diffVector.shape)
    for col in range(numCols):
        normalizedVector[:, col] = diffVector[:, col] / np.linalg.norm(diffVector[:, col])
        
    return normalizedVector


def getMatchScore(vec1, vec2):
    matchScore = 0
    numCols = vec1.shape[1]
    for col in range(numCols):
        matchScore += np.dot(vec1[:, col], vec2[:, col])
        
    return matchScore


def loadReferencePatterns():
    firstRefPattern = np.loadtxt(FIRST_REFERENCE_PATTERN_FILE)
    secondRefPattern = np.loadtxt(SECOND_REFERENCE_PATTERN_FILE)
    thirdRefPattern = np.loadtxt(THIRD_REFERENCE_PATTERN_FILE)
    firstRefVec = getNormalizedVector(firstRefPattern)
    secondRefVec = getNormalizedVector(secondRefPattern)
    thirdRefVec = getNormalizedVector(thirdRefPattern)
    return [firstRefVec, secondRefVec, thirdRefVec]


def genPatternAndScore(signals, sampleRate, referenceVecs):
    """Get the rdFC pattern for the signals"""

    filteredSignals = filterSignalList(signals, sampleRate)
    pattern = getPattern(filteredSignals, sampleRate)
    patternVec = getNormalizedVector(pattern)
    scores = np.zeros(3)
    for refVecIdx in range(len(referenceVecs)):       
        scores[refVecIdx] = getMatchScore(patternVec, referenceVecs[refVecIdx])
        
    return pattern, scores


def printResults(pattern, scores):
    print('rdFC Pattern:')
    
    for i in range(5):
        print('Order {}: {:8.4f} {:8.4f} {:8.4f}'.format(i+1, pattern[0][i], pattern[1][i], pattern[2][i])) 

    print('')
    print('Match Scores for rdFC Pattern:')
    for i in range(3):
        print('Reference Pattern {} : {:.4f}'.format(i+1, scores[i]))


def processTriplet(signalsFile, sampleRate):
    referenceVecs = loadReferencePatterns()
    signals = np.loadtxt(signalsFile)
    if signals.shape[0] != 3:
        print('Error: Expected 3 rows in input file. Found {} rows instead.'.format(signals.shape[0]))
        return
        
    numSamplesExpected = sampleRate * EEG_DURATION_SECS
    if signals.shape[1] != numSamplesExpected:
        print('Error: Expected {} samples per electrode in input file (5 minutes at sampling rate {}). Found {} samples per electrode instead.'.format(            numSamplesExpected, sampleRate, signals.shape[1]))
        return
    
    (pattern, scores) = genPatternAndScore(signals, sampleRate, referenceVecs)
    printResults(pattern, scores)


def parseArguments():
    parser = argparse.ArgumentParser(description='Generate rdFC Pattern for the given 5-minute EEG epoch of an electrode triplet  and compute its match score with each of the three reference patterns. Prior to pattern generation, the signals are bandpass filtered from 0.5Hz to 70Hz and notch filtered at the notch frequency specified on the command line.')
    parser.add_argument('--inputFile', type=str, required=True,
        help='File containing a 5-minute EEG epoch of an electrode triplet. Format of input file: 3 rows with (samplingRate * 300) samples.')
    parser.add_argument('--samplingRate', type=int, required=True,
        help='Sampling Rate of input signals')
    parser.add_argument('--notchFrequency', type=int, required=True,
        help='The notch frequency to use (Hz). Either 50Hz or 60Hz.')

    args = parser.parse_args()
    return args

def main():
    global NOTCH_FREQUENCY
    args = parseArguments()
    if args.notchFrequency == 50 or args.notchFrequency == 60:
        NOTCH_FREQUENCY = args.notchFrequency
    else:
        print('Error: Please specify a notch frequency of 50Hz or 60Hz')
        return
   
    processTriplet(args.inputFile, args.samplingRate)

if __name__== '__main__':
   main() 
