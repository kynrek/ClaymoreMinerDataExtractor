#Claymore Miner Data Extraction
#author Joshua Witt kynrek@gmail.com
#Date 2-21-2021
#Description : This python script is designed to capture the standard output from claymore miner and
#extract details from the text as json objects
#Claymore Miner Data Extraction
#author Joshua Witt kynrek@gmail.com
#Date 2-21-2021
#Description : This python script is designed to capture the standard output from claymore miner and
#extract details from the text as json objects

#below is a sample command
#The script accepts a command line parameter of the folder where to store the output log/data files

import os, sys
import subprocess
from subprocess import Popen, PIPE
import json
import re
from datetime import datetime
import argparse as ap

parser = ap.ArgumentParser(description="Claymore Miner Data Extractor")

output_directory = ''

parser.add_argument('-o', '--outputlocation', type=str, help='directory where logs and report files will be saved')
parser.add_argument('-s', '--settingsfile', type=str, help='location of a .json settings file for the miner')

args = parser.parse_args()

#if get the output location argument and assign it to 
#output_directory, if there is no trailing slash for 
#the directory then add it

if args.outputlocation is not None:
	if args.outputlocation[-1] != '\\':
		output_directory = '{}\\'.format(args.outputlocation)
	else: 
		output_directory = args.outputlocation
	if not os.path.isdir(output_directory):
		sys.stdout.write('Output Directory {} does not exist'.format(output_directory))
		exit(-1)
	
#load the miner settings json file
#miner_settings_file_path = 'miner_settings.json'
if args.settingsfile is not None:
	if os.path.isfile(args.settingsfile):

		# Opening JSON file
		settings_file = open(args.settingsfile)
		# It returns JSON object as dictionary
		try:
			miner_settings = json.load(settings_file)
		except Exception as e:
			sys.stdout.write('error parsing settings file {}'.format(str(e)))
			exit(-3)
	else:
		sys.stdout.write('miner settings file {} does not exist'.format(args.settingsfile))
		exit(-2)
		
		mining_pool_username = miner_settings['ewal'].split('.')[0]
		mining_pool_worker_name = miner_settings['ewal'].split('.')[1].split(':')[0]
		
		miner_settings = {
		 "executable" : "C:\Claymore.s.dual.ethereum.v15.0.-.widows\EthDcrMiner64.exe",
		 "epool" : "us-east.ethash-hub.miningpoolhub.com:20535",
		 "ewal" : "kynrek.3070:x", 
		 "fanmin" : "75",
		 "fanmax": "100",
		 "epsw" : "x", 
		 "mode" : "1", 
		 "dbg" : "-1", 
		 "mport" : "0",
		 "etha" : "0",
		 "ftime" : "55", 
		 "retrydelay" : "1",
		 "tt" : "79", 
		 "ttli" : "77", 
		 "tstop" : "89",
		 "esm" : "2"
		}

mining_command = []
for setting_key in miner_settings:
	if setting_key == 'executable':
		mining_command.append(miner_settings[setting_key])
	else:
		mining_command.append("-{}".format(setting_key))
		mining_command.append(miner_settings[setting_key])
print(mining_command)

#get the current timestamp for naming files
fileNow = datetime.now().strftime("%m-%d-%Y-%H-%M-%S")

#create a variable to count the number of summary records written
summary_records_written = 0

#generate our file names
summaryCSVFileName = '{}minerSummary-{}.csv'.format(output_directory,fileNow)
summaryJSONFileName = '{}minerSummary-{}.json'.format(output_directory,fileNow)
summaryLogFileName = '{}logfile-{}.txt'.format(output_directory,fileNow)

mining_pool_username = miner_settings['ewal'].split('.')[0]
mining_pool_worker_name = miner_settings['ewal'].split('.')[1].split(':')[0]
		
#open our files for write only mode
summaryCSVFile = open(summaryCSVFileName,"w") 
summaryJSONFile = open(summaryJSONFileName,"w") 
summaryLogFile = open(summaryLogFileName,"w")

#write to the log file to note the start time
summaryLogFile.write('Process Claymore Data Script for account {} worker {} Started {}\n'.format(mining_pool_username,mining_pool_worker_name,datetime.now().strftime("%m/%d/%Y %H-%M-%S")))
summaryLogFile.flush()

#initialize maximumDifficultyOfFoundShare as it is not always present and we need an initial value
maximumDifficultyOfFoundShare = ""

#create our list of files for our CSV file header
fields = [
'miningPoolUsername',
'miningPoolWorkerName',
'hoursMined',
'minutesMined',
'timeStampMonth',
'timeStampDay',
'timeStampHours',
'timeStampMinutes',
'miningServer',
'miningPort',
'miningDurationHours',
'miningDurationMinutes', 
'incorrectShares',
'incorrectSharePercentage',
'estimatedStalesPercentage',
'maximumDifficultyOfFoundShare',
'acceptedShares',
'staleShares',
'rejectedShares',
'rejectedStaleShares',
'averageSpeedMinutes',
'averageMegaHashes',
'effectiveSpeed',
'effectiveSpeedAtPool',
'recordLastModified'
]

#create the header line string
headerString = ','.join(fields)
summaryCSVFile.write('{}\n'.format(headerString))
summaryCSVFile.flush()

summaryJSONFile.write('[\n')
summaryJSONFile.flush()
try:
	#Start the miner program using subprocess in order to capture the output
	p = subprocess.Popen(mining_command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
	while True:
		retcode = p.poll()
		input_line = p.stdout.readline().decode('utf-8')
		sys.stdout.write(input_line)
		
		#get the timestamp from the first line of the summary
		m = re.match("\*+ (\d+):(\d+) \*+ (\d+)/(\d+) (\d+):(\d+).*", input_line)
		if m:
			matches = m.groups()
			timeStamp = {
			"hoursMined" : matches[0],
			"minutesMined" : matches[1],
			"timeStampMonth" : matches[2],
			"timeStampDay" : matches[3],
			"timeStampHours" : matches[4],
			"timeStampMinutes" : matches[5]
			}
			
		#get connection info
		#g='Eth: Mining ETH on us-east.ethash-hub.miningpoolhub.com:20535 for 0:19'
		m = re.match("Eth: Mining ETH on (.*):(\d+) for (\d+):(\d+)", input_line)
		if m:
			matches=m.groups()
			connectionInfo= {
			'miningServer' : matches[0],
			'miningPort' : matches[1],
			'miningDurationHours' : matches[2],
			'miningDurationMinutes' : matches[3]
			}
			#print(connectionInfo)
			
		#get incorrect shares line
		m = re.match("Eth: Incorrect shares (\d+) \((\d+\.\d+)\%\), est. stales percentage (\d+\.\d+)\%", input_line)
		if m:
			matches=m.groups()
			incorrectShares={
			"incorrectShares" : matches[0],
			"incorrectSharePercentage" : matches[1],
			"estimatedStalesPercentage" : matches[2]
			}
			
		#get max difficulty
		m = re.match("Eth: Maximum difficulty of found share: (\d+.\d+) GH \(!\)", input_line)
		if m:
			matches=m.groups()
			maximumDifficultyOfFoundShare = matches[0]

		#get Share count
		m = re.match("Eth: Accepted shares (\d+) \((\d+) stales\), rejected shares (\d+) \((\d+) stales\)", input_line)
		if m:
			matches = m.groups()
			shareCount = {
			"acceptedShares" : matches[0],
			"staleShares" : matches[1],
			"rejectedShares" : matches[2],
			"rejectedStaleShares" : matches[3]
			}
			
		#get average speed
		m = re.match("Eth: Average speed \((\d+) min\): (\d+.\d+) MH/s", input_line)
		if m:
			matches=m.groups()
			averageSpeed = {
			'averageSpeedMinutes' : matches[0],
			'averageMegaHashes' : matches[1]
			}
			
		#get effective speed
		m = re.match("Eth: Effective speed: (\d+.\d+) MH/s; at pool: (\d+.\d+) MH/s", input_line)
		if m:
			matches=m.groups()
			effectiveSpeed = {
			'effectiveSpeed' : matches[0],
			'effectiveSpeedAtPool' : matches[1]
			}
			
			summaryRecord = {
			'miningPoolUsername' : mining_pool_username,
			'miningPoolWorkerName' : mining_pool_worker_name,
			'timeStamp' : timeStamp,
			'connectionInfo' : connectionInfo,
			'shareCount' : shareCount,
			'incorrectShares' : incorrectShares,
			'maximumDifficultyOfFoundShare' : maximumDifficultyOfFoundShare,
			'averageSpeed' : averageSpeed,
			'effectiveSpeed' : effectiveSpeed
			}
			
			if summary_records_written > 0:
				summaryJSONFile.write(',{}\n'.format(summaryRecord))
				summaryJSONFile.flush()
			else:
				summaryJSONFile.write('{}\n'.format(json.dumps(summaryRecord)))
				summaryJSONFile.flush()
				
			summary_records_written = summary_records_written + 1
			
			values=[
			mining_pool_username,
			mining_pool_worker_name,
			timeStamp['hoursMined'],
			timeStamp['minutesMined'],
			timeStamp['timeStampMonth'],
			timeStamp['timeStampDay'],
			timeStamp['timeStampHours'],
			timeStamp['timeStampMinutes'],
			connectionInfo['miningServer'],
			connectionInfo['miningPort'],
			connectionInfo['miningDurationHours'],
			connectionInfo['miningDurationMinutes'],
			incorrectShares['incorrectShares'],
			incorrectShares['incorrectSharePercentage'],
			incorrectShares['estimatedStalesPercentage'],
			maximumDifficultyOfFoundShare,
			shareCount['acceptedShares'],
			shareCount['staleShares'],
			shareCount['rejectedShares'],
			shareCount['rejectedStaleShares'],
			averageSpeed['averageSpeedMinutes'],
			averageSpeed['averageMegaHashes'],
			effectiveSpeed['effectiveSpeed'],
			effectiveSpeed['effectiveSpeedAtPool'],
			datetime.now().strftime("%m/%d/%Y %H:%M:%S")
			]
			
			dataString = ','.join(values)
			summaryCSVFile.write('{}\n'.format(dataString))
			summaryCSVFile.flush()
			
		#get GPU Details
		#h='GPU1: 43C 75% 120W'
		m = re.match("GPU(\d+): (\d+)C (\d+)% (\d+)W", input_line)
		if m:
			matches=m.groups()
			gpuDetails={
			'gpuNumber' : matches[0],
			'gpuTemperatureCelcius' : matches[1],
			'gpuPowerPercentage' : matches[2],
			'gpuWattage' : matches[3]
			}

		#get GPU Details
		#j='GPUs power: 119.8 W'
		m = re.match("GPUs power: (\d+.\d+) W", input_line)
		if m:
			matches=m.groups()
			gpuPower={
			'totalGPUsPower' : matches[0]
			}

		#getspeedupdate
		#k='Eth speed: 57.581 MH/s, shares: 17/0/0, time: 1:05'
		m = re.match("Eth speed: (\d+.\d+) MH/s, shares: (\d+)/(\d+)/(\d+), time: (\d+):(\d+)", input_line)
		if m:
			matches=m.groups()
			speedUpdate={
			'ethSpeedMegaHashes' : matches[0],
			'acceptedShares' : matches[1],
			'staleShares' : matches[2],
			'rejectedShares' : matches[3],
			'miningDurationHours' : matches[4],
			'miningDurationMinutes' : matches[5]
			}

		if retcode is not None:
			break

except:	
	p.terminate()
	
#make sure to terminate the process and write close the json array in the output file		
finally:
	summaryJSONFile.write(']\n')
	summaryJSONFile.flush()
	summaryLogFile.write('Process Claymore Data Script for account {} worker {} Ended {}\n'.format(mining_pool_username,mining_pool_worker_name,datetime.now().strftime("%m/%d/%Y %H-%M-%S")))
	summaryLogFile.flush()


#below is a sample command
#The script accepts a command line parameter of the folder where to store the output log/data files

import os, sys
import subprocess
from subprocess import Popen, PIPE
import json
import re
from datetime import datetime
import argparse as ap

parser = ap.ArgumentParser(description="Claymore Miner Data Extractor")

output_directory = ''

parser.add_argument('-o', '--outputlocation', type=str, help='directory where logs and report files will be saved')
parser.add_argument('-s', '--settingsfile', type=str, help='location of a .json settings file for the miner')

args = parser.parse_args()

#if get the output location argument and assign it to 
#output_directory, if there is no trailing slash for 
#the directory then add it

if args.outputlocation is not None:
	if args.outputlocation[-1] != '\\':
		output_directory = '{}\\'.format(args.outputlocation)
	else: 
		output_directory = args.outputlocation
	if not os.path.isdir(output_directory):
		sys.stdout.write('Output Directory {} does not exist'.format(output_directory))
		exit(-1)
	
#load the miner settings json file
#miner_settings_file_path = 'miner_settings.json'
if args.settingsfile is not None:
	if os.path.isfile(args.settingsfile):

		# Opening JSON file
		settings_file = open(args.settingsfile)
		# It returns JSON object as dictionary
		try:
			miner_settings = json.load(settings_file)
		except Exception as e:
			sys.stdout.write('error parsing settings file {}'.format(str(e)))
			exit(-3)
	else:
		sys.stdout.write('miner settings file {} does not exist'.format(args.settingsfile))
		exit(-2)
		
		miner_settings = {
		 "executable" : "C:\Claymore.s.dual.ethereum.v15.0.-.widows\EthDcrMiner64.exe",
		 "epool" : "us-east.ethash-hub.miningpoolhub.com:20535",
		 "ewal" : "kynrek.3070:x", 
		 "fanmin" : "75",
		 "fanmax": "100",
		 "epsw" : "x", 
		 "mode" : "1", 
		 "dbg" : "-1", 
		 "mport" : "0",
		 "etha" : "0",
		 "ftime" : "55", 
		 "retrydelay" : "1",
		 "tt" : "79", 
		 "ttli" : "77", 
		 "tstop" : "89",
		 "esm" : "2"
		}

mining_command = []
for setting_key in miner_settings:
	if setting_key == 'executable':
		mining_command.append(miner_settings[setting_key])
	else:
		mining_command.append("-{}".format(setting_key))
		mining_command.append(miner_settings[setting_key])
print(mining_command)

#get the current timestamp for naming files
fileNow = datetime.now().strftime("%m-%d-%Y-%H-%M-%S")

#create a variable to count the number of summary records written
summary_records_written = 0

#generate our file names
summaryCSVFileName = '{}minerSummary-{}.csv'.format(output_directory,fileNow)
summaryJSONFileName = '{}minerSummary-{}.json'.format(output_directory,fileNow)
summaryLogFileName = '{}logfile-{}.txt'.format(output_directory,fileNow)

#open our files for write only mode
summaryCSVFile = open(summaryCSVFileName,"w") 
summaryJSONFile = open(summaryJSONFileName,"w") 
summaryLogFile = open(summaryLogFileName,"w")

#write to the log file to note the start time
summaryLogFile.write('Process Claymore Data Script Started {}\n'.format(datetime.now().strftime("%m/%d/%Y %H-%M-%S")))
summaryLogFile.flush()

#initialize maximumDifficultyOfFoundShare as it is not always present and we need an initial value
maximumDifficultyOfFoundShare = ""

#create our list of files for our CSV file header
fields = [
'hoursMined',
'minutesMined',
'timeStampMonth',
'timeStampDay',
'timeStampHours',
'timeStampMinutes',
'miningServer',
'miningPort',
'miningDurationHours',
'miningDurationMinutes', 
'incorrectShares',
'incorrectSharePercentage',
'estimatedStalesPercentage',
'maximumDifficultyOfFoundShare',
'acceptedShares',
'staleShares',
'rejectedShares',
'rejectedStaleShares',
'averageSpeedMinutes',
'averageMegaHashes',
'effectiveSpeed',
'effectiveSpeedAtPool',
'recordLastModified'
]

#create the header line string
headerString = ','.join(fields)
summaryCSVFile.write('{}\n'.format(headerString))
summaryCSVFile.flush()

summaryJSONFile.write('[\n')
summaryJSONFile.flush()
try:
	#Start the miner program using subprocess in order to capture the output
	p = subprocess.Popen(mining_command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
	while True:
		retcode = p.poll()
		input_line = p.stdout.readline().decode('utf-8')
		sys.stdout.write(input_line)
		
		#get the timestamp from the first line of the summary
		m = re.match("\*+ (\d+):(\d+) \*+ (\d+)/(\d+) (\d+):(\d+).*", input_line)
		if m:
			matches = m.groups()
			timeStamp = {
			"hoursMined" : matches[0],
			"minutesMined" : matches[1],
			"timeStampMonth" : matches[2],
			"timeStampDay" : matches[3],
			"timeStampHours" : matches[4],
			"timeStampMinutes" : matches[5]
			}
			
		#get connection info
		#g='Eth: Mining ETH on us-east.ethash-hub.miningpoolhub.com:20535 for 0:19'
		m = re.match("Eth: Mining ETH on (.*):(\d+) for (\d+):(\d+)", input_line)
		if m:
			matches=m.groups()
			connectionInfo= {
			'miningServer' : matches[0],
			'miningPort' : matches[1],
			'miningDurationHours' : matches[2],
			'miningDurationMinutes' : matches[3]
			}
			#print(connectionInfo)
			
		#get incorrect shares line
		m = re.match("Eth: Incorrect shares (\d+) \((\d+\.\d+)\%\), est. stales percentage (\d+\.\d+)\%", input_line)
		if m:
			matches=m.groups()
			incorrectShares={
			"incorrectShares" : matches[0],
			"incorrectSharePercentage" : matches[1],
			"estimatedStalesPercentage" : matches[2]
			}
			
		#get max difficulty
		m = re.match("Eth: Maximum difficulty of found share: (\d+.\d+) GH \(!\)", input_line)
		if m:
			matches=m.groups()
			maximumDifficultyOfFoundShare = matches[0]

		#get Share count
		m = re.match("Eth: Accepted shares (\d+) \((\d+) stales\), rejected shares (\d+) \((\d+) stales\)", input_line)
		if m:
			matches = m.groups()
			shareCount = {
			"acceptedShares" : matches[0],
			"staleShares" : matches[1],
			"rejectedShares" : matches[2],
			"rejectedStaleShares" : matches[3]
			}
			
		#get average speed
		m = re.match("Eth: Average speed \((\d+) min\): (\d+.\d+) MH/s", input_line)
		if m:
			matches=m.groups()
			averageSpeed = {
			'averageSpeedMinutes' : matches[0],
			'averageMegaHashes' : matches[1]
			}
			
		#get effective speed
		m = re.match("Eth: Effective speed: (\d+.\d+) MH/s; at pool: (\d+.\d+) MH/s", input_line)
		if m:
			matches=m.groups()
			effectiveSpeed = {
			'effectiveSpeed' : matches[0],
			'effectiveSpeedAtPool' : matches[1]
			}
			
			summaryRecord = {
			'timeStamp' : timeStamp,
			'connectionInfo' : connectionInfo,
			'shareCount' : shareCount,
			'incorrectShares' : incorrectShares,
			'maximumDifficultyOfFoundShare' : maximumDifficultyOfFoundShare,
			'averageSpeed' : averageSpeed,
			'effectiveSpeed' : effectiveSpeed
			}
			
			if summary_records_written > 0:
				summaryJSONFile.write(',{}\n'.format(summaryRecord))
				summaryJSONFile.flush()
			else:
				summaryJSONFile.write('{}\n'.format(json.dumps(summaryRecord)))
				summaryJSONFile.flush()
				
			summary_records_written = summary_records_written + 1
			
			values=[
			timeStamp['hoursMined'],
			timeStamp['minutesMined'],
			timeStamp['timeStampMonth'],
			timeStamp['timeStampDay'],
			timeStamp['timeStampHours'],
			timeStamp['timeStampMinutes'],
			connectionInfo['miningServer'],
			connectionInfo['miningPort'],
			connectionInfo['miningDurationHours'],
			connectionInfo['miningDurationMinutes'],
			incorrectShares['incorrectShares'],
			incorrectShares['incorrectSharePercentage'],
			incorrectShares['estimatedStalesPercentage'],
			maximumDifficultyOfFoundShare,
			shareCount['acceptedShares'],
			shareCount['staleShares'],
			shareCount['rejectedShares'],
			shareCount['rejectedStaleShares'],
			averageSpeed['averageSpeedMinutes'],
			averageSpeed['averageMegaHashes'],
			effectiveSpeed['effectiveSpeed'],
			effectiveSpeed['effectiveSpeedAtPool'],
			datetime.now().strftime("%m/%d/%Y %H:%M:%S")
			]
			
			dataString = ','.join(values)
			summaryCSVFile.write('{}\n'.format(dataString))
			summaryCSVFile.flush()
			
		#get GPU Details
		#h='GPU1: 43C 75% 120W'
		m = re.match("GPU(\d+): (\d+)C (\d+)% (\d+)W", input_line)
		if m:
			matches=m.groups()
			gpuDetails={
			'gpuNumber' : matches[0],
			'gpuTemperatureCelcius' : matches[1],
			'gpuPowerPercentage' : matches[2],
			'gpuWattage' : matches[3]
			}

		#get GPU Details
		#j='GPUs power: 119.8 W'
		m = re.match("GPUs power: (\d+.\d+) W", input_line)
		if m:
			matches=m.groups()
			gpuPower={
			'totalGPUsPower' : matches[0]
			}

		#getspeedupdate
		#k='Eth speed: 57.581 MH/s, shares: 17/0/0, time: 1:05'
		m = re.match("Eth speed: (\d+.\d+) MH/s, shares: (\d+)/(\d+)/(\d+), time: (\d+):(\d+)", input_line)
		if m:
			matches=m.groups()
			speedUpdate={
			'ethSpeedMegaHashes' : matches[0],
			'acceptedShares' : matches[1],
			'staleShares' : matches[2],
			'rejectedShares' : matches[3],
			'miningDurationHours' : matches[4],
			'miningDurationMinutes' : matches[5]
			}

		if retcode is not None:
			break

except:	
	p.terminate()
	
#make sure to terminate the process and write close the json array in the output file		
finally:
	summaryJSONFile.write(']\n')
	summaryJSONFile.flush()
	summaryLogFile.write('Process Claymore Data Script Ended {}\n'.format(datetime.now().strftime("%m/%d/%Y %H-%M-%S")))
	summaryLogFile.flush()

