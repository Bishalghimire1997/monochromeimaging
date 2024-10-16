"""Detects the object that moved in a two images"""
import cv2
import numpy as np
import skimage as si
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
        cv2.imshow("ref", grayA)
        cv2.imshow("target",grayB)
        cv2.waitKey(0)


        return thresh
   
       
      
    
    def check_for_match(self):
        mask = self.generate_mask()
        shift = cv2.SIFT_create()
        ref_image_key_points,ref_image_descriptor  = shift.detectAndCompute(self.ref_image,mask)
        target_image_key_points,target_image_discriptor = shift.detectAndCompute(self.target_image,mask)
        brute_force_object= cv2.BFMatcher()
        target_ref_matches =  brute_force_object.match(ref_image_descriptor,target_image_discriptor)
        match_image = self.__show_matches(self.ref_image, ref_image_key_points, self.target_image, target_image_key_points, target_ref_matches[:])    
        self.compute_homography(ref_image_key_points,target_image_key_points,target_ref_matches)
        cv2.imshow("ref target match", match_image)  
        cv2.waitKey(0)
        cv2.destroyAllWindows()



    
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

       # self.crop(self.get_mask(),self.target_image,aligned_img_affine)

        cv2.imshow("Affine Aligned Image", aligned_img_affine)

        cv2.waitKey(0)
        cv2.destroyAllWindows()

   
    def get_contour(self,image):
        contours, _ = cv2.findContours(image, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        filtered_contours = [cnt for cnt in contours if cv2.contourArea(cnt) > 200]
        sorted_contours = sorted(filtered_contours, key=cv2.contourArea, reverse=True)
        return sorted_contours[:10]
    def crop_to_contour(self,contour, image):
        crops = []
        for i in contour:
            x, y, w, h = cv2.boundingRect(i)
            crops.append(image[y:y+h, x:x+w])
        return crops
    def check_similarity(self,crops1:list,crops2:list):
        temp = []
        match= []

        for i in range(len(crops1)):
            for j in range(len (crops2)):
                index,_ = si.metrics.structural_similarity(crops1[i], crops2[j], full=True)
                temp.append(index)
            match.append(crops2[index(max(temp))])
        return[crops1,match]
    # def filter(self,crops):
    #     filtered = []
    #     for i in crops:
    #         if len(i) > 20 and len(i[0]) > 20:
    #             filtered.append(i)
    #     return filtered
            