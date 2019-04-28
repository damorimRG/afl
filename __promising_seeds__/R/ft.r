#!/usr/bin/env Rscript

args = commandArgs(trailingOnly=TRUE)
if (length(args)==0) {
  stop("Please indicate the title.n", call.=FALSE)
}
title = args[1]
complement = args[2]

numplots=5
linetype <- c(1:numplots)
colors <- rainbow(numplots)
plotchar <- seq(18,18+numplots,1)
names <- c('no-min', 'libfuzzer', 'mosa', 'uwsc', 'wsc-size')

# load the data
list1 = read.csv("ft-nomin.data", header=FALSE, sep=" ")
list2 = read.csv("ft-libfuzzer.data", header=FALSE, sep=" ")
list3 = read.csv("ft-mosa.data", header=FALSE, sep=" ")
list4 = read.csv("ft-uwsc.data", header=FALSE, sep=" ")
list5 = read.csv("ft-wsc-size.data", header=FALSE, sep=" ")

# get the range for the x and y axis
xrange <- range(list1$V1, list2$V1, list3$V1, list4$V1, list5$V1)
yrange <- range(list1$V2, list2$V2, list3$V2, list4$V2, list5$V2)

## setup the plot
plot(xrange, yrange, type="n", xlab="Time", ylab="Ft")

## plot one
lines(list1$V1, list1$V2, type="o", lwd=1.5, lty=linetype[1], col=colors[1], pch=plotchar[1])
lines(list2$V1, list2$V2, type="o", lwd=1.5, lty=linetype[2], col=colors[2], pch=plotchar[2])
lines(list3$V1, list3$V2, type="o", lwd=1.5, lty=linetype[3], col=colors[3], pch=plotchar[3])
lines(list4$V1, list4$V2, type="o", lwd=1.5, lty=linetype[4], col=colors[4], pch=plotchar[4])
lines(list5$V1, list5$V2, type="o", lwd=1.5, lty=linetype[5], col=colors[5], pch=plotchar[5])

# add a legend
par(mar=c(0, 0, 0, 0))
# c(bottom, left, top, right)
# plot.new()
# legend('center','groups',c("A","B","C"), lty = c(1,2,3),
#        col=c('black','black','blue'),ncol=3,bty ="n")
#legend(xrange[1], yrange[2], names, cex=0.9, col=colors,  pch=plotchar, lty=linetype, title="minimization")
#legend('center','groups', names, cex=0.9, col=colors,  pch=plotchar, lty=linetype, title="minimization")
legend('bottomright', names, cex=0.9, col=colors,  pch=plotchar, lty=linetype, title="minimization")

title(paste(title, complement, sep=" "), line = -20)