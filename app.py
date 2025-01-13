# ==========================================
# Variables Potentially Requiring Adjustment
# ==========================================
_fuzzy_white_value = 200 # Lowest RGB pixel value considered 'white'
_fuzzy_noise_value = 1e8 # Maximum pixel area size used to filter scanned image noise
# ==========================================

import datetime, os, subprocess
from threading import Thread

from tkinter import filedialog
from tkinter import *

from PIL import Image, ImageTk
from scipy import ndimage
import numpy as np

_expected_naps_path = 'C:\\Program Files\\NAPS2\\NAPS2.Console.exe'
_ico_filename = 'img\\folder-30.png'

_err  = '[ Error ]   '
_info = '[ Info  ]   '

# Globals- could clean this up
_app = None
_logbox = None
_img_thread = None
_scan_btn = None
_output_dir = None
_output_dir_btn = None
_output_dir_btn_ico = None

def scan_disabled(isdisabled):
    global _scan_btn, _output_dir_btn
    if isdisabled:
        _scan_btn.config(state=DISABLED)
        _output_dir_btn.config(state=DISABLED)
    else:
        _scan_btn.config(state=ACTIVE)
        _output_dir_btn.config(state=ACTIVE)

def log(type, text):
    _logbox.insert(END, "{}{}\n".format(type, text))

def scan(filename):
    scan_disabled(True)
    command = [
        _expected_naps_path,
        "--progress",
        "--deskew",
        "-o", filename
    ]
    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = process.communicate()

    scan_disabled(False)
    if len(stderr) > 0:
        log(_err, stderr)
        return False
    else:
        return True

def process_image(filename):
    img = Image.open(filename)

    img = img.convert('RGB')
    mask = img.convert("L").point(lambda p: p < _fuzzy_white_value and 255)
    
    # Convert mask to numpy array for processing
    mask_array = np.array(mask)
    
    # Label connected components in the mask
    structure = np.ones((3, 3), dtype=np.int)  # 8-connectivity
    labeled_array, num_features = ndimage.label(mask_array, structure)
    
    # Calculate the areas of each component
    sizes = ndimage.sum(mask_array, labeled_array, range(num_features + 1))

    # Find the label of the largest component
    largest_component_label = sizes.argmax()
    largest_size = sizes[largest_component_label]

    index = 1
    while largest_size > _fuzzy_noise_value:    
        # Create a new mask that only includes the largest component
        largest_component_mask = (labeled_array == largest_component_label)
    
        # Get the bounding box of the largest component
        coords = np.column_stack(np.where(largest_component_mask))
        min_row, min_col = coords.min(axis=0)
        max_row, max_col = coords.max(axis=0)
        bbox = (min_col, min_row, max_col, max_row)

        cropped_img = img.crop(bbox)
        cropped_img.save("{}_cropped_{}.jpg".format(filename[:-4], index))

        # Replace max size with 0 and get the next largest component
        sizes[largest_component_label] = 0
        largest_component_label = sizes.argmax()
        largest_size = sizes[largest_component_label]

        index += 1
    
    return index - 1

def process_image_thread(filename):
    if scan(filename):
        num_images = process_image(filename)
        log(_info, "{} images saved".format(num_images))

def scan_and_process():
    global _output_dir, _img_thread
    if len(_output_dir.get()) == 0:
        if not setoutputdir():
            log(_err, 'You must set an output directory before running scan')
            return

    datetimestr = datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
    filename = os.path.join(_output_dir.get(), "scan_{}.jpg".format(datetimestr))
    log(_info, 'Scanning and processing image \"{}\". This will take a moment...'.format(filename))

    # Spin up thread to scan and process image
    _img_thread = Thread(target=process_image_thread, args=(filename,))
    _img_thread.start()

def exitapp():
    global _app, _img_thread
    if _img_thread is not None and _img_thread.isAlive:
        _img_thread.join()
    _app.destroy()

def setoutputdir():
    global _output_dir
    _output_dir.set(filedialog.askdirectory())

    if len(_output_dir.get()) > 0:
        log(_info, "Output directory set to {}".format(_output_dir.get()))
        return True
    else:
        return False

def buildapp():
    global _app
    global _logbox
    global _scan_btn
    global _output_dir
    global _output_dir_btn
    global _output_dir_btn_ico

    _app=Tk()
    _app.title('NAPS2 Assistant')
    _app.resizable= True
    _app.minsize(width=1200, height=400)
    
    # Set up left frame
    lframe=Frame(_app)
    lframe.grid(row=0, column=0, sticky="nsew")

    canvas=Canvas(lframe)
    canvas.pack(side=LEFT, expand=True, fill=BOTH)

    scrollbar = Scrollbar(canvas)
    scrollbar.pack(side=RIGHT, fill=Y)

    _logbox = Text(canvas, wrap=WORD, yscrollcommand=scrollbar.set)
    _logbox.bindtags((_logbox, canvas, "all"))

    _logbox.pack(side=LEFT, expand=True, fill=BOTH)
    scrollbar.config(command=_logbox.yview)

    # Set up right frame
    rframe=Frame(_app)
    rframe.grid(row=0, column=1, sticky="nsew")
    
    # we need a global ref to this, otherwise it gets destroyed
    _output_dir = StringVar(value="")
    outputentry = Entry(rframe, textvariable=_output_dir)
    outputentry.grid(row=1, column=0, columnspan=1, sticky="ew", pady=(10,0), padx=(10,5))

    ico_filepath = os.path.join(os.path.dirname(os.path.abspath(__file__)), _ico_filename)
    ico = Image.open(ico_filepath)
    ico_szd = ico.resize((14,14), Image.LANCZOS)
    _output_dir_btn_ico = ImageTk.PhotoImage(ico_szd)
    _output_dir_btn = Button(rframe, image=_output_dir_btn_ico, command=setoutputdir)
    _output_dir_btn.grid(row=1, column=1, columnspan=1, sticky="ew", pady=(10,0), padx=(0,10), ipadx=1, ipady=1)

    _scan_btn = Button(rframe, text='Scan', width=20, command=scan_and_process)
    _scan_btn.grid(row=2, column=0, columnspan=2, sticky="e", padx=10, pady=(10,2))

    exitbutton = Button(rframe, text='Exit', width=20, command=exitapp)
    exitbutton.grid(row=3, column=0, columnspan=2, sticky="e", padx=10)

    rframe.columnconfigure(0, weight=1)

    _app.rowconfigure(0, weight=1)
    _app.columnconfigure(0, weight=1)
    _app.columnconfigure(1, weight=1)

if __name__ == '__main__':
    # Build GUI app, set up log box and scan button so we can reference these in other funcs
    buildapp()
    log(_info, 'Welcome to the NAPS2 Assistant! Please install NAPS2 and set up your scanner to continue. Scan images one at a time using the \"Scan\" button on the right. Images will automatically be rotated and cropped.')

    # Try to find NAPS2
    if not os.path.exists(_expected_naps_path):
        log(_err, 'Unable to find NAPS2 at \"{}\". Try installing, then run again.'.format(_expected_naps_path))
        scan_disabled(True)
    
    # Run gui
    mainloop()