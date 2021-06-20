import ImageSteganography
import os
import argparse
from Utils import raiseErrorAndExit
from sys import exit


def main():
    parser = argparse.ArgumentParser(description="A simple program that can be used to encode data into images using steganography.")

    parser.add_argument("--method", "-m", type=str, choices=["append", "dataToPix", "pixToData", "dataToChannel", "channelToData"], help="The method that will be used to encode/decode the data.", required=True)

    parser.add_argument("--input", "-i", type=str, help="The path to the image you want to decode/encode.", required=True)
    parser.add_argument("--data", "-d", type=str, help="The path to the data you want to encode into the output image.")
    parser.add_argument("--channel", "-c", type=int, help="The channel you would like to use to encode/decode the data")
    parser.add_argument("output", type=str, help="The path of where the encoded or decoded data will be saved to.")

    args = parser.parse_args()

    if not os.path.exists(args.input):
         raiseErrorAndExit("File not found. Please check your file paths, and make sure they exist.")

    if args.method != "pixToData" and args.method != "channelToData":
        if bool(args.data):
            if not os.path.exists(args.data):
                raiseErrorAndExit("File not found. Please check your file paths, and make sure they exist.")
        else:
            raiseErrorAndExit("Missing Data Flag.")

    if (args.method == "dataToChannel" or args.method == "channelToData") and not bool(args.channel):
        raiseErrorAndExit("Missing channel flag.")

    if args.method == "append":
        if os.path.isdir(args.data):
            imgIn = open(args.input, "rb")
            imgInData = imgIn.read()

            ImageSteganography.appendDataToImage(imgInData, args.data, args.output)
        else:
            raiseErrorAndExit(f"The path, \"{args.data}\" is  not a folder.")

    elif args.method == "dataToPix":
        if args.input.split(".")[-1] != "bmp":
            raiseErrorAndExit("Not a \".bmp\"/bitmap type image.")
        if os.path.isfile(args.data):
            imgIn = open(args.input, "rb")
            imgInData = imgIn.read()

            dataIn = open(args.data, "rb")
            dataInData = dataIn.read()
        else:
            raiseErrorAndExit(f"The path, \"{args.data}\" is not a file.")

        returnValue = ImageSteganography.dataToPixels(imgInData, dataInData, args.output)

        if returnValue == -1:
            raiseErrorAndExit(f"Data too Large for Image. {len(bytearray(dataInData))} / {len(bytearray(imgInData))} B")

    elif args.method == "pixToData":
        if args.input.split(".")[-1] != "bmp":
            raiseErrorAndExit("Not a \".bmp\"/bitmap type image.")
        else:
            imgIn = open(args.input, "rb")
            imgInData = imgIn.read()

            ImageSteganography.pixelsToData(imgInData, args.output)

    elif args.method == "dataToChannel":
        dataFile = open(args.data, "rb")
        data = dataFile.read()

        returnValue = ImageSteganography.dataToChannel(args.input, data, args.output, args.channel - 1)

        if returnValue == -1:
            raiseErrorAndExit(f"Data file too large for image. Data file size: {len(bytearray(data))}")
        elif returnValue == -2:
            raiseErrorAndExit(f"There is no {args.channel} channel in the image.")

    elif args.method == "channelToData":
        returnValue = ImageSteganography.channelToData(args.input, args.output, args.channel - 1)

        if returnValue == -2:
            raiseErrorAndExit(f"There is no {args.channel} channel in the image.")

    print("Operation Successfully Completed!")
    print(f"Your file was saved too \"{os.path.abspath(args.output)}\".")

    return 0


if __name__ == "__main__":
    main()

    exit(0)
