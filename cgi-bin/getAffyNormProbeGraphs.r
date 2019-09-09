
# Craig has installed xvfb on impala now do this first: "export DISPLAY=localhost:999"
# Ensure you use display number 999 !

# read command line args.
args=(commandArgs(TRUE))

if(length(args)==0 ){
	# quit with error message if no args supplied
	print('Usage: Rscript --vanilla graphs_from_file.r i=<data_filename> o=<image_filename> w=<image_width> h=<image_height> f=<image_format>')
	print(' e.g.  Rscript --vanilla graphs_from_file.r i=CS37003138FFFFB_at.txt o=test.jpg h=1200 w=1200 f=jpeg')
	q()
}else{
	library(lattice) #needed for trellis

	#image defaults
	imagewidth <- 480
	imageheight <- 480
	imageformat <- 'png'
        yscale <- 'linear'
	
	# seperate and parse command-line args
	for (e in args) {
	  ta <- strsplit(e,"=",fixed=TRUE)
	    switch(ta[[1]][1],
	     "i"= inputfilename <- ta[[1]][2],
	     "o" = outputfilename <- ta[[1]][2],
	     "w" = imagewidth <- as.numeric(ta[[1]][2]),
	     "h" = imageheight <- as.numeric(ta[[1]][2]),
	     "f" = imageformat <- ta[[1]][2],
	     "m" = plotname <- ta[[1]][2] ,
	     "n" = norminputfilename <- ta[[1]][2],
             "yscale" = yscale <- ta[[1]][2]
	    )
	}

	# read tab-seperated data file 
	stacked.data.pm <- read.delim(inputfilename)                      # raw values
	stacked.data.pm.normalized <- read.delim(norminputfilename)       # normalised values

        # make plotFrame , a frame containing both raw and normalised values. The Slide and probe number vectors are doubled in 
        # length, and the raw and normalised vectors are concatenated, resulting in a combined data frame with double the 
        # number of rows as the raw/normalised frames.
        if(yscale == "log") {
           plotFrame=data.frame(Slide=rep(stacked.data.pm$Slide,2), probe.number=rep(stacked.data.pm$probe.number,2)  , all.intensity=c(log(stacked.data.pm$pm.intensity),log(stacked.data.pm.normalized$pm.intensity)))
        }
        else {
           plotFrame=data.frame(Slide=rep(stacked.data.pm$Slide,2), probe.number=rep(stacked.data.pm$probe.number,2)  , all.intensity=c(stacked.data.pm$pm.intensity,stacked.data.pm.normalized$pm.intensity))
        }
           


        #stacked.data.pm.norm <- rbind(stacked.data.pm, stacked.data.pm.normalized)      # using rbind to paste the normalized rows of data below the raw data
        n.slides <- 30                                                                  # used in code below to determine how many probes in each panel of the graph, so that can colour the first x (= raw data) one colour, 
                                                                                # and the next x the next colour.  Note that with xyplot, the colours get set for each panel independently.

	# set up the output file
	trellis.device(
			imageformat, 
			file = outputfilename,
			width = imagewidth,
			height = imageheight
			)

	# print the image
	print(
		xyplot(
#			pm.intensity ~ probe.number|Slide,
#			data = stacked.data.pm.norm, 
			all.intensity ~ probe.number|Slide,
			data = plotFrame, 
      type = "p",
      pch = 20,
			xlab = "Probe number", 
			ylab = c("Probe intensity (B=raw R=normalised)",yscale) , 
#			main = stacked.data.pm$pN,
			main = plotname,
			par.strip.text=list(cex=0.5),
			col = c(rep("black",nrow(plotFrame)/(n.slides * 2)), rep("red",nrow(plotFrame)/(n.slides * 2))), 
			)
		)

	dev.off()

	# cleanup
	rm(list=ls(all=TRUE))
}
