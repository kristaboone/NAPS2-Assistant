import os

import cv2
from PIL import Image
import numpy as np
from scipy import ndimage
import matplotlib.pyplot as plt

FUZZY_WHITE_VALUE = 200
FUZZY_NOISE_VALUE = 1e8

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
    largest_size = sizes[largest_component_label]

    index = 1
    while largest_size > FUZZY_NOISE_VALUE:    
        # Create a new mask that only includes the largest component
        largest_component_mask = (labeled_array == largest_component_label)
    
        # Get the bounding box of the largest component
        coords = np.column_stack(np.where(largest_component_mask))

        min_row, min_col = coords.min(axis=0)
        max_row, max_col = coords.max(axis=0)
        bbox = (min_col, min_row, max_col, max_row)
        cropped_img = img.crop(bbox)

        cropped_img_cv = cv2.cvtColor(np.array(cropped_img), cv2.COLOR_RGB2BGR)
        angle = cv2.minAreaRect(coords)[-1]

        (h, w) = cropped_img_cv.shape[:2]
        center = (w // 2, h // 2)
        M = cv2.getRotationMatrix2D(center, angle, 1.0)
        rotated_img = cv2.warpAffine(cropped_img_cv, M, (w, h), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)
        cv2.imwrite("{}_processed_{}.jpg".format(filename[:-4], index), rotated_img)

        # Replace max size with 0 and get the next largest component
        sizes[largest_component_label] = 0
        largest_component_label = sizes.argmax()
        largest_size = sizes[largest_component_label]

        index += 1

path = "C:\\Users\\Krista\\Desktop\\scans\\"
file = "scan_2025-01-13-12-49-13.jpg"

os.chdir(path)
process_image(file)