import cv2
import numpy as np
from h5_file_format_package.h5_format import H5FormatRead
def detect_feature(image, roi=None, detector_type="SIFT"):
        image_red = image
        kp=[]
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
        if detector_type in ["SIFT", "SURF", "ORB", "BRISK", "AKAZE", "KAZE"]:
            keypoints, descriptors = detector.detectAndCompute(image,None)           
        else:
            keypoints = detector.detect(image_red, None)
            descriptors = None
        # scaled_keypoints = []
        # for kp in keypoints:
        # # Access attributes of the KeyPoint object
        #     scaled_kp = cv2.KeyPoint(
        #     x=kp.pt[0] * 4,  # Scale x-coordinate
        #     y=kp.pt[1] * 4,  # Scale y-coordinate
        #     size=kp.size * 4,  # Scale size
        #     angle=kp.angle,  # Keep the same angle
        #     response=kp.response,  # Keep the same response
        #     octave=kp.octave,  # Keep the same octave
        #     class_id=kp.class_id  # Keep the same class_id
        # )
        
        # scaled_keypoints.append(scaled_kp)
        

        #plot_keypoints(image_red, keypoints)
        #plot_keypoints(image, scaled_keypoints)
        return keypoints, descriptors

def plot_keypoints(image, keypoints):
    """
    Plots keypoints on the input image.

    Args:
        image (numpy.ndarray): The input image (grayscale or color).
        keypoints (list of cv2.KeyPoint): List of keypoints to plot.

    Returns:
        numpy.ndarray: The image with keypoints drawn.
    """
    # Create a copy of the image to avoid modifying the original
    output_image = image.copy()

    # Draw keypoints on the image
    output_image = cv2.drawKeypoints(
        image=output_image,
        keypoints=keypoints,
        outImage=None,  # Output image (None means create a new image)
        color=(0, 255, 0),  # Color of the keypoints (BGR format, green in this case)
        flags=cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS  # Draw circles and orientations
    )
    cv2.imshow("Keypoints",output_image)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

 

def update_matches(target_ref_matches, match_number):
        # First, apply the ratio test``
         
        sorted_matches = sorted(target_ref_matches, key=lambda x: x.distance)
        n = min(match_number, len(sorted_matches))
        filtered_matches = sorted_matches[:n]
        return filtered_matches

def check_for_match_second(input_image_descriptor,input_image_key_points,target_image_discriptor,target_image_key_points):
        brute_force_object= cv2.BFMatcher()
        target_ref_matches =  brute_force_object.knnMatch(input_image_descriptor,
                                                          target_image_discriptor,k=4)
        good = []
        for m,n,o,p in target_ref_matches:
            if m.distance < 0.75*n.distance:
                print(m,n)
                good.append(m)

        #target_ref_matches = update_matches(target_ref_matches,500)
        return [input_image_key_points,target_image_key_points,input_image_descriptor,target_image_discriptor,good]

def draw_match(input_image,input_image_key_points,input_image_descriptor,target_image,
                   target_image_key_points,target_image_discriptor,target_ref_matches):
        match_plot = cv2.drawMatches(input_image,input_image_key_points,target_image,
                        target_image_key_points,
                        target_ref_matches,None,flags=cv2.DrawMatchesFlags_NOT_DRAW_SINGLE_POINTS)
        
        cv2.imshow("Match",match_plot)
        cv2.waitKey(0)
        cv2.destroyAllWindows()
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
def apply_afine(image,transformation_matrix):
        height, width = image.shape[:2]
        aligned_img_affine = cv2.warpAffine(image,transformation_matrix, (width, height))
        return aligned_img_affine

def run():
    var=0
    read_imaegs = H5FormatRead()
    result = None 
    for i in range(2):
        algorithm = "SIFT"
        b = str(var)
        g = str(var+1)
        r= str (var+2)
        var=var+3        
        green = read_imaegs.read_files("image.h5",g)
        red = read_imaegs.read_files("image.h5",r)
        blue = read_imaegs.read_files("image.h5",b)
        keypoints_blue, descriptors_blue = detect_feature(blue, detector_type=algorithm)
        keypoints_green, descriptors_green = detect_feature(green, detector_type=algorithm)    
        keypoints_red, descriptors_red = detect_feature(red, detector_type=algorithm)
        result = check_for_match_second(descriptors_blue,keypoints_blue,descriptors_red,keypoints_red)
        result_blue_green = check_for_match_second(descriptors_blue,keypoints_blue,descriptors_green,keypoints_green)
        
        draw_match(blue,result[0],result[2],red,result[1],result[3],result[4])
        draw_match(blue,result_blue_green[0],result_blue_green[2],green,result_blue_green[1],result_blue_green[3],result_blue_green[4])
        blue_red_matrix = compute_homography(result[0],result[1],result[4],1)
        blue_green_matrix = compute_homography(result_blue_green[0],result_blue_green[1],result_blue_green[4],1)
        transformed_red = apply_afine(red,blue_red_matrix)
        transformed_green = apply_afine(green,blue_green_matrix)
        color = cv2.merge([blue,transformed_green,transformed_red])
        cv2.imshow("Color",color)
        cv2.waitKey(0)

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
        

        

        
     
if __name__ == "__main__":
    run()