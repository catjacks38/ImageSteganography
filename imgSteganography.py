import shutil
import os


def appendDataToImg(imgIn, outImgPath, dataFolderPath):
    shutil.make_archive("temp", "zip", dataFolderPath)
    tempZip = open("temp.zip", "rb")

    if os.path.exists(outImgPath):
        os.remove(outImgPath)

    outImgFile = open(outImgPath, "wb")

    outImgFile.write(imgIn.read())
    outImgFile.write(tempZip.read())

    tempZip.close()
    os.remove("temp.zip")

    return True
