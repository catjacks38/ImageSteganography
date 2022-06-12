# ImageSteganography—Hiding Data in Plain Sight!
## Introduction:

You can use this program to hide data into images using steganography.

Here is a Wikipedia article on steganography, if you don't know what it is:
https://en.wikipedia.org/wiki/Steganography

## Script Requirements:
Script made for Python 3

Install requirements with `pip3 install -r requirements.txt`

## CLI Usage:

`ImageSteganography [--help/-h] --method/-m {append, LSBEncode, LSBDecode, LSBCEncode, LSBCDecode, dataToChannel, channelToData, autoDecode, discordEncode} --input/-i <input file path> [--data/-d <data file path>] [--channel/-c <channel>] [--LSBMode {1-8}] [--overide/-o <override dict>] [--lightMode/-L] <output file path>`

## Argument Explanation:
`--help/-h`: Shows the help screen. (optional)

`--method/-m`: Which method will be use for encoding/decoding data in the image. It can only be these:
1. append
2. LSBEncode
3. LSBDecode
4. LSBCEncode
5. LSBCDecode
6. dataToChannel
7. channelToData
8. autoDecode
9. discordEncode

(required)

`--input/-i`: The input file. (required)

`--data/-d`: The original source data to encode into the image. Only required for the "append", "LSBEncode", "LSBCEncode", and "dataToChannel" methods.* (optional/required)

`--channel/-c`: The image channel to encode/decode the data from. It's a number from one to four. Channel one is red, channel two is green, channel three is blue, and channel four is alpha. You must use this argument for the "dataToChannel", "channelToData", "LSBCEncode", and "LSBCDecode" methods. (optional/required)

`--LSBMode/-l`: The amount of least significant bits that will be used to encode/decode the data per pixel. Can only be a value from one to eight. If the flag isn't used/specified for the "LSBEncode" or the "LSBCEncode" method, the optimal LSBMode will be automatically selected. If the flag isn't used/specified for the "LSBDecode" or "LSBCDecode" methods, the program will attempt to read metadata or request an approximate output file size from the user to automatically select LSBMode as a last resort. (optional/recommended)

`--override/-o`: Intended for developers, this flag bypasses all metadata checks and accepts a properly escaped and json-formatted dict containing variables to be set. Presently, `fileSize` in bytes (float -> int) and `bypassNullLSB` (bool) are the only arguments accepted, `fileSize` being treated as an estimate excepting the use of `bypassNullLSB` or the presence an LSBMode flag. `bypassNullLSB` changes the behavior of `fileSize` from an estimate (used for LSBMode calculation, but size of output file is the maximum possible given image size and LSBMode) to a hard output size (exact number of bytes, as it would be with an explicit LSBMode). Bash and most other quote-neutral terminals will accept `{\"fileSize\":9e5}`, Powershell requires ``{\`"fileSize\`":9e5}``. All dict keys are optional, so an empty dict can be passed to just ignore corrupted/incorrect metadata. (optional/cautioned)

`--lightMode/-L`: If you want to the image to be hidden to light mode users. By default, the image will hidden to dark mode users. (optional)


The last positional argument is the path of the output file to save. If the "autoDecode" method is used, provide a file path without the extension. The "autoDecode" method will automatically put the correct file extension at the end of the path. (required)

\**If you are using the "append" method the source data must be a folder. But if you are using the "LSBEncode", the "LSBCEncode", or the "dataToChannel" method, the source data must be a file.*

## What does each Method do?
1. The "append" method archives a folder in zip format, and appends it to the start of the image. The "append" method will not change the pixels in the image, but it will increase the file size from the original image.
2. The "dataToChannel" method encodes the data into a specific channel. This method is less efficient than the "dataToPix" method, but it changes the pixel data of the image less. This should not increase image size too much.
3. The "LSBEncode" method writes each bit from the source data into the least significant bits of your choice (LSBMode) of each channel value in the image. Using a smaller LSBMode is less noticeable than a higher LSBMode, but you will need a larger image to store the same amount of data. If you set the LSBMode to eight, it will give results like what the old "dataToPix" method used to do. Due to the higher complexity of this method, it takes longer to encode and decode compared to the other methods. But it isn't too much longer.
4. The "LSBCEncode" method does the same thing as the "LSBEncode" method, but it writes the bits to just one channel (similar to what the "dataToChannel" method does).
5. The "discordEncode" method converts the input image to grayscale. After that, the final image's alpha channel gets set to the grayscale image. Then the final image's RGB values are set to (54, 57, 63) unless the `--lightMode` flag is supplied, then the RGB values will be set to (255, 255, 255).

## How to View the Hidden Data:

### Suggested method (try this first):
Run this command:

`ImageSteganography --method autoDecode --input <the path to the input image you want to decode> <path to decoded output without the file extension>`

If this method returns the error, "Input image has corrupted or non-existent metadata to be auto decoded.", the "autoDecode" method will not work. Try the other methods.

### If the image uses the "discordEncode" method:
Open the image in the Discord image previewer.

### If the image uses the "append" method:
Open the image in a zip extractor, and extract the contents. Any zip extractor should work. I used 7-Zip while testing this method.

### If the image uses the "LSBEncode" method:
Run this command:

`ImageSteganography --method LSBDecode --input <the path to the image you want to decode> --LSBMode <the LSBMode of the encoded data> <path to the decoded data that will be saved>`

### If the image uses the "dataToChannel" method:
Run this command:

`ImageSteganography --method channelToData --input <the path to the image you want to decode> --channel <channel where the data was encoded into> <path to the decoded data that will be saved>`

### If the image uses the "LSBCEncode" method:
Run this command:

`ImageSteganography --method LSBDecode --input <the path to the image you want to decode> --channel <channel where the data was encoded into> --LSBMode <the LSBMode of the encoded data> <path to the decoded data that will be saved>`
