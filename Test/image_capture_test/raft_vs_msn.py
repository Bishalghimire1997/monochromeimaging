"""This code intends to compare the performance of the Raft models trained on Things Chairs Kitti and sintel with
model trained on our approach. Our hypothesis for the nonridgid regestration, our model should outperform raft's because 
our model is trained on perlin noise which is non ridgid deformation to start with"""

import numpy as np 
import h5py
import cv2
from processing_using_raft.evaluation import Evaluation
from processing_using_raft.raft_impl import ChannelReg
class Raft_v_msn():
    def __init_(self):
        self.eval = Evaluation()
        self.reg = ChannelReg()
        pass
    def compute_ssim_delta_E(self,ref,target):
        ssim = self.eval.get_structure_similarity(ref,target)
        del_e = self.eval.compute_del_e(ref,target)
        return ssim,del_e.mean()
    def read_sample(self,file_path,dataset_name = "reference",number_of_frames = 10, esc= 0,crop =False): 

          image1 = []     
          image2 = []          
          offset = 20 +esc 
          with h5py.File(file_path, 'r') as f:
              if dataset_name not in f:
                  print(f"Dataset '{dataset_name}' not found in the file.")
                  return
              
              video_data1 = f["reference"]  # Assume shape (num_frames, H, W [,C])
              video_data2 = f["target"]  # Assume shape (num_frames, H, W [,C])
              num_frames = video_data1.shape[0]

              print(f"Video shape: {video_data1.shape}, dtype: {video_data1.dtype}")

              for i in range(number_of_frames):
                  frame1 = video_data1[i+offset]
                  frame2 = video_data2[i+offset]
                  # Normalize if necessary
                  if frame1.dtype != np.uint8:
                      frame1 = (255 * (frame1 - frame1.min()) / (frame1.ptp() + 1e-8)).astype(np.uint8)
                
                  image1.append(cv2.resize(frame1, (960, 540),interpolation=cv2.INTER_AREA))
                  image2.append(cv2.resize(frame2, (960, 540),interpolation=cv2.INTER_AREA)) 
          if crop:
                image1_crop = []
                image2_crop = []
                if self.roi is None:
                    self.roi = cv2.selectROI("image",image1[0],fromCenter=False)
                for ref,targ in zip(image1,image2):
                    ref = ref[self.roi[1]:self.roi[1]+self.roi[3],self.roi[0]:self.roi[0]+self.roi[2]]
                    targ = targ[self.roi[1]:self.roi[1]+self.roi[3],self.roi[0]:self.roi[0]+self.roi[2]]
                    image1_crop.append(ref)
                    image2_crop.append(targ)
                return image1_crop,image2_crop 
          else:
                return image1,image2


    def run_on_endoscopy_dataset(self):       
        eval_im = Evaluation()
        path = "image.h5" 
        reg = ChannelReg()       
        ssim_before = []
        del_e_before = []
        ssim_after = []
        del_e_after=[]
       
        offset = 0 
        ref,target = self.read_sample(path,crop = True)
        for j in range(5):
        
            structural_similarity_before = np.mean(eval_im.get_structure_similarity(ref, target))    


            color_index_before = np.mean(eval_im.compute_del_e(ref, target)) 
            image_batch = []
            for i in range(10):    
        
                #  cv2.imshow("image", ref[i])
                #  cv2.wa Key(0) 
                #  cv2.destroyAllWindows()    
                 image_batch.append(ref[i])
            flow = reg.compute_flow(fix_batch=ref,floating_batch=target)
            registered = reg.warp_batch(target,flow)
            structural_similarity_after = np.mean(eval_im.edge_structural_similarity(ref, registered))
            color_index_after = np.mean(eval_im.compute_del_e(ref, registered))
            
            
            
               
            print(f"Frame {i+1}: SSIM before registration = {structural_similarity_before:.4f}, SSIM after registration = {structural_similarity_after:.4f}")
            print(f"Frame {i+1}: Color before registration = {color_index_before:.4f}, Color after registration = {color_index_after:.4f}")
           
            offset = offset + 10

            ssim_before.append(structural_similarity_before)
            ssim_after.append(structural_similarity_after)
            del_e_before.append(color_index_before)
            del_e_after.append(color_index_after)
            ref,target = self.read_sample(path,esc=offset,crop = True)
        print("ROI",self.roi)
        print("average delta e before registration",np.mean(color_index_before))
        print("average delta e after registration",np.mean(color_index_after))
        print("average of 50 ssim  before registration",np.mean(ssim_before))
        print("average of 50 ssim  after registration",np.mean(ssim_after))
       
    
obj = Raft_v_msn()
obj.run_on_endoscopy_dataset()