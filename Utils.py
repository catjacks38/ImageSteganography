from sys import exit
from PIL.PngImagePlugin import PngImageFile, PngInfo
import cv2

dataToChannel = 0
LSBEncode = 1
LSBCEncode = 2


def raiseErrorAndExit(error):
    print("Sheesh, seems like there was an error while running this program:\n")
    errList = error.split("\n")
    maxSize = max(map(len, errList))

    print("="*(maxSize+4))

    for err in errList:
        print(f"| {err + ' '*(maxSize - len(err))} |")

    print("="*(maxSize+4))

    print("\nIf this doesn't help, then you might just need to play more.")

    exit(-1)



def saveMetadata(outImgPath, method, option, fileSize, fileExtension):
    # Opens PNG image.
    inImg = PngImageFile(outImgPath)

    # Creates metadata.
    metadata = PngInfo()
    metadata.add_text("method", str(method))
    metadata.add_text("option", str(option))
    metadata.add_text("fileSize", str(fileSize))
    metadata.add_text("fileExtension", fileExtension)

    # Saves metadata to image
    inImg.save(outImgPath, pnginfo=metadata)

    return 0


def readMetadata(inImgPath):
    # Reads and extracts metadata
    inImg = PngImageFile(inImgPath)
    metadata = inImg.text

    # Checks to make sure there is metadata.
    # Returns -1 if metadata is not found.
    try:
        return int(metadata["method"]), list(map(int, metadata["option"].split())), int(metadata["fileSize"]), metadata["fileExtension"]
    except:
        return -1


def optimalLSBMode(inImgPath, data, isLSBC):
    # Reads the input image and gets size of data in bits.
    inImg = cv2.imread(inImgPath, cv2.IMREAD_UNCHANGED)
    dataBitSize = len(data) * 8

    # Calculates correct max data size based on which LSB encoding method is chosen.
    if isLSBC:
        maxSize = inImg.shape[0] * inImg.shape[1]

    else:
        maxSize = inImg.shape[0] * inImg.shape[1] * 4

    # Finds lowest LSBMode to use for LSBEncode or LSBCEncode. 
    mode = dataBitSize // maxSize + 1

    return mode if mode < 9 else -1
    # If no optimal LSBMode is found, the function returns -1.
