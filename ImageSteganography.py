import shutil
import os


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


def dataToPixels(imgInData, dataFileData, outImgPath):
    imgData = bytearray(imgInData)
    data = bytearray(dataFileData)

    if len(data) > len(imgData) - 54:
        return -1

    if os.path.exists(outImgPath):
        os.remove(outImgPath)

    for i in range(len(data)):
        imgData[i + 54] = data[i]

    finalImgFile = open(outImgPath, "wb")

    finalImgFile.write(imgData)

    return 0


def pixelsToData(imgInData, outImgPath):
    if os.path.exists(outImgPath):
        os.remove(outImgPath)

    outImg = open(outImgPath, "wb")

    outImg.write(imgInData[54:])

    return 0
