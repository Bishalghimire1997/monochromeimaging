
from image_processing_package.Compute_color_difference import ColorDifference
from h5_file_format_package.h5_format import H5FormatRead
import cv2
def run():
    cd=ColorDifference()
    b = H5FormatRead().read_files("image.h5","0")
    g = H5FormatRead().read_files("image.h5","1")
    r = H5FormatRead().read_files("image.h5","2")
    color1=cv2.merge([b,g,r])
    color2=color1.copy()
    cd.cied_2000(color1,color2)
run()
