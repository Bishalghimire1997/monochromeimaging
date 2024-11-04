import cv2
from image_processing_package.processing_routines import Processing
from h5_file_format_package.h5_format_read import ReadH5
class ColorGeneration():
    def __init__(self):
        self.read = ReadH5()
        pass
    def red_green_transformatio_generation(self):
        print("OK")
        red= self.read.read_files("red.h5","5")
        green = self.read.read_files("blue.h5","5")
        blue = self.read.read_files("green.h5","5")
      

        red= cv2.cvtColor(red, cv2.COLOR_GRAY2BGR)
        green= cv2.cvtColor(green, cv2.COLOR_GRAY2BGR)
        blue =  cv2.cvtColor(blue, cv2.COLOR_GRAY2BGR)
        Processing.open_images(blue,"blue")
        Processing.open_images(green,"green")
        Processing.open_images(red,"red")

       
        
        Processing.get_color_correction_matrix(red,blue,240,"RedBlue")
        Processing.get_color_correction_matrix(red,green,240,"RedGreen")

        pass
    def red_green_transformation_apply(self):
        red= self.read.read_files("red.h5","5")
        weight1 = self.read.read_files("RedGreen.h5","0")
        weight2= self.read.read_files("RedBlue.h5","0")
        green = Processing.corrrect_color(cv2.cvtColor(red, cv2.COLOR_GRAY2BGR),weight1)
        blue = Processing.corrrect_color(cv2.cvtColor(red, cv2.COLOR_GRAY2BGR),weight2)

        transformed = Processing.image_reconstruction(blue[0, :, :],green[:, 1, :],red)
        Processing.open_images(transformed,"transformed")

        pass
    def red_blue_transformation_generation(self):
        pass
    def red_blue_transformation_application(self):
        pass
obj= ColorGeneration()
obj.red_green_transformation_apply()