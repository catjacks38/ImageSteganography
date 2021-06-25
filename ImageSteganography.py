import shutil
import os
import cv2
import numpy as np
from bitstring import BitArray
from tqdm import tqdm
from math import floor, ceil
import Utils


def appendDataToImage(imgInData, dataFolderPath, outImgPath):
    # Makes temporary zip archive of folder and reads it.
    shutil.make_archive("temp", "zip", dataFolderPath)
    tempZip = open("temp.zip", "rb")

    # Deletes the output image file, if it exists, and reads it.
    if os.path.exists(outImgPath):
        os.remove(outImgPath)

    outImgFile = open(outImgPath, "wb")

    # Append the zip archive to the beginning of a copy of the input image
    outImgFile.write(imgInData)
    outImgFile.write(tempZip.read())

    # Closes and deletes temporary zip file
    tempZip.close()
    os.remove("temp.zip")

    return 0


def dataToChannel(inImgPath, data, outImgPath, channel):
    # The only material advantage of D2C over by-channel LSB (Implementation In-Progress) is speed

    img = cv2.imread(inImgPath, cv2.IMREAD_UNCHANGED)

    # Helps with reading in jpgs, but won't remove existing alpha
    if img.shape[2] < 4: img = cv2.cvtColor(img, cv2.COLOR_RGB2RGBA)

    try:
        flattened = img[:, :, channel].flatten()
    except:
        return -2

    dataByteArray = bytearray(data)


    if len(flattened) < len(dataByteArray):
        return -1

    # Spread each byte out over multiple pixels
    pixCount = floor(len(flattened) / len(dataByteArray))
    splitDBA = [pixCount]
    for i in dataByteArray:
        splitDBA.append(floor(i/pixCount) + i%pixCount)
        for j in range(pixCount-1):
            splitDBA.append(floor(i/(pixCount)))

    # Makes images look less suspicious by matching data size to image size
    for i in range(len(flattened) - len(splitDBA) - 2):
        splitDBA.append(splitDBA[i])

    # Especially helpful for alpha
    # Localizing would be better, but more costly
    meanF = round(sum(flattened)/len(flattened))
    meanD = round(sum(splitDBA)/len(splitDBA))
    shiftOpt = meanF - meanD

    if max(splitDBA)+shiftOpt > 255: 
        shift = 255-max(splitDBA)      
    elif min(splitDBA)+shiftOpt < 0:
        shift = 0-min(splitDBA)
    else: 
        shift = shiftOpt

    flattened[0] = shift

    for i in (range(len(splitDBA))):
        flattened[i+1] = splitDBA[i] + shift

    img[:, :, channel] = np.reshape(flattened, (img.shape[0], img.shape[1]))

    cv2.imwrite(outImgPath, img)

    return 0


def channelToData(inImgPath, outDataPath, channel):
    img = cv2.imread(inImgPath, cv2.IMREAD_UNCHANGED)

    if os.path.exists(outDataPath):
        os.remove(outDataPath)

    outDataFile = open(outDataPath, "wb")

    try:
        flattened = img[:, :, channel].flatten()
    except:
        return -2

    shift = -1*(flattened[0])

    pixCount = flattened[1] + shift
    flattenedTmp = []

    for i in range(floor(len(flattened)/pixCount)-2):
        a = [flattened[(i*pixCount)+2+j]+shift 
                for j in range(pixCount)]
        flattenedTmp.append(sum(a))

    
    flattenedFin = np.array(flattenedTmp).astype(np.byte)
    outData = bytes(flattenedFin)

    outDataFile.write(outData)

    return 0


def LSBEncode(inImgPath, data, outImgPath, mode):
    inImg = cv2.imread(inImgPath, cv2.IMREAD_UNCHANGED)

    # Converts image to 4 channel RGBA if it isn't already 4 channel RGBA.
    # This will allow for data to be more efficiently stored.
    if inImg.shape[2] < 4:
        inImg = cv2.cvtColor(inImg, cv2.COLOR_RGB2RGBA)

    # Gets image and data ready for processing.
    dataBitString = BitArray(bytes=data).bin

    flattened = inImg.flatten()

    # Appends extra bits to dataBitString in order to make it divisible by the mode, so there is no ending byte corruption
    while 1:
        if len(dataBitString) % mode == 0:
            break

        dataBitString += "0"

    # Checks to make sure the LSBMode is an int from 1-8.
    # If it isn't, then the function returns -2
    if mode > 8 or mode < 1 or not float(mode).is_integer():
        return -2

    # Checks to make sure there is enough channel values in the image to store all of the data.
    # If there isn't, then the function returns -1
    if len(flattened) < len(dataBitString) / mode:
        return -1

    for bit in tqdm(range(int(len(dataBitString) / mode))):

        # Converts 8 bit uint channel value to a bit list.
        channelValueBitString = list(BitArray(uint=flattened[bit], length=8).bin)

        # Writes the bits to the LSB(s) of the channel value
        channelValueBitString[8 - mode:8] = dataBitString[(bit * mode):(bit * mode) + mode]

        # Converts list into 8 bit uint, and is written to the channel on the flattened image
        channelValueBitString = "".join(channelValueBitString)
        flattened[bit] = BitArray(bin=channelValueBitString).uint

    # Reshapes the flattened image, and saves it to the outImgPath.
    cv2.imwrite(outImgPath, flattened.reshape(inImg.shape[0], inImg.shape[1], inImg.shape[2]))

    return 0


def LSBDecode(inImgPath, outPath, mode, fileSize):
    # Checks to make sure LSBMode is from 1-8
    # Returns -2 if it isn't
    if mode > 8 or mode < 1 or not float(mode).is_integer():
        return -2

    inImg = cv2.imread(inImgPath, cv2.IMREAD_UNCHANGED)

    # Removes the output file, if it already exists.
    if os.path.exists(outPath):
        os.remove(outPath)

    outFile = open(outPath, "wb")

    flattened = inImg.flatten()
    bits = ""

    # Checks to make sure the file size is greater than 0.
    # If the file size is less than 0, it is assumed the file size is unknown
    if not fileSize <= 0:
        for pixel in tqdm(flattened[0:ceil((fileSize * 8) / mode)]):

            # Appends the bits read from the LSB(s) of each channel value to the rest of the bit string
            bits += BitArray(uint=pixel, length=8).bin[8 - mode:8]
    else:
        for pixel in tqdm(flattened):

            # Appends the bits read from the LSB(s) of each channel value to the rest of the bit string
            bits += BitArray(uint=pixel, length=8).bin[8 - mode:8]

    # Appends extra bits to the end to make sure the final bit string is divisible by zero.
    while 1:
        if len(bits) % 8 == 0:
            break

        bits += "0"

    # Converts bit string to bytes, and writes it to the output path.
    outFile.write(BitArray(bin=bits).bytes)

    return 0


def autoDecode(inImgPath, outPath):
    # Grabs metadata from image
    metadata = Utils.readMetadata(inImgPath)

    # Returns -4 if there is no metadata in the image
    if not type(metadata) is tuple:
        return -4

    # Find out which method was used to encode the data.
    # If the method can not be found, the function returns -3
    if metadata[0] == Utils.dataToChannel:
        print("Encoding Method: dataToChannel")
        print(f"Channel: {metadata[1] + 1}")
        print(f"File Extension: {metadata[3]}")

        returnValue = channelToData(inImgPath, f"{outPath}.{metadata[3]}", metadata[1])
    elif metadata[0] == Utils.LSBEncode:
        print("Encoding Method: LSBEncode")
        print(f"LSBMode: {metadata[1]}")
        print(f"File Size: {metadata[2]}")
        print(f"File Extension: {metadata[3]}")

        returnValue = LSBDecode(inImgPath, f"{outPath}.{metadata[3]}", metadata[1], metadata[2])
    else:
        return -3

    # Returns the return value of the method that was used.
    # Should be 0 if there was no errors.
    return returnValue
