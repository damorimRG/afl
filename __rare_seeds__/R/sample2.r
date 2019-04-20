#!/usr/bin/env Rscript

numplots=3
linetype <- c(1:numplots)
colors <- rainbow(numplots)
plotchar <- seq(18,18+numplots,1)
names <- c('cmin','multi objective','no min.')

# load the data

list1 = read.csv("file-cmin.data", header=FALSE, sep=",")
list2 = read.csv("file-mobj.data", header=FALSE, sep=",")
list3 = read.csv("file-nomin.data", header=FALSE, sep=",")

# get the range for the x and y axis
xrange <- range(list1$V1, list2$V1, list3$V1)
yrange <- range(list1$V2, list2$V2, list3$V2)

## setup the plot
plot(xrange, yrange, type="n", xlab="Time", ylab="Coverage" )

## plot one
lines(list1$V1, list1$V2, type="b", lwd=1.5, lty=linetype[1], col=colors[1], pch=plotchar[1])
lines(list2$V1, list2$V2, type="b", lwd=1.5, lty=linetype[2], col=colors[2], pch=plotchar[2])
lines(list3$V1, list3$V2, type="b", lwd=1.5, lty=linetype[3], col=colors[3], pch=plotchar[3])

# add a legend
legend(xrange[1], yrange[2], names, cex=0.9, col=colors,
   pch=plotchar, lty=linetype, title="minimization")