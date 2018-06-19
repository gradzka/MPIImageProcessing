from PIL import Image
# problem z importem:   pip uninstall PIL
#                       pip uninstall Pillow
#                       pip install Pillow
import math
import copy

def my_sum(red_proc1, red_proc2, mpi_datatype):
    for rank in red_proc2.completedRanks:
        proc2_first = int((rank * red_proc2.picture.height) / red_proc2.size)
        proc2_last = int(((rank+1) * red_proc2.picture.height) / red_proc2.size)
        for iterJ in range (proc2_first, proc2_last):
            for iterI in range (0, red_proc1.picture.width):
                pixelOUT = red_proc2.picture.getpixel((iterI,iterJ))
                R = pixelOUT[0]
                G = pixelOUT[1]
                B = pixelOUT[2]
                red_proc1.picture.putpixel((iterI,iterJ),(R,G,B))
        red_proc1.addToCompletedRanks(rank)
    return red_proc1

def my_histogram_sum(histogram1, histogram2, mpi_datatype):
    histogram = {"R":[0]*256, "G":[0]*256, "B":[0]*256}
    for iter in range(0, 256):
        histogram["R"][iter] = histogram1["R"][iter] + histogram2["R"][iter] # R
        histogram["G"][iter] = histogram1["G"][iter] + histogram2["G"][iter] # G
        histogram["B"][iter] = histogram1["B"][iter] + histogram2["B"][iter] # B
    return histogram

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
def RGBSelection(INPicture, myFirst, myLast, RGB): # (option: R(0)|G(1)|B(2))
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
            OUTpicture.putpixel((iterI,iterJ),(int(pixel[0]+change), int(pixel[1]+change), int(pixel[2]+change)))
    return OUTpicture

# kontrast
def contrast(INPicture, myFirst, myLast, contrast):
    OUTpicture = Image.new("RGB",(INPicture.width, INPicture.height), (0,0,0))
    for iterJ in range (myFirst, myLast):
        for iterI in range (0, INPicture.width):
            pixel = INPicture.getpixel((iterI,iterJ))
            OUTpicture.putpixel((iterI,iterJ),((int((pixel[0] - 128) * contrast) + 128), (int((pixel[1] - 128) * contrast) + 128), (int((pixel[2] - 128) * contrast) + 128)))
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

imageProcessing = {"histogram" : histogram,
           "rotation" : rotation,
           "mirrorReflection" : mirrorReflection,
           "RGBSelection" : RGBSelection,
           "negative" : negative,
           "shadesOfGrey" : shadesOfGrey,
           "brightness" : brightness,
           "contrast" : contrast,
           "gamma" : gamma,
}
