from PIL import Image
# problem z importem:   pip uninstall PIL
#                       pip uninstall Pillow
#                       pip install Pillow
import math
import copy

# histogram
def histogram(INPixels, myFirst, myLast): # INPixels - list of pixels
    histogram = {"R":[0]*256, "G":[0]*256, "B":[0]*256}
    # INPixels list of pixels: [(R0, G0, B0), (R1, G1, B1) ... (Rn, Gn, Bn)]
    # histogram is the dictionary:  KEY: "R", "G", "B"
    #                               VALUE: histograms for "R", "G", "B" (256 elements)                 
    for iter in range (myFirst, myLast):      
        histogram["R"][INPixels[iter][0]]+=1 # R
        histogram["G"][INPixels[iter][1]]+=1 # G
        histogram["B"][INPixels[iter][2]]+=1 # B

    return histogram

# wybor skladowej (RGB) (opcja: R(0)|G(1)|B(2))
def selectionOfRGB(INPicture, myFirst, myLast, RGB): # (option: R(0)|G(1)|B(2))
    OUTpicture = Image.new("RGB",(INPicture.width, INPicture.height), (0,0,0))
    for iterJ in range (myFirst, myLast):
        for iterI in range (0, INPicture.width):
            pixel = INPicture.getpixel((iterI,iterJ))
            if RGB == 0: # R
                OUTpicture.putpixel((iterI,iterJ),(pixel[0],0,0))
            elif RGB == 1: # G
                OUTpicture.putpixel((iterI,iterJ),(0,pixel[1],0))
            elif RGB == 2: # B
                OUTpicture.putpixel((iterI,iterJ),(0,0,pixel[2]))
    return OUTpicture

# negatyw (inwersja)
def negative(INPicture, myFirst, myLast):
    # R = 255 - R
    # G = 255 - G
    # B = 255 - B
    OUTpicture = Image.new("RGB",(INPicture.width, INPicture.height), (0,0,0))
    for iterJ in range (myFirst, myLast):
        for iterI in range (0, INPicture.width):
            pixel = INPicture.getpixel((iterI,iterJ))
            OUTpicture.putpixel((iterI,iterJ),(255 - pixel[0], 255 - pixel[1], 255 - pixel[2]))
    return OUTpicture

# odcienie szarosci
def shadesOfGrey(INPicture, myFirst, myLast):
    OUTpicture = Image.new("RGB",(INPicture.width, INPicture.height), (0,0,0))
    for iterJ in range (myFirst, myLast):
        for iterI in range (0, INPicture.width):
            pixel = INPicture.getpixel((iterI,iterJ))
            GRAY = 0.299 * pixel[0] + 0.587 * pixel[1] + 0.114 * pixel[2]
            OUTpicture.putpixel((iterI,iterJ),(int(GRAY), int(GRAY), int(GRAY)))
    return OUTpicture

# jasnosc 
def brightness(INPicture, myFirst, myLast, change):
    OUTpicture = Image.new("RGB",(INPicture.width, INPicture.height), (0,0,0))
    for iterJ in range (myFirst, myLast):
        for iterI in range (0, INPicture.width):
            pixel = INPicture.getpixel((iterI,iterJ))
            OUTpicture.putpixel((iterI,iterJ),(pixel[0]+change, pixel[1]+change, pixel[2]+change))
    return OUTpicture

# kontrast
def contrast(INPicture, myFirst, myLast, contrast):
    OUTpicture = Image.new("RGB",(INPicture.width, INPicture.height), (0,0,0))
    for iterJ in range (myFirst, myLast):
        for iterI in range (0, INPicture.width):
            pixel = INPicture.getpixel((iterI,iterJ))
            OUTpicture.putpixel((iterI,iterJ),(((pixel[0] - 128) * contrast) + 128, ((pixel[1] - 128) * contrast) + 128, ((pixel[2] - 128) * contrast) + 128))
    return OUTpicture

# gamma
def gamma(INPicture, myFirst, myLast, gamma):
    OUTpicture = Image.new("RGB",(INPicture.width, INPicture.height), (0,0,0))
    for iterJ in range (myFirst, myLast):
        for iterI in range (0, INPicture.width):
            pixel = INPicture.getpixel((iterI,iterJ))
            OUTpicture.putpixel((iterI,iterJ),(int(255 * math.pow(pixel[0]/255.0, 1.0 /gamma)), int(255 * math.pow(pixel[1]/255.0, 1.0 /gamma)), int(255 * math.pow(pixel[2]/255.0, 1.0 /gamma))))
    return OUTpicture

# obrot o 90, 180, 270 (opcja: 90(0)|180(1)|270(2))
def rotation(INPicture, myFirst, myLast, option): # (option: 90(0)|180(1)|270(2))
    if option == 0: # 90
        OUTpicture = Image.new("RGB",(INPicture.height, INPicture.width), (0,0,0))
        for iterJ in range (myFirst, myLast):
            for iterI in range (0, INPicture.width): 
                OUTpicture.putpixel((iterJ,iterI),(INPicture.getpixel((iterI,INPicture.height - iterJ - 1))))
    elif option == 1: # 180
        OUTpicture = Image.new("RGB",(INPicture.width, INPicture.height), (0,0,0))
        for iterJ in range (myFirst, myLast):
            for iterI in range (0, INPicture.width):
                OUTpicture.putpixel((iterI, iterJ),(INPicture.getpixel((INPicture.width - iterI - 1, INPicture.height - iterJ - 1))))
    elif option == 2: # 270
        OUTpicture = Image.new("RGB",(INPicture.height, INPicture.width), (0,0,0))
        for iterJ in range (myFirst, myLast):
            for iterI in range (0, INPicture.width):
                OUTpicture.putpixel((iterJ, iterI),(INPicture.getpixel((INPicture.width - iterI - 1, iterJ))))
    return OUTpicture

# odbicie lustrzane (opcja: pionowe(0)|poziome(1))
def mirrorReflection(INPicture, myFirst, myLast, option):# option: vertical(0)|horizontal(1)
    if option == 0: # vertical
        OUTpicture = Image.new("RGB",(INPicture.width, INPicture.height), (0,0,0))
        for iterJ in range (myFirst, myLast):
            for iterI in range (0, INPicture.width): 
                OUTpicture.putpixel((iterI,iterJ),(INPicture.getpixel((iterI,INPicture.height - iterJ - 1))))
    if option == 1: # horizontal
        OUTpicture = Image.new("RGB",(INPicture.width, INPicture.height), (0,0,0))
        for iterJ in range (myFirst, myLast):
            for iterI in range (0, INPicture.width): 
                OUTpicture.putpixel((iterI,iterJ),(INPicture.getpixel((INPicture.width - iterI - 1, iterJ))))
    return OUTpicture
