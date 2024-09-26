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
    def tune_monochrome( image_input, image_target):
        """This methods returns the weight for liner transformation 
        the weights are computed based on the equation 
        w∗=(XT X)−1 XTy : analytical solotion for liner regression 
        This method can be used for color correction.
        Args:
            image_input (numpy array): _description_
            image_target (numyp array): _description_

        Returns:
             numpy array: Optimum weight that describes the relation between Input image and Targer image;
        """        
        x_trans_dot_x = np.dot(image_input.T,image_input)
        x_trans_dot_y = np.dot(image_input.T,image_target)
        return np.dot(np.linalg.inv(x_trans_dot_x), x_trans_dot_y )
    @staticmethod
    def tune_color(image_input, image_target):
        channels_input = image_input.T  # Transposing to get channels separately
        channels_target = image_target.T
        weight = []
        for idx, (input_channel, target_channel) in enumerate(zip(channels_input, channels_target)):
            weight.append(Processing.tune_monochrome(input_channel, target_channel))
        return np.array(weight).T

    @staticmethod
    def linear_transform_monochrome(image,weights):
        """_summary_

        Args:
            image (numpy array): image to be tune
            weights (numpy array): weights for linear transforamtion 

        Returns:
            numpy array: tuned image
        """
        return np.dot(weights,image)
    @staticmethod
    def linear_transform_color(color_weights,color_image):
        weights = color_weights.T  # Transposing to get channels separately
        channels = color_image.T
        transformed = []
        for idx, (input_weight, input_channel) in enumerate(zip(weights, channels)):
            transformed.append(Processing.linear_transform_monochrome(input_weight.T, input_channel))
        return np.array(transformed).T

