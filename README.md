# ClaymoreMinerDataExtractor
A Python utility that extracts data from the claymore miner output and saves it at .json and .csv data files

## Miner settings
```miner_settings.json``` a json file that contains all of the settings needed for starting the claymore miner

Before using the script you must change the folowing values in your ```miner_settings.json``` settings file:
```executable``` should be the path to EthDcrMiner64.exe. Be sure to use two backslashes for windows paths
```ewal``` should be to your username and worker name with 'x' as the password to get credit for mining
you may want to change other settings for gpu fan and temperature settings

## Usage
example usage:

```python claymoreminerdataextractor.py -o C:\Claymore.s.dual.ethereum.v15.0.-.widows\logs -s C:\Claymore.s.dual.ethereum.v15.0.-.widows\miner_settings.json```

Usage:
optional arguments:

  -h, --help            show this help message and exit
  
  -o OUTPUTLOCATION, --outputlocation OUTPUTLOCATION
                        directory where logs and report files will be saved
						
  -s SETTINGSFILE, --settingsfile SETTINGSFILE
                        location of a .json settings file for the miner