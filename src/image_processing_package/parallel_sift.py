import cv2  
import numpy as np
import concurrent.futures
import functools

class ParallelSift():
    def detectAndCompute(self, image, ro=None):
        height, width = image.shape[:2]
        rois = [
            (0, 0, width // 2, height // 2),  # Top-left
            (width // 2, 0, width , height // 2),  # Top-right
            (0, height // 2, width // 2, height),  # Bottom-left
            (width // 2, height // 2, width, height)  # Bottom-right
        ]
        with concurrent.futures.ThreadPoolExecutor() as executor:
            results = list(executor.map(functools.partial(self.define, image), rois))
        all_keypoints = []
        all_descriptors = []
        for keypoints, descriptors in results:
            all_keypoints.extend(keypoints)  # Combine keypoints
            if descriptors is not None:
                all_descriptors.append(descriptors)  # Collect descriptors
        
        # Stack descriptors into a single numpy array (if descriptors exist)
        if all_descriptors:
            all_descriptors = np.vstack(all_descriptors)
        else:
            all_descriptors = np.array([])  # Return an empty array if no descriptors
        
        return all_keypoints, all_descriptors

            
        return kp_dserial, all_descriptors


    def define(self, image, roi):
        x, y, w, h = roi
        roi_image = image[y:y+h, x:x+w]
        detector = cv2.SIFT_create(125)  # You can choose another detector (ORB, AKAZE, etc.)
        keypoints, descriptors = detector.detectAndCompute(roi_image, None)
        keypoints_tuple = [(kp.pt[0], kp.pt[1], kp.size, kp.angle, kp.response, kp.octave, kp.class_id) for kp in keypoints]
        return keypoints_tuple, descriptors

  