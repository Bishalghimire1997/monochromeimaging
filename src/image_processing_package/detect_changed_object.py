"""Detects the object that moved in a two images"""
import cv2
import numpy as np
import skimage as si
from image_processing_package.processing_routines import Processing
class DetectChanges():
    
    """_summary_
    """
    def __init__(self,ref_image,target_image):
        self.ref_image = ref_image
        self.target_image = target_image

    def generate_mask(self):
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

        
        


        kernel = np.ones((5,5),np.float32)/25
        grayA = cv2.filter2D(self.ref_image,-1,kernel)
        grayB = cv2.filter2D(self.target_image,-1,kernel)

        _, diff = si.metrics.structural_similarity(grayB, grayA, full=True)
        diff = (diff * 255).astype("uint8")
        thresh =  cv2.threshold(diff, 0, 255,cv2.THRESH_BINARY_INV | cv2.THRESH_OTSU)[1]
        return thresh
    
    def update_matches(self, target_ref_matches):
        n=30
        sorted_matches = sorted(target_ref_matches, key=lambda x: x.distance)
        n = min(n, len(sorted_matches))
        target_ref_matches = sorted_matches[:n]
        return target_ref_matches

    def check_for_match_second(self):
        shift = cv2.SIFT_create()
        brute_force_object= cv2.BFMatcher()
        roi_refrence = cv2.selectROI("Select ROI", self.ref_image, fromCenter=False, showCrosshair=True)
        mask_refrence = self.generate_mask_from_roi(roi_refrence,self.ref_image)
        ref_image_key_points,ref_image_descriptor  = shift.detectAndCompute(self.ref_image,mask_refrence)
        target_image_key_points,target_image_discriptor = shift.detectAndCompute(self.target_image,None)
        target_ref_matches =  brute_force_object.match(ref_image_descriptor,target_image_discriptor)
        target_ref_matches = self.update_matches(target_ref_matches)
        match_image = self.__show_matches(self.ref_image, ref_image_key_points, self.target_image, target_image_key_points, target_ref_matches[:])  
        Processing.open_images(match_image)  
        transformed= self.compute_homography(ref_image_key_points,target_image_key_points,target_ref_matches)
        return transformed


    
    def __show_matches(self, ref_image, keypoints_ref, target_image, keypoints_target, matches):
        img_matches = cv2.drawMatches(ref_image, keypoints_ref, target_image, keypoints_target, matches, None, 
                                   flags=cv2.DrawMatchesFlags_NOT_DRAW_SINGLE_POINTS)
        return img_matches

    def compute_homography(self,input_keypoints,target_keypoints,matches):
        input_points = []
        target_points = []
        for i in matches:
            input_points.append(input_keypoints[i.queryIdx].pt)
            target_points.append(target_keypoints[i.trainIdx].pt)
        
        input_points = np.array(input_points).reshape(-1,1,2)
        target_points = np.array(target_points).reshape(-1,1,2)
        affine_matrix  = cv2.estimateAffine2D(target_points, input_points)
        print(affine_matrix)
        height, width = self.target_image.shape[:2]

        aligned_img_affine = cv2.warpAffine(self.target_image,affine_matrix[0], (width, height))
        return aligned_img_affine


    def generate_mask_from_roi(self,roi,refrence_image):
        height, width= refrence_image.shape
        mask = np.zeros((height, width), dtype=np.uint8)
        x, y, w, h = roi
        mask[y:y+h, x:x+w] = 255
        return mask

            