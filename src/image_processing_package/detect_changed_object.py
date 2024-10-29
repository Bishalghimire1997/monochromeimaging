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
        match_number=10
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
    def check_for_match_second(roi,input_image,target_image):
        shift = cv2.SIFT_create()
        brute_force_object= cv2.BFMatcher()
       
        mask_refrence = DetectChanges.generate_mask_from_roi(roi,input_image)
        #mask_refrence = DetectChanges.generate_mask(input_image,target_image)
        input_image_key_points,input_image_descriptor  = shift.detectAndCompute(input_image,mask_refrence)
        target_image_key_points,target_image_discriptor = shift.detectAndCompute(target_image,None)
        target_ref_matches =  brute_force_object.match(input_image_descriptor,target_image_discriptor)
        target_ref_matches = DetectChanges.update_matches(target_ref_matches)
        match_image = DetectChanges.__show_matches(input_image, input_image_key_points, target_image, target_image_key_points, target_ref_matches[:])  
        Processing.open_images(match_image,"Match")  
        transformatoion_matrix= DetectChanges.compute_homography(input_image_key_points,target_image_key_points,target_ref_matches)
        transformed = DetectChanges.apply_afine(target_image,transformatoion_matrix[0])
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
            print(i)
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
    def Serch_crop_object_in_images(cropped_images,input_image,target_image):
        shift = cv2.SIFT_create()
        brute_force_object= cv2.BFMatcher()
        cropped_image_key_points,cropped_image_descriptor = shift.detectAndCompute(cropped_images,None)
        input_image_key_points,input_image_descriptor  = shift.detectAndCompute(input_image,None)
        target_image_key_points,target_image_discriptor = shift.detectAndCompute(target_image,None)
        target_crop_matches =  brute_force_object.match(target_image_discriptor,cropped_image_descriptor)
        input_crop_matches =  brute_force_object.match(input_image_descriptor,cropped_image_descriptor)
        target_crop_matches = DetectChanges.update_matches(target_crop_matches)
        input_crop_matches = DetectChanges.update_matches(input_crop_matches)
        match_image = DetectChanges.__show_matches(target_image, target_image_key_points, cropped_images, cropped_image_key_points, target_crop_matches[:])
        Processing.open_images(match_image,"match")
        transformed= DetectChanges.compute_homography(input_image,input_image_key_points,cropped_image_key_points,input_crop_matches)
        Processing.open_images(transformed,"Input_crop")
        transformed= DetectChanges.compute_homography(transformed,input_image_key_points,target_image_key_points,target_crop_matches)
        Processing.open_images(transformed,"Crop_target")
        return transformed
    @staticmethod
    def compute_homography_crop(input_keypoints,target_keypoints,matches):
        input_points = []
        target_points = []
        for i in matches:
            print(i)
            input_points.append(input_keypoints[i.queryIdx].pt)
            target_points.append(target_keypoints[i.trainIdx].pt)        
        input_points = np.array(input_points).reshape(-1,1,2)
        target_points = np.array(target_points).reshape(-1,1,2)
        affine_matrix  = cv2.estimateAffine2D(target_points, input_points)
        return affine_matrix
    @staticmethod
    def apply_afine(image,transformation_matrix):
        height, width = image.shape[:2]
        aligned_img_affine = cv2.warpAffine(image,transformation_matrix, (width, height))
        return aligned_img_affine
    @staticmethod
    def unapply_affin(image, transformation_matrix):
        height,width = image.shape[:2]
        transformation_matrix = np.linalg.pinv(transformation_matrix).reshape(2,3)
        allign_img_affine = cv2.warpAffine(image,transformation_matrix,(width,height))
        return allign_img_affine
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
    def Serch_crop_object_in_images_modified(roi, cropped_images, input_image, target_image):        
        sift = cv2.SIFT_create()
        bf_matcher = cv2.BFMatcher()
        
        # Detect and compute features for cropped image, input image, and target image
        cropped_keypoints, cropped_descriptors = sift.detectAndCompute(cropped_images, None)
        input_keypoints, input_descriptors = sift.detectAndCompute(input_image, None)
        target_keypoints, target_descriptors = sift.detectAndCompute(target_image, None)
        input_matches = bf_matcher.match(input_descriptors, cropped_descriptors)
        target_matches = bf_matcher.match(target_descriptors, cropped_descriptors)
        input_matches = DetectChanges.update_matches(input_matches)
        target_matches = DetectChanges.update_matches(target_matches)
        match_image = DetectChanges.__show_matches(target_image, target_keypoints, cropped_images, cropped_keypoints, target_matches[:])
        Processing.open_images(match_image,"Match")
        input_points = []
        target_points =[]
        for i in range(min(len(input_matches),len(target_matches))):
            input_points.append(input_keypoints[input_matches[i].queryIdx].pt)
            target_points.append(target_keypoints[target_matches[i].queryIdx].pt)
        input_points = np.array(input_points).reshape(-1,1,2)
        target_points = np.array(target_points).reshape(-1,1,2)
        affine_matrix  = cv2.estimateAffine2D(target_points, input_points)
        transformed=  DetectChanges.apply_afine(input_image,affine_matrix[0])
        Processing.open_images(transformed,"transformed")
        return transformed   

        

    @staticmethod
    def updateRoi(crop, first_image, second_image):
        shift = cv2.SIFT_create()
        brute_force_object= cv2.BFMatcher()

       
        roi_image = crop
        keypoints_roi, descriptors_roi = shift.detectAndCompute(roi_image, None)
        keypoints_second, descriptors_second = shift.detectAndCompute(second_image, None)
        matches = brute_force_object.match(descriptors_roi, descriptors_second)
        matches = DetectChanges.update_matches(matches)
        match_image = DetectChanges.__show_matches(roi_image,keypoints_roi, second_image, keypoints_second, matches[:])
        Processing.open_images(match_image,"match")

        points_roi = np.zeros((len(matches), 2), dtype=np.float32)
        points_second = np.zeros((len(matches), 2), dtype=np.float32)
        for i, match in enumerate(matches):
            points_roi[i, :] = keypoints_roi[match.queryIdx].pt
            points_second[i, :] = keypoints_second[match.trainIdx].pt
        if len(matches) >= 4:  # Need at least 4 points to find a bounding box
            x_min = int(np.min(points_second[:, 0]))
            y_min = int(np.min(points_second[:, 1]))
            x_max = int(np.max(points_second[:, 0]))
            y_max = int(np.max(points_second[:, 1]))

            updated_roi = (x_min, y_min, x_max - x_min, y_max - y_min)
        else:
            updated_roi = None

        return updated_roi