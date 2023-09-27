#
# Étiquetteuse Brother-QL
# par Mathieu Légaré <levelkro@yahoo.ca>
#
# v2.23.09.27
#  ^- Version
#    ^^- Year
#       ^^- Month
#          ^^- Day
#   of this realease

# Importations
from PIL import Image, ImageDraw, ImageFont
import getopt, sys, os, time, datetime
import configparser, re, shlex
from datetime import datetime
import textwrap
if os.name == 'nt':
    import win32api, win32print

# fonction interne
def loadConfig():
    global config
    config = configparser.ConfigParser()
    config.read('config.ini', encoding='utf-8')
    
def loadDraw():
    global drawRules
    drawRules = configparser.ConfigParser()
    drawRules.read(drawFile, encoding='utf-8')

def loadBarcode():
    if(barcode is False):
        barcode=True
        import treepoem
        
def debug(text):
    if(DEBUG==True):
        print("[DEBUG]:", text)

def setCut(w,h):
    global cutCrop,drawBanner
    w=w + 1
    h=h + 1
    if(drawBanner and w>cutCrop):
        cutCrop=w
    elif(h>=cutCrop):
        cutCrop=h
        
def getValue(value):
    global drawValues
    return drawValues.get(value)

def saveDraw():
    global config,outFile,outDraw,outImage,cutCrop
    debug("Save the draw")
    if(drawBanner):
        debug("Is a banner, rotating output")
        outImage=outImage.rotate(90, expand=True)
    if(cutCrop>0):
        debug("Draw is over, cutting for "+str(drawWidth)+"x"+str(cutCrop))
        
        if(drawRules['paper']['width']=="0"):
            outImage=outImage.crop((0, 0, cutCrop, drawHeight))
        elif(drawRules['paper']['height']=="0"):
            outImage=outImage.crop((0, 0, drawWidth, cutCrop))
    outImage.save(outFile, format='PNG')
            
def printDraw():
    global config,outCopy
    i=1
    debug("Printing  "+str(outCopy)+" copies")
    if(DEBUG!=True):
        while( i <= outCopy):
            debug("Printing copy #"+str(i)+" from "+str(outCopy)+" copies")
            if os.name == 'nt':
                os.system('print.bat print.lbx "@output.png"')  
            else:
                os.system('sudo brother_ql -m '+config['printer']['model']+' -p usb://'+config['printer']['usb']+'/'+config['printer']['serial']+' print '+outFile+' -l 62 --600dpi')
            time.sleep(2)
            i+=1
    else:  
        debug("Send the output draw to printer (disabled when DEBUG is enabled)")
        
def lineDraw(posx,posy,width,height):
    global config,outDraw
    debug("Draw a line")
    shape = [(posx, posy), (posx+width, posy+height)]
    outDraw.line(shape, fill =cBlack, width = 0)
        
def textDraw(text,posx,posy,width,height,align,overflow):
    #postion of text
    global config,outDraw,outImage,drawWidth,drawHeight
    if(int(width)==0):
        width=int(drawWidth - posx)
    if(int(height)==0):
        height=int(drawHeight - posy)
    if(outImage):
        debug("Adding text '" + text +"'")
        textFont = ImageFont.truetype(config['default']['font'], height)
        fontSize=False
        if(overflow=="fit"):
            debug("Try to fit text into space")
            # Text do not overflow
            lastFontSize=False
            testFontSize=height
            while(testFontSize >= 0 and fontSize is False):
                testFont = ImageFont.truetype(config['default']['font'], testFontSize)
                if(testFont.getbbox(text)[3] <= height and testFont.getbbox(text)[2]<=width):
                    # Text is lower of the height of space
                    if((testFont.getbbox(text)[3] == height or testFont.getbbox(text)[2] >= (height - 2))):
                        debug("Font size found")
                        # Text is same of above the limit of height
                        # Font size found
                        fontSize=testFontSize
                    else:
                        debug("Font size found, but increase it")
                        # Text can get more space, increase it ?
                        lastFontSize=testFontSize
                        testFontSize=testFontSize + 1
                else:
                    # Heigh or with Overflow
                    if(lastFontSize):
                        debug("Use last font size found")
                        # Previous check is good, the new overflow, use the last good result
                        # Font size found
                        fontSize=lastFontSize
                    else:
                        debug("Try a smaller fon size")
                        # Size overflow, test a smaller size
                        testFontSize=testFontSize - 1
        elif(overflow=="wrap"):
            debug("Try to wrap text")
            # Text do not overflow, adding return for paragraph text
            #TODO
            # Test multi lines, if \r not work, try by cut he total height and split lines
            # calc car len, / 2, split by space, count each word added for car len, when over the half, add return
            # if do not fit, retry with / 3, / 4 , etc...
            #TODO

            lines = textwrap.wrap(text, width=width)
            draw.multiline_text((x,y), '\n'.join(lines))
            
            
            fontSize=height #to replace
        else:
            debug("Do nothing for text overflow")
            # past without rework
            fontSize=height
        textFont = ImageFont.truetype(config['default']['font'], fontSize)
        textWidth=textFont.getbbox(text)[2]
        textHeight=textFont.getbbox(text)[3]
        np=0
        if(align=="center"):
            debug("Centering text")
            # Centering the text
            np=width - textWidth
            setCut(posx + textWidth + np,posy + textHeight) 
            posx=posx + round(np / 2,0)
        elif(align=="right"):
            debug("Text to right")
            # Text begin at right
            np=width - textWidth
            posx=posx + np
            setCut(posx + textWidth,posy + textHeight) 
        else:
            debug("Text to left")
            # Text degin at left
            posx=posx  
            setCut(posx + textWidth,posy + textHeight)  
        outDraw.text((posx,posy), str(text), font=textFont, fill=cBlack)
    else:
        print("*** Can't adding text, image is no created")

def imageDraw(file,posx,posy,width,height):
    global config,outDraw,outImage,drawWidth,drawHeight
    debug("Open image : "+str(file)+" and try to generate with "+str(width)+"x"+str(height))
    if(outImage):
        image = Image.open(file).convert("RGBA")
        if(int(width)!=0 or int(height)!=0):
            if(int(width)!=0 and int(height)==0):
                wpercent = (width/float(image.size[0]))
                height = round((float(image.size[1])*float(wpercent)),0)
            elif(int(width)==0 and int(height)!=0):
                hpercent = (height/float(image.size[1]))
                width = round((float(image.size[0])*float(hpercent)),0)
            debug("Resize image to "+str(width)+"x"+str(height))
            image=image.resize((int(width), int(height)))
        debug("Drawing image at "+str(posx)+"x"+str(posy)+" with size of "+str(image.size[0])+"x"+str(image.size[1]))
        outImage.paste(image, (posx,posy), image)
        setCut(posx + width,posy + height)  
    else:
        print("*** Can't adding text, image is no created")

def barcodeDraw(code,posx,posy,width,height,sub):
    encode="code128"
    global config,outDraw,outImage,drawWidth,drawHeight
    debug("Generating barcode")
    if(outImage):
        image = treepoem.generate_barcode(barcode_type=encode,data=code,)
        image.convert("1").save("barcode.jpg")
        if(sub=="sub"):
            subSize=round(height / 5,0)
            imageDraw("barcode.jpg",posx,posy,width,height - subSize)
            textDraw(code,posx,int(posy + (height - subSize)),int(width),int(subSize),"center","fit")
        else:
            imageDraw("barcode.jpg",posx,posy,width,height)
    else:
        print("*** Can't adding text, image is no created")
    
def newDraw():
    global config,outImage,outDraw,drawRules,drawWidth,drawHeight,drawRotate,drawBanner
    if(drawRules):
        debug("Create Draw")
        drawWidth=int(drawRules['paper']['width'])
        drawHeight=int(drawRules['paper']['height'])
        drawRotate=int(drawRules['paper']['rotate'])
        if(drawWidth == 0):
           drawWidth=int(config['default']['paperlength'])
        if(drawHeight == 0):
           drawHeight=int(config['default']['paperlength'])
        if(drawRotate == 1):
           drawBanner=True
        debug("New draw with dimension of "+str(drawWidth)+"x"+str(drawHeight)+" pixels")
        if(drawBanner):
            debug("Draw is a banner")
        outImage=Image.new('RGBA', (int(drawWidth), int(drawHeight)), color = cWhite)
        outDraw=ImageDraw.Draw(outImage)
        debug("Draw created")
    else:
        print("*** No drawing rules loaded")
        
## Configurations
loadConfig()
drawFile=False
drawRules=False
drawWidth=0
drawHeigh=0
drawRotate=0
drawBanner=False
drawValues={}
cutCrop=0
barcode=False

## Couleurs
cWhite=(255,255,255)
cBlack=(0,0,0)

## Police de caractère
fName=config['default']['font']

## Paramètre de sortie
outDraw=False
outImage=False
outFile="output.png"
outCopy=1

## Mode Debug
if(str(config['default']['debug'])=="True"):
    print("Debug Enabled")
    DEBUG=True
else:
    DEBUG=False
    
# application
argv = sys.argv[1:]
opts, args = getopt.getopt(argv,"ha:f:c:v:")
help=False
cmd=False
for opt, arg in opts:
    if opt == '-h':
        help=True
        cmd=True
        print("*** Help for command parameters")
        print("\t-f\t<filepath>\t\tLoading draw file\r\n\t--file\t<filepath>")
        print("\t-v\t<id=\"value\":id=\"value\">\tReplace values of id in draw file\r\n\t--value\t<id=\"value\";id=\"value\">")
        print("\t-c\t<copies>\t\tPrint number of copies of result\r\n\t--copies\t<copies>")        
    elif opt == '-f' or opt == "--file":
        cmd=True
        debug("Loading draw file " + arg)
        drawFile=arg
    elif opt == '-c' or opt == "--copies":
        cmd=True
        if(int(arg) >= 1):
            debug("Printing " + arg + " copies")
            outCopy=int(arg)
        else:
            debug("Can't set copies to " + str(arg) + ". Must be granter or equal to 1")
    elif opt == '-v' or opt == "--values":
        cmd=True
        debug("Loading draw values " + arg)
        #drawValues = arg
        items = arg.split(';')
        # Récupérer les valeurs des arguments de ligne de commande
        for item in items:
            # Vérifier si le séparateur '=' est présent dans la chaîne item
            if '=' in item:
                key, value = item.split('=')
                drawValues[key] = value.replace('"','')
    else:
        #Determine parameters
        debug("Unknown parameter '"+ str(opt) + "'.")
        
if(help is False and cmd is True):
    # Help is not diosplayed, running app
    if(drawFile):
        # Drawing from file
        loadDraw()
    else:
        # Drawing from command line
        drawRules=False

    # Generating the new draw
    newDraw()

    # Reading if is a drawFile
    if(drawFile):
        for section in drawRules.sections():
            if section.lower() != 'paper':
                # Traitez ici chaque section autre que 'paper'
                if(drawRules[section]['type']=="text"):
                    if(getValue(section) is not None):
                        value=getValue(section)
                    else:
                        value=drawRules[section]['value']
                    textDraw(str(value),int(drawRules[section]['posx']),int(drawRules[section]['posy']),int(drawRules[section]['width']),int(drawRules[section]['height']),drawRules[section]['align'],drawRules[section]['overflow'])
                    
                elif(drawRules[section]['type']=="image"):
                    if(getValue(section) is not None):
                        value=getValue(section)
                    else:
                        value=drawRules[section]['value']
                    imageDraw(value,int(drawRules[section]['posx']),int(drawRules[section]['posy']),int(drawRules[section]['width']),int(drawRules[section]['height']))

                elif(drawRules[section]['type']=="barcode"):
                    loadBarcode()
                    if(getValue(section) is not None):
                        value=getValue(section)
                    else:
                        value=drawRules[section]['value']
                    barcodeDraw(str(value),int(drawRules[section]['posx']),int(drawRules[section]['posy']),int(drawRules[section]['width']),int(drawRules[section]['height']),drawRules[section]['params'])                    
                
                elif(drawRules[section]['type']=="line"):
                    lineDraw(int(drawRules[section]['posx']),int(drawRules[section]['posy']),int(drawRules[section]['width']),int(drawRules[section]['height']))                    
                
                else:
                    print("*** Type unknow of entry")

    # Save the draw
    saveDraw()
    
    # Send to printer
    printDraw()

elif(cmd is False):
    print("Missing a valid parameter. Try '-h' for help.")
    
# Exiting the app
sys.exit()