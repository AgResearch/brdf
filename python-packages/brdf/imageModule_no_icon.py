#
# This module is used to generate various images on the fly for
# the . It depends on the Python image library - see
# http://effbot.org/downloads/#imaging
#
from PIL import Image, ImageDraw, ImageFont
import os.path



def makeOpGlyph(linkText, imageDirectory, obs,instanceCount,linkFirstObject=False):
    """ this method makes the glyphs used to display "ops" - i.e. relations between two or more objects in the
    database. These glyphs are optionally filled circles - filled if there is an instance of the operation.
    linkText - the description of the relation as a whole
    imageDirectory - path to image directory where the glyph will be written
    obs - a tuple of tuples. Each tuple is a pair describing an object in the
       relation : (Display Name, instanceCount)
       if displayName is None, then the glyph will be that of a fact relation
       if instanceCount is 0 then this object is missing in the relation and an empty circle will be
       drawn
    instanceCount - this is the number of instances of the relation as a whole. If there are none then
    the glyph is drawn in grey to indicate an uninstantiated relation

    There are a finite number of glyphs and we do not want to create a glyph if it has previously
    been created. The image directory is first searched for a file with a name that is the
    same as a hash of the descriptor we have been given.
    """

    # check if we have already created a glyph for this descriptor.
    fileExists = False
    filename = str(abs(hash(linkText + imageDirectory + str(obs) + str(instanceCount)))) + ".gif"
    filepath = os.path.join(imageDirectory,  filename ) 
    if os.path.exists(filepath) :
        fileExists = True
    

    # set up graphics and basic sizing
    font = ImageFont.load_default()
    #im = Image.new("P", (600,45), 500)
    #im = Image.new("P", (800,45), 500)
    if len(obs) <= 2:
        im = Image.new("P", (380,45), 500)
    else:
        im = Image.new("P", (160 + 90 * len(obs) ,45),500)

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
    lineLength = 90

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

            draw.ellipse(outerCircle,outline=drawColour)
            if target[1] > 0 and instanceCount > 0:
                draw.ellipse(innerCircle,outline=128,fill=instanceColour)

        
            if linkFirstObject:
                imagemap += """
                <area href="__link%s__"
                shape="circle"
                coords="%s,%s,%s"
                alt="Link to related information"/>
                """%( targetCount, (outerCircle[0] + outerCircle[2])/2, (outerCircle[1] + outerCircle[3])/2, outerCircleDiameter/2)


            # print the object type text.
            # the start point is , from the middle of the outer circle, left by
            # half the text length, and down by borderDelta
            textSize = font.getsize(target[0])
            draw.text((outerCircle[0] + outerCircleDiameter/2 - textSize[0]/2,outerCircle[3] + borderDelta),target[0],fill=drawColour,font=font)

            # if there is only one target this is a fact table so we now draw the line
            if len(obs) == 1:
                draw.line((outerCircle[2],(outerCircle[1] + outerCircle[3])/2 \
                  , outerCircle[2] + lineLength, (outerCircle[1] + outerCircle[3])/2) \
                  ,fill=drawColour)

                # finish the line with a box
                draw.rectangle((outerCircle[2] + lineLength - smallSquareDelta[0], \
                          (outerCircle[1] + outerCircle[3])/2 - smallSquareDelta[1], \
                          outerCircle[2] + lineLength + smallSquareDelta[0],  \
                          (outerCircle[1] + outerCircle[3])/2 + smallSquareDelta[1]),fill=drawColour)
                # draw a small "info" for info
                if instanceCount > 0:
                    infoColour = white
                else:
                    infoColour = offwhite
                textSize = font.getsize("info")
                draw.text((outerCircle[2] + lineLength - smallSquareDelta[0] + borderDelta/2,\
                               (outerCircle[1] + outerCircle[3])/2 - textSize[1]/2),"info",fill=infoColour,font=font)
                         
                          
                targetCount += 1

                imagemap += """
                   <area href="__link%s__"
                   shape="rect"
                   coords="%s,%s,%s,%s"
                   alt="Link to related information"/>
                   """%( targetCount, outerCircle[2], (outerCircle[1] + outerCircle[3])/2 - circleDelta ,outerCircle[2] + lineLength + smallSquareDelta[0], (outerCircle[1] + outerCircle[3])/2 + circleDelta)                
                

                # update the circle, just so the text gets put in the correct place
                outerCircle = (outerCircle[2] + lineLength ,outerCircle[1],\
                     outerCircle[2] + lineLength  + outerCircleDiameter, \
                      outerCircle[3])                     
                
        else:                
            
            # draw a line from the edge of the circle pointing right.
            draw.line((outerCircle[2],(outerCircle[1] + outerCircle[3])/2 \
                  , outerCircle[2] + lineLength, (outerCircle[1] + outerCircle[3])/2) \
                  ,fill=drawColour)

            # if we have a non-null instance count draw the outer circle which represents the type

            if instanceCount != None:

                outerCircle = (outerCircle[2] + lineLength ,outerCircle[1],\
                         outerCircle[2] + lineLength  + outerCircleDiameter, \
                          outerCircle[3])

            
                draw.ellipse(outerCircle,outline=drawColour,fill=(255,255,255))

                # if there is an instance then draw the inner circle
                if target[1] > 0 and instanceCount > 0:
                    innerCircle = map(lambda x,y:x+y,outerCircle,(circleDelta,circleDelta,-1*circleDelta,-1*circleDelta))
                    draw.ellipse(innerCircle,outline=drawColour,fill=drawColour)

                    imagemap += """
                    <area href="__link%s__"
                    shape="circle"
                    coords="%s,%s,%s"
                    alt="Link to related database object(s)"/>
                    """%( 1+targetCount, (outerCircle[0] + outerCircle[2])/2, (outerCircle[1] + outerCircle[3])/2, outerCircleDiameter/2)                

                # print the object type text.
                # the start point is , from the middle of the outer circle, left by
                # half the text length, and down by borderDelta
                textSize = font.getsize(target[0])
                draw.text((outerCircle[0] + outerCircleDiameter/2 - textSize[0]/2,outerCircle[3] + borderDelta),target[0],fill=drawColour,font=font)
        

                targetCount += 1
            else:  # we have a null instance count - this is a dynamic link, we draw a triangle
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
                draw.text((outerCircle[0] + outerCircleDiameter/2 - textSize[0]/2,outerCircle[3] + borderDelta),target[0],fill=drawColour,font=font)
        

                targetCount += 1                
                


    # start point for link text is past the end of the last circle
    # just above the midpoint
    textSize = font.getsize(linkText)
    textDelta = textSize[1]/2
    #draw.text((outerCircle[2] + 5*textDelta,(outerCircle[1] + outerCircle[3])/2 - textDelta),linkText,fill=128,font=font)
    draw.text((outerCircle[2] + 5*textDelta,(outerCircle[1] + outerCircle[3])/2 - textDelta),linkText,fill=drawColour,font=font)
        


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



if __name__ == "__main__" :
    # set up a tuple of objects involved in the op. Each target is a tuple of :
    # targetText, instanceCount
    #targets=(("BioProtocol",1),("Lab Resource",1),("BioSample",1))
    targets=(("Microarray",1),)
    #targets=((None,0),)
    print makeOpGlyph(linkText="Microarray Spot Fact", imageDirectory="c:/temp/", obs=targets, instanceCount=1)
    #makeOpGlyph(linkText="Genetic Function Fact", imageDirectory="c:/temp/", obs=targets)

