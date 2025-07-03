import cv2
import h5py
import numpy as np
from skimage.metrics import structural_similarity as ssim
from processing_using_raft.raft_impl import ChannelReg
class raft_tetst():
    def __init__(self):
        pass
    def read_sample(self,file_path,dataset_name = "reference",number_of_frames = 10): 
          image1 = []     
          image2 = []              
          with h5py.File(file_path, 'r') as f:
              if dataset_name not in f:
                  print(f"Dataset '{dataset_name}' not found in the file.")
                  return
              
              video_data1 = f["reference"]  # Assume shape (num_frames, H, W [,C])
              video_data2 = f["target"]  # Assume shape (num_frames, H, W [,C])
              num_frames = video_data1.shape[0]

              print(f"Video shape: {video_data1.shape}, dtype: {video_data1.dtype}")

              for i in range(number_of_frames):
                  frame1 = video_data1[i]
                  frame2 = video_data2[i]
                  # Normalize if necessary
                  if frame1.dtype != np.uint8:
                      frame1 = (255 * (frame1 - frame1.min()) / (frame1.ptp() + 1e-8)).astype(np.uint8)
               
                  image1.append(cv2.resize(frame1, (960, 540),interpolation=cv2.INTER_AREA))
                  image2.append(cv2.resize(frame2, (960, 540),interpolation=cv2.INTER_AREA)) 
          return image1,image2


    def read_from_camera1(self,path):   
        image = []
        im1 = []        
        with h5py.File(path, 'r') as f:
            k=0
            for i in range(500):
                for j in range(3):
                   im1.append(f[str(k+j)][:]) 
                   print(k+j)
                imtemp=[]
                b=im1[0]
                g = im1[2]
                r=im1[1]
                imtemp.append(b)
                imtemp.append(g)
                imtemp.append(r)
                im = cv2.merge(imtemp) 
                # cv2.imshow("merged",im)
                # cv2.waitKey(0)
                # cv2.destroyAllWindows()

                image.append(cv2.resize(im, (960, 540),interpolation=cv2.INTER_AREA))
                im1 = []
                k = k+3
        return image     
    def read_from_camera(self,path,channel):
        image = []
       
        imtemp_blue=[]
        imtemp_green=[]
        imtemp_red=[]
        blue_3 = []
        green_3 = []
        red_3 = []        
        with h5py.File(path, 'r') as f:                
            k=0            
            for i in range(1000):
                im1 = []
                for j in range(3):
                   im1.append(f[str(k+j)][:]) 
                   print(k+j)
                b=im1[0]
                g = im1[1]
                r=im1[2]
                imtemp_blue.append(g)
                imtemp_green.append(r)
                imtemp_red.append(b)
                k=k+3
                # cv2.imshow("merged",im)
                # cv2.waitKey(0)
                # cv2.destroyAllWindows() 
            if channel == "b":
                print("reading blue channel") 
                for i in range(len(b)):
                    temp = []         
                   
                    for j in range(3):              
                        if i+k>len(imtemp_blue)-3:
                            return blue_3
                        else:
                            temp.append(imtemp_blue[k+j])
                            print(j+k)
                    temporary_hold = cv2.merge(temp)
                    blue_3.append(cv2.resize(temporary_hold, (1920, 1080),interpolation=cv2.INTER_AREA))
                    # cv2.imshow("blue",cv2.merge(temp))
                    # cv2. itKey(0)
                    # cv2.destroyAllWindows()
                    k=k+3
                return blue_3
            elif channel == "g":
                k=0
                for i in range(len(b)):
                    temp = []
                    for j in range(3):
                        if i+k>len(imtemp_blue)-3:
                            return blue_3
                        else:
                            temp.append(imtemp_green[k+j])
                            print(j+k)
                    temporary_hold = cv2.merge(temp)
                    blue_3.append(cv2.resize(temporary_hold, (1920, 1080),interpolation=cv2.INTER_AREA))
                    k=k+3
                return blue_3            
            elif channel == "r":
                 k=0
                 for i in range(len(b)):
                    temp = []
                    for j in range(3):
                        if i+k>len(imtemp_green)-3:
                            return blue_3
                        else:
                            temp.append(imtemp_green[k+j])
                    temporary_hold = cv2.merge(temp)
                    blue_3.append(cv2.resize(temporary_hold, (1920, 1080),interpolation=cv2.INTER_AREA))
                    k=k+3
                 return blue_3  
            else:
                return self.read_from_camera1(path) 
    def compute_ssim_list(self,ref_images, target_images):
        assert len(ref_images) == len(target_images), "Lists must be of same length"    
        ssim_scores = []
        for ref, tgt in zip(ref_images, target_images):
        # Convert both to grayscale if they are color
           if ref.ndim == 3 and ref.shape[-1] == 3:
                ref = cv2.cvtColor(ref, cv2.COLOR_BGR2GRAY)  
           if tgt.ndim == 3 and tgt.shape[-1] == 3:
                tgt = cv2.cvtColor(tgt, cv2.COLOR_BGR2GRAY)        
           score = ssim(ref, tgt,full = False)
           ssim_scores.append(score)    
        return ssim_scores
    
    def run(self):
        path = "image.h5"
        reg = ChannelReg() 
        image = self.read_from_camera1("image1.h5")
        #similarity_index_before = self.compute_ssim_list(image, target)

        image_batch = []
        offset = 100
        for i in range(10):
            cv2.imshow("image", image[i])
            cv2.waitKey(0)
            cv2.destroyAllWindows()
            image_batch.append(image[i + offset])
        images = reg.register_channels(image_batch)
        #similarity_index_after = self.compute_ssim_list(images, target)
        for unreg, reg_img in zip(image_batch, images):
        # Ensure images are the same size
            if unreg.shape != reg_img.shape:
                reg_img = cv2.resize(reg_img, (unreg.shape[1], unreg.shape[0]))

        # Horizontally stack for side-by-side comparison
            split_screen = cv2.hconcat([unreg, reg_img])

        # Show combined image
            cv2.imshow("Unregistered (Left)  |  Registered (Right)", split_screen)
            key = cv2.waitKey(0)
            if key == 27:  # ESC to break early
                break
        #for i, (before, after) in enumerate(zip(similarity_index_before, similarity_index_after)):
        #    print(f"Frame {i+1}: SSIM before registration = {before:.4f}, SSIM after registration = {after:.4f}")

    cv2.destroyAllWindows()
obj = raft_tetst()
obj.run()
