import segment_anything
from segment_anything import SamAutomaticMaskGenerator, sam_model_registry
from h5_file_format_package.h5_format_read import ReadH5
from image_processing_package.processing_routines import Processing
def image_segmentation_test():
    obj = ReadH5()
    red = obj.read_files("red.h5","8")
    blue = obj.read_files("blue.h5","8")
    green = obj.read_files("green.h5","8")
    sam = sam_model_registry["vit_b"](checkpoint="C://Users//SIU856587710//Downloads")
    mask_generator = SamAutomaticMaskGenerator(sam)
    masks = mask_generator.generate(blue)
    Processing.open_images(masks[0])
image_segmentation_test()


   