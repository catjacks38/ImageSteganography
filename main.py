import ImageSteganography
import os
import argparse
import Utils
from Utils import raiseErrorAndExit
from sys import exit


def main():
    parser = argparse.ArgumentParser(description="A simple program that can be used to encode data into images using steganography.")

    # Adds arguments to parser.
    parser.add_argument("--method", "-m", type=str, choices=["append", "LSBEncode", "LSBDecode", "LSBCEncode", "LSBCDecode", "dataToChannel", "channelToData", "autoDecode"], help="The method that will be used to encode/decode the data.", required=True)

    parser.add_argument("--input", "-i", type=str, help="The path to the image you want to decode/encode.", required=True)
    parser.add_argument("--data", "-d", type=str, help="The path to the data you want to encode into the output image.")
    
    parser.add_argument("--LSBMode", "-l", type=int, choices=range(1, 9), help="Which LSB mode to encode/decode the image with.")
    parser.add_argument("--channel", "-c", type=int, help="The channel you would like to use to encode/decode the data")

    parser.add_argument("output", type=str, help="The path of where the encoded or decoded data will be saved to. If the \"autoDecode\" method is selected, provide the file path with no extension (the correct extension will be automatically put at the end of the file path).")

    args = parser.parse_args()
    fileSize = 0

    # Input file path check.
    if not os.path.exists(args.input):
         raiseErrorAndExit("File not found. Please check your file paths, and make sure they exist.")

    # Data flag and file path check:
    if not args.method in ["LSBDecode", "channelToData", "autoDecode", "LSBCDecode"]:
        if bool(args.data):
            if not os.path.exists(args.data):
                raiseErrorAndExit("File not found. Please check your file paths, and make sure they exist.")
        else:
            raiseErrorAndExit("Missing Data Flag.")

    # Channel flag check.
    if (args.method in ["dataToChannel", "channelToData", "LSBCEncode", "LSBCDecode"]) and not bool(args.channel):
        raiseErrorAndExit("Missing \"channel\" flag.")

    # LSBMode flag check.
    if (args.method in ["LSBEncode", "LSBCEncode"]) and not bool(args.LSBMode):
        print("Missing \"LSBMode\" flag.\nAttempting to find optimal LSBMode...")
        with open(args.data, "rb") as dataFile:
            readData = dataFile.read()
            args.LSBMode = Utils.optimalLSBMode(args.input, readData, False if args.method == "LSBEncode" else True)

            if args.LSBMode == -1:
                raiseErrorAndExit(f"Could not find suitable LSBMode for image, because source data size of {len(readData)} B is too large.")

            print(f"Using optimal LSBMode of {args.LSBMode}!\n")

    elif (args.method in ["LSBDecode", "LSBCDecode"]) and not bool(args.LSBMode):
        print("Missing \"LSBMode\" flag, attempting to read metadata...")
        try:
            args.LSBMode = Utils.readMetadata(args.input)[1][0]
        except:
            try: 
                fileSize = int(float(input("Unable to read LSBMode, enter estimated size of data in bytes, scientific notation using \"e\" is permitted: \n")))
                args.LSBMode = -1
                os.system("cls" if os.name == "nt" else "clear")
            except:
                raiseErrorAndExit("Either LSBMode or fileSize must be provided for decoding images without metadata.")


    # PNG file checks.
    if (args.method in ["LSBEncode", "LSBCEncode", "dataToChannel"]) and args.output.split(".")[-1] != "png":
        raiseErrorAndExit("Output file must be a \"PNG\" file.")

    if args.method == "autoDecode" and args.input.split(".")[-1] != "png":
        raiseErrorAndExit("Input must be a \"PNG\" file.")

    # Argument Parsing.
    if args.method == "append":
        if os.path.isdir(args.data):
            with open(args.input, "rb") as imgIn:
                imgInData = imgIn.read()

            ImageSteganography.appendDataToImage(imgInData, args.data, args.output)
        else:
            raiseErrorAndExit(f"The path, \"{args.data}\" is  not a folder.")

    elif args.method == "LSBEncode":
        if os.path.isfile(args.data):
            with open(args.data, "rb") as dataFile:
                data = dataFile.read()
        else:
            raiseErrorAndExit(f"The path, \"{args.data}\" is not a file.")

        returnValue = ImageSteganography.LSBEncode(args.input, data, args.output, args.LSBMode)

        if returnValue == -1:
            raiseErrorAndExit(f"Data too Large for Image. {len(bytearray(data))} B")
        elif returnValue == -2:
            raiseErrorAndExit(f"The LSBMode provided, {args.LSBMode if args.LSBMode != -1 else 'Undetermined - Using File Size'} would appear to be invalid.")

        Utils.saveMetadata(args.output, Utils.LSBEncode, args.LSBMode, len(data), args.data.split(".")[-1])

    elif args.method == "LSBDecode":
        try:
            fileSize = Utils.readMetadata(args.input)[2]
        except:
            if not fileSize:
                fileSize = -1
            

        returnValue = ImageSteganography.LSBDecode(args.input, args.output, args.LSBMode, fileSize)

        if returnValue == -1:
            raiseErrorAndExit(f"The LSBMode provided, {args.LSBMode if args.LSBMode != -1 else 'Undetermined - Using File Size'} would appear to be invalid.")

    elif args.method == "LSBCEncode":
        if os.path.isfile(args.data):
            with open(args.data, "rb") as dataFile:
                data = dataFile.read()
        else:
            raiseErrorAndExit(f"The path, \"{args.data}\" is not a file.")
        
        returnValue = ImageSteganography.LSBCEncode(args.input, data, args.output, args.LSBMode, args.channel - 1)

        if returnValue == -1:
            raiseErrorAndExit(f"Data too Large for Image. {len(bytearray(data))} B")
        elif returnValue == -2:
            raiseErrorAndExit(f"There is no channel {args.channel} in the image")
        elif returnValue == -3:
            raiseErrorAndExit(f"The LSBMode provided, {args.LSBMode if args.LSBMode != -1 else 'Undetermined - Using File Size'} would appear to be invalid.")

        Utils.saveMetadata(args.output, Utils.LSBCEncode, f"{args.LSBMode} {args.channel}", len(data), args.data.split(".")[-1])

    elif args.method == "LSBCDecode":
        try:
            fileSize = Utils.readMetadata(args.input)[2]
        except:
            if not fileSize:
                fileSize = -1
            

        returnValue = ImageSteganography.LSBCDecode(args.input, args.output, args.LSBMode, args.channel - 1, fileSize)

        if returnValue == -1:
            raiseErrorAndExit(f"The LSBMode provided, {args.LSBMode if args.LSBMode != -1 else 'Undetermined - Using File Size'} would appear to be invalid.")
        elif returnValue == -2:
            raiseErrorAndExit(f"There is no channel {args.channel} in the image")

    elif args.method == "dataToChannel":
        if os.path.isfile(args.data):
            with open(args.data, "rb") as dataFile:
                data = dataFile.read()

        returnValue = ImageSteganography.dataToChannel(args.input, data, args.output, args.channel - 1)

        if returnValue == -1:
            raiseErrorAndExit(f"Data file too large for image. Data file size: {len(data)}")
        elif returnValue == -2:
            raiseErrorAndExit(f"There is no channel {args.channel} in the image.")

        Utils.saveMetadata(args.output, Utils.dataToChannel, args.channel - 1, len(data), args.data.split(".")[-1])

    elif args.method == "channelToData": 
        try:
            fileSize = Utils.readMetadata(args.input)[2]
        except:
            fileSize = -1
            

        returnValue = ImageSteganography.channelToData(args.input, args.output, args.channel - 1, fileSize)

        if returnValue == -2:
            raiseErrorAndExit(f"There is no channel {args.channel} in the image.")

    elif args.method == "autoDecode":
        returnValue = ImageSteganography.autoDecode(args.input, args.output)

        if returnValue != 0:
            raiseErrorAndExit("Input image has corrupted or non-existent metadata to be auto decoded.")

    # Prints success message and exits function.
    print("Operation Successfully Completed!")
    if args.method == "autoDecode":
        metadata = Utils.readMetadata(args.input)
        print(f"Your file was saved to \"{os.path.abspath(args.output)}.{metadata[3]}\".")
    else:
        print(f"Your file was saved to \"{os.path.abspath(args.output)}\".")

    return 0


if __name__ == "__main__":
    main()
    exit(0)
