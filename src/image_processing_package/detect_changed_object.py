"""Detects the object that moved in a two images"""
import cv2
import numpy as np
class DetectChanges():
    
    """_summary_
    """
    def __init__(self,ref_image,target_image):
        self.ref_image = ref_image
        self.target_image = target_image

    def __generate_mask(self):
        """ Changes are detected in the the image via following steps
            
            1. compute the abslute differecne of two image. 
            2. Apply the threshold to the difference
            3. Detect the contours (GET the ROI by thresholding)
            4. create a dark image of same size
            5. Fill the white PIXELS withing detected ROIS from step 3: this is called mask
            6. return the mask


        Args:
            ref_image (numpy array): refrence image:  
            changed_image (numpy array):  

        Returns:
            _type_: _description_
        """  
        diff = cv2.absdiff(self.ref_image,self.target_image)
        
        _, mask = cv2.threshold(diff, 0, 255, cv2.THRESH_OTSU)
        kernel = np.ones((5,5), np.uint8)
        mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        dark_image = np.zeros_like(self.ref_image)  
        for contour in contours:
            if cv2.contourArea(contour) > 10: 
                x, y, w, h = cv2.boundingRect(contour)
                cv2.rectangle(dark_image, (x, y), (x + w, y + h), (255, 255, 255), -1) 
        return dark_image
    
    def check_for_match(self):
        mask_blue_red = self.__generate_mask()
        shift = cv2.SIFT_create()
        ref_image_key_points,ref_image_descriptor  = shift.detectAndCompute(self.ref_image,mask_blue_red)
        target_image_key_points,target_image_discriptor = shift.detectAndCompute(self.target_image,mask_blue_red)
        brute_force_object= cv2.BFMatcher()
        target_ref_matches =  brute_force_object.match(ref_image_descriptor,target_image_discriptor)
        match_image = self.__show_matches(self.ref_image, ref_image_key_points, self.target_image, target_image_key_points, target_ref_matches[:])        
        cv2.imshow("ref target match", match_image)  
        cv2.waitKey(0)
        cv2.destroyAllWindows()



    
    def __show_matches(self, ref_image, keypoints_ref, target_image, keypoints_target, matches):
        img_matches = cv2.drawMatches(ref_image, keypoints_ref, target_image, keypoints_target, matches, None, 
                                   flags=cv2.DrawMatchesFlags_NOT_DRAW_SINGLE_POINTS)
        return img_matches
    
    def get_mask(self):
        return self.__generate_mask()
    


