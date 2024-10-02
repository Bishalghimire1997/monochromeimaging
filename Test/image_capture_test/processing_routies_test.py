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
    """reconstruct colot i
    
    mage from RGB image"""
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
   

# def image_tuning_test():
#     """test to tune the color"""
#     image = cv2.imread("WithSaturation.jpg")
#     roi =  cv2.selectROI("Select ROI", image, showCrosshair=True, fromCenter=False)
#     print(roi)
#     Processing.color_correction(roi, [255,255,255,],image)
#     pass 

# def color_corr_test():
#     image_blue, image_green, image_red = cv2.split(cv2.imread("WithoutSaturation.jpg"))
#     ref_blue,ref_green,ref_red= cv2.split(cv2.imread("WithSaturation.jpg"))
#     W_blue, _, _, _ = np.linalg.lstsq(image_blue, ref_blue, rcond=None)
#     W_green, _, _, _ = np.linalg.lstsq(image_green, ref_green, rcond=None)
#     W_red, _, _, _ = np.linalg.lstsq(image_red, ref_red, rcond=None)
#     transformed_blue =np.dot(image_blue,W_blue)
#     transformed_green =np.dot(image_blue,W_green)
#     transformed_red =np.dot(image_blue,W_red)
#     transformed_image = np.stack((transformed_blue.astype(np.uint8),transformed_green.astype(np.uint8),transformed_red.astype(np.uint8)),axis=-1) 

def weight_generation_test():
    """test to tune the color"""
    image = cv2.imread("rgb.png")
    roi =  cv2.selectROI("Select ROI", image, showCrosshair=True, fromCenter=False)
    print(roi)
    Processing.get_weight(roi, [225,255,255],image)

def weight_application_test():
    """test to tune the color"""
    image = image_reconstruction_test()
    roib =  cv2.selectROI("Select ROI", image, showCrosshair=True, fromCenter=False)
    roig= cv2.selectROI("Select ROI", image, showCrosshair=True, fromCenter=False)
    roir =cv2.selectROI("Select ROI", image, showCrosshair=True, fromCenter=False)
    for i in range(1):
        wb= Processing.get_weight(roib, [255,0,0],image)       
        wg= Processing.get_weight(roig, [0,255,0],image)         
        wr= Processing.get_weight(roir, [0,0,255],image)
        transformed_new = Processing.fit_colors(wb,wg,wr,image)
        
        image = transformed_new
        cv2.imshow("new",transformed_new)
        cv2.waitKey(0)
        cv2.destroyAllWindows()

