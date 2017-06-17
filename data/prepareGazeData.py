# Script for downsampling output of E-Prime/Tobii gaze file

# specify the names of the gaze data files
csv_files = ["FixedPositionAOI-10-1.gazedata", "FixedPositionAOI-8-1.gazedata"]

# The file expects Praat annotation for the acoustic stimuli in acoustic/, so it can
# align the beginning of the downsampled output with the onset of the initial consonant.

import csv
import os

def makeSureKeyExists(table,key,value):
   if(not(key in table)):
     table[key] = value

IGNORE_ROWS = 0

def readCSVIntoDictList(fileName,delimiter):
 csvfile = open(fileName, 'rb')
 resultsfile = csv.reader(csvfile, delimiter=delimiter, quotechar='|')
 results = []
 keylist = []
 counter = 0
 for row in resultsfile:
     if counter == 0:
        keylist = row
     elif counter > IGNORE_ROWS:
        dictForItem = {}
        results.append(dictForItem)
        for i in range(0,len(row)):
           assert(i < len(keylist))
           dictForItem[keylist[i]] = row[i]

     counter += 1
 return results


results = []
for csvName in csv_files:
   results += readCSVIntoDictList(csvName,"\t")
position = 0
trialIDs = map(lambda x:x["BackColor"], results)

print("\t".join(map(str,['targetFix','distractorFix','othersFix','startOfBin','trialID','target','distractor','sound','absoluteTime', 'Critical.Or.Not','Participant'])))


while True:
  currentTrial = trialIDs[position]
  reactionTime = results[position]["RT"]
  auditory = results[position]["Prime"]
  image1 = results[position]["AOI1"]
  image2 = results[position]["AOI2"]
  participant = results[position]["Subject"]
  firstOtherIndex = position
  firstStimulusIndex = -1
  for k in range(position,len(results)):
    if firstStimulusIndex < 0 and results[k]["CurrentObject"] == "Stimulus":
      firstStimulusIndex = k
    if trialIDs[k] != currentTrial:
       firstOtherIndex = k
       break
  trialData = results[firstStimulusIndex:firstOtherIndex]

  if len(trialData) == 0:
     break

  soundFile = trialData[0]["Sound"]

  onsetInSoundFile = 0
  with open("acoustic/sound-"+soundFile+"-marked.TextGrid", "r") as soundFileStream:
    soundFileStream = soundFileStream.read().split("\n")
    if "C" in currentTrial:
      i1 = soundFileStream.index("        intervals [2]:")
      i2 = soundFileStream.index("        intervals [3]:")
      assert i1 < i2
      assert "xmax" in soundFileStream[i1+2]
      onsetInSoundFile = float(soundFileStream[i1+2].split(" = ")[1])
  onsetTime = float(trialData[0]["TETTime"]) + onsetInSoundFile * 1000
  fixationsPerBin = []
  BIN_LENGTH = 10
  currentStart = onsetTime
  currentBin = {'target' : 0, 'distractor' : 0, 'others' : 0}
  for row in trialData:
    if float(row["TETTime"]) >= currentStart + BIN_LENGTH:
      fixationsPerBin.append(currentBin)
      currentStart = currentStart + BIN_LENGTH
      currentBin = {'target' : 0, 'distractor' : 0, 'others' : 0}
    if float(row["TETTime"]) >= currentStart: # jump over datapoints before onset
      if row["AOI"] != "" and row["AOI"] != "Fixation":
          if row["AOIStimulus"] == row["Target"]:
             currentBin['target'] += 1
          elif row["AOIStimulus"] == row["Distractor"]:
             currentBin['distractor'] += 1
          else:
             currentBin['others'] += 1
  time = 0
  for fixBin in fixationsPerBin:
    print("\t".join(map(str,[fixBin['target'],fixBin['distractor'],fixBin['others'],time,currentTrial, trialData[0]["Target"], trialData[0]["Distractor"],  soundFile ,onsetTime + time, currentTrial[0], participant  ])))
    time += BIN_LENGTH
  position = firstOtherIndex
  



