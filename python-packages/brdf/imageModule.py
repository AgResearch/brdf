#
# This module is used to generate various images on the fly for
# the . It depends on the Python image library - see
# http://effbot.org/downloads/#imaging
#
from types import *
from PIL import Image, ImageDraw, ImageFont, ImageOps, ImageEnhance, PSDraw
import os
import os.path
import logging
import globalConf
import math
from random import randint


imagemodulelogger = logging.getLogger('imagemodulelogger')
#hdlr = logging.FileHandler('c:/temp/nutrigenomicsforms.log')
imagemodulehdlr = logging.FileHandler(os.path.join(globalConf.LOGPATH,'imagemodule.log'))
formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
imagemodulehdlr.setFormatter(formatter)
imagemodulelogger.addHandler(imagemodulehdlr) 
imagemodulelogger.setLevel(logging.INFO)


featureColourKey = {
    'gene': (150,0,0),
    'exon': (0,150,0),
    'cds':(150,150,150),
    'referencecolour' : (255,0,0),
    'backgroundcolour' : (0,255,0),
    'defaultfeaturecolour' : (0,255,0)
    }



def makeOpGlyph(linkText, imageDirectory, obs,instanceCount,linkFirstObject=False, namedInstances = True):
    """ this method makes the glyphs used to display "ops" - i.e. relations between two or more objects in the
    database. These glyphs are optionally filled circles - filled if there is an instance of the operation.
    linkText - the description of the relation as a whole
    imageDirectory - path to image directory where the glyph will be written
    obs - a tuple of tuples. Each tuple is a triple describing an object in the
       relation : (Display Name, instanceCount, imagefile)
       if displayName is None, then the glyph will be that of a fact relation
       if instanceCount is 0 then this object is missing in the relation and an empty circle will be
       drawn
    instanceCount - this is the number of instances of the relation as a whole. If there are none then
    the glyph is drawn in grey to indicate an uninstantiated relation

    There are a finite number of glyphs and we do not want to create a glyph if it has previously
    been created. The image directory is first searched for a file with a name that is the
    same as a hash of the descriptor we have been given.
    """
    # this constant can be used to force new hashed filenames and hence image updates
    hashConstant = '7'

    # check if we have already created a glyph for this descriptor.
    fileExists = False
    filename = str(abs(hash(linkText + imageDirectory + str(obs) + str(instanceCount) + str(namedInstances) + hashConstant))) + ".gif"
    filepath = os.path.join(imageDirectory,  filename ) 
    if os.path.exists(filepath) :
        fileExists = True
    

    # set up graphics and basic sizing
    font = ImageFont.load_default()
    #im = Image.new("P", (600,45), 500)
    #im = Image.new("P", (800,45), 500)
    if len(obs) <= 2:
        #im = Image.new("P", (380,45), 500)
        im = Image.new("RGB", (380,45), (255,255,255))        
    else:
        #im = Image.new("P", (160 + 90 * len(obs) ,45),500)
        im = Image.new("RGB", (160 + 90 * len(obs) ,45),(255,255,255))


    iconsize=32
    iconcursor=(0,0)

        

    draw = ImageDraw.Draw(im)
    circleDelta = 4
    borderDelta = 8
    smallSquareDelta=(15,10)
    smallTriangleDelta=4

    instanceColour = (100,0,100)
    typeColour = (128,128,128)
    testColour = (180,0,0)
    white = (255,255,255)
    offwhite = (200,200,200)
    
    #outerCircle = (6,6,24,24)
    outerCircle = (46,6,64,24)
    outerCircleDiameter=outerCircle[2]-outerCircle[0]
    innerCircle = map(lambda x,y:x+y,outerCircle,(circleDelta,circleDelta,-1*circleDelta,-1*circleDelta))    
    lineLength = 105


    if instanceCount > 0:
        drawColour = instanceColour
    elif instanceCount == None:
        drawColour = testColour
    else:
        drawColour = typeColour            


    
    targetCount = 0
    exampleimagemap =  """
      <map name="obtypelink" id="obtypelink">
      <area href="__link%s__"
      shape="circle"
      coords="%s,%s"
      alt="Describe this object"/>
      </map>"""
    imagemap =  """
      <map name="%s" id="%s">"""
    

    for target in obs:


        if targetCount == 0:
            # draw the first object - there must be at least one
            targetCount += 1



            #draw.ellipse(outerCircle,outline=drawColour)
            #if target[1] > 0 and instanceCount > 0:
            #    draw.ellipse(innerCircle,outline=128,fill=instanceColour)

            #open its image file , resize, draw
            iconfp = open(target[2],"rb")
            iconimin = Image.open(iconfp)
            if instanceCount == 0:
                iconimin = ImageEnhance.Brightness(ImageEnhance.Contrast(ImageOps.grayscale(iconimin)).enhance(.8)).enhance(.8)
            iconimin=iconimin.resize((iconsize,iconsize))
            im.paste(iconimin,iconcursor)
            iconfp.close()            

        
            if linkFirstObject:
                #imagemap += """
                #<area href="__link%s__"
                #shape="circle"
                #coords="%s,%s,%s"
                #alt="Link to related information"/>
                #"""%( targetCount, (outerCircle[0] + outerCircle[2])/2, (outerCircle[1] + outerCircle[3])/2, outerCircleDiameter/2)
                imagemap += """
                <area href="__link%s__"
                shape="rect"
                coords="%s,%s,%s,%s"
                alt="Link to related information"/>
                """%( targetCount, iconcursor[0],iconcursor[1],iconcursor[0] + iconsize,iconcursor[1] + iconsize)
                


            # print the object type text.
            # the start point is , from the middle of the outer circle, left by
            # half the text length, and down by borderDelta
            textSize = font.getsize(target[0])
            #draw.text((outerCircle[0] + outerCircleDiameter/2 - textSize[0]/2,outerCircle[3] + borderDelta),target[0],fill=drawColour,font=font)
            draw.text((iconcursor[0],iconcursor[1]+iconsize),target[0],fill=drawColour,font=font)
            
            # if there is only one target this is a fact table so we now draw the line
            if len(obs) == 1:
                #draw.line((outerCircle[2],(outerCircle[1] + outerCircle[3])/2 \
                #  , outerCircle[2] + lineLength, (outerCircle[1] + outerCircle[3])/2) \
                #  ,fill=drawColour)
                draw.line((iconcursor[0]+iconsize, iconcursor[1] + iconsize/2 \
                  , iconcursor[0]+iconsize + lineLength, iconcursor[1] + iconsize/2) \
                  ,fill=drawColour)
                

                # finish the line with a box
                #draw.rectangle((outerCircle[2] + lineLength - smallSquareDelta[0], \
                #          (outerCircle[1] + outerCircle[3])/2 - smallSquareDelta[1], \
                #          outerCircle[2] + lineLength + smallSquareDelta[0],  \
                #          (outerCircle[1] + outerCircle[3])/2 + smallSquareDelta[1]),fill=drawColour)
                draw.rectangle((iconcursor[0]+iconsize + lineLength - smallSquareDelta[0], \
                          iconcursor[1] + iconsize/2 - smallSquareDelta[1], \
                          iconcursor[0]+iconsize + lineLength + smallSquareDelta[0],  \
                          iconcursor[1] + iconsize/2 + smallSquareDelta[1]),fill=drawColour)
                # draw a small "info" for info
                if instanceCount > 0:
                    infoColour = white
                else:
                    infoColour = offwhite
                textSize = font.getsize("info")
                #draw.text((outerCircle[2] + lineLength - smallSquareDelta[0] + borderDelta/2,\
                #               (outerCircle[1] + outerCircle[3])/2 - textSize[1]/2),"info",fill=infoColour,font=font)
                draw.text((iconcursor[0]+iconsize + lineLength - smallSquareDelta[0] + borderDelta/2,\
                               iconcursor[1] + iconsize/2 - textSize[1]/2),"info",fill=infoColour,font=font)
                         
                          
                targetCount += 1

                #imagemap += """
                #   <area href="__link%s__"
                #   shape="rect"
                #   coords="%s,%s,%s,%s"
                #   alt="Link to related information"/>
                #   """%( targetCount, outerCircle[2], (outerCircle[1] + outerCircle[3])/2 - circleDelta ,outerCircle[2] + lineLength + smallSquareDelta[0], (outerCircle[1] + outerCircle[3])/2 + circleDelta)
                imagemap += """
                   <area href="__link%s__"
                   shape="rect"
                   coords="%s,%s,%s,%s"
                   alt="Link to related information"/>
                   """%( targetCount, iconcursor[0]+iconsize + lineLength - smallSquareDelta[0], \
                          iconcursor[1] + iconsize/2 - smallSquareDelta[1], \
                          iconcursor[0]+iconsize + lineLength + smallSquareDelta[0],  \
                          iconcursor[1] + iconsize/2 + smallSquareDelta[1])                
                
                

                # update the circle, just so the text gets put in the correct place
                #outerCircle = (outerCircle[2] + lineLength ,outerCircle[1],\
                #     outerCircle[2] + lineLength  + outerCircleDiameter, \
                #      outerCircle[3])                     
                iconcursor = (iconcursor[0]+lineLength,iconcursor[1])
        else:                
            
            # draw a line from the edge of the circle pointing right.
            #draw.line((outerCircle[2],(outerCircle[1] + outerCircle[3])/2 \
            #      , outerCircle[2] + lineLength, (outerCircle[1] + outerCircle[3])/2) \
            #      ,fill=drawColour)
            # draw a line from the edge of the icon pointing right.
            draw.line((iconcursor[0]+iconsize,iconcursor[1] + iconsize/2 \
                  , iconcursor[0]+iconsize + lineLength, iconcursor[1] + iconsize/2) \
                  ,fill=drawColour)            
            

            # if we have a non-null instance count draw the outer circle which represents the type

            if instanceCount != None:

                #outerCircle = (outerCircle[2] + lineLength ,outerCircle[1],\
                #         outerCircle[2] + lineLength  + outerCircleDiameter, \
                #          outerCircle[3])
                iconcursor = (iconcursor[0]+lineLength,iconcursor[1])
                

            
                #draw.ellipse(outerCircle,outline=drawColour,fill=(255,255,255))
                #open its image file , resize, draw
                iconfp = open(target[2],"rb")
                iconimin = Image.open(iconfp)
                if instanceCount == 0:
                    iconimin = ImageEnhance.Brightness(ImageEnhance.Contrast(ImageOps.grayscale(iconimin)).enhance(.8)).enhance(.8)
                iconimin=iconimin.resize((iconsize,iconsize))
                im.paste(iconimin,iconcursor)
                iconfp.close()                         
                

                # if there is an instance then draw the inner circle
                if target[1] > 0 and instanceCount > 0:
                    #innerCircle = map(lambda x,y:x+y,outerCircle,(circleDelta,circleDelta,-1*circleDelta,-1*circleDelta))
                    #draw.ellipse(innerCircle,outline=drawColour,fill=drawColour)

                    #imagemap += """
                    #<area href="__link%s__"
                    #shape="circle"
                    #coords="%s,%s,%s"
                    #alt="Link to related database object(s)"/>
                    #"""%( 1+targetCount, (outerCircle[0] + outerCircle[2])/2, (outerCircle[1] + outerCircle[3])/2, outerCircleDiameter/2)


                    imagemap += """
                    <area href="__link%s__"
                    shape="rect"
                    coords="%s,%s,%s,%s"
                    alt="Link to related database object(s)"/>
                    """%( 1+ targetCount, iconcursor[0],iconcursor[1],iconcursor[0] + iconsize,iconcursor[1] + iconsize)                
                    

                # print the object type text.
                # the start point is , from the middle of the outer circle, left by
                # half the text length, and down by borderDelta
                textSize = font.getsize(target[0])
                #draw.text((outerCircle[0] + outerCircleDiameter/2 - textSize[0]/2,outerCircle[3] + borderDelta),target[0],fill=drawColour,font=font)
                draw.text((iconcursor[0],iconcursor[1]+iconsize),target[0],fill=drawColour,font=font)
        

                targetCount += 1
            else:  # we have a null instance count - this is a dynamic link, we draw a triangle
                # note that this section needs updating to use the new icons - there are currently
                # not dynamic links set up
                outerCircle = (outerCircle[2] + lineLength ,outerCircle[1],\
                         outerCircle[2] + lineLength  + outerCircleDiameter, \
                          outerCircle[3])

                draw.polygon((outerCircle[0],(outerCircle[1]+outerCircle[3])/2-smallTriangleDelta,\
                             outerCircle[0],(outerCircle[1]+outerCircle[3])/2+smallTriangleDelta,\
                             outerCircle[0] + smallTriangleDelta,(outerCircle[1]+outerCircle[3])/2),\
                             outline=drawColour,fill=drawColour)
                             
                             
                #draw.ellipse(outerCircle,outline=drawColour,fill=(255,255,255))


           
                #imagemap += """
                #<area href="__link%s__"
                #shape="rect"
                #coords="%s,%s,%s,%s"
                #alt="Link to related information (dynamic)"/>
                
                imagemap += """
                <area href="zz_contents.htm"
                shape="rect"
                coords="%s,%s,%s,%s"
                alt="Link to related information (dynamic) *** not currently supported *** "/>
                """%(outerCircle[0]-lineLength+outerCircleDiameter/2, (outerCircle[1] + outerCircle[3])/2 - smallSquareDelta[1] ,outerCircle[0] + smallTriangleDelta, (outerCircle[1] + outerCircle[3])/2 + smallSquareDelta[1])                

                # print the object type text.
                # the start point is , from the middle of the outer circle, left by
                # half the text length, and down by borderDelta
                textSize = font.getsize(target[0])
                #draw.text((outerCircle[0] + outerCircleDiameter/2 - textSize[0]/2,outerCircle[3] + borderDelta),target[0],fill=drawColour,font=font)
                draw.text((iconcursor[0],iconcursor[1]+iconsize),target[0],fill=drawColour,font=font)

                # if there a named instances of this relation then we underline the text to make it
                # look like a hyperlink, and add an additional area to the image-map
                
                
        

                targetCount += 1                
                


    # start point for link text is past the end of the last circle
    # just above the midpoint
    textSize = font.getsize(linkText)
    textDelta = textSize[1]/2
    #draw.text((outerCircle[2] + 5*textDelta,(outerCircle[1] + outerCircle[3])/2 - textDelta),linkText,fill=128,font=font)
    #draw.text((outerCircle[2] + 5*textDelta,(outerCircle[1] + outerCircle[3])/2 - textDelta),linkText,fill=drawColour,font=font)
    draw.text((iconcursor[0]+iconsize + 5*textDelta,iconcursor[1] + iconsize/2 - textDelta),linkText,fill=drawColour,font=font)


    # if there are named instances of this relation , and it is binary or greater then we underline the text to make it
    # look like a hyperlink
    if namedInstances and len(obs) > 1:
        draw.line((iconcursor[0]+iconsize + 5*textDelta,\
                iconcursor[1] + iconsize/2 - textDelta + textSize[1] ,\
                iconcursor[0]+iconsize + 5*textDelta + textSize[0],
                iconcursor[1] + iconsize/2 - textDelta + textSize[1]),
                fill=drawColour)
        imagemap += """
                    <area href="__link%s__"
                    shape="rect"
                    coords="%s,%s,%s,%s"
                    alt="Link to related database object(s)"/>
                """%( 1+ targetCount, \
                      iconcursor[0]+iconsize + 5*textDelta,\
                      iconcursor[1] + iconsize/2 - textDelta,\
                      iconcursor[0]+iconsize + 5*textDelta + textSize[0],
                      iconcursor[1] + iconsize/2 - textDelta + textSize[1])                
        


    # write to file if does not exist
    if not fileExists:
        fp = file(filepath,"wb")
        im.save(fp, "GIF")
        fp.close()

    # complete the imagemap
    imagemap +=  """
    </map>"""
    imagemap = imagemap%(filename.split('.')[0],filename.split('.')[0])
    if instanceCount ==0:
        imagemap = ""

    # return a tuple of the filename of the image ,plus an image map
    
    return (filename,imagemap)


def makeBarGraph(imageDirectory,datatuples,currenttuple=None,drawColour=(240,120,240),label1="",label2="",barwidth=3,colourScheme=None):
    """ this method makes a small bar graph icon to graphically present a vector of numbers
    Rach tuple has the format
    (x,elementmouseover,elementlink[,bar label])
    """

    imagemodulelogger.info("makeBarGraph called for %s"%str(datatuples))

    # check if we have already created a glyph for this descriptor.
    fileExists = False
    if currenttuple != None:
        filename = str(abs(hash(str(datatuples) + '1' + label1 + label2 + str(drawColour) + str(currenttuple) + str(colourScheme)))) + ".gif"
    else:
        filename = str(abs(hash(str(datatuples) + '1' + label1 + label2 + str(drawColour) + str(colourScheme)))) + ".gif"
        
    filepath = os.path.join(imageDirectory,  filename ) 
    if os.path.exists(filepath) :
        fileExists = True
    

    # set up graphics and basic sizing
    font = ImageFont.load_default()
    #barwidth=8
    bargap=3
    barheight=80
    textdelta=3


    # if the tuples have length 4 then we will need to label each bar. Calculate
    # bar width as the length of the longest label
    if len(datatuples[0]) >= 4:
        for datatuple in datatuples:
            if font.getsize("%s "%datatuple[3])[0] > barwidth:
                barwidth = font.getsize("%s "%datatuple[3])[0]
    labelwidth = font.getsize(label1)[0] + font.getsize(label2)[0]

    im = Image.new("RGB", (labelwidth + (barwidth + bargap)* len(datatuples) ,barheight),(255,255,255))


    # if colourScheme is defined then get it
    if colourScheme != None:
        colourArray = getColourScheme(len(datatuples), colourScheme)
        
                
    
    
    draw = ImageDraw.Draw(im)

    cursorColour = (200,0,0)
    textColour = (50,50,50)
    barCount = 0
    exampleimagemap =  """
      <map name="obtypelink" id="obtypelink">
      <area href="__link%s__"
      shape="circle"
      coords="%s,%s"
      alt="Describe this object"/>
      </map>"""
    imagemap =  """
      <map name="%s" id="%s">"""

    # calculate the range of the data points
    minx = min([tuple[0] for tuple in datatuples if tuple[0] != None])
    maxx = max([tuple[0] for tuple in datatuples if tuple[0] != None])


    # scale the x
    if minx < 0:
        barcursor = (bargap,barheight/2)
        xscalefactor = (barheight/2.0) / (1.0* max((abs(minx),abs(maxx))))
    else:
        barcursor=(bargap,0)    
        xscalefactor = (barheight/1.0) / (1.0 * maxx)

    #define a lambda function to map coordinates to the drawing box - which starts
    # with (0,0) as the top left hand corner. 
    tobox = lambda x : int(barheight - x)

    
    tuplecount = 0
    for datatuple in datatuples:

        if colourScheme != None:
            drawColour = colourArray[tuplecount]

        if datatuple[0] == None:
            textSize = font.getsize('X')
            if minx < 0:
                draw.text((barcursor[0],barcursor[1]-textSize[1]),'X',fill=textColour,font=font)
            else:
                draw.text((barcursor[0],tobox(barcursor[1] + minx * xscalefactor)-textSize[1]),'X',fill=textColour,font=font)

            # draw the label if there is one
            if len(datatuple) >= 4:
                draw.text((barcursor[0],tobox(barcursor[1] + maxx/2.0 * xscalefactor)),datatuple[3],fill=textColour,font=font)
            
            barcursor = (barcursor[0]+barwidth+bargap,barcursor[1])
            tuplecount += 1     
        else:
            if currenttuple != None:
                if currenttuple == tuplecount:
                    draw.rectangle((barcursor[0], tobox(barcursor[1] + (datatuple[0] * xscalefactor)), barcursor[0]+barwidth, tobox(barcursor[1]) ),fill=cursorColour)
                else:
                    draw.rectangle((barcursor[0], tobox(barcursor[1] + (datatuple[0] * xscalefactor)), barcursor[0]+barwidth, tobox(barcursor[1]) ),fill=drawColour)
            else:
                draw.rectangle((barcursor[0], tobox(barcursor[1] + (datatuple[0] * xscalefactor)), barcursor[0]+barwidth, tobox(barcursor[1]) ),fill=drawColour)

            if len(datatuple) >= 4:
                draw.text((barcursor[0],(barcursor[1] + maxx/2.0 * xscalefactor)),datatuple[3],fill=textColour,font=font)
                
        
            imagemap += """
            <area href=%s
            shape="rect"
            coords="%s,%s,%s,%s"
            alt="%s"/>
            """%(datatuple[2],barcursor[0], tobox(barcursor[1] + (datatuple[0] * xscalefactor)), barcursor[0]+barwidth, \
                 tobox(barcursor[1]) , datatuple[1])
            barcursor = (barcursor[0]+barwidth+bargap,barcursor[1])
            tuplecount += 1        
                    


    # draw text - the max and min value
    if minx < 0:
        axismax = max(abs(minx),abs(maxx))
        axismin = -1 * axismax
    else:
        axismax = maxx
        axismin = 0
    textSize = font.getsize(str(axismax))
    draw.text((textdelta,textdelta),str(axismax),fill=textColour,font=font)
    textSize = font.getsize(str(axismin))
    draw.text((textdelta,barheight - textSize[1] - textdelta),str(axismin),fill=textColour,font=font)


    # draw text - the label
    if label1 != "":
        textSize = font.getsize(label1)
        draw.text((barcursor[0]+textdelta,barheight/2 - textSize[1]),label1,fill=textColour,font=font)
    if label2 != "":
        textSize = font.getsize(label2)
        draw.text((barcursor[0]+textdelta,barheight/2 + textdelta),label2,fill=textColour,font=font)

    
    
    
    
    # write to file if does not exist
    if not fileExists:
        fp = file(filepath,"wb")
        im.save(fp, "GIF")
        fp.close()

    # complete the imagemap
    imagemap +=  """
    </map>"""
    imagemap = imagemap%(filename.split('.')[0],filename.split('.')[0])

    # return a tuple of the filename of the image ,plus an image map    
    return (filename,imagemap)

def getJPEGThumbs(imageDirectory,filename,xy,xyoffset=(0,0),thumbcount=1,thumbdimensions=(25,25),zoomincrement=25,pixelsize=10):
    """ Function to retrieve thumbnails from a jpeg input, write to a temp file and return the
    filenames
    """
    """
    Example :
    clustercontigs.tmp
gpr_jpegorigin = 520, 12560
X,Y=20340 58380 
"pool 3 array mid scan.jpg"

1 103 430 "BrightCorner" "BrightCorner" 20340 58380 100 1078 1109 367 750 776 2
47 61 30 0 8324 8817 2461 298 314 155 100 100 0 0.041 0.042 0.045 0.035 3.731 0.
034 0.182 80 488 8354 8878 -4.613 328 8026 359 8519 0 
"""
    #fpin = open(filename,"rb")
    imagemodulelogger.info("getting array thumb using imageDirectory,filename,xy,xyoffset,thumbcount,thumbdimensions,zoomincrement,pixelsize = %s,%s,%s,%s,%s,%s,%s,%s"%(imageDirectory,filename,xy,xyoffset,thumbcount,thumbdimensions,zoomincrement,pixelsize))
    

    topixel = lambda myxy : ((myxy[0]-xyoffset[0])/(1.0* pixelsize), (myxy[1]-xyoffset[1])/(1.0*pixelsize))
    
    imin = Image.open(filename)
    #print imin.size

    
    #print topixel(xy)[0]
    
    #imin.thumbnail((400,400))
    #imin.save("c:/temp/thumb.jpg","GIF")
    #return


    outfiles = []
    for i in range(0,thumbcount):
        
        box=(max(0,topixel(xy)[0]-(thumbdimensions[0] + zoomincrement *i)),max(0,topixel(xy)[1]-(thumbdimensions[1] + zoomincrement *i)),\
             min(imin.size[0],topixel(xy)[0]+(thumbdimensions[0] + zoomincrement *i)),min(imin.size[1],topixel(xy)[1]+(thumbdimensions[1] + zoomincrement *i)))
        #print str(box)
        region = imin.crop(box)
        outfilename = str(abs(hash(filename + str(xy) + str(xyoffset) + str(box) + str(i * zoomincrement ) )))
        outfilename = "%s.jpg"%outfilename
        outfilepath = os.path.join(imageDirectory,outfilename)
        fpout = file(outfilepath,"wb")
        region.save(fpout,"JPEG")
        outfiles.append(outfilename)
        fpout.close()

    #fpin.close()
    return outfiles



def makeBlobGraph(blobCanvasFile , imageDirectory, datatuples,currenttuple=None,drawColour=(240,120,240),label1="",label2="",colourScheme=None,maxBlobSize=50):
    """ this method takes a given image and draws various sized blobs on it at specified positions, to represent
    a series of numeric quantities. Each tuple is :
    (x,elementmouseover,elementlink[,Blob label])
    The coordinates of each plot point on the axis are obtained from a lookup function
    """

    imagemodulelogger.info("makeBlobGraph called for %s"%str(datatuples))

    # check if we have already created a glyph for this descriptor.
    fileExists = False
    if currenttuple != None:
        filename = str(abs(hash(str(datatuples) + label1 + label2 + str(drawColour) + str(currenttuple) + str(colourScheme)))) + ".gif"
    else:
        filename = str(abs(hash(str(datatuples) + label1 + label2 + str(drawColour) + str(colourScheme)))) + ".gif"
        
    filepath = os.path.join(imageDirectory,  filename ) 
    if os.path.exists(filepath) :
        fileExists = True

    # get the background and set up the drawing canvas and copy the background to it.
    imin = Image.open(os.path.join(imageDirectory,  blobCanvasFile ))
    im = Image.new("RGB", imin.size) 
    im.paste(imin,(0,0))
    

    # set up graphics and basic sizing
    font = ImageFont.load_default()
    labelwidth = font.getsize(label1)[0] + font.getsize(label2)[0]
    #imin = Image.open(os.path.join(imageDirectory,  blobCanvasFile ))
    #print imin.format, imin.size, imin.mode
    draw = ImageDraw.Draw(im)


    # if colourScheme is defined then get it
    if colourScheme != None:
        colourArray = getColourScheme(len(datatuples), colourScheme)

    # get the plot points
    plotPoints = getPlotPoints(blobCanvasFile)
    if len(plotPoints) != len(datatuples):
       imagemodulelogger.info("image module : number of data points does not equal number of plot points on %s"%blobCanvasFile)
       return ("image module : number of data points does not equal number of plot points on %s"%blobCanvasFile,\
               "image module : number of data points does not equal number of plot points on %s"%blobCanvasFile)

    cursorColour = (200,0,0)
    textColour = (50,50,100)
    barCount = 0
    exampleimagemap =  """
      <map name="obtypelink" id="obtypelink">
      <area href="__link%s__"
      shape="circle"
      coords="%s,%s"
      alt="Describe this object"/>
      </map>"""
    imagemap =  """
      <map name="%s" id="%s">"""

    # calculate the range of the data points
    minx = abs(min([tuple[0] for tuple in datatuples if tuple[0] != None]))
    maxx = abs(max([tuple[0] for tuple in datatuples if tuple[0] != None]))


    xscalefactor = (maxx * 1.0) / (maxBlobSize * 2.0)  # will scale a given data point to the radius of a blob

    # function to return the bounding box of a blob given the data point number 
    getBlobBoundingBox = lambda i: (int(.5 + plotPoints[i][0] - xscalefactor * abs(datatuples[i][0])),\
                                              int(.5 + plotPoints[i][1] - xscalefactor * abs(datatuples[i][0])),\
                                              int(.5 + plotPoints[i][0] + xscalefactor * abs(datatuples[i][0])),\
                                              int(.5 + plotPoints[i][1] + xscalefactor * abs(datatuples[i][0])))

    
    tuplecount = 0
    fillColours = {
        True : (0,255,0),
        False : (255,0,0)
    }
    for datatuple in datatuples:

        if colourScheme != None:
            drawColour = colourArray[tuplecount]

        if datatuple[0] == None:
            textSize = font.getsize('X')
            draw.text(plotPoints[tuplecout],'X',fill=textColour,font=font)

            # draw the label if there is one
            if len(datatuple) >= 4:
                draw.text(plotPoints[tuplecount],datatuple[3],fill=textColour,font=font)
            tuplecount += 1     
        else:
            if currenttuple != None:
                if currenttuple == tuplecount:
                    draw.ellipse(getBlobBoundingBox(tuplecount),outline=drawColour,fill=fillColours[datatuple[0]>=0])
                else:
                    draw.ellipse(getBlobBoundingBox(tuplecount),outline=drawColour,fill=fillColours[datatuple[0]>=0])
            else:
                #print getBlobBoundingBox(tuplecount)
                #draw.ellipse(getBlobBoundingBox(tuplecount),fill=(255,0,0))
                draw.ellipse(getBlobBoundingBox(tuplecount),fill=(255,0,0))


            if len(datatuple) >= 4:
                draw.text(plotPoints[tuplecount],datatuple[3],fill=textColour,font=font)
                
        
            imagemap += """
            <area href=%s
            shape="circle"
            coords="%s,%s,%s,%s"
            alt="%s"/>
            """%((datatuple[2],)+getBlobBoundingBox(tuplecount)+(datatuple[1],))
            tuplecount += 1        
                    




    # draw text - the label
    #if label1 != "":
    #    textSize = font.getsize(label1)
    #    draw.text((barcursor[0]+textdelta,barheight/2 - textSize[1]),label1,fill=textColour,font=font)
    #if label2 != "":
    #    textSize = font.getsize(label2)
    #    draw.text((barcursor[0]+textdelta,barheight/2 + textdelta),label2,fill=textColour,font=font)

    
    
    
    
    # write to file if does not exist
    if not fileExists:
        fp = file(filepath,"wb")
        im.save(fp, "GIF")
        fp.close()

    # complete the imagemap
    imagemap +=  """
    </map>"""
    imagemap = imagemap%(filename.split('.')[0],filename.split('.')[0])

    # return a tuple of the filename of the image ,plus an image map    
    return (filename,imagemap)



def drawFeatureImage(list=(("refSeqId",100,800,"gene"),("id2a",100,600, "gene"),("id2b",500,600,"exon")), imageSize = (1000, 300), widthScale=1,
                     colourDictionary = None):
    """ Basic call to get a feature type image from a tuple of tuples and image size attributes (default tuples are provided for testing)
    extra catagory attribute is provided so colors for catagories can be assigned (maybe set up a key value list for this...
    can overide scale attribute if function called to create a zoomed in image, default of 1 is obviously "normal" size where
    reference feature width is scaled to fit the image size parameters
    Author Jonathon Warren

    Change Log :

    * 1/2007 ColorDict :
       - made a module variable featureColourKey so available from othe modules.
       - added default colour , if feature name is not in the colorDict (and commented out defaultFeatureColor as not actually used)
       - made all feature names in the dictionary lower case, to do case-insensitive lookup
       - get the referenceColour from the dictionary rather than hard-coded
       - add an optional colour dictionary to the function parameters so use can specify their own colour table if they want
       - changed background colour so obtained from the colour dictionary 
    """
   
    #colorKey = {'gene': (150,0,0), 'exon': (0,150,0), 'CDS':(150,150,150)}
    if colourDictionary == None:
        colorKey = featureColourDict
    else:
        colorKey = featureColourDict
        colorKey.update(colourDictionary) # so will contain what they passed in plus what we define that is not passed in 



    
    #print colorKey
    
    marginHeight=10
    marginWidth=50
    
    heightScale=1
    featureHeightDrop=20 # level to drop to if moving feature down (need to add if collision=true code yet?????
    featureHeight=5 #currently the width of line drawing
    imageTitle="Image Title e.g. Feature Viewer"
    # changed reference Color to be obtained from colour dictionary
    #referenceColor=(255,0,0)
    referenceColor = colorKey['referencecolour']
        
        

    
    #assume refSequence is the first one in tuple for now
    #contains id, startCodon, stopCodon
    #tuple to hold tuples of original of id start stop 
    #work out scale based on referenceFeature - assume this to be the longest or widest feature so this is stop - start =length
    referenceLength=list[0][2]-list[0][1]
    referenceSeqStart=list[0][1]
    referenceSeqStop=list[0][2]
    widthScale=float (imageSize[0]-marginWidth*2)/referenceLength #*2 to account for right margin
    print "referenceLength=",referenceLength,"imageWidth=",imageSize[0], "widthScale=" ,widthScale

    
    #bkgColor=(250,250,250)# background color
    bkgColor = colorKey['backgroundcolour']
    #defaultFeatureColor=(0,255,0)  # commented out as not actually used 
    fontColor=(0,0,0)
    im=Image.new('RGB', imageSize, color=bkgColor)
    
    xy=(10,20)
    draw=ImageDraw.Draw(im)
    
    
    #change this code to generate rectangles which will have collision detection
    for i in range(len(list)): 
        if i==0:
            featureColor=referenceColor
        else:
            #featureColor=colorKey[list[i][3]]
            # handle case of feature name not in dictionary
            featureColor = eval({ True : 'colorKey[string.lower(list[i][3])]', False : 'colorKey["defaultfeaturecolour"]'}[string.lower(list[i][3]) in colorKey])
            #print colorKey[list[i][3]] 
        draw.line(((list[i][1]-referenceSeqStart)*widthScale+marginWidth,featureHeightDrop*i+marginHeight,(list[i][2]-referenceSeqStart
        )*widthScale+marginWidth,featureHeightDrop*i+marginHeight), fill=featureColor, width=featureHeight)
        
        #draw.rectangle((100, 100,200, 200),(100,50,50),(0,0,0))
        draw.text(((list[i][1]-referenceSeqStart)*widthScale+marginWidth,featureHeightDrop*i+marginHeight+2), list[i][0], fill=fontColor, font=None, anchor=None)
        #text for start and text for stop
        draw.text(((list[i][1]-referenceSeqStart)*widthScale+marginWidth,featureHeightDrop*i+marginHeight-featureHeight-2), str(list[i][1]), fill=fontColor, font=None, anchor=None)
        draw.text(((list[i][2]-referenceSeqStart)*widthScale+marginWidth,featureHeightDrop*i+marginHeight-featureHeight-2), str(list[i][2]), fill=fontColor, font=None, anchor=None)
    im.save("C:/temp/imagetest.jpg")
    im.show()



    


def getColourScheme(numColours, scheme = 0):
    """ return an array of colours. These were originally obtained using (e.g.) the following
    scheme100 = [tuple([randint(160,254) for i in range(0,3)]) for j in range(0,100)]
    """
    schemes = []
    schemes.append([(163, 181, 254), (163, 207, 253), (175, 174, 253), (234, 240, 234), (215, 242, 201), (166, 253, 215), \
                    (205, 209, 209), (217, 254, 203), (191, 233, 176), (233, 235, 183), (177, 241, 184), (183, 177, 254), \
                    (162, 187, 252), (224, 244, 179), (180, 160, 178), (197, 234, 228), (174, 206, 189), (166, 214, 182), \
                    (246, 248, 207), (208, 172, 237), (167, 226, 175), (210, 251, 182), (190, 230, 219), (222, 253, 222), \
                    (173, 235, 185), (248, 187, 245), (196, 205, 232), (166, 203, 247), (201, 221, 247), (170, 168, 197), \
                    (234, 180, 248), (165, 211, 172), (178, 230, 231), (248, 244, 237), (233, 220, 190), (250, 208, 239), \
                    (198, 164, 228), (222, 250, 178), (208, 199, 235), (234, 234, 199), (213, 162, 190), (171, 238, 202), \
                    (244, 185, 217), (208, 176, 166), (254, 220, 200), (166, 179, 165), (238, 229, 166), (238, 236, 197), \
                    (207, 179, 210), (251, 190, 215), (211, 218, 172), (203, 196, 235), (211, 164, 192), (197, 161, 196), \
                    (226, 222, 247), (237, 239, 170), (223, 195, 169), (160, 164, 178), (187, 210, 196), (216, 197, 167), \
                    (183, 226, 240), (249, 231, 248), (188, 211, 210), (217, 177, 218), (183, 185, 189), (229, 194, 252), \
                    (165, 206, 240), (247, 253, 165), (236, 247, 164), (241, 232, 248), (186, 165, 171), (248, 238, 244), \
                    (208, 164, 195), (244, 244, 161), (201, 168, 188), (192, 190, 184), (224, 239, 229), (182, 167, 197), \
                    (235, 242, 161), (207, 166, 191), (171, 242, 244), (229, 208, 217), (235, 160, 196), (247, 201, 163), \
                    (206, 221, 171), (236, 241, 235), (192, 176, 207), (205, 240, 191), (162, 219, 213), (187, 161, 166), \
                    (176, 202, 222), (232, 197, 163), (192, 252, 226), (224, 162, 218), (218, 241, 205), (189, 208, 251), \
                    (199, 179, 160), (244, 182, 230), (175, 246, 218), (238, 208, 244)])
    schemes.append([(190,190,220)])
    myscheme = min(scheme,len(schemes)-1)
    colourScheme = [schemes[myscheme][i%len(schemes[myscheme])] for i in range (0,numColours)]
    return colourScheme

def getPlotPoints(canvasFile):
    if canvasFile == 'follicle.jpg':
        return ((104,56),(50,128),(44,214),(107,256),(173,208),(159,124))
    else:
        return None


    
    



if __name__ == "__main__" :
    # set up a tuple of objects involved in the op. Each target is a tuple of :
    # targetText, instanceCount
    #targets=(("BioProtocol",1),("Lab Resource",1),("BioSample",1))
    #targets=(("Microarray",1,"c:/temp/biosequence.jpg"),)
    #targets=((None,0),)
    #print makeOpGlyph(linkText="Microarray Spot Fact", imageDirectory="c:/temp/", obs=targets, instanceCount=1)
    #makeOpGlyph(linkText="Genetic Function Fact", imageDirectory="c:/temp/", obs=targets)
    #print makeBarGraph("c:/temp/",[(61928.5,"hrefblah1","dfdf","BABA"),(80000.0,"hrefblah2","dfgd","BCEB"),(90000.5,"hrefblah3","dfgd","ONDC")],\
    #                   currenttuple=2,label1="Tissue Expression for",label2="CS3906876876",\
    #                   barwidth=20,colourScheme=0)
    #eval("""makeBarGraph("c:/temp/",[(61928.5,"hrefblah1","dfdf","BABA"),(80000.0,"hrefblah2","dfgd","BCEB"),(90000.5,"hrefblah3","dfgd","ONDC")],\
    #                   currenttuple=2,label1="Tissue Expression for",label2="CS3906876876",\
    #                   barwidth=20,colourScheme=0)""")
    #print getJPEGThumbs(imageDirectory="c:/temp",filename="C:/temp/test.jpg",xy=(150,150),xyoffset=(0,0),thumbcount=2)
    #print getJPEGThumbs(imageDirectory="c:/temp",filename="C:/working/zaneta/9072 ratio 1 mid scan .jpg",xy=(10430,43890),xyoffset=(780, 12780),thumbcount=3)
    print makeBlobGraph("follicle.jpg" , "c:/temp", [(6,"hrefblah1","dfdf","Exp1"),(-8,"hrefblah2","dfgd","Exp2"),(-9,"hrefblah3","dfgd","Exp3"),\
                                                     (10,"hrefblah3","Exp4","Exp4"),(20,"hrefblah3","Exp5","Exp4"),(1,"hrefblah3","Exp5","Exp4")]\
                  ,drawColour=(240,120,240),label1="",label2="",colourScheme=None,maxBlobSize=20)


    
    
    #print getColourScheme(200)
    

