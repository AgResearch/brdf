
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
	
	# seperate and parse command-line args
	for (e in args) {
	  ta <- strsplit(e,"=",fixed=TRUE)
	    switch(ta[[1]][1],
	     "i"= inputfilename <- ta[[1]][2],
	     "o" = outputfilename <- ta[[1]][2],
	     "w" = imagewidth <- as.numeric(ta[[1]][2]),
	     "h" = imageheight <- as.numeric(ta[[1]][2]),
	     "f" = imageformat <- ta[[1]][2],
	     "m" = plotname <- ta[[1]][2],
             "mm" = includemm <- ta[[1]][2]
	    )
	}

	# read tab-seperated data file
	stacked.data.pm <- read.delim(inputfilename)

        n.slides <- 4 # !!! todo : this needs to be obtained from the data 


	# set up the output file
	trellis.device(
			imageformat, 
			file = outputfilename,
			width = imagewidth,
			height = imageheight
			)

        # make a data frame for plotting, depending on what is wanted
        colour1 = "blue"
        colour2 = "blue"
        if (includemm == "True") {
           # include mismatch values
           plotFrame=data.frame(Slide=rep(stacked.data.pm$Slide,2), probe.number=rep(stacked.data.pm$probe.number,2)  , all.intensity=c(stacked.data.pm$pm.intensity,stacked.data.pm$mm.intensity))
           colour2 = "red"
        }
        else {
           plotFrame=data.frame(Slide=stacked.data.pm$Slide, probe.number=stacked.data.pm$probe.number , all.intensity=stacked.data.pm$pm.intensity)
        }



	# print the image
	print(
		xyplot(
#			#pm.intensity ~ probe.number|Slide,
			all.intensity ~ probe.number|Slide,
#			data = stacked.data.pm, 
			data = plotFrame, 
	                type = "p",
                  	pch = 20,
			xlab = "Probe number", 
			ylab = "Probe intensity (B=pm R=mm)", 
#			main = stacked.data.pm$pN,
			main = plotname,
			par.strip.text=list(cex=0.5),
                        col = c(rep(colour1,nrow(plotFrame)/(n.slides * 2)), rep(colour2,nrow(plotFrame)/(n.slides * 2)))
			)
		)

	dev.off()

	# cleanup
	rm(list=ls(all=TRUE))
}
