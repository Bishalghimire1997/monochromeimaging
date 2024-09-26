"""test"""
import numpy as np
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
    Processing.open_images(color_image)

def image_reconstruction_using_ratio():
    """Reconstructing image by taking the ration of images"""
    obj = ReadH5()
    red = obj.read_files("red.h5","8")
    blue = obj.read_files("blue.h5","8")
    green =obj.read_files("green.h5","8")
    white  =obj.read_files("White.h5","8")
    color_image=  Processing.ratio_method(white,blue,green,red)

def image_tuning_test():
    """Image tuning test"""
 # random color image
    random_color_image_input = np.random.randint(0, 256, size=(1080, 1920, 3), dtype=np.uint8)
    random_color_image_target = np.random.randint(0, 256, size=(1080, 1920, 3), dtype=np.uint8)


 # input image : 
    color_image = np.ones((1080, 1920, 3), dtype=np.uint8)
    color_image[:, :, 0] = 180   # Red channel
    color_image[:, :, 1] = 45  # Green channel
    color_image[:, :, 2] = 90  # Blue channel

# target image 
    target = np.ones((1080, 1920, 3), dtype=np.uint8)
    target[:, :, 0] = 90   # Red channel
    target[:, :, 1] = 60  # Green channel
    target[:, :, 2] = 180  # Blue channel

  # generate Pure red image 

    red_image = np.zeros((1080, 1920, 3), dtype=np.uint8)
    red_image[:, :, 0] = 255

# generate pure white image 
    white_image = np.ones((1080, 1920, 3), dtype=np.uint8) * 255

# generate pink image for testing
    pink_image = np.zeros((1080, 1920, 3), dtype=np.uint8)
    pink_image[:, :, 0] = 255  # Red
    pink_image[:, :, 2] = 192  # Blue


    weight = Processing.tune_color(random_color_image_input,random_color_image_target)
    transformed = Processing.linear_transform_color(white_image,weight)
    Processing.open_images(transformed)
 
    
image_tuning_test()
