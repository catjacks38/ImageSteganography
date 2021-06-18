# ImageSteganography: Hiding Data in Plain Sight!
## Introduction:

You can use this program to hide data into images using steganography.

Here is a Wikipedia article on steganography if you don't know what it is:
https://en.wikipedia.org/wiki/Steganography

## Usage:
1. Place all of the files you want to hide into the image in a folder
2. Run the `main.py` script with the following arguments: 

   - Windows: `python main.py --imgIn <input image path> --dataFolder <folder with the data to hide> <output image path>`
   - Linux: `python3 main.py --imgIn <input image path> --dataFolder <folder with the data to hide> <output image path>`
3. Open the output image file in any zip extractor, and extract it to view the hidden data inside the image.

If you need any help, you can type in:
   - Windows: `python main.py --help`
   - Linux: `python main.py --help`

## TODO:
1. Add standalone executable CLI
2. Add more methodes of steganography in images
3. Maybe add methodes of steganography into non-image file types
