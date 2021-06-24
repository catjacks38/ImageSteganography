import shutil
import os
import cv2
import numpy as np
from bitstring import BitArray
from tqdm import tqdm
from math import floor, ceil
import Utils


def appendDataToImage(imgInData, dataFolderPath, outImgPath):
    shutil.make_archive("temp", "zip", dataFolderPath)
    tempZip = open("temp.zip", "rb")

    if os.path.exists(outImgPath):
        os.remove(outImgPath)

    outImgFile = open(outImgPath, "wb")

    outImgFile.write(imgInData)
    outImgFile.write(tempZip.read())

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
    for i in range(len(flattened)- len(splitDBA) - 2):
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

    if inImg.shape[2] < 4:
        inImg = cv2.cvtColor(inImg, cv2.COLOR_RGB2RGBA)

    dataBitString = BitArray(bytes=data).bin

    flattened = inImg.flatten()

    while 1:
        if len(dataBitString) % mode == 0:
            break

        dataBitString += "0"

    if mode > 8 or mode < 1 or not float(mode).is_integer():
        return -2

    if len(flattened) < len(dataBitString) / mode:
        return -1

    for bit in tqdm(range(int(len(dataBitString) / mode))):
        channelValueBitString = list(BitArray(uint=flattened[bit], length=8).bin)
        channelValueBitString[8 - mode:8] = dataBitString[(bit * mode):(bit * mode) + mode]
        channelValueBitString = "".join(channelValueBitString)

        flattened[bit] = BitArray(bin=channelValueBitString).uint

    cv2.imwrite(outImgPath, flattened.reshape(inImg.shape[0], inImg.shape[1], inImg.shape[2]))

    return 0


def LSBDecode(inImgPath, outPath, mode, fileSize):
    if mode > 8 or mode < 1 or not float(mode).is_integer():
        return -2

    inImg = cv2.imread(inImgPath, cv2.IMREAD_UNCHANGED)

    if os.path.exists(outPath):
        os.remove(outPath)

    outFile = open(outPath, "wb")

    flattened = inImg.flatten()
    bits = ""

    if not fileSize <= 0:
        for pixel in tqdm(flattened[0:ceil((fileSize * 8) / mode)]):
            bits = bits + BitArray(uint=pixel, length=8).bin[8 - mode:8]
    else:
        for pixel in tqdm(flattened):
            bits = bits + BitArray(uint=pixel, length=8).bin[8 - mode:8]

    while 1:
        if len(bits) % 8 == 0:
            break

        bits += "0"

    outFile.write(BitArray(bin=bits).bytes)

    return 0


def autoDecode(inImgPath, outPath):
    metadata = Utils.readMetadata(inImgPath)

    if not type(metadata) is tuple:
        return -4

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

    return returnValue

