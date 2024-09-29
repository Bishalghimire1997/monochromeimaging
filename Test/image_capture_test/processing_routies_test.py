"""test"""
import numpy as np
import cv2
from matplotlib import pyplot as plt
from h5_file_format_package.h5_format_read import ReadH5
from image_processing_package.processing_routines import Processing

def histogram_test():
    """ test method
    """
    obj = ReadH5()
    red = Processing.histogram(obj.read_files("red.h5","8"))
    blue =  Processing.histogram(obj.read_files("blue.h5","8"))
    green =  Processing.histogram(obj.read_files("green.h5","8"))
    white  = Processing.histogram(obj.read_files("White.h5","8"))
    dark = Processing.histogram(obj.read_files("dark.h5","8"))
    plt.plot(blue, label="Blue")
    plt.plot(red, label="Red")
    plt.plot(green, label="Green")
    plt.plot(dark, label="Dark")
    plt.plot(white, label="White")
    plt.xlabel("Pixel Intensity")
    plt.ylabel("Frequency")
    plt.legend()
    plt.show()

def image_reconstruction_test():
    """reconstruct colot image from RGB image"""
    obj = ReadH5()
    red = obj.read_files("red.h5","8")
    blue = obj.read_files("blue.h5","8")
    green =obj.read_files("green.h5","8")
    color_image = Processing.image_reconstruction(blue,green,red)
    print(len(color_image))
    print(np.shape(color_image))
    return color_image

def image_reconstruction_using_ratio():
    """Reconstructing image by taking the ration of images"""
    obj = ReadH5()
    red = obj.read_files("red.h5","8")
    blue = obj.read_files("blue.h5","8")
    green =obj.read_files("green.h5","8")
    white  =obj.read_files("White.h5","8")
    color_image=  Processing.ratio_method(white,blue,green,red)
   

def image_tuning_test():
    """test to tune the color"""
    image = cv2.imread("WithSaturation.jpg")
    roi =  cv2.selectROI("Select ROI", image, showCrosshair=True, fromCenter=False)
    print(roi)
    Processing.color_correction(roi, [0,0,255,],image)
    pass 
image_tuning_test()