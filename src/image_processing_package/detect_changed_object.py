import cv2
import numpy as np
from h5_file_format_package.h5_format import H5FromatWrite
from matplotlib import pyplot as plt
from image_processing_package.tracking import Track
from image_processing_package.parallel_sift import ParallelSift
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
        target_ref_matches =  brute_force_object.knnMatch(input_image_descriptor,
                                                          target_image_discriptor,k=4)
        good = []
        for m,n,o,p in target_ref_matches:
            if m.distance < 0.8*n.distance:
                good.append(m)

        #target_ref_matches = update_matches(target_ref_matches,500)
        return [input_image_key_points,target_image_key_points,input_image_descriptor,target_image_discriptor,good]
    @staticmethod
    def draw_match(input_image,input_image_key_points,input_image_descriptor,target_image,
                   target_image_key_points,target_image_discriptor,target_ref_matches):
        match_plot = cv2.drawMatches(input_image,input_image_key_points,input_image_descriptor,target_image,
                        target_image_key_points,target_image_discriptor,
                        target_ref_matches,None,flags=cv2.DrawMatchesFlags_NOT_DRAW_SINGLE_POINTS)
        
        cv2.imshow("Match",match_plot)
        cv2.waitKey(0)
        cv2.destroyAllWindows()
  
        pass
    @staticmethod
    def detect_feature(image, roi=None, detector_type="SIFT"):
        """
        Detects features in an image using the specified feature detector.
    """
    # Initialize the detector based on the detector_type
        if detector_type == "SIFT":
           #detector = ParallelSift()
           detector = cv2.SIFT_create()
        elif detector_type == "SURF":
            detector = cv2.xfeatures2d.SURF_create(500) if 'xfeatures2d' in dir(cv2) else None
        elif detector_type == "ORB":
            detector = cv2.ORB_create()
        elif detector_type == "FAST":
            detector = cv2.FastFeatureDetector_create(500)
        elif detector_type == "BRISK":
            detector = cv2.BRISK_create(500)
        elif detector_type == "AKAZE":
            detector = cv2.AKAZE_create(descriptor_type=cv2.AKAZE_DESCRIPTOR_MLDB,  # Default, but can be reduced to reduce computation
    descriptor_size=0,  # Default, keep small to reduce computation
    descriptor_channels=3,  # Reduce channels if needed
    threshold=0.002,  # Increase threshold (default is 0.001) to detect fewer keypoints
    nOctaves=2,  # Reduce octaves (default is 4), fewer scales = faster computation
    nOctaveLayers=2,  # Reduce octave layers (default is 4)
    diffusivity=cv2.KAZE_DIFF_PM_G2  # Keep default for speed
    )
        elif detector_type == "KAZE":
            detector = cv2.KAZE_create(500)
        elif detector_type == "MSER":
            detector = cv2.MSER_create(500)
        elif detector_type == "AGAST":
            detector = cv2.AgastFeatureDetector_create(500)


        else:
            raise ValueError(f"Unsupported detector type: {detector_type}")

        if detector is None:
            raise ValueError(f"{detector_type} is not available in your OpenCV installation.")

    # Generate mask if ROI is provided
        # mask = None
        # if roi:
        #     mask = DetectChanges.generate_mask_from_roi(roi, image)

    # Detect keypoints and compute descriptors
        if detector_type in ["SIFT", "SURF", "ORB", "BRISK", "AKAZE", "KAZE"]:
            #x, y, w, h = roi
            keypoints, descriptors = detector.detectAndCompute(image,None)
           
        else:
            keypoints = detector.detect(image, None)
            descriptors = None

    # Convert keypoints to a list of tuples
        keypoints_tuple = [(kp.pt[0], kp.pt[1], kp.size, kp.angle, kp.response, kp.octave, kp.class_id) for kp in keypoints]

        return keypoints_tuple, descriptors
    # @staticmethod
    # def update_keypoints_parallel(images: list, roi: list, detector_type="SIFT"):
    #     param = []
    #     kp_dserial = []
        
    #     for i, image in enumerate(images):
    #         height, width = image.shape[:2]
    #         rois = [
    #             (0, 0, width // 2, height // 2),  # Top-left
    #             (width // 2, 0, width // 2, height // 2),  # Top-right
    #             (0, height // 2, width // 2, height // 2),  # Bottom-left
    #             (width // 2, height // 2, width // 2, height // 2)  # Bottom-right
    #         ]
    #         for roi_coords in rois:
    #             param.append((image, roi_coords, detector_type))
        
    #     with multiprocessing.Pool(processes=12) as pool:
    #         result = pool.starmap(DetectChanges.detect_feature, param)
        
    #     for i in range(len(images)):
    #         keypoints = []
    #         descriptors = []
    #         for j in range(4):
    #             kp, desc = result[i * 4 + j]
    #             x_offset, y_offset, _, _ = roi[i]
    #             keypoints.extend([cv2.KeyPoint(x[0] + x_offset, x[1]+ y_offset, x[2], x[3], x[4], x[5], x[6]) for x in kp])
    #             if desc is not None:
    #                 descriptors.append(desc)
    #         if descriptors:
    #             descriptors = np.vstack(descriptors)
    #         else:
    #             descriptors = None
    #         kp_dserial.append([keypoints, descriptors])
        
    #     return kp_dserial
    @staticmethod
    def update_keypoints(images:list,detector_type="SIFT"):
        # image_list = []
        # for i in images:
        #     image_list.append(DetectChanges.reduce_image_quality(i))
        param=[]
        param1=[]
        key_points = []
        kp_dserial = []     
        for i ,image in enumerate(images):
             param.append((image,detector_type))
        with multiprocessing.Pool(processes=len(images)) as pool:
            result = pool.starmap(DetectChanges.detect_feature,param)
        for i in result:
            kp_dserial.append([[cv2.KeyPoint(x[0], x[1], x[2], x[3], x[4], x[5], x[6]) for x in i[0]],i[1]])         
           
        # for i,image in enumerate (images):
        #     param1.append(DetectChanges.compute_descriptosr(key_points[i],image))
        # for i, descriptor in  enumerate(param1):
        #     kp_dserial.append([key_points[i],descriptor])
        return kp_dserial
    @staticmethod
    def compute_descriptosr(key_points,images):    
        #keypoints = [cv2.KeyPoint(float(kp[0]), float(kp[1]), float(kp[2]), float(kp[3]), float(kp[4]), int(kp[5]), int(kp[6])) for kp in key_points]
        sift = cv2.SIFT_create()
        _,descriptors = sift.compute(images,key_points)
        return descriptors
   
                
    @staticmethod
    def update_keypoints_roi_case(old_KPD,old_roi,old_images,new_images,tracker:Track, detector_type="SIFT"):
        case_val = []
        for i,image in enumerate(old_images):
            case_val.append(np.array_equal(image,new_images[i]))
        match case_val:
            case (True, True, True):
                return [old_KPD,old_roi,tracker]                
            case (True, True, False):
                 temp_roi = tracker.update_roi([new_images[2]])          
                 temp_kpd = DetectChanges.update_keypoints([new_images[2]],temp_roi,detector_type)
                 old_KPD[2][0]=temp_kpd[0][0]
                 old_KPD[2][1]=temp_kpd[0][1]
                 old_roi[2] = temp_roi[0]
                 return [old_KPD,old_roi,tracker]
            case (True, False, True):
                 temp_roi = tracker.update_roi([new_images[1]])          
                 temp_kpd = DetectChanges.update_keypoints([new_images[1]],temp_roi,detector_type)
                 old_KPD[1][0]=temp_kpd[0][0]
                 old_KPD[1][1]=temp_kpd[0][1]
                 old_roi[1] = temp_roi[0]
                 return ([old_KPD,old_roi,tracker])            
            case (True, False, False):
                temp_roi = tracker.update_roi([new_images[1],new_images[2]])          
                temp_kpd = DetectChanges.update_keypoints([new_images[1],new_images[2]],temp_roi,detector_type)
                old_KPD[1][0]=temp_kpd[0][0]
                old_KPD[2][0]=temp_kpd[1][0]
                old_KPD[1][1]=temp_kpd[0][1]
                old_KPD[2][1]=temp_kpd[1][1]
                old_roi[1] = temp_roi[0]
                old_roi[2] = temp_roi[0]
                return ([old_KPD,old_roi,tracker])            
            case (False, True, True):
                temp_roi = tracker.update_roi([new_images[0]])          
                temp_kpd = DetectChanges.update_keypoints([new_images[0]],temp_roi,detector_type)
                old_KPD[0][0]=temp_kpd[0][0]
                old_KPD[0][1]=temp_kpd[0][1]
                old_roi[0] = temp_roi[0]
                return ([old_KPD,old_roi,tracker])            
            case (False, True, False):
                temp_roi = tracker.update_roi([new_images[0],new_images[2]])          
                temp_kpd = DetectChanges.update_keypoints([new_images[0],new_images[2]],temp_roi,detector_type)
                old_KPD[0][0]=temp_kpd[0][0]
                old_KPD[2][0]=temp_kpd[1][0]
                old_KPD[0][1]=temp_kpd[0][1]
                old_KPD[2][1]=temp_kpd[1][1]
                old_roi[0] = temp_roi[0]
                old_roi[2] = temp_roi[0]
                return [old_KPD,old_roi,tracker]
            case (False, False, True):                               
                temp_roi = tracker.update_roi([new_images[0],new_images[1]])          
                temp_kpd = DetectChanges.update_keypoints([new_images[0],new_images[1]],temp_roi,detector_type)
                old_KPD[0][0]=temp_kpd[0][0]
                old_KPD[1][0]=temp_kpd[1][0]
                old_KPD[0][1]=temp_kpd[0][1]
                old_KPD[1][1]=temp_kpd[1][1]
                old_roi[0] = temp_roi[0]
                old_roi[1] = temp_roi[0]
                return [old_KPD,old_roi,tracker]
                
            case (False, False, False):
                temp_roi = tracker.update_roi([new_images[0],new_images[1],new_images[2]])          
                temp_kpd = DetectChanges.update_keypoints([new_images[0],new_images[1],new_images[2]],temp_roi,detector_type)
                old_KPD= temp_kpd
                old_roi = temp_roi
                return [old_KPD,old_roi,tracker]
            case _:
                return [old_KPD, old_roi, tracker]
        

  
    @staticmethod
    def transform(input_image,input_image_key_points,target_image_key_points,target_ref_matches,scale_factor):
        transformatoion_matrix= DetectChanges.compute_homography(input_image_key_points,
                                                                 target_image_key_points,target_ref_matches,scale_factor)
        transformed = DetectChanges.apply_afine(input_image,transformatoion_matrix)
        return transformed
    @staticmethod
    def transform_pr(input_image,input_image_key_points,target_image_key_points,target_ref_matches):
        transformatoion_matrix= DetectChanges.compute_prespective_shift_matrix(input_image_key_points,
                                                                               target_image_key_points,target_ref_matches)
       
        transformed = DetectChanges.apply_prespective_transformation(input_image,transformatoion_matrix)
        return transformed

    @staticmethod
    def compute_homography(input_keypoints,target_keypoints,matches,scale_factor):
        input_points = []
        target_points = []
        for i in matches:
            input_points.append(input_keypoints[i.queryIdx].pt)
            target_points.append(target_keypoints[i.trainIdx].pt)   
        input_points = np.array(input_points).reshape(-1,1,2)
        target_points = np.array(target_points).reshape(-1,1,2)
        affine_matrix, _  = cv2.estimateAffine2D(target_points, input_points)
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
        roi = source_image[y:y+h, x:x+w]
        if roi.shape != target_image[y:y+h, x:x+w].shape:
            raise ValueError("The ROI size doesn't match the target region size.")
        target_image[y:y+h, x:x+w] = roi
        return target_image
    @staticmethod
    def reduce_image_quality(image):
        """Reduces the quality of the image for smoother display.
        Args:
            image: The image captured by the camera.
        Returns:
            A reduced-quality version of the image."""
        width = image.shape[1]
        height = image.shape[0]
        reduced_image = cv2.resize(image.copy(), (int(height/4), int(width/4)), interpolation=cv2.INTER_CUBIC)
        return reduced_image
    @staticmethod
    def run(all_new_images,i,result):        
        dec_ch = DetectChanges()
        if i ==0:
            updated_value = DetectChanges.update_keypoints(all_new_images,detector_type="SIFT")
            result = updated_value
        blue_image_key_points,blue_image_descriptor = result[0]
        green_image_key_points,green_image_descriptor = result[1]
        red_image_key_points,red_image_descriptor = result[2]

        param=dec_ch.check_for_match_second(blue_image_descriptor,
                                            blue_image_key_points,green_image_descriptor,
                                            green_image_key_points)
        
        
        
        green= dec_ch.transform(all_new_images[1],param[0],param[1],param[4],scale_factor=1)
        param= dec_ch.check_for_match_second(blue_image_descriptor,blue_image_key_points
                                             ,red_image_descriptor,red_image_key_points)
        
        red= dec_ch.transform(all_new_images[2],param[0],param[1],param[4],scale_factor=1)

        blue= all_new_images[0]
        return [blue,green,red],result

    