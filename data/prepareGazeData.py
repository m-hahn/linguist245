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
     #print ' -- '.join(row)
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

if False:
 criticalStimuli = {}
 with open("stimuli.csv") as stimulusFile:
  stimuli = stimulusFile.read().split("\n")
  critical = stimuli[stimuli.index("CRITICAL")+1:]
  for line in critical:
    line = line.split("\t")
    if len(line) < 2:
      continue
    assert(not(line[6] in criticalStimuli))
    criticalStimuli[line[6]] = line

 print(criticalStimuli)

csv_files = filter(lambda x:x.endswith(".gazedata"), os.listdir("."))
#   ["FixedPositionAOI-1-1.gazedata","FixedPositionAOI-2-1.gazedata"]
results = []
for csvName in csv_files:
   results += readCSVIntoDictList(csvName,"\t")
position = 0
trialIDs = map(lambda x:x["BackColor"], results)

print("\t".join(map(str,['targetFix','distractorFix','othersFix','startOfBin','trialID','target','distractor','sound','absoluteTime', 'Critical.Or.Not'])))


while True:
  currentTrial = trialIDs[position]
  reactionTime = results[position]["RT"]
  auditory = results[position]["Prime"]
  image1 = results[position]["AOI1"]
  image2 = results[position]["AOI2"]
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
  with open("ZOOM2trimmedPost/trimmedZOOM2"+soundFile+"-marked.TextGrid", "r") as soundFileStream:
    soundFileStream = soundFileStream.read().split("\n")
    if "C" in currentTrial:
      i1 = soundFileStream.index("        intervals [2]:")
      i2 = soundFileStream.index("        intervals [3]:")
      assert i1 < i2
      assert "xmax" in soundFileStream[i1+2]
      onsetInSoundFile = float(soundFileStream[i1+2].split(" = ")[1])
  onsetTime = float(trialData[0]["TETTime"]) + onsetInSoundFile * 1000
#  print(float(trialData[0]["TETTime"]))
#  print(onsetInSoundFile)
#  print(onsetTime)
#  position = firstOtherIndex
#  continue

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
#          currentBin[int(row["AOI"])-1] += 1
  time = 0
  for fixBin in fixationsPerBin:
    print("\t".join(map(str,[fixBin['target'],fixBin['distractor'],fixBin['others'],time,currentTrial, trialData[0]["Target"], trialData[0]["Distractor"],  soundFile ,onsetTime + time, currentTrial[0]  ])))
    time += BIN_LENGTH
 # print(fixationsPerBin)
#  print(len(fixationsPerBin))
  position = firstOtherIndex
  



