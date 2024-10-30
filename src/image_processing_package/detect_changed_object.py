"""Detects the object that moved in a two images"""
import cv2
import numpy as np
import skimage as si
from image_processing_package.processing_routines import Processing
class DetectChanges():
    @staticmethod
    def generate_mask(input_image,target_image):
        """ Changes are detected in the the image via following steps
            
            1. compute the abslute differecne of two image. 
            2. Apply the threshold to the difference
            3. Detect the contours (GET the ROI by thresholding)
            4. create a dark image of same size
            5. Fill the white PIXELS withing detected ROIS from step 3: this is called mask
            6. return the mask
        Args:
            input_image (numpy array): refrence image:  
            changed_image (numpy array):  
        Returns:
            _type_: _description_
        """
        kernel = np.ones((5,5),np.float32)/25
        gray_a = cv2.filter2D(input_image,-1,kernel)
        gray_b = cv2.filter2D(target_image,-1,kernel)
        _, diff = si.metrics.structural_similarity(gray_a, gray_b, full=True)
        diff = (diff * 255).astype("uint8")
        thresh =  cv2.threshold(diff, 0, 255,cv2.THRESH_BINARY_INV | cv2.THRESH_OTSU)[1]
        return thresh
    @staticmethod
    def update_matches(target_ref_matches):
        # First, apply the ratio test
        match_number=20
        ratio_threshold = 0.75
        # good_matches = []
        # for m, n in zip(target_ref_matches[:-1], target_ref_matches[1:]):
        #     if m.distance < ratio_threshold * n.distance:
        #         good_matches.append(m)
        
        sorted_matches = sorted(target_ref_matches, key=lambda x: x.distance)
        n = min(match_number, len(sorted_matches))
        filtered_matches = sorted_matches[:n]
        return filtered_matches
    @staticmethod
    def update_matches1(target_ref_matches):
        # First, apply the ratio test
        match_number=20
        ratio_threshold = 0.75
        good_matches = []
        for m, n in zip(target_ref_matches[:-1], target_ref_matches[1:]):
             if m.distance < ratio_threshold * n.distance:
                 good_matches.append(m)
        
        sorted_matches = sorted(target_ref_matches, key=lambda x: x.distance)
        n = min(match_number, len(sorted_matches))
        filtered_matches = sorted_matches[:n]
        return filtered_matches
    @staticmethod
    def check_for_match_second(roi,input_image,target_image):
        shift = cv2.SIFT_create()
        brute_force_object= cv2.BFMatcher()
       
        mask_refrence = DetectChanges.generate_mask_from_roi(roi,input_image)
        #mask_refrence = DetectChanges.generate_mask(input_image,target_image)
        input_image_key_points,input_image_descriptor  = shift.detectAndCompute(input_image,mask_refrence)
        target_image_key_points,target_image_discriptor = shift.detectAndCompute(target_image,None)
        target_ref_matches =  brute_force_object.match(input_image_descriptor,target_image_discriptor)
        target_ref_matches = DetectChanges.update_matches(target_ref_matches)
        return [input_image_key_points,target_image_key_points,input_image_descriptor,target_image_discriptor,target_ref_matches]
    @staticmethod
    def check_for_match_third(roi1,roi2,input_image,target_image):
        shift = cv2.SIFT_create()
        brute_force_object= cv2.BFMatcher()
       
        mask_refrence = DetectChanges.generate_mask_from_roi(roi1,input_image)
        mask_target = DetectChanges.generate_mask_from_roi(roi2,target_image)
        #mask_refrence = DetectChanges.generate_mask(input_image,target_image)
        input_image_key_points,input_image_descriptor  = shift.detectAndCompute(input_image,mask_refrence)
        target_image_key_points,target_image_discriptor = shift.detectAndCompute(target_image,mask_target)
        target_ref_matches =  brute_force_object.match(input_image_descriptor,target_image_discriptor)
        target_ref_matches = DetectChanges.update_matches(target_ref_matches)
        return [input_image_key_points,target_image_key_points,input_image_descriptor,target_image_discriptor,target_ref_matches]
    @staticmethod
    def transform(input_image,input_image_key_points,target_image_key_points,target_ref_matches):
       # match_image = DetectChanges.__show_matches(input_image, input_image_key_points, target_image, target_image_key_points, target_ref_matches[:])  
        #Processing.open_images(match_image,"Match")  
        transformatoion_matrix= DetectChanges.compute_homography(input_image_key_points,target_image_key_points,target_ref_matches)
        transformed = DetectChanges.apply_afine(input_image,transformatoion_matrix[0])
        return transformed
    @staticmethod
    def __show_matches(input_image, keypoints_ref, target_image, keypoints_target, matches):
        img_matches = cv2.drawMatches(input_image, keypoints_ref, target_image, keypoints_target, matches, None, 
                                   flags=cv2.DrawMatchesFlags_NOT_DRAW_SINGLE_POINTS)
        return img_matches
    @staticmethod
    def compute_homography(input_keypoints,target_keypoints,matches):
        input_points = []
        target_points = []
        for i in matches:
            input_points.append(input_keypoints[i.queryIdx].pt)
            target_points.append(target_keypoints[i.trainIdx].pt)        
        input_points = np.array(input_points).reshape(-1,1,2)
        target_points = np.array(target_points).reshape(-1,1,2)
        affine_matrix  = cv2.estimateAffine2D(target_points, input_points)
        return affine_matrix

    @staticmethod
    def generate_mask_from_roi(roi,refrence_image):
        height, width= refrence_image.shape
        mask = np.zeros((height, width), dtype=np.uint8)
        x, y, w, h = roi
        mask[y:y+h, x:x+w] = 255
        return mask
    @staticmethod
    def apply_afine(image,transformation_matrix):
        height, width = image.shape[:2]
        aligned_img_affine = cv2.warpAffine(image,transformation_matrix, (width, height))
        return aligned_img_affine

    @staticmethod                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                        
    def select_and_crop_roi(image):
      image_copy = image.copy()
      roi = cv2.selectROI("Select ROI", image_copy, fromCenter=False, showCrosshair=True)
      cv2.destroyWindow("Select ROI")
      x, y, w, h = roi
      cropped_roi = image[y:y+h, x:x+w]
      output_image = np.zeros_like(image)
      output_image[y:y+h, x:x+w] = cropped_roi
      return roi, output_image
    

        

    @staticmethod
    def updateRoi(roi, first_image, second_image):
       parameters=  DetectChanges.check_for_match_second(roi,first_image,second_image)
       mask = DetectChanges.generate_mask_from_roi(roi,first_image)
       mask= DetectChanges.transform(mask,parameters[0],parameters[1],parameters[4])
       blurred = cv2.GaussianBlur(mask, (5, 5), 0)
       edges = cv2.Canny(blurred, 50, 150)
       contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
       max_contour = max(contours, key=cv2.contourArea)
       return cv2.boundingRect(max_contour)