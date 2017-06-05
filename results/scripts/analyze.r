library(ggplot2)


# TODO saccades instead of fixations

data = read.table("pilot-data-2.csv",header=TRUE,sep="\t")
 dataC = data[data$Critical.Or.Not == "C",]

dataC$totalFix = dataC$targetFix + dataC$distractorFix + dataC$othersFix

dataC$targetProportion = dataC$targetFix / dataC$totalFix
dataC$distractorProportion = dataC$distractorFix / dataC$totalFix
dataC$othersProportion = dataC$othersFix / dataC$totalFix


dataC = dataC[dataC$startOfBin < 400,]


averagedTarget = aggregate(dataC[,12], list(dataC$startOfBin), mean, na.rm=TRUE)
averagedDistractor = aggregate(dataC[,13], list(dataC$startOfBin), mean, na.rm=TRUE)
averagedOthers = aggregate(dataC[,14], list(dataC$startOfBin), mean, na.rm=TRUE)

# pdf('fixations-plot.pdf')
ggplot(averagedTarget, aes(Group.1,x, color="Target")) +
  geom_point() +
  geom_point(data = averagedDistractor, aes(Group.1,x, color="Competitor")) +
  geom_point(data = averagedOthers, aes(Group.1,x, color="Distractors")) +
  xlab("Time after Onset") +
  ylab("Fixations")
#dev.off()



sumTarget = aggregate(dataC[,12], list(dataC$startOfBin), sum, na.rm=TRUE)
sumDistractor = aggregate(dataC[,13], list(dataC$startOfBin), sum, na.rm=TRUE)

library(zoo)
targetMoving = rollsum(sumTarget$x, 4)
distractorMoving = rollsum(sumDistractor$x, 4)
totalMoving = targetMoving + distractorMoving

chiSquare = (targetMoving - (0.5 * totalMoving))^2 / (0.5 * totalMoving)

timeMoving = rollmax(sumTarget$Group.1,4)

#pdf('chi-squared-result.pdf')
plot(timeMoving, chiSquare, xlab="Time after Onset", ylab="Chi-Squared Statistic")
#dev.off()
