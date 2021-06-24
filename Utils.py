from sys import exit
from PIL.PngImagePlugin import PngImageFile, PngInfo

dataToChannel = 0
LSBEncode = 1


def raiseErrorAndExit(error):
    print("Sheesh, seems like there was an error while running this program:\n")

    for _ in range(len(error) + 4):
        print("=", end="")

    print(f"\n| {error} |")

    for _ in range(len(error) + 4):
        print("=", end="")

    print("\n\nIf this doesn't help, then you might just need to play more.")

    exit(-1)


def saveMetadata(outImgPath, method, option, fileExtension):
    inImg = PngImageFile(outImgPath)

    metadata = PngInfo()
    metadata.add_text("method", str(method))
    metadata.add_text("option", str(option))
    metadata.add_text("fileExtension", fileExtension)

    inImg.save(outImgPath, pnginfo=metadata)

    return 0


def readMetadata(inImgPath):
    inImg = PngImageFile(inImgPath)
    metadata = inImg.text

    try:
        return int(metadata["method"]), int(metadata["option"]), metadata["fileExtension"]
    except:
        return -1
