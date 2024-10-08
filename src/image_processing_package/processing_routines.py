"""Class to process the image"""
import cv2
import numpy as np
from h5_file_format_package.h5_format import H5Fromat

class Processing():
    """class to process the image """    
    @staticmethod
    def image_substraction(img1,img2):
        """Substracts two images

        Args:
            img1 (numpy array): _description_
            img2 (numpy array): _description_
        """
        return img1-img2
    @staticmethod
    def image_averaging(image:list):
        """Computes the average of the images"""
    @staticmethod
    def histogram(image):
        """returns the histogram of the image

        Args:
            image (2D numpy array): _description_

        Returns:
            _type_: 1 d nupy array
        """
        return np.histogram(image, bins=256)[0]
    @staticmethod
    def image_reconstruction(image_blue, image_green, image_red):
        """Creats one 3D matrix from three 2D matri

        Args:
            image_blue (numpy array): Image taken in the prescence of blue light
            image_green (numpy array): Image taken in the prescence of green light
            image_red (numpy array): Image taken in the prescence of Red light

        Returns:
            _type_: _description_
        """
        return np.stack((image_blue,image_green,image_red),axis=-1)
    @staticmethod
    def image_reconstruction_multi(image_white, image_rg,image_rb, image_bg):
        """Generates the color image from the four imges
        Args:
            image_white (numpy array): image taken in the White light
            image_rg (numpy array): image taken in red green light 
            image_rb (numpy array): Image taken in red blue  light 
            image_bg (numpy array): image taken in blue green light

        Returns:
            numyp array: Colored Images
        """
        r= ((image_white-image_bg)*2).astype(np.uint8)
        g= ((image_white- image_rb)*2).astype(np.uint8)
        b= ((image_white - image_rg)*2).astype(np.uint8)
        return Processing.image_reconstruction(b,g,r)

    @staticmethod
    def image_reconstruction_with_dark_image_refrecne(image_blue,image_green,image_red,image_dark):

        pure_red= Processing.image_substraction(image_red,image_dark)
        pure_blue = Processing.image_substraction(image_blue,image_dark)
        pure_green = Processing.image_substraction(image_green,image_dark)
        return Processing.image_reconstruction(Processing.scale(pure_blue),Processing.scale(pure_green),Processing.scale(pure_red))
    @staticmethod
    def open_images( image):
        """displys the numpy array as image
        Args:
            image (np.Arrayterator): numpy array
        """
        cv2.imshow("image",image)
        cv2.waitKey(0)
        cv2.destroyAllWindows()
    @staticmethod
    def ratio_method(white_image, red_image,blue_image,green_image):

        """tries to reconstruct the image computign the ration WRT white image

        Returns:
           numpy array: reconstructed images
        """
        red_to_white = red_image/white_image
        blue_to_white = blue_image/white_image
        green_to_white =green_image/white_image
        return Processing.image_reconstruction(
        Processing.scale( red_to_white),
        Processing.scale(blue_to_white),
        Processing.scale( green_to_white)
        )
    @staticmethod
    def scale(arr):
        """scale the image in the range of 0 to 255 pixel value

        Args:
            arr (numpy array): image as a numpy array

        Returns:
            numpy array:scaled images
        """
        scaled= ((arr-np.min(arr))/(np.max(arr)-np.min(arr)))*255
        return scaled.astype(np.uint8)    
    @staticmethod
    def get_weight(roi:tuple,refrence_color: list, image):
        """Generates the weight required to reansfer average
          pixel value of ROI to refrence p[ixel value 
        Args:
            roi (tuple): Region of interest 
            refrence_color (list): To what color ROI be transformed
            image (np array): Color imaga as a anumpy array
        Returns:
            numpy array : Weights value 
        """
        obj=H
        x, y, w, h = roi
        cropped_image = image[y:y+h, x:x+w]
        b_pixel = np.mean(cropped_image[:, :, 0])
        g_pixel = np.mean(cropped_image[:, :, 1])
        r_pixel = np.mean(cropped_image[:, :, 2])
        pixel_value = np.array([[b_pixel,g_pixel,r_pixel]])
        print(pixel_value)
        refrence = np.array([refrence_color])
        weight, _, _, _ = np.linalg.lstsq(pixel_value, refrence, rcond=None)

        return weight
    @staticmethod
    def fit(image, weight):
        """transforms the image with the help of weight 

        Args:
            image (numpy array ): Color image to be transformation 
            weight (numpy array): Weights for transformation 

        Returns:
            _type_: _description_
        """
        image_reshaped = image.reshape(-1, 3)
        transformed_image = np.dot(image_reshaped, weight)
        transformed_image = np.clip(transformed_image, 0, 255)
        transformed_image = transformed_image.reshape(
            len(image), len(image[0]), 3)
        return transformed_image.astype(np.uint8)
    @staticmethod
    def get_color_correction_matrix(image_to_be_corrected, refrence_image,number_of_rois:int):
        """generates the weight that can transform the color-
          of imput image into the olor of refrence image

        Args:
            image_to_be_corrected (numpy array): image whose color should be corrected
            refrence_image (numpy array)): refrence image for the color correction 
            number_of_rois (int): total number of region of interest to be considered

        Returns: Weights
            numpy array: 3*3 transformation matrix
        """
        obj = H5Fromat("weight")
        target_matrix = Processing.__get_matrix(refrence_image,number_of_rois)
        input_matrix= Processing.__get_matrix(image_to_be_corrected,number_of_rois)
        weight= np.linalg.lstsq(input_matrix,target_matrix)
        obj.record_images(weight[0],0)
    @staticmethod
    def corrrect_color(image, weight):
        """corrects the color in the image WRT weight 

        Args:
            image (numpy array): image in which correction to be applied
            weight (numpy array): 3*3 matrix

        Returns: Corrected image 
            numpy array: Color corrected image
        """
        h, w, c = image.shape
        flattened_image = image.reshape(-1, 3)
        transformed_image_flat = flattened_image @ weight
        transformed_image_flat = np.clip(transformed_image_flat, 0, 255)
        transformed_image = transformed_image_flat.reshape(h, w, c)
        return transformed_image.astype(np.uint8)    
    @staticmethod
    def __get_matrix(image,total_sample_roi):
        i=0
        current= []
        while i<total_sample_roi:
            current.append(Processing.__get_pixel(
                cv2.selectROI("Select ROI",
                image, showCrosshair=True, fromCenter=False),image))
            i=i+1
        return   np.array(current)
    @staticmethod
    def __get_pixel(roi:tuple, image):
        """Generates the weight required to reansfer average pixel
          value of ROI to refrence p[ixel value 
        Args:
            roi (tuple): Region of interest 
            refrence_color (list): To what color ROI be transformed
            image (np array): Color imaga as a anumpy array
        Returns:
            numpy array : Weights value 
        """
        x, y, w, h = roi
        cropped_image = image[y:y+h, x:x+w]
        b_pixel = np.mean(cropped_image[:, :, 0])
        g_pixel = np.mean(cropped_image[:, :, 1])
        r_pixel = np.mean(cropped_image[:, :, 2])
        return [b_pixel,g_pixel,r_pixel]
    