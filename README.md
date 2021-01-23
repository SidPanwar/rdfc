
# genrdfcpattern

`gen_rdfc_pattern.py` is a Python based command line tool for generating the 5th order recursive dynamic functional connectivity pattern for EEG signals and computing the resulting pattern's match scores with the reference rdFC patterns.


# System Requirements
## Hardware requirements
The command line tool requires only a standard computer with enough RAM to support the in-memory operations.

## Software requirements
### OS Requirements
This package is supported for *macOS*, *Linux* and *Windows*. The package has been tested on the following systems:
+ macOS: Sierra (10.12.6)
+ Linux: Ubuntu 16.04
+ Windows: Windows 10

### Python Dependencies
`gen_rdfc_pattern.py` requires Python version >= 3.6.8 and the following packages in the Python scientific stack:

+ numpy (>= 1.14.3)
+ pandas (>= 0.23)
+ scipy (>= 1.1.0)

# Installation And Usage

To install, unzip genrdfcpattern.zip. There are no further steps necessary to complete installation. Expected time for installation on a reasonably configured desktop is on the order of a few seconds.

**Usage:**

On the command line console, go to the folder containing the contents unzipped above and run the command line as shown below:

```console
python gen_rdfc_pattern.py [-h] --inputFile INPUTFILE --samplingRate SAMPLINGRATE --notchFrequency NOTCHFREQUENCY

Generate rdFC Pattern for the given 5-minute EEG epoch of an electrode triplet and compute its match score 
with each of the three reference patterns. Prior to pattern generation, the signals are bandpass filtered from 0.5Hz to 70Hz and notch filtered at the notch frequency specified on the command line.

  -h, --help                        Show this help message and exit
  
  --inputFile INPUTFILE             File containing a 5-minute EEG epoch of an electrode triplet. 
                                    Format of input file: 3 rows with (samplingRate * 300) samples.
                         
  --samplingRate SAMPLINGRATE       Sampling Rate of input signals
  
  --notchFrequency NOTCHFREQUENCY   The notch frequency to use (Hz). Either 50Hz or 60Hz.
```

# Demo

**Expected Runtime:** 10 seconds per example on a reasonably configured desktop.

## Example 1
**Command line**
```console
python gen_rdfc_pattern.py  --inputFile sampleEpochs/sample1.txt --samplingRate 256 --notchFrequency 50
```

**Output**
```console
rdFC Pattern:
Order 1:   0.8226   0.8069   0.6666
Order 2:   0.4342   0.5789   0.7059
Order 3:   0.4954   0.1349   0.3543
Order 4:   0.1944   0.3162   0.0262
Order 5:  -0.0186   0.0810   0.1773

Match Scores for rdFC Pattern:
Reference Pattern 1 : 2.7722
Reference Pattern 2 : -0.6200
Reference Pattern 3 : 1.9540
```

## Example 2
**Command line**
```console
python gen_rdfc_pattern.py  --inputFile sampleEpochs/sample2.txt --samplingRate 256 --notchFrequency 60
```

**Output**
```console
rdFC Pattern:
Order 1:   0.9150   0.9116   0.9211
Order 2:   0.8627   0.9118   0.7611
Order 3:   0.2219   0.6268   0.4624
Order 4:   0.2975   0.1251   0.4108
Order 5:   0.2002   0.1177   0.0715

Match Scores for rdFC Pattern:
Reference Pattern 1 : 0.2599
Reference Pattern 2 : 3.0101
Reference Pattern 3 : -0.3989
```

# License

This project is covered under the **BSD 3-Clause License**.
