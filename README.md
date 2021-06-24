# ImageSteganography—Hiding Data in Plain Sight!
## Introduction:

You can use this program to hide data into images using steganography.

Here is a Wikipedia article on steganography, if you don't know what it is:
https://en.wikipedia.org/wiki/Steganography

## Script Requirements:
1. Python 3
2. opencv-python
3. bitstring
4. tqdm
5. numpy
6. pillow

## CLI Usage:
Windows: `ImageSteganography.exe [--help/-h] --method/-m {append, LSBEncode, LSBDecode, dataToChannel, channelToData, autoDecode} --input/-i <input file path> [--data/-d <data file path>] [--channel/-c <channel>] [--LSBMode {1-8}] <output file path>`

Linux: `./ImageSteganography [--help/-h] --method/-m {append, LSBEncode, LSBDecode, dataToChannel, channelToData, autoDecode} --input/-i <input file path> [--data/-d <data file path>] [--channel/-c <channel>] [--LSBMode {1-8}] <output file path>`

## Argument Explanation:
`--help/-h`: Shows the help screen. (optional)

`--method/-m`: Which method will be use for encoding/decoding data in the image. It can only be these:
1. append
2. LSBEncode
3. LSBDecode
4. dataToChannel
5. channelToData
6. autoDecode

(required)

`--input/-i`: The input file. (required)

`--data/-d`: The original source data to encode into the image. Only required for the "dataToPix" and "append" methods.* (optional/required)

`--channel/-c`: The image channel to encode/decode the data from. It's a number from one to four. Channel one is red, channel two is green, channel three is blue, and channel four is alpha. You must use this argument for the "dataToChannel" and "channelToData" methods. (optional/required)

`--LSBMode/-l`: The amount of least significant bits that will be used to encode/decode the data per pixel. Can only be a value from one to eight. You must use this argument for the "LSBEncode" and "LSBDecode" methods. (optional/required)

The last positional argument is the path of the output file to save. If the "autoDecode" method is used, provide a file path without the extension. The "autoDecode" method will automatically put the correct file extension at the end of the path. (required)

\**If you are using the "append" method the source data must be a folder. But if you are using the "LSBEncode" or the "dataToChannel" methods, the source data must be a file.*

## What does each Method do?
1. The "append" method archives a folder in zip format, and appends it to the start of the image. The "append" method will not change the pixels in the image, but it will increase the file size from the original image.
2. The "dataToChannel" method encodes the data into a specific channel. This method is less efficient than the "dataToPix" method, but it changes the pixel data of the image less. This should not increase image size too much. I would suggest saving the image in a non-lossy image format—like bitmap or png.
3. The "LSBEncode" method writes each bit from the source data into the least significant bits of your choice (LSBMode) of each channel value in the image. Using a smaller LSBMode is less noticeable than a higher LSBMode, but you will need a larger image to store the same amount of data. If you set the LSBMode to eight, it will give results like what the old "dataToPix" method used to do. Due to the higher complexity of this method, it takes longer to encode and decode compared to the other methods. But it isn't too much longer.

## How to View the Hidden Data:

### Suggested method (try this first):
Run this command:

Windows: `ImageSteganography.exe --method autoDecode --input <the path to the input image you want to decode> <path to decoded output without the file extension>`

Linux: `./ImageSteganography --method autoDecode --input <the path to the input image you want to decode> <path to decoded output without the file extension>`

If this method returns the error, "Input image has corrupted or non-existent metadata to be auto decoded.", the "autoDecode" method will not work. Try the other methods.

### If the image uses the "append" method:
Open the image in a zip extractor, and extract the contents. Any zip extractor should work. I used 7-Zip while testing this method.

### If the image uses the "LSBEncode" method:
Run this command:

Windows: `ImageSteganography.exe --method LSBDecode --input <the path to the image you want to decode> --LSBMode <the LSBMode of the encoded data> <path to the decoded data that will be saved>`

Linux: `./ImageSteganography --method LSBDecode --input <the path to the image you want to decode> --LSBMode <the LSBMode of the encoded data> <path to the decoded data that will be saved>`

### If the image uses the "dataToChannel" method:
Run this command:

Windows: `ImageSteganography.exe --method channelToData --input <the path to the image you want to decode> --channel <channel where the data was encoded into> <path to the decoded data that will be saved>`

Linux: `./ImageSteganography --method channelToData --input <the path to the image you want to decode> --channel <channel where the data was encoded into> <path to the decoded data that will be saved>`

## TODO:
1. Add more methods of using steganography to hide data into images
2. Maybe add methods of using steganography for non-image file types
3. Improve and refactor code
