library(ggplot2)
library(lme4)
library(zoo)


# Read the critical trials
dataC = read.table("../../data/pilot-downsampled.csv",header=TRUE,sep="\t")
dataC = dataC[dataC$Critical.Or.Not == "C",]
dataC = dataC[dataC$startOfBin < 800,]


#######################################################################

# Logistic model predicting target fixations over time

# aggregate, for each trial and each bin, whether there was a target fixation
fixationsOverTime = aggregate(dataC["targetFix"], by=c(dataC["startOfBin"],dataC["Participant"], dataC["trialID"]), sum, na.rm=TRUE)
fixationsOverTime$hasTargetFix = sign(fixationsOverTime$targetFix)

# center and rescale predictors
fixationsOverTime$startOfBin = fixationsOverTime$startOfBin / 800
fixationsOverTime$startOfBin = fixationsOverTime$startOfBin - mean(fixationsOverTime$startOfBin)
fixationsOverTime$Participant = fixationsOverTime$Participant - mean(fixationsOverTime$Participant)

# fit logistic mixed-effects model
model = glmer(formula = hasTargetFix ~ startOfBin * Participant   + (1|trialID), family = binomial("logit"), data=fixationsOverTime)



##############################################################################

# Logistic model comparing three early time windows

# Restrict to early data
dataC = dataC[dataC$startOfBin < 300,]

# Helmert coding of time windows
dataC$contrast1 = -2/3 * (dataC$startOfBin < 100) + 1/3 * (dataC$startOfBin >= 100)
dataC$contrast2 = -1/2 * (dataC$startOfBin >= 100 & dataC$startOfBin < 200) + 1/2 * (dataC$startOfBin >= 200 & dataC$startOfBin < 300)

# for each trial and each window, aggregate whether there was a target fixation
fixationsPerWindows = aggregate(dataC["targetFix"], by=c(dataC["contrast1"], dataC["contrast2"],  dataC["Participant"], dataC["trialID"]), sum, na.rm=TRUE)
fixationsPerWindows$hasTargetFix = sign(fixationsPerWindows$targetFix)

# fit logistic mixed-effects model
model = glmer(formula = hasTargetFix ~ contrast1 + contrast2    + (1|trialID), family = binomial("logit"), data=fixationsPerWindows)




##############################################################################

# Plot fraction of trials with fixations to the different regions over time

dataC = read.table("../../data/pilot-downsampled.csv",header=TRUE,sep="\t")
dataC = dataC[dataC$Critical.Or.Not == "C",]
dataC = dataC[dataC$startOfBin < 800,]

# for each trial and each bin, record whether there was a target fixation, competitor fixation, or distractor fixation
dataC$totalFix = dataC$targetFix + dataC$distractorFix + dataC$othersFix

dataC$targetProportion = sign(dataC$targetFix)
dataC$distractorProportion = sign(dataC$distractorFix)
dataC$othersProportion = sign(dataC$othersFix)

# aggregate over all trials
averagedTarget = aggregate(dataC["targetProportion"], by=c(dataC["startOfBin"]), mean, na.rm=TRUE)
averagedDistractor = aggregate(dataC["distractorProportion"], by=c(dataC["startOfBin"]), mean, na.rm=TRUE)
averagedOthers = aggregate(dataC["othersProportion"], by=c(dataC["startOfBin"]), mean, na.rm=TRUE)


ggplot(averagedTarget, aes(Group.1,x, color="Target")) +
  geom_point() +
  geom_point(data = averagedDistractor, aes(Group.1,x, color="Competitor")) +
  geom_point(data = averagedOthers, aes(Group.1,x, color="Distractors")) +
  xlab("Time after Onset") +
  ylab("Fixations")



########################################

# Plot chi-squared statistic over moving windows

dataC$targetProportion = sign(dataC$targetFix)
dataC$distractorProportion = sign(dataC$distractorFix)
dataC$othersProportion = sign(dataC$othersFix)

sumTarget = aggregate(dataC["targetProportion"], by=c(dataC["startOfBin"]), sum, na.rm=TRUE)
sumDistractor = aggregate(dataC["distractorProportion"], by=c(dataC["startOfBin"]), sum, na.rm=TRUE)

# aggregate over moving windows of length 40ms
targetMoving = rollmean(sumTarget$targetProportion, 4)
distractorMoving = rollmean(sumDistractor$distractorProportion, 4)
totalMoving = targetMoving + distractorMoving

# Chi-Square statistic. The null hypothesis is that fixations to targets and competitors are equally likely.
chiSquare = (targetMoving - (0.5 * totalMoving))^2 / (0.5 * totalMoving)

timeMoving = rollmax(sumTarget$startOfBin,4)

plot(timeMoving, chiSquare, xlab="Time after Onset", ylab="Chi-Squared Statistic")



##############################################################################

