import ImageSteganography
import os
import argparse
import Utils
from Utils import raiseErrorAndExit
from sys import exit


def main():
    parser = argparse.ArgumentParser(description="A simple program that can be used to encode data into images using steganography.")

    # Adds arguments to parser.
    parser.add_argument("--method", "-m", type=str, choices=["append", "LSBEncode", "LSBDecode", "dataToChannel", "channelToData", "autoDecode"], help="The method that will be used to encode/decode the data.", required=True)

    parser.add_argument("--input", "-i", type=str, help="The path to the image you want to decode/encode.", required=True)
    parser.add_argument("--data", "-d", type=str, help="The path to the data you want to encode into the output image.")

    parser.add_argument("--channel", "-c", type=int, help="The channel you would like to use to encode/decode the data")
    parser.add_argument("--LSBMode", "-l", type=int, choices=range(1, 9), help="Which LSB mode to encode/decode the image with.")

    parser.add_argument("output", type=str, help="The path of where the encoded or decoded data will be saved to. If the \"autoDecode\" method is selected, provide the file path with no extension (the correct extension will be automatically put at the end of the file path).")

    args = parser.parse_args()

    # Input file path check.
    if not os.path.exists(args.input):
         raiseErrorAndExit("File not found. Please check your file paths, and make sure they exist.")

    # Data flag and file path check:
    if args.method != "LSBDecode" and args.method != "channelToData" and args.method != "autoDecode":
        if bool(args.data):
            if not os.path.exists(args.data):
                raiseErrorAndExit("File not found. Please check your file paths, and make sure they exist.")
        else:
            raiseErrorAndExit("Missing Data Flag.")

    # Channel flag check.
    if (args.method == "dataToChannel" or args.method == "channelToData") and not bool(args.channel):
        raiseErrorAndExit("Missing \"channel\" flag.")

    # LSBMode flag check.
    if (args.method == "LSBDecode" or args.method == "LSBEncode") and not bool(args.LSBMode):
        raiseErrorAndExit("Missing \"LSBMode\" flag.")

    # PNG file checks.
    if (args.method == "LSBEncode" or args.method == "dataToChannel") and args.output.split(".")[-1] != "png":
        raiseErrorAndExit("Output file must be a \"PNG\" file.")

    if args.method == "autoDecode" and args.input.split(".")[-1] != "png":
        raiseErrorAndExit("Input must be a \"PNG\" file.")

    # Argument Parsing.
    if args.method == "append":
        if os.path.isdir(args.data):
            imgIn = open(args.input, "rb")
            imgInData = imgIn.read()

            ImageSteganography.appendDataToImage(imgInData, args.data, args.output)
        else:
            raiseErrorAndExit(f"The path, \"{args.data}\" is  not a folder.")

    elif args.method == "LSBEncode":
        if os.path.isfile(args.data):
            dataIn = open(args.data, "rb")
            dataInData = dataIn.read()
        else:
            raiseErrorAndExit(f"The path, \"{args.data}\" is not a file.")

        returnValue = ImageSteganography.LSBEncode(args.input, dataInData, args.output, args.LSBMode)

        if returnValue == -1:
            raiseErrorAndExit(f"Data too Large for Image. {len(bytearray(dataInData))} B")

        Utils.saveMetadata(args.output, Utils.LSBEncode, args.LSBMode, len(dataInData), args.data.split(".")[-1])

    elif args.method == "LSBDecode":
        ImageSteganography.LSBDecode(args.input, args.output, args.LSBMode, 0)

    elif args.method == "dataToChannel":
        dataFile = open(args.data, "rb")
        data = dataFile.read()

        returnValue = ImageSteganography.dataToChannel(args.input, data, args.output, args.channel - 1)

        if returnValue == -1:
            raiseErrorAndExit(f"Data file too large for image. Data file size: {len(bytearray(data))}")
        elif returnValue == -2:
            raiseErrorAndExit(f"There is no {args.channel} channel in the image.")

        Utils.saveMetadata(args.output, Utils.dataToChannel, args.channel - 1, 0, args.data.split(".")[-1])

    elif args.method == "channelToData":
        returnValue = ImageSteganography.channelToData(args.input, args.output, args.channel - 1)

        if returnValue == -2:
            raiseErrorAndExit(f"There is no {args.channel} channel in the image.")

    elif args.method == "autoDecode":
        returnValue = ImageSteganography.autoDecode(args.input, args.output)

        if returnValue != 0:
            raiseErrorAndExit("Input image has corrupted or non-existent metadata to be auto decoded.")

    # Prints success message and exits function.
    print("Operation Successfully Completed!")
    print(f"Your file was saved too \"{os.path.abspath(args.output)}\".")

    return 0


if __name__ == "__main__":
    main()
    exit(0)
