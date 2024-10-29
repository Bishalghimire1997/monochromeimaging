import segment_anything
import cv2
from segment_anything import SamAutomaticMaskGenerator, sam_model_registry
from h5_file_format_package.h5_format_read import ReadH5
from image_processing_package.processing_routines import Processing
def image_segmentation_test():
    obj = ReadH5()
    red = obj.read_files("red.h5","8")
    blue = obj.read_files("blue.h5","8")
    green = obj.read_files("green.h5","8")
    image_3ch =Processing.image_reconstruction(blue,green,red)
    sam = sam_model_registry["vit_b"](checkpoint="C:\git\monochromeimaging\sam_vit_b_01ec64.pth")
    mask_generator = SamAutomaticMaskGenerator(sam)
    masks = mask_generator.generate(image_3ch)
    area=[]
    for i in masks:
       area.append(i["bbox"])
    image_with_rectangle = image_3ch
    for i in area:
         x, y, w, h =i
         image_with_rectangle = cv2.rectangle(image_with_rectangle, (x, y), (x + w, y + h), (0, 255, 0), 2) 
    Processing.open_images(image_with_rectangle)
    

    


image_segmentation_test()


   