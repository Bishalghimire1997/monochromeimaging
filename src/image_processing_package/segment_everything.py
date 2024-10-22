import segment_anything
import cv2
from segment_anything import SamAutomaticMaskGenerator, sam_model_registry
from h5_file_format_package.h5_format_read import ReadH5
from image_processing_package.processing_routines import Processing

class Segment_image():


    def image_segmentation_test(self,image_1ch):
       
        image_3ch =cv2.cvtColor(image_1ch, cv2.COLOR_GRAY2RGB)
        sam = sam_model_registry["vit_b"](checkpoint="C:\git\monochromeimaging\sam_vit_b_01ec64.pth")
        mask_generator = SamAutomaticMaskGenerator(sam)
        masks = mask_generator.generate(image_3ch)
        area=[]
        for i in masks:
           area.append(i["bbox"])
        return area