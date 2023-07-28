import math
import numpy as np
import tkinter as tk
from PIL import Image, ImageFont, ImageDraw

PIL_GRAYSCALE = 'L'
PIL_WIDTH_INDEX = 0
PIL_HEIGHT_INDEX = 3
GSCALE1 = "$@B%8&WM#*oahkbdpqwmZO0QLCJUYXzcvunxrjft/\|()1{}[]?-_+~<>i!lI;:,\"^`'. "
GSCALE2 = '@%#*+=-:. '
COMMON_MONO_FONT_FILENAMES = [
    'DejaVuSansMono.ttf',  # Linux
    '/System/Library/Fonts/Menlo.ttc',   # MacOS, I think
    'Consola.ttf',         # Windows, I think
]

def getAverageL(image):
    """
    Given PIL Image, return average value of grayscale value
    """
    # get image as numpy array
    im = np.array(image)

    # get shape
    w,h = im.shape

    # get average
    return np.average(im.reshape(w*h))

def covertImageToAscii(fileName, cols, scale, moreLevels):
    """
    Given Image and dims (rows, cols) returns an m*n list of Images
    """
    # declare globals
    # global gscale1, gscale2
    scale = 0.475
    # open image and convert to grayscale
    image = Image.open(fileName).convert('L')

    # store dimensions
    W, H = image.size[0], image.size[1]
    print("input image dims: %d x %d" % (W, H))

    # compute width of tile
    w = W/cols

    # compute tile height based on aspect ratio and scale
    h = w/scale

    # compute number of rows
    rows = int(H/h)
    
    print("cols: %d, rows: %d" % (cols, rows))
    print("tile dims: %d x %d" % (w, h))

    # check if image size is too small
    if cols > W or rows > H:
        print("Image too small for specified cols!")
        exit(0)

    # ascii image is a list of character strings
    aimg = []
    # generate list of dimensions
    for j in range(rows):
        y1 = int(j*h)
        y2 = int((j+1)*h)

        # correct last tile
        if j == rows-1:
            y2 = H

        # append an empty string
        aimg.append("")

        for i in range(cols):

            # crop image to tile
            x1 = int(i*w)
            x2 = int((i+1)*w)

            # correct last tile
            if i == cols-1:
                x2 = W

            # crop image to extract tile
            img = image.crop((x1, y1, x2, y2))

            # get average luminance
            avg = int(getAverageL(img))

            # look up ascii char
            if moreLevels:
                gsval = GSCALE1[int((avg*69)/255)]
            else:
                gsval = GSCALE2[int((avg*9)/255)]

            # append ascii char to string
            aimg[j] += gsval
    
    # return txt image
    return aimg

def textfile_to_image(textfile_path, RGBbc, RGBfc):
    """Convert text file to a grayscale image.

    arguments:
    textfile_path - the content of this file will be converted to an image
    font_path - path to a font file (for example impact.ttf)
    """
    # parse the file into lines stripped of whitespace on the right side
    with open(textfile_path) as f:
        lines = tuple(line.rstrip() for line in f.readlines())

    # choose a font (you can see more detail in the linked library on github)
    font = None
    large_font = 20  # get better resolution with larger size
    for font_filename in COMMON_MONO_FONT_FILENAMES:
        try:
            font = ImageFont.truetype(font_filename, size=large_font)
            print(f'Using font "{font_filename}".')
            break
        except IOError:
            print(f'Could not load font "{font_filename}".')
    if font is None:
        font = ImageFont.load_default()
        print('Using default font.')

    # make a sufficiently sized background image based on the combination of font and lines
    font_points_to_pixels = lambda pt: round(pt * 96.0 / 72)
    margin_pixels = 20

    # height of the background image
    tallest_line = max(lines, key=lambda line: font.getbbox(line)[PIL_HEIGHT_INDEX])
    max_line_height = font_points_to_pixels(font.getbbox(tallest_line)[PIL_HEIGHT_INDEX])
    realistic_line_height = max_line_height * 0.8  # apparently it measures a lot of space above visible content
    image_height = int(math.ceil(realistic_line_height * len(lines) + 2 * margin_pixels))

    # width of the background image
    widest_line = max(lines, key=lambda s: ((font.getbbox(s)[2])-(font.getbbox(s)[0])))
    max_line_width = font_points_to_pixels((font.getbbox(widest_line)[2])-(font.getbbox(widest_line)[0]))
    realistic_line_width = max_line_width * 0.75 
    image_width = int(math.ceil(realistic_line_width + (2 * margin_pixels)))

    # draw the background
    if RGBbc:
        background_color = tuple(map(int, RGBbc.split(",")))
        print(background_color)
    else:
        background_color = (255,255,255)  # white
    #Plum: (221,160,221)
    #White: (255,255,255)
    #HoneyDew: (240,255,240)
    #Khaki: (240,230,140)
    #PaleGreen (151,255,152)
    image = Image.new('RGB', (image_width, image_height), color=background_color)
    draw = ImageDraw.Draw(image)

    # draw each line of text
    if RGBfc:
        font_color = tuple(map(int, RGBfc.split(",")))
    else:
        font_color = (0,0,0)  # black
    horizontal_position = margin_pixels
    for i, line in enumerate(lines):
        vertical_position = int(round(margin_pixels + (i * realistic_line_height)))
        draw.text((horizontal_position, vertical_position), line, fill=font_color, font=font, stroke_width= 1)

    return image


def main():
    
    # Img to text
    img_file = str(input("Enter path for input img file (.jpg, .png, etc): "))
    text_file = (img_file.split('.'))[0]+'_ASCII.txt'
    out_file = str(input('Enter path to out file or leave blank for "inputfile_ASCII": '))
    if out_file == '':
        out_file = img_file.split('.')[0]+'_ASCII.'+img_file.split('.')[1]
    scale = 0.43
    cols = int(input("Enter the number of columns: "))
    ML = str(input("More levels? (y/n): "))
    RGBvaluebackground = (input("Enter RGB background value, leave blank for white EX: ###,###,###: "))
    RGBvaluetext = (input("Enter RGB text value, leave blank for black EX: ###,###,###: "))
    if ML == "y":
        moreLevels = True
    else:
        moreLevels = False
    print('generating ASCII text file...')
    aimg = covertImageToAscii(img_file, cols, scale, moreLevels)
    f = open(text_file, 'w')
    for row in aimg:
        f.write(row + '\n')
    f.close()
    print("ASCII text file written to %s" % text_file)

    # Text to image
    image = textfile_to_image(text_file, RGBvaluebackground, RGBvaluetext) 
    print('generating ASCII image file...')
    image.show()
    image.save(out_file)
    print("ASCII img file written to %s" % out_file)

if __name__ == '__main__':
    main()
    


