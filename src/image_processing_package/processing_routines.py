"""Class to process the image"""
import cv2
from h5_file_format_package.h5_format import H5Fromat
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
    def color_correction (roi:tuple,refrence_color: list, image):
        x, y, w, h = roi
        cropped_image = image[y:y+h, x:x+w]
        b_channel = cropped_image[:, :, 0]
        g_channel = cropped_image[:, :, 1]
        r_channel = cropped_image[:, :, 2]
        b_channel_ref = np.full((h,w),refrence_color[0],dtype=np.uint8)
        g_channel_ref=  np.full((h,w),refrence_color[1],dtype=np.uint8)
        r_channel_ref = np.full((h,w),refrence_color[2],dtype=np.uint8)


        W_blue, _, _, _ = np.linalg.lstsq(b_channel, b_channel_ref, rcond=None)
        W_green, _, _, _ = np.linalg.lstsq(g_channel, g_channel_ref, rcond=None)
        W_red, _, _, _ = np.linalg.lstsq(r_channel, r_channel_ref, rcond=None)

        transformed_blue =np.dot(b_channel,W_blue)
        transformed_green =np.dot(g_channel,W_green)
        transformed_red =np.dot(r_channel,W_red)
        transformed_image = np.stack((transformed_blue.astype(np.uint8),transformed_green.astype(np.uint8),transformed_red.astype(np.uint8)),axis=-1)

        print(W_blue)
        print("")
        print(W_red)

        print("")
        print(W_green)
        cv2.imshow("transformed image",transformed_image)
        cv2.waitKey(0)
        cv2.destroyAllWindows()
        
        print(W_blue)
        print("")
        print(W_red)

        print("")
        print(W_green)
        
        pass
    @staticmethod
    def pixel_correction(roi:tuple,refrence_color: list, image):
         x, y, w, h = roi
         cropped_image = image[y:y+h, x:x+w]
         b_pixel = np.mean(cropped_image[:, :, 0])
         g_pixel = np.mean(cropped_image[:, :, 1])
         r_pixel = np.mean(cropped_image[:, :, 2])

         

        # channel_arr = np.array([b_channel,g_channel,r_channel])

         pixel_value = np.array([[b_pixel,g_pixel,r_pixel]])
         print(pixel_value)
         refrence = np.array([refrence_color])        

         W, _, _, _ = np.linalg.lstsq(pixel_value, refrence, rcond=None)  
         
         return W       

         

    @staticmethod
    def fit(image, weight):
          image_reshaped = image.reshape(-1, 3)
          transformed_image = np.dot(image_reshaped, weight.T)
          transformed_image = np.clip(transformed_image, 0, 255)
          transformed_image = transformed_image.reshape(len(image), len(image[0]), 3)
          return transformed_image.astype(np.uint8)
    @staticmethod
    def fit_colors(wb,wg,wr,colored_image):
        blue_fit = Processing.fit(colored_image,wb)
        green_fit = Processing.fit(colored_image,wg)
        red_fit = Processing.fit(colored_image,wr)
        blue_reshape = blue_fit.reshape(-1,3)
        green_reshape =  green_fit.reshape(-1,3)
        red_reshape = red_fit.reshape(-1,3)
        return  np.stack((blue_fit[:, :, 0],green_fit[:, :, 1],red_fit[:, :, 2]),axis = -1)#sum.reshape(len(colored_image), len(colored_image[0]), 3).astype(np.uint8) #np.stack((blue_fit[:, :, 0],green_fit[:, :, 1],red_fit[:, :, 2]),axis = -1)
          
    @staticmethod
    def pixel_retio_correction(orginal_image, transformed_image):
        ratio = orginal_image/255
        ratio_rgb_channel = ratio.reshape(-1,3)
        bgr_transformed = transformed_image.reshape(-1,3)
        bgr_orginal= orginal_image.reshape(-1,3)
        ref= bgr_orginal[0]
        blue_ratio_trasformed = ((ref*ratio_rgb_channel[1]).astype(np.uint8))        
        green_ratio_transformed = (ref*ratio_rgb_channel[1]).astype(np.uint8)
        red_ratio_trasformed = ((ref*ratio_rgb_channel[1]).astype(np.uint8))        
       



       
         
         


    


        
        




