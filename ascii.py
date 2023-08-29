import math
import sys
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
    h,w = im.shape

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
        scale = (.572*(1/(1.5/(7564/5240))))

    # open image and convert to grayscale
    image = Image.open(fileName).convert('L')

    # store dimensions
    W, H = image.size[0], image.size[1]
    print("\tinput image dims: %d x %d" % (W, H))

    # compute width of tile
    w = W/cols

    # compute tile height based on aspect ratio and scale
    h = w/scale

    # compute number of rows
    rows = int(H/h)
    
    print("\tcols: %d, rows: %d" % (cols, rows))
    print("\ttile dims: %d x %d" % (w, h))

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

    # choose a font
    font = None
    large_font = 20  # get better resolution with larger size
    for font_filename in COMMON_MONO_FONT_FILENAMES:
        try:
            font = ImageFont.truetype(font_filename, size=large_font)
            print(f'\tUsing font "{font_filename}".')
            break
        except IOError:
            pass
            #print(f'\tCould not load font "{font_filename}".')
    if font is None:
        font = ImageFont.load_default()
        print('\tUsing default font.')

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
    possible_image_files = ['jpg','JPG','JPEG','jpeg','rgb','gif','pbm','pgm','ppm','tiff','rast','xbm','bmp','png','webp','exr']
    global filenames, img_file_label, display_frame
    if switch.get() == 0:

        rloc = 0
        cloc = 0

        filenames = filedialog.askopenfilenames(initialdir='/', title='Select Files')
        filenames = [f for f in filenames if os.path.isfile(f)]
        filenames = [f for f in filenames if f.split('.')[1] in possible_image_files]
        img_file_label = tk.Label(window, text='Files\n' + '\n'.join(filenames)).pack()
        display_frame = tk.Frame(window)
        display_frame.pack(expand=True)
        for my_img_file in filenames:
            resized_img = Image.open(my_img_file).resize((200,200))
            selected = ImageTk.PhotoImage(resized_img)
            index = filenames.index(my_img_file)
            cloc = index % 3
            img_label = tk.Label(display_frame, image=selected)
            img_label.image = selected
            img_label.grid(row=rloc, column=cloc)
            cloc += 1
            if cloc == 3:
                rloc += 1
        return filenames
    else:

        rloc = 0
        cloc = 0 

        directoryname = filedialog.askdirectory(initialdir='/')
        directoryname_label = tk.Label(window, text=directoryname).pack()
        filenames = os.listdir(directoryname)
        filenames = [f for f in filenames if os.path.isfile(directoryname+'/'+f)]
        filenames = [f for f in filenames if f.split('.')[1] in possible_image_files]
        filenames = [directoryname+'/'+f for f in filenames]
        display_frame = tk.Frame(window)
        display_frame.pack(expand=True)
        for my_img_file in filenames:
            resized_img = Image.open(my_img_file).resize((200,200))
            selected = ImageTk.PhotoImage(resized_img)
            index = filenames.index(my_img_file)
            cloc = index % 3
            img_label = tk.Label(display_frame, image=selected)
            img_label.image = selected
            img_label.grid(row=rloc, column=cloc)
            cloc += 1
            if cloc == 3:
                rloc += 1
        return filenames

        
        
    

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
    for my_img_file in filenames:
        print(f'\nConverting image ({filenames.index(my_img_file)+1}/{len(filenames)})')
        img_file=my_img_file
        cols=slideval.get()
        RGBvaluetext=new_FG_tuple
        RGBvaluebackground=new_BG_tuple

        # Create new folder with current date if not already existing
        now = datetime.now()
        folder_name = now.strftime('%Y-%m-%d')
        folder_path = os.path.join(os.getcwd(),'output',folder_name)
        folder_exists = os.path.exists(folder_path)
        if folder_exists:
            output_path = folder_path
        else:
            os.makedirs(folder_path)
            print(f'New folder created {folder_path}')
            output_path = folder_path
        
        # Create new file name
        date_time = now.strftime('%Y-%m-%d_%H-%M-%S')
        text_file = os.path.join(output_path, img_file.split('/')[-1].split('.')[0] + f'_ASCII_{date_time}.txt')
        out_file = os.path.join(output_path, img_file.split('/')[-1].split('.')[0]+f'_ASCII_{date_time}.'+img_file.split('.')[1])
        
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
    print('Process completed')

def restart():
    print('\nRestarting...')
    python = sys.executable
    os.execl(python, python, * sys.argv)


def main():
    # Declare globals
    global window, switch, slideval, ML_switch

    # Main window
    window = tk.Tk()
    window.title('ASCII Image Converter')
    window.geometry('600x600')

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
    slideval.set(200)
    col_slider = tk.Scale(frame2, from_=10, to=1500, orient='horizontal', length=200, variable=slideval).pack(side='left')

    # Select BG/FG colors
    frame3 = tk.Frame(window, bg='grey')
    frame3.pack(fill='x', after=frame2)
    bg_color_button = tk.Button(frame3, text='Background\nColor', command=set_BG_color).pack(side='left')
    fg_color_button = tk.Button(frame3, text='Foreground\nColor', command=set_FG_color).pack(side='left')

    # More levels 
    frame4 = tk.Frame(window, bg='grey')
    frame4.pack(fill='x', after=frame3)
    #mL_label = tk.Label(frame4, text='Image\n Quality').pack(side='left')
    ML_switch = tk.IntVar()
    ML_switch.set(0)
    ML_yes_RB = tk.Radiobutton(frame4, text='Detailed', variable=ML_switch, value=0).pack(side='left', fill='y')
    ML_no_RB = tk.Radiobutton(frame4, text='High Contrast', variable=ML_switch, value=1).pack(side='left', fill='y')

    # Generate
    generate_button = tk.Button(frame4, text='Generate', command=generate).pack(side='left', fill='y')

    #Restart
    clear_button = tk.Button(frame4, text='Restart', command=restart).pack(side='right', fill='y')
    window.mainloop()

if __name__ == '__main__':
    main()