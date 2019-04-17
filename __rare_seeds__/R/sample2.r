#!/usr/bin/env Rscript

numplots=2
linetype <- c(1:numplots)
colors <- rainbow(numplots)
plotchar <- seq(18,18+numplots,1)

# load the data

list1 = read.csv("file1.data", header=FALSE, sep=",")
list2 = read.csv("file2.data", header=FALSE, sep=",")

# get the range for the x and y axis
xrange <- range(list1$V1, list2$V1)
yrange <- range(list1$V2, list2$V2)

## setup the plot
plot(xrange, yrange, type="n", xlab="Time", ylab="Coverage" )

## plot one
lines(list1$V1, list1$V2, type="b", lwd=1.5, lty=linetype[1], col=colors[1], pch=plotchar[1])
lines(list2$V1, list2$V2, type="b", lwd=1.5, lty=linetype[2], col=colors[2], pch=plotchar[2])
