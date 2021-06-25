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
        return int(metadata["method"]), int(metadata["option"]), int(metadata["fileSize"]), metadata["fileExtension"]
    except:
        return -1
