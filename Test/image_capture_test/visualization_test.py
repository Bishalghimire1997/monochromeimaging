from data_visualization_packege.visualize import Visualize
from h5_file_format_package.h5_format_read import ReadH5
from image_processing_package.processing_routines import Processing
def image_vis():
    """initial test case"""
    obj2 = ReadH5()
    blue1 = obj2.read_files("image.h5","102")
    green = obj2.read_files("image.h5","103")
    red = obj2.read_files("image.h5","104")
    image = Processing.image_reconstruction(blue1,green,red)
    vis = Visualize()
    vis.plot_3d_interactive(image)
image_vis()