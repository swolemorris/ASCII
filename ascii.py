import math
import os
import numpy as np
import platform
import tkinter as tk
from tkinter import filedialog, colorchooser
from PIL import Image, ImageTk, ImageFont, ImageDraw
from datetime import datetime


new_BG_tuple = None
new_FG_tuple = None
PIL_GRAYSCALE = 'L'
PIL_WIDTH_INDEX = 0
PIL_HEIGHT_INDEX = 3
GSCALE1 = "$@B%8&WM#*oahkbdpqwmZO0QLCJUYXzcvunxrjft/\|()1{}[]?-_+~<>i!lI;:,\"^`'. "
GSCALE2 = '@%#*+=-:. '
COMMON_MONO_FONT_FILENAMES = [
    'DejaVuSansMono.ttf',  # Linux, I think
    '/System/Library/Fonts/Menlo.ttc',   # MacOS, I think
    'C:/Windows/Fonts/consola.ttf',         # Windows
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

    # Set scale depending on OS
    if platform.system() == 'Darwin':
        scale = 0.475
    elif platform.system() == 'Windows':
        scale = 0.572

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
        background_color = RGBbc
    else:
        background_color = (255,255,255)  # white
    image = Image.new('RGB', (image_width, image_height), color=background_color)
    draw = ImageDraw.Draw(image)

    # draw each line of text
    if RGBfc:
        font_color = RGBfc
    else:
        font_color = (0,0,0)  # black
    horizontal_position = margin_pixels
    for i, line in enumerate(lines):
        vertical_position = int(round(margin_pixels + (i * realistic_line_height)))
        draw.text((horizontal_position, vertical_position), line, fill=font_color, font=font, stroke_width= 1)

    return image

def open_file():
    """
    Called when open file button is clicked
    Returns image below widget pannel along with file path
    """
    global my_img_file
    if switch.get() == 0:
        filenames = filedialog.askopenfilenames(initialdir='/', title='Select Files')
        img_file_label = tk.Label(window, text=filenames).pack()
        for my_img_file in filenames:
            selected = ImageTk.PhotoImage(Image.open(my_img_file))
            img_label = tk.Label(image=selected)
            img_label.image = selected
            img_label.pack()
        return my_img_file
    else:
        directoryname = filedialog.askdirectory(initialdir='/')
        directoryname_label = tk.Label(window, text=directoryname).pack()
        return directoryname
    

def set_BG_color():
    """
    Called when Background Color button is clicked
    Returns selected color as RGB tuple
    """
    global new_BG_tuple
    new_color = colorchooser.askcolor()[0]
    templist = []
    if new_color:
        for x in new_color:
            y = round(x)
            templist.append(y)
        new_BG_tuple = tuple(templist)
    return new_BG_tuple

def set_FG_color():
    """
    Called when Foreground Color button is clicked
    Returns selected color as RGB tuple
    """
    global new_FG_tuple
    new_color = colorchooser.askcolor()[0]
    templist = []
    if new_color:
        for x in new_color:
            y = round(x)
            templist.append(y)
        new_FG_tuple = tuple(templist)
    return new_FG_tuple

def generate():
    """
    Called when generate button is clicked
    Assigns selected options to variables and calls conversion functions.
    Returns generated image.
    """

    # Assign variables
    img_file=my_img_file
    cols=slideval.get()
    RGBvaluetext=new_FG_tuple
    RGBvaluebackground=new_BG_tuple
    
    # Create new file name
    now = datetime.now()
    date_time = now.strftime('%m-%d-%Y_%H-%M-%S')
    text_file = os.getcwd()+'/output/'+img_file.split('/')[-1].split('.')[0]+f'_ASCII_{date_time}.txt'
    out_file = os.getcwd()+'/output/'+ img_file.split('/')[-1].split('.')[0]+f'_ASCII_{date_time}.'+img_file.split('.')[1]
    
    # place holder
    scale = 0.43
    # registers more levels option
    if ML_switch.get() == 0:
        more_levels = True
    else:
        more_levels = False

    # Convert image to ascii text file
    aimg = covertImageToAscii(img_file, cols, scale, more_levels)
    f = open(text_file, 'w')
    for row in aimg:
        f.write(row + '\n')
    f.close()

    # Convert ascii text file to image file
    image = textfile_to_image(text_file, RGBvaluebackground, RGBvaluetext)
    image.show()
    image.save(out_file)
    print(f'ASCII image generated to {out_file}')



def main():
    # Declare globals
    global window, switch, slideval, ML_switch

    # Main window
    window = tk.Tk()
    window.title('ASCII Image Converter')
    window.geometry('400x400')

    # Select files or folder
    frame1 = tk.Frame(window, bg='grey')
    frame1.pack(fill='x',)
    switch = tk.IntVar()
    switch.set(0)
    open_file_Rb = tk.Radiobutton(frame1, text='File(s)', variable=switch, value = 0).pack(side='left')
    open_folder_Rb = tk.Radiobutton(frame1, text='Folder', variable=switch, value=1).pack(side='left')
    open_button = tk.Button(frame1, text='Open', command=open_file).pack(side='left')

    # Select number of columns
    frame2 = tk.Frame(window, bg='grey')
    frame2.pack(fill='x',after=frame1)
    slideval = tk.IntVar()
    slideval.set(10)
    col_slider = tk.Scale(frame2, from_=10, to=1500, orient='horizontal', length=200, variable=slideval).pack(side='left')

    # Select BG/FG colors
    frame3 = tk.Frame(window, bg='grey')
    frame3.pack(fill='x', after=frame2)
    bg_color_button = tk.Button(frame3, text='Background\nColor', command=set_BG_color).pack(side='left')
    fg_color_button = tk.Button(frame3, text='Foreground\nColor', command=set_FG_color).pack(side='left')

    # More levels 
    frame4 = tk.Frame(window, bg='grey')
    frame4.pack(fill='x', after=frame3)
    mL_label = tk.Label(frame4, text='More\n Levels?').pack(side='left')
    ML_switch = tk.IntVar()
    ML_switch.set(0)
    ML_yes_RB = tk.Radiobutton(frame4, text='Yes', variable=ML_switch, value=0).pack(side='left', fill='y')
    ML_no_RB = tk.Radiobutton(frame4, text='No', variable=ML_switch, value=1).pack(side='left', fill='y')

    # Generate
    generate_button = tk.Button(frame4, text='Generate', command=generate).pack(side='left', fill='y')

    window.mainloop()

if __name__ == '__main__':
    main()