from flir_image_capture_package.hardware_trigger import FlirTriggerControl
from flir_image_capture_package.software_trigger import FlirTriggerControl as FTC
from scipy.spatial import cKDTree
from matplotlib import pyplot as plt
import numpy as np
import cv2
from image_processing_package.detect_changed_object import DetectChanges
from h5_file_format_package.h5_format import H5FormatRead
from flir_camera_parameter_package.flir_camera_parameters import FlirCamParam
class StaticSceanFeatureExperimts:
    def __init__(self):
        self.param= FlirCamParam()
        self.param.snap_count = 300
        self.param.shutter_time = 1800
        self.param.path = "static_scean_270.h5"
        pass

    def capture_static_scean(self):

        obj = FlirTriggerControl(self.param)
        obj.capture(feed = True,record=True)

        pass
    def read_images(self):
        """Reads 3 consucative the images from the h5 file"""
        "returns color image as well as blue, green and red channel images"
        file  = H5FormatRead()
        print("path",self.param.path)
        blue  = file.read_files(self.param.path,"0")
        green = file.read_files(self.param.path,"2")
        red   = file.read_files(self.param.path,"1")
        color_image = cv2.merge([blue,green,red])
        cv2.imshow("color_image",color_image)
        cv2.waitKey(0)
        cv2.destroyAllWindows()
        #color_image = cv2.imread("example.PNG")
        #blue = color_image[:,:,0]
        #green = color_image[:,:,1]
        #red = color_image[:,:,2]
        return [blue,green,red]



        pass
    def detect_features(self,detector,images):

        result = DetectChanges.update_keypoints(images,detector)  
        return result
    def get_unique_keypoints_and_descriptors(self, detector,features):
      #feature = self.detect_features(detector)
      unique_feature = []
      kp =[]
      dis =[]
    
      # Collect all keypoints and descriptors
      all_keypoints = []
      all_descriptors = []
      print("features length",len(features))
      for key_points, descriptors in features:
          all_keypoints.append(np.array([kp.pt for kp in key_points]))
          all_descriptors.append(descriptors)
      print("All Keypoints" ,len(all_keypoints))
    # Filter unique keypoints and descriptors for each image
      for i, keypoints in enumerate(all_keypoints):
          is_unique = np.ones(len(keypoints), dtype=bool)  # Assume all keypoints are unique initially
        
          for j, other_keypoints in enumerate(all_keypoints):
              temp = []
              if i != j and len(other_keypoints) > 0:
                  tree = cKDTree(other_keypoints)
                  distances, _ = tree.query(keypoints, distance_upper_bound=10)  # Threshold for uniqueness
                  is_unique &= (distances == np.inf)  # Mark non-matching keypoints as unique
        
          unique_kp = [features[i][0][idx] for idx in range(len(keypoints)) if is_unique[idx]]
          unique_desc = all_descriptors[i][is_unique] if all_descriptors[i] is not None else None
          print("unique keypoints",len(unique_kp))
          temp.append(unique_kp)
          temp.append(unique_desc)


          unique_feature.append(temp)
    
      return unique_feature

    def plot_keypoints_2d(self,detector):
        feature = self.detect_features(detector)
        ## each i is a lis that containd keypoints and descriptors for the image passed
        print(len(feature))
        colors = ['gray', 'blue', 'green', 'red']
        for i, (key_points, descriptors) in enumerate(feature):
        # Extract x, y coordinates from keypoints
            x_coords = [kp.pt[0] for kp in key_points]
            y_coords = [kp.pt[1] for kp in key_points]
            plt.scatter(x_coords, y_coords, color=colors[i], label=f"Image {i+1}", alpha=0.6)

        plt.xlabel("X-coordinate")
        plt.ylabel("Y-coordinate")
        plt.title("Keypoints from Multiple Images")
        plt.legend()
        plt.gca().invert_yaxis()  # Invert y-axis to match image coordinates
        plt.show()
    def plot_unique_keypoints_2d(self, detector):
        colors = ['gray', 'blue', 'green', 'red']
        feature = self.get_unique_keypoints_and_descriptors(detector)
        print(len(feature))
    
        plt.figure(figsize=(8, 6))
        for i, (key_points, descriptors) in enumerate(feature):
            if len(key_points) == 0:
                continue  # Skip if no keypoints
        
            x_coords = [kp.pt[0] for kp in key_points]
            y_coords = [kp.pt[1] for kp in key_points]
            plt.scatter(x_coords, y_coords, color=colors[i % len(colors)], label=f"Image {i+1}", alpha=0.6)
    
        plt.xlabel("X-coordinate")
        plt.ylabel("Y-coordinate")
        plt.title("Unique Keypoints from Multiple Images")
        plt.legend()
        plt.gca().invert_yaxis()  # Invert y-axis to match image coordinates
        plt.grid(True)
        plt.show()

    def draw_unique_keypoints_2d(self, detector,images,feature,l):
        colors = [ (255, 0, 0), (0, 255, 0), (0, 0, 255)]  # Gray, Blue, Green, Red
        image = cv2.merge([images[0], images[1], images[2]])  # Merge blue, green, and red channels
        image_temp = image.copy()
        for i, (key_points, descriptors) in enumerate(feature):
           if len(key_points) == 0:
                continue  # Skip if no keypoints
           # Copy the image to avoid modifying the original
           color = colors[i]
           image_temp=cv2.drawKeypoints(image_temp, key_points, None, color, cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS)  # Draw keypoints
        #    for kp in key_points:
        #         x, y = int(kp.pt[0]), int(kp.pt[1])
        #         cv2.circle(image_temp, (x, y), 20, color, -1)  # Draw keypoint as a filled circle
        
        cv2.imshow(f"Image {i+1} - Keypoints", image_temp)
    
        cv2.waitKey(0)
        cv2.destroyAllWindows()
        cv2.imwrite("keypoints_image_"+detector+str(l)+".jpg", image_temp)  # Save the image with keypoints

      
    def plot_keypoints_3d(self,detector):
        feature = self.detect_features(detector)  # Detect features for 4 images
    
        fig = plt.figure(figsize=(10, 7))
        ax = fig.add_subplot(111, projection='3d')  # Create a 3D subplot
    
        colors = ['gray', 'blue', 'green', 'red']  # Define colors for different images

    # Iterate over each image's keypoints
        for i, (key_points, descriptors) in enumerate(feature):
            x_coords = [kp.pt[0] for kp in key_points]  # X-coordinates
            y_coords = [kp.pt[1] for kp in key_points]  # Y-coordinates
            z_coords = [i] * len(key_points)  # Use image index as Z-coordinates

        # Plot keypoints in 3D
            ax.scatter(x_coords, y_coords, z_coords, color=colors[i], s=2.5,label=colors[i], alpha=0.6)

    # Labels and title
        ax.set_xlabel("X-coordinate")
        ax.set_ylabel("Y-coordinate")
        ax.set_zlabel("Channels")
        ax.set_title("3D Keypoints from Multiple Images")
        ax.legend()    
        plt.show()

        
    def main(self):
        self.capture_static_scean() 
        self.read_images()
        self.detect_features()
        self.plot_keypoints()
    def consistent_keypoints(self,detector,channel):
       unique_feature = []
       matches = []
       val = 0
       """This method will check the unique feature in channel and try to match the unique channel feature with the  unique 
       featrue in other test imges within the same channel"""
       # initilize file path
       """We are trying to test for the five test images"""
       path_0 = "static_scean_0.h5"
       path_90 = "static_scean_90.h5"
       path_180 = "static_scean_180.h5"
       path_270 = "static_scean_270.h5"
       path_scaled = "static_scean_scaled.h5"

       """Reading the images from path_0 files"""
       self.param.path = path_0
       img_0  = self.read_images()
       """Reading the images from path_90 files"""
       self.param.path = path_90
       img_90  = self.read_images()
       """Reading the images from path_180 files"""
       self.param.path = path_180
       img_180  = self.read_images()
       """Reading the images from path_270 files"""
       self.param.path = path_270
       img_270  = self.read_images()
    #    """Reading the images from path_scaled files"""
    #    self.param.path = path_scaled
    #    img_scaled  = self.read_images()
       
       images = [img_0,img_90,img_180,img_270]
       #Detecting keypoints and descriptors for the images
       features_img_0 = self.detect_features(detector,img_0)
       print("number of blue keypoints",len(features_img_0[0][0]))
       print("number of green keypoints",len(features_img_0[1][0]))
       print("number of red keypoints",len(features_img_0[2][0]))
       feature_img_90 = self.detect_features(detector,img_90)
       print("number of blue keypoints",len(feature_img_90[0][0]))
       print("number of green keypoints",len(feature_img_90[1][0]))
       print("number of red keypoints",len(feature_img_90[2][0]))
       feature_img_180 = self.detect_features(detector,img_180)
       print("number of blue keypoints",len(feature_img_180[0][0]))
       print("number of green keypoints",len(feature_img_180[1][0]))
       print("number of red keypoints",len(feature_img_180[2][0]))
       feature_img_270 = self.detect_features(detector,img_270)
       print("number of blue keypoints",len(feature_img_270[0][0]))
       print("number of green keypoints",len(feature_img_270[1][0]))
       print("number of red keypoints",len(feature_img_270[2][0]))
     
       features = [features_img_0,feature_img_90,feature_img_180,feature_img_270]

       # drawing the unique keypoints for each image

         # Now we have the features for each image, we can find the unique keypoints and descriptors 
         #We now compute the unique keypoints and descriptors for each image
       for i in features:
           unique_feature.append(self.get_unique_keypoints_and_descriptors(detector,i))  
       print("unique feature length",len(unique_feature[0]))
  
       for i,fe in enumerate(unique_feature):
           self.draw_unique_keypoints_2d(detector,images[i],fe,i)
           
         # Now we can find the matches between the unique keypoints and descriptors of the first image and the others
       matches_all = [] 
       
       for i in range(len(unique_feature)):
           matches=DetectChanges.check_for_match_second(unique_feature[0][channel][1],unique_feature[0][channel][0],unique_feature[i][channel][1],unique_feature[i][channel][0])
           matches_all.append(matches)
        #drawing_all_matches_for corresponding_channels
       imgs =[]
       imgs.append(images[0][channel])
       for i,match in enumerate(matches_all):
           print(" total Matches = ",len(match[4]))
           print("Total keypoints in input image = ",len(match[0]))
           print("Total feature in target image = ",len(match[1]))
           if i== 0:
               continue
           target_image = images[0][channel]
           input_image = images[i][channel]

           input_keypoints = match[0]             # Keypoints for ref_image
           target_keypoints = match[1]          # Keypoints for test_image
           input_descriptors = match[2]           # Descriptors for ref_image
           target_descriptors = match[3]        # Descriptors for test_image
           target_ref_matches = match[4]  
           valid_matches = [m for m in target_ref_matches
                if m.queryIdx < len(target_keypoints) 
                and m.trainIdx < len(input_keypoints)]      # Matches between ref and test
           target_ref_matches = valid_matches
                # Debug: confirm keypoint type

        # Draw matches between the reference and test image
           print("Target Keypoints",len(target_keypoints))
           print("Input Keypoints",len(input_keypoints))
           print("Target descriptor matches",len(target_descriptors))
           matched_image = cv2.drawMatches(target_image, target_keypoints,
                                        input_image, input_keypoints,
                                        target_ref_matches, None,
                                        flags=cv2.DrawMatchesFlags_NOT_DRAW_SINGLE_POINTS)

        # Show the matches
           cv2.imwrite(f"matches_{detector}_{channel}_{i}.jpg", matched_image)
           
               
        
         # now we compute the transformation matrix for the matched keypoints
           mat = DetectChanges.compute_affin(input_keypoints,target_keypoints, target_ref_matches,1)
           print("transformation matrix",mat)
        # now we a apply the transformaton and combine the BGR channels
           imgs.append(DetectChanges.apply_afine(input_image, mat))

       final= cv2.merge([imgs[0],imgs[1],imgs[2]])
       cv2.imshow("final",final)
       cv2.waitKey(0)
       cv2.destroyAllWindows()
       cv2.imwrite("final_image.jpg",final)
       return  final 
    def compute_mse_psnr(self,img1, img2):
        print("img1 shape",img1.shape)
        print("img2 shape",img2.shape)
        assert img1.shape == img2.shape, "Images must have the same dimensions"
        mse = np.mean((img1 - img2) ** 2)
        if mse == 0:
            psnr = float('inf')  
        else:
            max_pixel = 255.0
            psnr = 20 * np.log10(max_pixel / np.sqrt(mse))
    
        return mse, psnr
    def matric_computation(self,detector,channel):
        if channel == 0:
            refrence = cv2.imread("final_image_blue.jpg")
            print("blue")
        elif channel == 1:
            refrence = cv2.imread("final_image_green.jpg")
            print("green")
        else:
            print("red")
            refrence = cv2.imread("final_image_red.jpg")
        target = self.consistent_keypoints(detector,channel)
        target



        #target_green = self.consistent_keypoints("SIFT",1)  
        #target_red = self.consistent_keypoints("SIFT",2)
        mse_blue, psnr_blue = self.compute_mse_psnr(refrence, target)
       
        print("MSE :", mse_blue)
        print("PSNR :", psnr_blue)
  

if __name__ == "__main__":
    obj = StaticSceanFeatureExperimts()   
    obj.matric_computation("ORB",2)
      