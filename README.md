# ImageSteganography—Hiding Data in Plain Sight!
## Introduction:

You can use this program to hide data into images using steganography.

Here is a Wikipedia article on steganography, if you don't know what it is:
https://en.wikipedia.org/wiki/Steganography

## Script Requirements:
1. Python 3

## CLI Usage:
Windows: `ImageSteganography.exe [--help/-h] --method/-m {append, dataToPix, pixToData} --input/-i <input file path> [--data/-d <path to data to encode>] <file output path>`

Linux: `./ImageSteganography [--help/-h] --method/-m {append, dataToPix, pixToData} --input/-i <input file path> [--data/-d <path to data to encode>] <file output path>`

## Argument Explanation:
`--help/-h`: Shows the help screen. (optional)

`--method/-m`: Which method will be use for encoding/decoding data in the image. It can only be "append", "dataToPix", or "pixToData". (required)

`--input/-i`: The input file. (required)

`--data/-d`: The original source data to encode into the image. Only required for the "dataToPix" and "append" methods.* (optional/required)

The last positional argument is the path of the output file to save. (required)

\**If you are using the "append" method the source data must be a folder. But if you are using the "dataToPix" method the source data must be a file.*

## What does each Method do?
1. The "append" method archives a folder in zip format, and appends it to the start of the image. The "append" method will not change the pixels in the image, but it will increase the file size from the original image.
2. The "dataToPix" method converts the data in the original source file to pixels that are written onto the image. This method does not increase the file size of the image, but it will change the pixels in the image.

## How to View the Hidden Data:
### If the image uses the "append" method:
Open the image in a zip extractor, and extract the contents. Any zip extractor should work. I used 7-Zip while testing this method.

### If the image uses the "dataToPix" method:
Run this command:

Windows: `ImageSteganography.exe --method pixToData --input <the path to the image you want to decode> <path to the decoded data that will be saved>`

Linux: `./ImageSteganography --method pixToData --input <the path to the image you want to decode> <path to the decoded data that will be saved>`

## TODO:
1. Add more methodes of using steganography to hide data into images
2. Maybe add methodes of using steganography for non-image file types
