# ----------------------------------------------------------------------------- #
# This script performs basic analysis of a single GPR file - e.g. reporting
# coding, diagnostic plots etc
# ----------------------------------------------------------------------------- # 

seriesanalysis1 <- function(targetsfile, argslidepath, plot1file, plot2file, plot3file, plot4file, text1file, text2file,text3file,text4file) {

   library(limma)                                     

   setwd(argslidepath)

  
   wt.flags <- function(x) {       # Function which gives spots with flag values > = 0 a weighting of 1 and 0 otherwise.
      as.numeric(x$Flags >= 0)      # A weight of 0 means that the BAD spot is multiplied by 0 and so 'disappears'.  
   }                               # A weight of 1 = a GOOD spot. 

   # graphics parameters to be used
   mypointsize = 12



   targets <- readTargets(targetsfile) 
   targets

   
   #print("calling read.maimages...")
   RG <- read.maimages(targets$FileName, source="genepix.median", 
                    wt.fun=wt.flags, other.columns="Flags")    # Reads in the files in dataDir using the median pixel values
                                                               # and weighting the data as defined in the weight function 

   #print("coding names...")
   # add a variable that will be used to code the genes
   RG$genes$old.ID <- RG$genes$ID                                # Make a copy of the original gene IDs
   RG$genes$ID[is.na(RG$genes$ID)] <- "blank"                    # Changes "NA" gene IDs to "blank" so are included in the analyses


   # Create a variable identifying the gene types...
   RG$genes$control.IDs <- RG$genes$ID                            # Create a copy of the gene Name
   RG$genes$control.IDs <- "General"                              # Then rename the gene IDs to be one of the 6 classes of spot found on the chip
   RG$genes$control.IDs[grep("^O.*HT$",RG$genes$ID,ignore.case=TRUE)] <- "Sheep"
   RG$genes$control.IDs[grep("^B.*HT$",RG$genes$ID)] <- "Cattle"
   RG$genes$control.IDs[grep("neg",RG$genes$ID)] <- "Neg"  
   RG$genes$control.IDs[grep("blank",RG$genes$ID,ignore.case=TRUE)] <- "Blank"
   RG$genes$control.IDs[grep("water",RG$genes$ID,ignore.case=TRUE)] <- "Blank"
   RG$genes$control.IDs[grep("h2o",RG$genes$ID,ignore.case=TRUE)] <- "Blank"
   RG$genes$control.IDs[grep("h20",RG$genes$ID,ignore.case=TRUE)] <- "Blank"
   RG$genes$control.IDs[grep("not.est",RG$genes$ID,ignore.case=TRUE)] <- "NotEST"


   # summary
   # Summary of Red and Green foreground and background intensities:
   # Tables of summary statistics

   summary(RG$R)                                        
   summary(RG$Rb)
   summary(RG$G)
   summary(RG$Gb)


   # Plot the RAW values for each gene type...  

   # calculate the grid of plots - it is to be as square as possible
   plotrows=trunc(sqrt(nrow(RG$targets)))
   if(plotrows * plotrows < nrow(RG$targets)) {
      plotcols = plotrows + 1
   } else {
      plotcols = plotrows
   }

   #print("starting png device")
   png(filename =plot1file, width=800, height=600,   pointsize=mypointsize,  bg="transparent")
   oldpar <- par()
   par(mfrow=c(plotrows,plotcols))
   #print("restting margins")
   par(mar=c(7,4,4,2)+0.1,mgp=c(3,1,0))

   slideNames <- rownames(RG$targets) 

   for (i in 1:nrow(RG$targets)) {
      plot(as.data.frame(RG$genes$control.IDs), log2(RG$R[,i]/RG$G[,i]),
        main=slideNames[i],cex.main=0.5, cex.lab=0.5 , cex.axis=0.5, ylab = "log2 ratio for the raw data", las = 2, cex = 0.8, 
        ylim=c(-4.5,4.5))
        abline(h=0)
   }
   par(oldpar)
   dev.off()

   
   # box plots of R and G
   slidesinorder = c(grep("low",slideNames,ignore.case=TRUE),grep("medium",slideNames,ignore.case=TRUE),grep("high",slideNames,ignore.case=TRUE) )
   
   # !!!! need to add this back in when fixed a bug that am not sure about !!!
   #if (is.null(slidesinorder)) {
   #   slidesinorder = 1:nrow(slideNames)
   #} else {
   #   # add in those not included in the above
   #   slidesinorder = c(slidesinorder, subset(slidesinorder, !(slidesinorder %in% 1:nrow(slideNames))))
   #}

   colour <- rep(c("blue","skyblue2", "light blue"),4)            # Set boxplot colours

   png(filename =plot2file, width=800, height=600,   pointsize=mypointsize,  bg="transparent")
   oldpar <- par()
   par(mfrow=c(1,1),mar=c(10,4,4,2)+0.1)                          # Set margins so that the x-axis labels can be entirely seen.  
   boxplot(data.frame(log(RG$R[,slidesinorder])), las = 2, main = "Red foreground", ylab = "log intensity", col = colour)  # Plots images in order given in targets

   par(oldpar)
   dev.off()

   png(filename =plot3file, width=800, height=600,   pointsize=mypointsize,  bg="transparent")
   oldpar <- par()
   par(mfrow=c(1,1),mar=c(10,4,4,2)+0.1)                          # Set margins so that the x-axis labels can be entirely seen.  
   boxplot(data.frame(log(RG$Rb[,slidesinorder])), las = 2, main = "Red background", ylab = "log intensity", col = colour)  # Plots images in order given in targets
   par(oldpar)
   dev.off()

   png(filename =plot4file, width=800, height=600,   pointsize=mypointsize,  bg="transparent")
   oldpar <- par()
   par(mfrow=c(1,1),mar=c(10,4,4,2)+0.1)                          # Set margins so that the x-axis labels can be entirely seen.  
   boxplot(data.frame(log(RG$G[,slidesinorder])), las = 2, main = "Green foreground", ylab = "log intensity", col = colour)  # Plots images in order given in targets
   par(oldpar)
   dev.off()

   png(filename =plot5file, width=800, height=600,   pointsize=mypointsize,  bg="transparent")
   oldpar <- par()
   par(mfrow=c(1,1),mar=c(10,4,4,2)+0.1)                          # Set margins so that the x-axis labels can be entirely seen.  
   boxplot(data.frame(log(RG$Gb[,slidesinorder])), las = 2, main = "Green background", ylab = "log intensity", col = colour)  # Plots images in order given in targets
   par(oldpar)
   dev.off()
}


args=(commandArgs(TRUE))
if(length(args)!=11 ){
   #quit with error message if wrong number of args supplied
   print('Usage example : Rscript --vanilla  argslidename=136-26.low.0.95.gpr  textinput1=/var/www/agbrdf/html/tmp/8062171096134337607  textoutput1=/var/www/agbrdf/html/tmp/1968825465357718355.csv imageoutput1=/var/www/agbrdf/html/tmp/1968825465357718355.png')
   print('args received were : ')
   for (e in args) {
      print(e)
   }
   q()
}else{
   print("Using...")
   # seperate and parse command-line args
   for (e in args) {
      print(e)
      ta <- strsplit(e,"=",fixed=TRUE)
      switch(ta[[1]][1],
         "argslidepath" = argslidepath <- ta[[1]][2],
         "textinput1" = targetsfile <- ta[[1]][2],
         "imageoutput1" = plot1file <- ta[[1]][2],
         "imageoutput2" = plot2file <- ta[[1]][2],
         "imageoutput3" = plot3file <- ta[[1]][2],
         "imageoutput4" = plot4file <- ta[[1]][2],
         "imageoutput5" = plot5file <- ta[[1]][2],
         "textoutput1" = text1file <- ta[[1]][2],
         "textoutput2" = text2file <- ta[[1]][2],
         "textoutput3" = text3file <- ta[[1]][2],
         "textoutput4" = text4file <- ta[[1]][2]
      )
   }
}

#print("calling seriesanalysis")
myresults = seriesanalysis1(targetsfile, argslidepath , plot1file, plot2file, plot3file, plot4file, text1file, text2file,text3file,text4file)
print(myresults)


