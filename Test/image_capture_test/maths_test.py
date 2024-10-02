import numpy as np
from processing_routies_test import image_reconstruction_test
from image_processing_package.processing_routines import  Processing
import cv2
def weight_fider_least_square():
    target=np.array( [[255,0,0],[0,255,0],[0,0,255]])
    image_input = image_reconstruction_test()
    image_target = cv2.imread("RGB.bmp")
    target_matrix = get_matrix(image_target,24)
    input_matrix= get_matrix(image_input,24)
    weight= np.linalg.lstsq(input_matrix,target_matrix)
    transformed_image= Processing.fit(image_input,weight[0])
    Processing.open_images(transformed_image)
    print(weight)
      
def weightFinder():
    target=np.array( [[255,0,0],[0,255,0],[0,0,255]])
    image_input = image_reconstruction_test()
    image_target = cv2.imread("RGB.bmp")
    target_matrix = get_matrix(image_target,24)
    input_matrix= get_matrix(image_input,24)
    print("target pixel = ", target_matrix)
    print("Input matrix = ", input_matrix)
    weight = target_matrix @ np.linalg.pinv(input_matrix)
    print(np.shape(weight))
    tansformed_image = apply_weight_to_image(image_input,weight)
    Processing.open_images(tansformed_image[25])


    

def weight_applier(pixel,weight):
      transformed = np.dot(pixel,weight).astype(np.uint8)
      print(transformed)


def get_matrix(image,total_sample_roi):
      i=0
      current= []
      while(i<total_sample_roi):
            current.append(get_pixel(cv2.selectROI("Select ROI", image, showCrosshair=True, fromCenter=False),image))
            i=i+1     

      return   np.array(current)

      
            
      

def get_pixel(roi:tuple, image):
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
        return [b_pixel,g_pixel,r_pixel]

def apply_weight_to_image(image, weight):
    
    h, w, c = image.shape 
    flattened_image = image.reshape(-1, 3)    
    transformed_image_flat = flattened_image @ weight.T      
    transformed_image_flat = np.clip(transformed_image_flat, 0, 255)   
    transformed_image = transformed_image_flat.reshape(h, w, c)
    return transformed_image.astype(np.uint8)

weight_fider_least_square()
