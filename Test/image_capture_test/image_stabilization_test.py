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
    Processing.open_images(Processing.image_reconstruction(blue,green,red),'reconstrucrted')
    obj = DetectChanges()
    obj1 = DetectChanges()
   # Processing.open_images(obj.get_mask())
    green = obj.check_for_match_second(blue,green)
    red= obj1.check_for_match_second(blue,red)
    Processing.open_images(Processing.image_reconstruction(blue,green,red),"after transformation ")




def segment_anything_impl_test():
    obj = ReadH5()
    blue = obj.read_files("blue.h5","8")
    green = obj.read_files("green.h5","8")
    dc  = DetectChanges()
    binary_mask = dc.generate_mask(blue,green)
    maskobj = Segment_image()
    mask_rectangle = maskobj.image_segmentation_test(binary_mask)
    print(mask_rectangle)
    for i in mask_rectangle:
         x, y, w, h =i
         binary_mask = cv2.rectangle(binary_mask, (x, y), (x + w, y + h), (0, 255, 0), 2) 
    Processing.open_images(binary_mask,"Mask")



def draw_rectangel():
    obj = ReadH5()


    blue = obj.read_files("blue.h5","8")
    green = obj.read_files("green.h5","8")
    dc  = DetectChanges()
    image = dc.generate_mask(blue,green)
    image= cv2.cvtColor(image, cv2.COLOR_GRAY2RGB)
    mask_image = 0
    mask= [[0, 0, 2447, 2044], [1063, 1169, 228, 345]]
    for i in mask:
         x, y, w, h =i
         mask_image = cv2.rectangle(image, (x, y), (x + w, y + h), (0, 255, 0), 2) 
    Processing.open_images(mask_image, "Mask")
    
def detect_from_crop():
    obj = ReadH5()
    blue = obj.read_files("image.h5","45")
    green = obj.read_files("image.h5","46")
    red = obj.read_files("image.h5","47")
    obj1 = DetectChanges()
    obj2 = DetectChanges()
    _,crop = obj1.select_and_crop_roi(blue)
    Processing.open_images(crop,"Crop")
    green = obj1.Serch_crop_object_in_images(crop,green,blue)
    red= obj2.Serch_crop_object_in_images(crop,red,blue)
    Processing.open_images(Processing.image_reconstruction(blue,green,red),"Colored Image")

inaitial_analysis()


