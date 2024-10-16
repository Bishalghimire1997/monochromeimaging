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
    Processing.open_images(blue)
    obj = DetectChanges(blue,green)
   # Processing.open_images(obj.get_mask())
    obj.check_for_match()

def contour_detection_test():
    obj = ReadH5()

    blue = obj.read_files("blue.h5","8")
    green = obj.read_files("green.h5","8")
    dc  = DetectChanges(blue,green)
    binary_mask = dc.generate_mask()
    Processing.open_images(binary_mask)
    contour_list = dc.get_contour(binary_mask)
    crop_refrence = dc.crop_to_contour(contour_list,blue)
    crop_target =  dc.crop_to_contour(contour_list,green)
    print(len(crop_refrence))
    print(len(crop_target))
    for i in range(len(crop_refrence)):
        Processing.open_images(crop_refrence[i])
        Processing.open_images(crop_target[i])
    matches = dc.check_similarity(crop_refrence,crop_target)

    for i in matches:
        for j in i:
            print(j)




contour_detection_test()