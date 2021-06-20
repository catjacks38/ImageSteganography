import shutil
import os
import cv2
import numpy as np


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


def dataToPixels(imgInData, data, outImgPath):
    imgData = bytearray(imgInData)

    if len(data) > len(imgData) - 54:
        return -1

    if os.path.exists(outImgPath):
        os.remove(outImgPath)

    for i in range(len(data)):
        imgData[i + 54] = data[i]

    finalImgFile = open(outImgPath, "wb")

    finalImgFile.write(imgData)

    return 0


def pixelsToData(imgInData, outDataPath):
    if os.path.exists(outDataPath):
        os.remove(outDataPath)

    outImg = open(outDataPath, "wb")

    outImg.write(imgInData[54:])

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

