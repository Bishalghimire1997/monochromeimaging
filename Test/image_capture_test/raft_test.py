import cv2
import h5py
import numpy as np
from processing_using_raft.evaluation import Evaluation
from skimage.metrics import structural_similarity as ssim
from experiments.local_deformation_correction.sample import RGBMisalignmentSimulator
from processing_using_raft.raft_impl import ChannelReg
class raft_tetst():
    def __init__(self):
        self.roi = None
        pass
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


    def read_from_camera1(self,path,batch_size = 6,start = 0):   
        image = []  
        im1 = []           
        with h5py.File(path, 'r') as f:
            k=start
            for i in range(batch_size) :
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

                image.append(cv2.resize(im, (960, 540),interpolation=cv2.INTER_AREA))
                im1 = []
                k = k+3
        return image  

        


    def read_from_camera(self,path,channel,batch_size = 6):
        image = []
        imtemp_blue=[]
        imtemp_green=[]     
        imtemp_red=[]
        blue_3 = []
        green_3 = []
        red_3 = []        
        with h5py.File(path, 'r') as f:                
            k=0            
            for i in range(batch_size):
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
                print("reading b    lue channel") 
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

    def run_on_endoscopy_dataset(self):       
        eval_im = Evaluation()
        path = "image.h5" 
        reg = ChannelReg()       
        sseb = []
        ssea=[]
        sscb=[] 
        ssca =[]   
        sscrb=[]
        sscra=[]
        sscbb=[]
        sscba=[]
        sscgb=[]
        sscga=[] 
        ssclb=[]
        sscla=[]  
       
        offset = 0 
        ref,target = self.read_sample("video090.h5",crop = True)
        for j in range(5):
            similarity_edge_before = np.mean(eval_im.edge_structural_similarity(  ref, target))
            structural_similarity_color_before = np.mean(eval_im.get_structure_similarity(ref, target,channel = "g"))
            structural_similarity_color_before_r = np.mean(eval_im.get_structure_similarity(ref, target,channel = "r"))
            structural_similarity_color_before_g = np.mean(eval_im.get_structure_similarity(ref, target,channel = "g"))
            structural_similarity_color_before_b = np.mean(eval_im.get_structure_similarity(ref, target,channel = "b"))
            structural_similarity_color_before_l = np.mean(eval_im.get_structure_similarity(ref, target,channel = "l"))    


            color_index_before = np.mean(eval_im.compute_del_e(ref, target)) 
            image_batch = []
            for i in range(10):    
        
                #  cv2.imshow("image", ref[i])
                #  cv2.wa Key(0)
                #  cv2.destroyAllWindows()    
                 image_batch.append(ref[i])
            images = reg.register_channels(image_batch)
            similarity_index_after = np.mean(eval_im.edge_structural_similarity(images, target))
            color_index_after = np.mean(eval_im.compute_del_e(images, target))
            for unreg, reg_img in zip(image_batch, images):
            # Ensure images are the same size 
                if unreg.shape != reg_img.shape:
                    reg_img = cv2.resize(reg_img, (unreg.shape[1], unreg.shape[0]))
 
            # Horizontally stack for side-by-side comparison
                split_screen = cv2.hconcat([unreg, reg_img])

            # Show combined image
                cv2.imshow("Unregistered (Left)  |  Registered (Right)", split_screen)
                key = cv2.waitKey(0)
                cv2.destroyAllWindows() 
                if key == 27:  # ESC to break early
                    break
            structural_similarity_edge_after = np.mean(eval_im.edge_structural_similarity(images, target))
            structural_similarity_color_after = np.mean(eval_im.get_structure_similarity(images, target,channel = "g"))
            structural_similarity_color_after_r = np.mean(eval_im.get_structure_similarity(images, target,channel = "r"))
            structural_similarity_color_after_g = np.mean(eval_im.get_structure_similarity(images, target,channel = "g"))
            structural_similarity_color_after_b = np.mean(eval_im.get_structure_similarity(images, target,channel = "b"))
            structural_similarity_color_after_l = np.mean(eval_im.get_structure_similarity(images, target,channel = "l"))
            color_index_after = np.mean(eval_im.compute_del_e(images, target)) 
            
            print(f"Frame {i+1}: SSIM before registration = {similarity_edge_before:.4f}, SSIM after registration = {structural_similarity_edge_after:.4f}")
            print(f"Frame {i+1}: Color before registration = {color_index_before:.4f}, Color after registration = {color_index_after:.4f}")
            print(f"Frame {i+1}: SSIM blue before registration = {structural_similarity_color_before_b:.4f}, SSIM blue after registration = {structural_similarity_color_after_b:.4f}")
            print(f"Frame {i+1}: SSIM green before registration = {structural_similarity_color_before_g:.4f}, SSIM green after registration = {structural_similarity_color_after_g:.4f}")
            print(f"Frame {i+1}: SSIM red before registration = {structural_similarity_color_before_r:.4f}, SSIM red after registration = {structural_similarity_color_after_r:.4f}")
            print(f"Frame {i+1}: SSIM all before registration = {structural_similarity_color_before:.4f}, SSIM all after registration = {structural_similarity_color_after:.4f}")
            print(f"Frame {i+1}: SSIM l before registration = {structural_similarity_color_before_l:.4f}, SSIM l after registration = {structural_similarity_color_after_l:.4f}")
            print("--------------------------------")
            offset = offset + 10
            sseb.append(similarity_edge_before)
            ssea.append(structural_similarity_edge_after)
            sscb.append(structural_similarity_color_before)
            ssca.append(structural_similarity_color_after)
            sscrb.append(structural_similarity_color_before_r)
            sscra.append(structural_similarity_color_after_r)
            sscbb.append(structural_similarity_color_before_b) 
            sscba.append(structural_similarity_color_after_b)
            sscgb.append(structural_similarity_color_before_g)
            sscga.append(structural_similarity_color_after_g)
            ssclb.append(structural_similarity_color_before_l)
            sscla.append(structural_similarity_color_after_l)
            ref,target = self.read_sample("video090.h5",esc=offset,crop = True)
        print("ROI",self.roi)
        print("average delta e before registration",np.mean(color_index_before))
        print("average delta e after registration",np.mean(color_index_after))
        print("average of 50 ssim of edges before registration",np.mean(sseb))
        print("average of 50 ssim of edges after registration",np.mean(ssea))
        print("average of 50 ssim of color before registration",np.mean(sscb))
        print("average of 50 ssim of color after registration",np.mean(ssca))
        print("average of 50 ssim of red before registration",np.mean(sscrb))
        print("average of 50 ssim of red after registration",np.mean(sscra))
        print("average of 50 ssim of blue before registration",np.mean(sscbb))
        print("average of 50 ssim of blue after registration",np.mean(sscba))
        print("average of 50 ssim of green before registration",np.mean(sscgb)) 
        print("average of 50 ssim of green after registration",np.mean(sscga))
        print("average of 50 ssim of l before registration",np.mean(ssclb))
        print("average of 50 ssim of l after registration",np.mean(sscla))

    def run_on_camera_capture(self):

        reg = ChannelReg()
        batch_size = 6
        self.path = "image.h5"
        self.itters = 1
        image= []
        registered = []
        for i in range(self.itters):
            image = self.read_from_camera1(self.path,batch_size =batch_size,start  =21)
            registered = reg.register_channels(image)

        for unreg, reg_img in zip(image, registered):
            # Ensure images are the same size 
                if unreg.shape != reg_img.shape:
                    reg_img = cv2.resize(reg_img, (unreg.shape[1], unreg.shape[0]))
 
            # Horizontally stack for side-by-side comparison
                split_screen = cv2.hconcat([unreg, reg_img])

            # Show combined image
                cv2.imshow("Unregistered (Left)  |  Registered (Right)", split_screen)
                key = cv2.waitKey(0)
                cv2.destroyAllWindows() 
                if key == 27:  # ESC to break early
                    break
    
    def run_on_camera_capture_color(self):
        reg = ChannelReg()
        self.path = "image.h5"
        sim = RGBMisalignmentSimulator(path=self.path)

        ref, target = sim.generate(from_index=20)                   # list of tensors
        registered = reg.register_channels_gpu(ref)    # list of tensors
 


        for i, j in zip(ref, registered):
            # Convert tensors to numpy [H,W,3]
            i_np = i.detach().cpu().permute(1, 2, 0).numpy()
            j_np = j.detach().cpu().permute(1, 2, 0).numpy()
 
           
            #j_np = j if isinstance(j, np.ndarray) else j.detach().cpu().numpy()

            # Scale to uint8 [0,255]
            if i_np.dtype != np.uint8:
                i_np = np.clip(i_np, 0, 255).astype(np.uint8) 
            if j_np.dtype != np.uint8: 
                j_np = np.clip(j_np, 0, 255).astype(np.uint8)
           
           # print(j_np)
           
            # Ensure both images are same size
            if i_np.shape[:2] != j_np.shape[:2]:
                j_np = cv2.resize(j_np, (i_np.shape[1], i_np.shape[0]))
  
            # Side-by-side stacking
           
            split_screen = cv2.hconcat([i_np, j_np])

            # Display
            cv2.imshow("Unregistered (Left)  |  Registered (Right)", split_screen)
            key = cv2.waitKey(0)
            if key == 27:  # ESC to break early
                break

    


obj = raft_tetst()
obj.roi = (229, 33, 526, 478) 
obj.run_on_camera_capture_color()


    