import os
from PIL import Image, ImageFont, PSDraw, ImageDraw

print "running FeatureImageCreator.py"

def drawFeatureImage(list=(("refSeqId",100,800,"gene"),("id2a",100,600, "gene"),("id2b",500,600,"exon")), imageSize = (1000, 300), widthScale=1):
   # Basic call to get a feature type image from a tuple of tuples and image size attributes (default tuples are provided for testing)
   #extra catagory attribute is provided so colors for catagories can be assigned (maybe set up a key value list for this...
   #can overide scale attribute if function called to create a zoomed in image, default of 1 is obviously "normal" size where
   #reference feature width is scaled to fit the image size parameters
    colorKey = {'gene': (150,0,0), 'exon': (0,150,0), 'CDS':(150,150,150)}
    print colorKey
    
    marginHeight=10
    marginWidth=50
    
    heightScale=1
    featureHeightDrop=20 # level to drop to if moving feature down (need to add if collision=true code yet?????
    featureHeight=5 #currently the width of line drawing
    imageTitle="Image Title e.g. Feature Viewer"
    referenceColor=(255,0,0)
    #assume refSequence is the first one in tuple for now
    #contains id, startCodon, stopCodon
    #tuple to hold tuples of original of id start stop 
    #work out scale based on referenceFeature - assume this to be the longest or widest feature so this is stop - start =length
    referenceLength=list[0][2]-list[0][1]
    referenceSeqStart=list[0][1]
    referenceSeqStop=list[0][2]
    widthScale=float (imageSize[0]-marginWidth*2)/referenceLength #*2 to account for right margin
    print "referenceLength=",referenceLength,"imageWidth=",imageSize[0], "widthScale=" ,widthScale
    bkgColor=(250,250,250)# background color
    defaultFeatureColor=(0,255,0)
    fontColor=(0,0,0)
    im=Image.new('RGB', imageSize, color=bkgColor)
    
    xy=(10,20)
    draw=ImageDraw.Draw(im)
    
    
    #change this code to generate rectangles which will have collision detection
    for i in range(len(list)): 
        if i==0:
            featureColor=referenceColor
        else:
            featureColor=colorKey[list[i][3]]
            print colorKey[list[i][3]] 
        draw.line(((list[i][1]-referenceSeqStart)*widthScale+marginWidth,featureHeightDrop*i+marginHeight,(list[i][2]-referenceSeqStart
        )*widthScale+marginWidth,featureHeightDrop*i+marginHeight), fill=featureColor, width=featureHeight)
        
        #draw.rectangle((100, 100,200, 200),(100,50,50),(0,0,0))
        draw.text(((list[i][1]-referenceSeqStart)*widthScale+marginWidth,featureHeightDrop*i+marginHeight+2), list[i][0], fill=fontColor, font=None, anchor=None)
        #text for start and text for stop
        draw.text(((list[i][1]-referenceSeqStart)*widthScale+marginWidth,featureHeightDrop*i+marginHeight-featureHeight-2), str(list[i][1]), fill=fontColor, font=None, anchor=None)
        draw.text(((list[i][2]-referenceSeqStart)*widthScale+marginWidth,featureHeightDrop*i+marginHeight-featureHeight-2), str(list[i][2]), fill=fontColor, font=None, anchor=None)
    im.save("C:/temp/imagetest.jpg")
    im.show()
    
    
  
  
  

def main():
    #main function calling of program   
    refExample=("refSeqId",100,800,"gene")
    exampleSeqIdA=("SequenceA",100,800,"gene")
    exampleSeqId=("sequence1",110,210, "CDS")
    exampleSeqId2=("sequence2",200,300,"exon")
    listTest=(refExample, exampleSeqIdA, exampleSeqId,exampleSeqId2)
    #drawFeatureImage(listTest)
    #try using default tuple list
    drawFeatureImage()


if __name__ == "__main__":
   main()




