import numpy as np
import cv2
from h5_file_format_package.h5_format_read import ReadH5
from image_processing_package.processing_routines import Processing
from image_processing_package.detect_changed_object import DetectChanges 
from image_processing_package.segment_everything import Segment_image

def inaitial_analysis():
    obj = ReadH5()
    red = obj.read_files("red.h5","8")
    blue = obj.read_files("blue.h5","8")
    green = obj.read_files("green.h5","8")
    Processing.open_images(blue)
    obj = DetectChanges(blue,green)
   # Processing.open_images(obj.get_mask())
    Processing.open_images(obj.check_for_match_second())

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




def segment_anything_impl_test():
    obj = ReadH5()
    blue = obj.read_files("blue.h5","8")
    green = obj.read_files("green.h5","8")
    dc  = DetectChanges(blue,green)
    binary_mask = dc.generate_mask()
    maskobj = Segment_image()
    mask_rectangle = maskobj.image_segmentation_test(binary_mask)
    print(mask_rectangle)
    for i in mask_rectangle:
         x, y, w, h =i
         binary_mask = cv2.rectangle(binary_mask, (x, y), (x + w, y + h), (0, 255, 0), 2) 
    Processing.open_images(binary_mask)



def draw_rectangel():
    obj = ReadH5()
    blue = obj.read_files("blue.h5","8")
    green = obj.read_files("green.h5","8")
    dc  = DetectChanges(blue,green)
    image = dc.generate_mask()
    image= cv2.cvtColor(image, cv2.COLOR_GRAY2RGB)
    mask_image = 0
    mask= [[0, 0, 2447, 2044], [1063, 1169, 228, 345]]
    for i in mask:
         x, y, w, h =i
         mask_image = cv2.rectangle(image, (x, y), (x + w, y + h), (0, 255, 0), 2) 
    Processing.open_images(mask_image)

def allignment_correction_test():
    obj = ReadH5()
    
    blue = obj.read_files("image.h5","45")
    green = obj.read_files("image.h5","46")
    red = obj.read_files("image.h5","47")
    Processing.open_images(Processing.image_reconstruction(blue,green,red))
    
    stable1 = DetectChanges(blue,red)
    stable2 = DetectChanges(blue,green)
    red=stable2.allign(blue,red)
    green = stable1.allign(blue,green)
    after = Processing.image_reconstruction(blue,green,red)
    Processing.open_images(after)
allignment_correction_test()
