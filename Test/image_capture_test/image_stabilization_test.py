import numpy as np
import cv2
from h5_file_format_package.h5_format_read import ReadH5
from image_processing_package.processing_routines import Processing
from image_processing_package.detect_changed_object import DetectChanges 
from image_processing_package.segment_everything import Segment_image

def inaitial_analysis():
    obj = ReadH5()
    blue = obj.read_files("image.h5","45")
    green = obj.read_files("image.h5","46")
    red = obj.read_files("image.h5","47")
    Processing.open_images(Processing.image_reconstruction(blue,green,red))
    obj = DetectChanges(blue,green)
    obj1 = DetectChanges(blue,red)
   # Processing.open_images(obj.get_mask())
    green = obj.check_for_match_second()
    red= obj1.check_for_match_second()
    Processing.open_images(Processing.image_reconstruction(blue,green,red))




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
inaitial_analysis()
