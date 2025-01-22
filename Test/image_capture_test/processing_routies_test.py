"""test"""
import numpy as np
import cv2
from matplotlib import pyplot as plt
from h5_file_format_package.h5_format import H5FormatRead
from image_processing_package.processing_routines import Processing

def histogram_test():
    """ test method
    """
    obj = H5FormatRead()
    red = Processing.histogram(obj.read_files("red.h5","3"))
    blue =  Processing.histogram(obj.read_files("blue.h5","3"))
    green =  Processing.histogram(obj.read_files("green.h5","8"))   
    plt.plot(blue, label="Blue")
    plt.plot(red, label="Red")
    plt.plot(green, label="Green")
    plt.xlabel("Pixel Intensity")
    plt.ylabel("Frequency")
    plt.legend()
    plt.show()
def image_reconstruction_test():
    """reconstruct color image from RGB image"""
    obj = H5FormatRead()
    red = obj.read_files("image.h5","48")
    blue = obj.read_files("image.h5","49")
    green =obj.read_files("image.h5","50")
    color_image = Processing.image_reconstruction(blue,green,red)
    print(len(color_image))
    print(np.shape(color_image))
    return color_image

def frame_reconstruction_test():
    Processing.frame_reconstruction("image.h5","r",1000)
def twochannelimagetest():
    obj = H5FormatRead()    
    blue = obj.read_files("image.h5","909")
    green =obj.read_files("image.h5","910")
    red = obj.read_files("image.h5","911")
    color_image = Processing.image_reconstruction(blue,green,red)
    Processing.open_images(color_image,"Image")


def color_correction_test():
    obj = H5FormatRead()
    b= obj.read_files("image.h5",str(8))
    g= obj.read_files("image.h5",str(9))
    r= obj.read_files("image.h5",str(10))

    image1 = cv2.merge([b,g,r])
    Processing.open_images(image1,"Img")

    image = Processing.image_reconstruction(b,g,r)
    ref = cv2.imread("image.bmp", cv2.IMREAD_COLOR)
    Processing.open_images(ref,"im")
    Processing.get_color_correction_matrix(image,ref,50,"weight")
def correct():
    obj = H5FormatRead()
    for i in range(300):       
        b = obj.read_files("image.h5",str(i))
        g= obj.read_files("image.h5",str(i+1))
        r= obj.read_files("image.h5",str(i+2))
        image = Processing.image_reconstruction(b,g,r)
        imaeg = Processing.corrrect_color(image,obj.read_files("weight.h5",str(0)))
        Processing.open_images(imaeg,"after")
         
frame_reconstruction_test()




