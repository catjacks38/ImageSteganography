import shutil
import os
import cv2
import numpy as np
from bitstring import BitArray
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
    if img.shape[2] < 4:
        img = cv2.cvtColor(img, cv2.COLOR_RGB2RGBA)

    try:
        flattened = img[:, :, channel].flatten()
    except:
        return -2

    # Unsqueeze Dim 0; concatenate only accepts existing dims
    dataByteArray = np.expand_dims(np.array(bytearray(data)), 0)

    if len(flattened) < dataByteArray.shape[1]:
        return -1

    # Spread each byte out over multiple pixels
    pixCount = len(flattened) // dataByteArray.shape[1]

    # Results in an array of shape (byteCount, pixCount) where the sum of each row is the byte value
    noPixDBA = np.concatenate([dataByteArray // pixCount + dataByteArray % pixCount] + [dataByteArray // pixCount]*(pixCount - 1), 0).transpose()

    dataArray = np.concatenate(([pixCount], noPixDBA.flatten()))

    # Makes images look less suspicious by matching data size to image size (less the pixel needed for shift)
    fullData = np.concatenate((dataArray, dataArray[:(len(flattened) % len(dataArray) - 1)])) 

    # Especially helpful for alpha
    # Localizing would be better, but more costly
    meanF = round(sum(flattened) / len(flattened))
    meanD = round(sum(fullData) / len(fullData))
    shiftOpt = meanF - meanD

    # Ensure shift in [0, 255]
    if max(fullData) + shiftOpt > 255:
        shift = 255 - max(fullData)
    elif min(fullData) + shiftOpt < 0:
        shift = 0 - min(fullData)
    else: 
        shift = shiftOpt

    # Prepending shift to the array allows for acquisition at decode, 
    # shift and pixCount may be worth storing in metadata rather than flattened[0] and flattened[1] in the future
    finalData = np.concatenate(([shift], fullData + shift))

    # finalData fully replaces flattened channel, unlike previous versions
    img[:, :, channel] = np.reshape(finalData, (img.shape[0], img.shape[1]))

    cv2.imwrite(outImgPath, img)

    return 0


def channelToData(inImgPath, outDataPath, channel, fileSize):
    img = cv2.imread(inImgPath, cv2.IMREAD_UNCHANGED)

    if os.path.exists(outDataPath):
        os.remove(outDataPath)

    outDataFile = open(outDataPath, "wb")

    # -2 is indicative of a non-existent channel
    try:
        flattened = img[:, :, channel].flatten()
    except:
        return -2

    # dataToChannel writes the shift utilized for encoding, the inverse operator must be used here (+ -> -, - -> +)
    shift = -1 * (flattened[0])

    pixCount = flattened[1] + shift

    fileSize = len(flattened) / pixCount - 2 if fileSize == -1 else fileSize

    # Split array of (fileSize, pixCount) into three arrays of (fileSize, 1) for summation
    dataArr = flattened[2:fileSize*pixCount + 2].reshape([fileSize, pixCount]) + shift
    byteArrs = np.split(dataArr, pixCount, 1)
    
    # flattenedFin should be dataToChannel's np.array(data)
    flattenedFin = np.array(np.sum(byteArrs, 0).flatten()).astype(np.byte)
    outData = bytes(flattenedFin)

    outDataFile.write(outData)

    return 0


def LSBEncode(inImgPath, data, outImgPath, mode):
    
    # In this case, -2 is indicative of an invalid mode
    if mode > 8 or mode < 1 or not float(mode).is_integer():
        return -2

    inImg = cv2.imread(inImgPath, cv2.IMREAD_UNCHANGED)

    # Greater channel count increases data capacity; 
    # Won't remove existing alpha from images, but adds channel for jpgs and non-alphas
    if inImg.shape[2] < 4:
        inImg = cv2.cvtColor(inImg, cv2.COLOR_RGB2RGBA)

    # Creates a bitstring padded to a multiple of {mode}
    dataBitString = list(BitArray(bytes=data).bin) 
    dataBitString += ["0"] * (mode - len(dataBitString) % mode if len(dataBitString) % mode else 0)

    # Initial array of data, padding 0s will be cut during bitString slicing at decode
    dataArray = np.array(dataBitString).reshape([len(dataBitString) // mode, mode])

    # The (bytes, bits) model is key to encoding LSB without iteration
    # (shaped bytes -> flattened bytes -> BitArray -> bitString -> list of bits -> flattened bits -> (bytes, bits))

    flattened = inImg.flatten()
    imgBits = np.array(list(BitArray(bytes=flattened).bin)).reshape([len(flattened), 8])

    if imgBits.shape[0] < dataArray.shape[0]:
        return -1

    # matches dataArray to the length of the image, reducing suspicion due to a cutoff of noise
    dataLong = np.concatenate([dataArray]*(imgBits.shape[0] // dataArray.shape[0]) + [dataArray[0:(imgBits.shape[0] % dataArray.shape[0])]])

    # Merges imgBits of (bytes, 8-mode) and dataLong, of (bytes, mode) to a resulting image of (bytes, bits)
    fullArray = np.concatenate((imgBits[:, :(8 - mode)], dataLong), 1)

    # ((bytes, bits) -> flattened bits -> bitString -> BitArray -> flattened bytes -> shaped bytes); 

    outputArr = np.array(bytearray(BitArray(bin="".join(fullArray.flatten())).bytes)).reshape(inImg.shape[0], inImg.shape[1], inImg.shape[2])

    cv2.imwrite(outImgPath, outputArr)

    return 0


def LSBDecode(inImgPath, outPath, mode, fileSize):

    # In this case, -2 is indicative of an invalid mode
    if not mode in list(range(1, 9)) + [-2, -1]:
        return -2

    inImg = cv2.imread(inImgPath, cv2.IMREAD_UNCHANGED)

    # Removes the output file, if it already exists.
    if os.path.exists(outPath):
        os.remove(outPath)

    outFile = open(outPath, "wb")

    # (shaped bytes -> flattened bytes -> BitArray -> bitString -> list of bits -> flattened bits -> (bytes, bits)) 
    flattened = inImg.flatten()
    imgBits = np.array(list(BitArray(bytes=flattened).bin)).reshape([len(flattened), 8])

    if fileSize > len(flattened):
        Utils.raiseErrorAndExit("fileSize provided too large for image, do these values appear correct?"
                                f"\nLSBMode: {mode if mode != -1 else 'Undetermined - Using File Size'}"
                                f"\nFile Size: {str(fileSize) + ' bytes' if fileSize != -1 else 'Undetermined - Using LSBMode'}"
                                )

    # Same process as in Utils.py to determine optimal mode, fileSize is reset to maximum incase the user was low
    if mode == -1: 
        mode = fileSize*8 // len(flattened) + 1
        print(f"Determined {mode} as optimal LSBMode\nCaution: \n\tThere is a possibility this was not the mode used for encoding \n\tThe output file may be corrupted\n")
        fileSize = -1
    elif mode == -2:
        mode = fileSize*8 // len(flattened) + 1    

    # Will read every byte from the image if no fileSize could be read from metadata
    fileSize = len(flattened) * mode // 8 if fileSize == -1 else fileSize

    # Relevant bits are extracted, padding 0s are dropped
    # (bytes, bits) -> ({fileSizeBits/mode} bytes, {mode} bits) -> padded flattened bits ->  relevant flattened bits -> bitString
    bits = "".join(imgBits[0:(fileSize * 8 // mode), (8 - mode):].flatten())[0:fileSize * 8]

    # bitString -> BitArray -> bytes -> file
    outFile.write(BitArray(bin=bits).bytes)

    return 0


def LSBCEncode(inImgPath, data, outImgPath, mode, channel):

    # In this case, -3 is indicative of an invalid mode
    if mode > 8 or mode < 1 or not float(mode).is_integer():
        return -3

    inImg = cv2.imread(inImgPath, cv2.IMREAD_UNCHANGED)

    # Greater channel count increases data capacity; 
    # Won't remove existing alpha from images, but adds channel for jpgs and non-alphas
    if inImg.shape[2] < 4:
        inImg = cv2.cvtColor(inImg, cv2.COLOR_RGB2RGBA)

    # Creates a bitstring padded to a multiple of {mode}
    dataBitString = list(BitArray(bytes=data).bin) 
    dataBitString += ["0"] * (mode - len(dataBitString) % mode if len(dataBitString) % mode else 0)

    # Initial array of data, padding 0s will be cut during bitString slicing at decode
    dataArray = np.array(dataBitString).reshape([len(dataBitString) // mode, mode])

    # The (bytes, bits) model is key to encoding LSB without iteration
    # (shaped bytes -> flattened channel bytes -> BitArray -> bitString -> list of bits -> flattened bits -> (bytes, bits))

    try:
        flattened = inImg[:, :, channel].flatten()
    except:
        return -2
    
    imgBits = np.array(list(BitArray(bytes=flattened).bin)).reshape([len(flattened), 8])

    if imgBits.shape[0] < dataArray.shape[0]:
        return -1

    # matches dataArray to the length of the image, reducing suspicion due to a cutoff of noise
    dataLong = np.concatenate([dataArray] * (imgBits.shape[0] // dataArray.shape[0]) + [dataArray[0:(imgBits.shape[0] % dataArray.shape[0])]])

    # Merges imgBits of (bytes, 8-mode) and dataLong, of (bytes, mode) to a resulting image of (bytes, bits)
    fullArray = np.concatenate((imgBits[:, :(8-mode)], dataLong), 1)

    # ((bytes, bits) -> flattened bits -> bitString -> BitArray -> flattened bytes -> shaped channel bytes -> full img); 

    outputArr = np.array(bytearray(BitArray(bin="".join(fullArray.flatten())).bytes))

    inImg[:, :, channel] = np.reshape(outputArr, (inImg.shape[0], inImg.shape[1]))

    cv2.imwrite(outImgPath, inImg)

    return 0

def LSBCDecode(inImgPath, outPath, mode, channel, fileSize):
    
    # In this case, -1 is indicative of an invalid mode, this error should never occur given the choices for LSBMode
    if not mode in list(range(1, 9)) + [-2, -1]:
        return -1

    inImg = cv2.imread(inImgPath, cv2.IMREAD_UNCHANGED)

    # Removes the output file, if it already exists.
    if os.path.exists(outPath):
        os.remove(outPath)

    outFile = open(outPath, "wb")

    # (shaped bytes -> flattened bytes -> BitArray -> bitString -> list of bits -> flattened bits -> (bytes, bits)) 
    # -2 is indicitive of a non-existant channel
    try: 
        flattened = inImg[:, :, channel].flatten()
    except:
        return -2

    imgBits = np.array(list(BitArray(bytes=flattened).bin)).reshape([len(flattened), 8])

    if fileSize > len(flattened):
        Utils.raiseErrorAndExit("fileSize provided too large for image, do these values appear correct?"
                                f"\nLSBMode: {mode if mode != -1 else 'Undetermined - Using File Size'}"
                                f"\nChannel: {channel + 1}"
                                f"\nFile Size: {str(fileSize) + ' bytes' if fileSize != -1 else 'Undetermined - Using LSBMode'}"
                                )

    # Same process as in Utils.py to determine optimal mode, fileSize is reset to maximum incase the user was low
    if mode == -1: 
        mode = fileSize*8 // len(flattened) + 1
        print(f"\nDetermined {mode} as optimal LSBMode\nCaution: \n\tThere is a possibility this was not the mode used for encoding \n\tThe output file may be corrupted\n")
        fileSize = -1
    elif mode == -2:
        mode = fileSize*8 // len(flattened) + 1

    # Will read every byte from the image if no fileSize could be read from metadata
    fileSize = len(flattened)*mode // 8 if fileSize == -1 else fileSize

    # Relevant bits are extracted, padding 0s are dropped
    # (bytes, bits) -> ({fileSizeBits/mode} bytes, {mode} bits) -> padded flattened bits ->  relevant flattened bits -> bitString
    bits = "".join(imgBits[0:(fileSize*8//mode), (8-mode):].flatten())[0:fileSize*8]

    # bitString -> BitArray -> bytes -> file
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
        print(f"Channel: {metadata[1][0] + 1}")
        print(f"File Size: {metadata[2]}")
        print(f"File Extension: {metadata[3]}")

        returnValue = channelToData(inImgPath, f"{outPath}.{metadata[3]}", metadata[1][0], metadata[2])

    elif metadata[0] == Utils.LSBEncode:
        print("Encoding Method: LSBEncode")
        print(f"LSBMode: {metadata[1][0]}")
        print(f"File Size: {metadata[2]}")
        print(f"File Extension: {metadata[3]}")

        returnValue = LSBDecode(inImgPath, f"{outPath}.{metadata[3]}", metadata[1][0], metadata[2])

    elif metadata[0] == Utils.LSBCEncode:
        print("Encoding Method: LSBCEncode")
        print(f"LSBMode: {metadata[1][0]}")
        print(f"Channel: {metadata[1][1]}")
        print(f"File Size: {metadata[2]}")
        print(f"File Extension: {metadata[3]}")

        returnValue = LSBCDecode(inImgPath, f"{outPath}.{metadata[3]}", metadata[1][0], metadata[1][1] - 1, metadata[2])
    else:
        return -3



    # Returns the return value of the method that was used.
    # Should be 0 if there was no errors.
    return returnValue
