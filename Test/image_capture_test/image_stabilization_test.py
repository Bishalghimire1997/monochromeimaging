import numpy as np
import cv2
from h5_file_format_package.h5_format_read import ReadH5
from image_processing_package.processing_routines import Processing
from image_processing_package.detect_changed_object import DetectChanges 

def inaitial_analysis():
    obj = ReadH5()
    red = obj.read_files("red.h5","8")
    blue = obj.read_files("blue.h5","8")
    green = obj.read_files("green.h5","8")
    obj = DetectChanges(green,red)
    Processing.open_images(obj.get_mask())
    obj.check_for_match()
   
inaitial_analysis()