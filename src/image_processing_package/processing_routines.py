"""Class to process the image"""
import cv2
import numpy as np

class Processing():
    """class to process the image """    
    @staticmethod
    def image_substraction(img1,img2):
        """Substracts two images

        Args:
            img1 (numpy array): _description_
            img2 (numpy array): _description_
        """
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
        """Generates the weight required to reansfer average pixel value of ROI to refrence p[ixel value 
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
        pixel_value = np.array([[b_pixel,g_pixel,r_pixel]])
        print(pixel_value)
        refrence = np.array([refrence_color])
        weight, _, _, _ = np.linalg.lstsq(pixel_value, refrence, rcond=None)
        return weight
    @staticmethod
    def __fit(image, weight):
        """transforms the image with the help of weight 

        Args:
            image (numpy array ): Color image to be transformation 
            weight (numpy array): Weights for transformation 

        Returns:
            _type_: _description_
        """
        image_reshaped = image.reshape(-1, 3)
        transformed_image = np.dot(image_reshaped, weight.T)
        transformed_image = np.clip(transformed_image, 0, 255)
        transformed_image = transformed_image.reshape(len(image), len(image[0]), 3)
        return transformed_image.astype(np.uint8)
    @staticmethod
    def fit_colors(wb,wg,wr,colored_image):
        """transforms the color based on weights

        Args:
            wb ( numpy array): _description_
            wg (numpy array ): _description_
            wr (numpy array): _description_
            colored_image (numpy array): _description_

        Returns:
            Transformed image: Image after transformation 
        """        
        blue_fit = Processing.__fit(colored_image,wb)
        green_fit = Processing.__fit(colored_image,wg)
        red_fit = Processing.__fit(colored_image,wr)        
        return  np.stack((blue_fit[:, :, 0],green_fit[:, :, 1],red_fit[:, :, 2]),axis = -1)
          
    
       
         
         


    


        
        




