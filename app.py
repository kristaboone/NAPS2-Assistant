import datetime, os, subprocess
from threading import Thread

from tkinter import filedialog
from tkinter import *

from PIL import Image
import numpy as np
from scipy import ndimage

NAPS2 = "C:\\Program Files\\NAPS2\\NAPS2.Console.exe"

FUZZY_WHITE_VALUE = 200

ERR  = '[ Error ]   '
INFO = '[ Info  ]   '

APP = None
LOGBOX = None
SCAN_BTN = None
OUTPUT_DIR_BTN = None

OUTPUT_DIR = None
IMG_THREAD = None

def scan_disabled(isdisabled):
    global SCAN_BTN
    global OUTPUT_DIR_BTN
    if isdisabled:
        SCAN_BTN.config(state=DISABLED)
        OUTPUT_DIR_BTN.config(state=DISABLED)
    else:
        SCAN_BTN.config(state=ACTIVE)
        OUTPUT_DIR_BTN.config(state=ACTIVE)

def log(type, text):
    LOGBOX.insert(END, "{}{}\n".format(type, text))

def scan(filename):
    scan_disabled(True)
    command = [
        NAPS2,
        "--progress",
        "--deskew",
        "-o", filename
    ]
    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = process.communicate()

    scan_disabled(False)
    if len(stderr) > 0:
        log(ERR, stderr)
        return False
    else:
        return True

def process_image(filename):
    img = Image.open(filename)

    img = img.convert('RGB')
    mask = img.convert("L").point(lambda p: p < FUZZY_WHITE_VALUE and 255)
    
    # Convert mask to numpy array for processing
    mask_array = np.array(mask)
    
    # Label connected components in the mask
    structure = np.ones((3, 3), dtype=np.int)  # 8-connectivity
    labeled_array, num_features = ndimage.label(mask_array, structure)
    
    # Calculate the areas of each component
    sizes = ndimage.sum(mask_array, labeled_array, range(num_features + 1))
    
    # Find the label of the largest component
    largest_component_label = sizes.argmax()
    
    # Create a new mask that only includes the largest component
    largest_component_mask = (labeled_array == largest_component_label)
    
    # Get the bounding box of the largest component
    coords = np.column_stack(np.where(largest_component_mask))
    min_row, min_col = coords.min(axis=0)
    max_row, max_col = coords.max(axis=0)
    bbox = (min_col, min_row, max_col, max_row)
    
    cropped_img = img.crop(bbox)
    cropped_img.save("{}_cropped.jpg".format(filename[:-4]))

def process_image_thread(filename):
    if scan(filename):
        process_image(filename)
    log(INFO, "Image saved")

def scan_and_process():
    global OUTPUT_DIR
    if OUTPUT_DIR is None:
        if not setoutputdir():
            log(ERR, 'You must set an output directory before running scan')
            return

    datetimestr = datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
    filename = os.path.join(OUTPUT_DIR, "scan_{}.jpg".format(datetimestr))
    log(INFO, 'Scanning and processing image \"{}\". This will take a moment...'.format(filename))

    # Spin up thread to scan and process image
    global IMG_THREAD
    IMG_THREAD = Thread(target=process_image_thread, args=(filename,))
    IMG_THREAD.start()

def exitapp():
    if IMG_THREAD is not None and IMG_THREAD.isAlive:
        IMG_THREAD.join()
    APP.destroy()

def setoutputdir():
    global OUTPUT_DIR
    OUTPUT_DIR = filedialog.askdirectory()

    if len(OUTPUT_DIR) > 0:
        log(INFO, "Output directory set to {}".format(OUTPUT_DIR))
        return True
    else:
        OUTPUT_DIR = None
        return False

def buildapp():
    root=Tk()
    root.title('NAPS2 Assistant')
    root.geometry('1500x400')
    root.minsize(400,400)
    
    frame=Frame(root)
    frame.pack(side=LEFT, expand=True, fill=BOTH)

    canvas=Canvas(frame)
    canvas.pack(side=LEFT, expand=True, fill=BOTH)

    scrollbar = Scrollbar(canvas)
    scrollbar.pack(side=RIGHT, fill=Y)

    logbox = Text(canvas, wrap=WORD, yscrollcommand=scrollbar.set)
    logbox.bindtags((logbox, canvas, "all"))

    logbox.pack(side=LEFT, expand=True, fill=BOTH)
    scrollbar.config(command=logbox.yview)

    outputbutton = Button(frame, text='Set Output Folder', width=25, command=setoutputdir)
    outputbutton.pack(side=TOP, padx=20, pady=10)

    scanbutton = Button(frame, text='Scan', width=25, command=scan_and_process)
    scanbutton.pack(side=TOP, padx=20)

    exitbutton = Button(frame, text='Exit', width=25, command=exitapp)
    exitbutton.pack(side=TOP, padx=20, pady=10)

    return root,logbox,scanbutton,outputbutton

if __name__ == '__main__':
    # Build GUI app, set up log box and scan button so we can reference these in other funcs
    APP, LOGBOX, SCAN_BTN, OUTPUT_DIR_BTN = buildapp()

    log(INFO, 'Welcome to the NAPS2 Assistant! Please install NAPS2 and set up your scanner to continue. Scan images one at a time using the \"Scan\" button on the right. Images will automatically be rotated and cropped.')

    # Try to find NAPS2
    if not os.path.exists(NAPS2):
        log(ERR, 'Unable to find NAPS2 at \"{}\". Try installing, then run again.'.format(NAPS2))
        scan_disabled(True)
    
    # Run gui
    mainloop()