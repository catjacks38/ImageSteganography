import imgSteganography
import os
import argparse


def raiseErrorAndExit(error):
    print("Sheesh, seems like there was an error while running this program:\n")

    for _ in range(len(error) + 4):
        print("=", end="")

    print(f"\n| {error} |")

    for _ in range(len(error) + 4):
        print("=", end="")

    print("\n\nIf this doesn't help, then you might just need to play more.")

    exit(-1)


def main():
    parser = argparse.ArgumentParser(description="A simple program that is used to encode data into images using steganography.")

    parser.add_argument("--imgIn", type=str, help="The path to the original image you want to encode the data into.", required=True)
    parser.add_argument("--dataFolder", type=str, help="The path to the folder you want to encode into the output image. (Everything inside of the folder will be encoded into the output image--the root folder itself will no be encoded into the output image.)", required=True)
    parser.add_argument("imgOut", type=str, help="The output path of the new image with the data encoded in it. (I would suggest giving the output image the same file extension as the input image, but you do you.)")

    args = parser.parse_args()

    if not os.path.exists(args.imgIn) or not os.path.exists(args.dataFolder):
        raiseErrorAndExit("File not found. Please check your file paths, and make sure they exist.")

    imgIn = open(args.imgIn, "rb")

    imgSteganography.appendDataToImg(imgIn, args.imgOut, args.dataFolder)

    print("Operation Successfully Completed!")
    print(f"Your file was saved too \"{os.path.abspath(args.imgOut)}\".")


if __name__ == "__main__":
    main()
