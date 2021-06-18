# ImageSteganography—Hiding Data in Plain Sight!
## Introduction:

You can use this program to hide data into images using steganography.

Here is a Wikipedia article on steganography if you don't know what it is:
https://en.wikipedia.org/wiki/Steganography

## Script Requirements:
1. Python 3

## Python Script Usage:
1. Place all of the files you want to hide into the image in a folder
2. Run the `main.py` script with the following arguments: 

   - Windows: `python main.py --imgIn <input image path> --dataFolder <folder with the data to hide> <output image path>`
   - Linux: `python3 main.py --imgIn <input image path> --dataFolder <folder with the data to hide> <output image path>`

If you need any help, you can type:
   - Windows: `python main.py --help`
   - Linux: `python3 main.py --help`

## CLI Usage:
1. Place all of the files you want to hide into the image in a folder
2. Run the CLI with the following arguments:
   - Windows: `ImageSteganography.exe --imgIn <input image path> --dataFolder <folder with the data to hide> <output image path>`
   - Linux: `./ImageSteganography --imgIn <input image path> --dataFolder <folder with the data to hide> <output image path>`

If you need any help, you can type:
   - Windows: `ImageSteganography.exe --help`
   - Linux: `./ImageSteganography --help`

## View the Hidden Data:
Open the output image file in a zip extractor, and extract it to view the hidden data inside of the image.

I used 7-Zip, but most zip extractors should work.

## TODO:
1. Add more methodes of using steganography to hide data into images
2. Maybe add methodes of using steganography for non-image file types
