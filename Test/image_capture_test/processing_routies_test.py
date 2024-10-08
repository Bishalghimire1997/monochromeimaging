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
    Processing.ratio_method(white,blue,green,red)
def image_reconstruction_using_white():
    "Reconstructring the image using substraction method"
    obj = ReadH5()
    w = obj.read_files("white.h5","8")
    rb = obj.read_files("rb.h5","8")
    rg =obj.read_files("rg.h5","8")
    bg = obj.read_files("bg.h5","8")
    image = Processing.image_reconstruction_multi(w,rg,rb,bg)
    return image
def image_reconstruction_using_dark():
    "constructs the image using the darrk image as the reference image"
    obj = ReadH5()
    red = obj.read_files("red.h5","8")
    blue = obj.read_files("blue.h5","8")
    green =obj.read_files("green.h5","8")
    dark  =obj.read_files("dark.h5","8")
    return Processing.image_reconstruction_with_dark_image_refrecne(blue,green,red, dark)
def color_correction_test():
    "color correction test"
    image_input = image_reconstruction_test ()
    image_target = cv2.imread("RGB.bmp")
    Processing.get_color_correction_matrix(image_input,image_target,24)
def color_correction_apply_test(image_input):

    "apply the color correction weight to the image"
    obj = ReadH5()
    weight = obj.read_files("weight.h5","0")
    Processing.open_images(image_reconstruction_test())
    Processing.open_images( Processing.corrrect_color(image_input,weight))

def noise_removal_test(image_input):

    obj = ReadH5()
    weight = obj.read_files("weight.h5","0")
    Processing.open_images(image_reconstruction_test())
    image_input= Processing.corrrect_color(image_input,weight)
    Processing.open_images(image_input)
    image_list= []

    
    for i in range (100):
        temp_image = (image_input +int(np.clip(np.random.normal(0, 1), 1, 100))).astype(np.int8)
        image_list.append(temp_image)

    average = np.mean(image_list,axis=0)
    average = np.clip(average, 0, 255).astype(np.uint8) 
    Processing.open_images(average)

#color_correction_apply_test( image_reconstruction_test())
noise_removal_test(image_reconstruction_test())



    

