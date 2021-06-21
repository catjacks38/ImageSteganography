import shutil
import os
import cv2
import numpy as np
from bitstring import BitArray
import math
from tqdm import tqdm


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
    img = cv2.imread(inImgPath, cv2.IMREAD_UNCHANGED)

    try:
        flattened = img[:, :, channel].flatten()
    except:
        return -2

    dataByteArray = bytearray(data)

    if len(flattened) < len(dataByteArray):
        return -1

    for i in range(len(dataByteArray)):
        flattened[i] = dataByteArray[i]

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

    flattened = flattened.astype(np.byte)

    outData = bytes(flattened)

    outDataFile.write(outData)

    return 0


def LSBEncode(inImgPath, data, outImgPath, mode):
    inImg = cv2.imread(inImgPath, cv2.IMREAD_UNCHANGED)

    dataBitString = BitArray(bytes=data).bin

    flattened = inImg.flatten()

    if mode > 8 or mode < 1 or not float(mode).is_integer():
        return -2

    if len(flattened) < math.floor(len(dataBitString) / mode):
        return -1

    for bit in tqdm(range(math.floor(len(dataBitString) / mode))):
        channelValueBitString = list(BitArray(uint=flattened[bit], length=8).bin)
        channelValueBitString[8 - mode:8] = dataBitString[(bit * mode):(bit * mode) + mode]
        channelValueBitString = "".join(channelValueBitString)

        flattened[bit] = BitArray(bin=channelValueBitString).uint

    cv2.imwrite(outImgPath, flattened.reshape(inImg.shape[0], inImg.shape[1], inImg.shape[2]))

    return 0


def LSBDecode(inImgPath, outPath, mode):
    if mode > 8 or mode < 1 or not float(mode).is_integer():
        return -2

    inImg = cv2.imread(inImgPath, cv2.IMREAD_UNCHANGED)

    if os.path.exists(outPath):
        os.remove(outPath)

    outFile = open(outPath, "wb")

    flattened = inImg.flatten()
    bits = ""

    for pixel in tqdm(flattened):
        bits = bits + BitArray(uint=pixel, length=8).bin[8 - mode:8]

    outFile.write(BitArray(bin=bits).bytes)

    return 0
