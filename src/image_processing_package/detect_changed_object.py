import cv2
import numpy as np
from h5_file_format_package.h5_format import H5FromatWrite
from image_processing_package.tracking import Track
import multiprocessing
class DetectChanges():
    @staticmethod
    def update_matches(target_ref_matches, match_number):
        # First, apply the ratio test``
         
        sorted_matches = sorted(target_ref_matches, key=lambda x: x.distance)
        n = min(match_number, len(sorted_matches))
        filtered_matches = sorted_matches[:n]
        return filtered_matches
    @staticmethod
    def check_for_match_second(input_image_descriptor,input_image_key_points,target_image_discriptor,target_image_key_points):
  
        brute_force_object= cv2.BFMatcher()
        target_ref_matches =  brute_force_object.match(input_image_descriptor,target_image_discriptor)
        target_ref_matches = DetectChanges.update_matches(target_ref_matches,20)
        return [input_image_key_points,target_image_key_points,input_image_descriptor,target_image_discriptor,target_ref_matches]
    @staticmethod
    def detect_feature(image,roi):
       
        shift = cv2.ORB_create(500)#cv2.SIFT_create(500)##
        if not roi:
            kp,b=shift.detectAndCompute(image,None)
            keypoints_tuple = [(kp.pt[0], kp.pt[1], kp.size, kp.angle, kp.response, kp.octave, kp.class_id) for kp in kp]
            return keypoints_tuple,b
        else:
            mask_refrence = DetectChanges.generate_mask_from_roi(roi,image)
            kp,b=shift.detectAndCompute(image,mask_refrence)
            keypoints_tuple = [(kp.pt[0], kp.pt[1], kp.size, kp.angle, kp.response, kp.octave, kp.class_id) for kp in kp]
            return keypoints_tuple,b
    @staticmethod
    def update_keypoints(images:list,roi:list):
        param=[]
        kp_dserial = []     
        for i ,image in enumerate(images):
            param.append((image,roi[i]))
        with multiprocessing.Pool(processes=len(images)) as pool:
            result = pool.starmap(DetectChanges.detect_feature,param)
        for i in result:
            kp_dserial.append([[cv2.KeyPoint(x[0], x[1], x[2], x[3], x[4], x[5], x[6]) for x in i[0]],i[1]])
        return kp_dserial
    @staticmethod
    def update_keypoints_roi_case(old_KPD,old_roi,old_images,new_images,tracker:Track):
        case_val = []
        for i,image in enumerate(old_images):
            case_val.append(np.array_equal(image,new_images[i]))

        print(case_val)
        match case_val:
            case (True, True, True):
                return [old_KPD,old_roi,tracker]
                
            case (True, True, False):
                 temp_roi = tracker.update_roi([new_images[2]])          
                 temp_kpd = DetectChanges.update_keypoints([new_images[2]],temp_roi)
                 old_KPD[2][0]=temp_kpd[0][0]
                 old_KPD[2][1]=temp_kpd[0][1]
                 old_roi[2] = temp_roi[0]
                 return [old_KPD,old_roi,tracker]

            case (True, False, True):
                 temp_roi = tracker.update_roi([new_images[1]])          
                 temp_kpd = DetectChanges.update_keypoints([new_images[1]],temp_roi)
                 old_KPD[1][0]=temp_kpd[0][0]
                 old_KPD[1][1]=temp_kpd[0][1]
                 old_roi[1] = temp_roi[0]
                 return ([old_KPD,old_roi,tracker])
            
            case (True, False, False):
                temp_roi = tracker.update_roi([new_images[1],new_images[2]])          
                temp_kpd = DetectChanges.update_keypoints([new_images[1],new_images[2]],temp_roi)
                old_KPD[1][0]=temp_kpd[0][0]
                old_KPD[2][0]=temp_kpd[1][0]

                old_KPD[1][1]=temp_kpd[0][1]
                old_KPD[2][1]=temp_kpd[1][1]

                old_roi[1] = temp_roi[0]
                old_roi[2] = temp_roi[0]

                return ([old_KPD,old_roi,tracker])
            
            case (False, True, True):
                temp_roi = tracker.update_roi([new_images[0]])          
                temp_kpd = DetectChanges.update_keypoints([new_images[0]],temp_roi)
                old_KPD[0][0]=temp_kpd[0][0]
                old_KPD[0][1]=temp_kpd[0][1]
                old_roi[0] = temp_roi[0]
                return ([old_KPD,old_roi,tracker])
            
            case (False, True, False):
                temp_roi = tracker.update_roi([new_images[0],new_images[2]])          
                temp_kpd = DetectChanges.update_keypoints([new_images[0],new_images[2]],temp_roi)

                old_KPD[0][0]=temp_kpd[0][0]
                old_KPD[2][0]=temp_kpd[1][0]

                old_KPD[0][1]=temp_kpd[0][1]
                old_KPD[2][1]=temp_kpd[1][1]

                old_roi[0] = temp_roi[0]
                old_roi[2] = temp_roi[0]
                return [old_KPD,old_roi,tracker]
            case (False, False, True):                               
                temp_roi = tracker.update_roi([new_images[0],new_images[1]])          
                temp_kpd = DetectChanges.update_keypoints([new_images[0],new_images[1]],temp_roi)

                old_KPD[0][0]=temp_kpd[0][0]
                old_KPD[1][0]=temp_kpd[1][0]

                old_KPD[0][1]=temp_kpd[0][1]
                old_KPD[1][1]=temp_kpd[1][1]

                old_roi[0] = temp_roi[0]
                old_roi[1] = temp_roi[0]
                return [old_KPD,old_roi,tracker]
                
            case (False, False, False):
                temp_roi = tracker.update_roi([new_images[0],new_images[1],new_images[2]])          
                temp_kpd = DetectChanges.update_keypoints([new_images[0],new_images[1],new_images[2]],temp_roi)
                old_KPD= temp_kpd
                old_roi = temp_roi
                return [old_KPD,old_roi,tracker]
            case _:
                return [old_KPD, old_roi, tracker]
        

  
    @staticmethod
    def transform(input_image,input_image_key_points,target_image_key_points,target_ref_matches):
        transformatoion_matrix= DetectChanges.compute_homography(input_image_key_points,target_image_key_points,target_ref_matches)
        transformed = DetectChanges.apply_afine(input_image,transformatoion_matrix[0])
        return transformed
    @staticmethod
    def transform_pr(input_image,input_image_key_points,target_image_key_points,target_ref_matches):
        transformatoion_matrix= DetectChanges.compute_prespective_shift_matrix(input_image_key_points,target_image_key_points,target_ref_matches)
        transformed = DetectChanges.apply_prespective_transformation(input_image,transformatoion_matrix)
        return transformed

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
    def compute_prespective_shift_matrix(input_keypoints,target_keypoints,matches):
        input_points = []
        target_points = []
        matches= DetectChanges.update_matches(matches,4)
        for i in matches:
            input_points.append(input_keypoints[i.queryIdx].pt)
            target_points.append(target_keypoints[i.trainIdx].pt)      
        input_points = np.array(input_points).astype(np.float32)
        target_points=  np.array(target_points).astype(np.float32)
        mat = cv2.getPerspectiveTransform(target_points, input_points)      
        return mat
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
    def apply_prespective_transformation(input_image,transformatoion_matrix):
         height, width = input_image.shape[:2]
         transformed_image = cv2.warpPerspective(input_image,transformatoion_matrix,(width,height))
         return transformed_image

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
    def reconstruct_background(blue_transformed: list, red_transformed: list, green_transformed: list,
                               blue_original: list, red_original: list, green_original: list, roi: list):
      blue = H5FromatWrite("bcb",override=True)
      green = H5FromatWrite("bcg",override=True)
      red = H5FromatWrite("bcr",override=True)
      for i in range(len(blue_original)):
         images= DetectChanges.stich_roi(blue_transformed[i],green_transformed[i],red_transformed[i],blue_original[i],
                                  green_original[i],red_original[i],roi[i])
         blue.record_images(images[0],str(i))
         green.record_images(images[1],str(i))
         red.record_images(images[2],str(i))

    @staticmethod
    def stich_roi(blue_t,green_t,red_t,blue_o,green_o,red_o,roi):
        b = DetectChanges.stitch_roi_into_grayscale_image(blue_o,blue_t,roi)
        g = DetectChanges.stitch_roi_into_grayscale_image(green_o,green_t,roi)
        r =DetectChanges.stitch_roi_into_grayscale_image(red_o,red_t,roi)
        return b,g,r
        
    @staticmethod
    def stitch_roi_into_grayscale_image(target_image: np.ndarray, source_image: np.ndarray, roi_coords: list):
        """
        Stitch an ROI from a source grayscale image into a target grayscale image.

        :param source_image: The source grayscale image from which the ROI will be extracted.
        :param target_image: The target grayscale image where the ROI will be stitched.
        :param roi_coords: A list defining the ROI coordinates [x_min, y_min, x_max, y_max].
        :return: A grayscale image with the ROI stitched from the source image."""   
        x, y, w, h = roi_coords
        print(roi_coords)
        roi = source_image[y:y+h, x:x+w]
        if roi.shape != target_image[y:y+h, x:x+w].shape:
            raise ValueError("The ROI size doesn't match the target region size.")
        target_image[y:y+h, x:x+w] = roi
        return target_image