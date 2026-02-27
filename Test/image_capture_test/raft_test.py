import cv2
import h5py
import numpy as np
from matplotlib import pyplot as plt 
import torch
import pandas as pd
import torch.nn.functional as F
from processing_using_raft.evaluation import Evaluation
from skimage.metrics import structural_similarity as ssim
from experiments.local_deformation_correction.sample import RGBMisalignmentSimulator
from processing_using_raft.visualize import FlowVisualizer
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
    
    def run_on_camera_capture_color(self,batch_size:int =12,from_index:int = 0,path = "src/defocus_Exp/0.h5"):
        reg = ChannelReg()
        self.path = path
        jump = 1
       
        sim = RGBMisalignmentSimulator(path=self.path,batch_size = batch_size)

        ref, target = sim.generate(from_index,jump,batch_size)                   # list of tensors
        flow_blue,flow_red,registered = reg.register_channels_gpu(ref)    # list of tensors
        return ref,target,registered,flow_blue,flow_red
 


    def graph(self,ssim_list,color_list):
        # Create figure
        plt.figure(figsize=(8, 5))

        # Plot both
        plt.plot(ssim_list, label="SSIM", marker='o')
        plt.plot(color_list, label="ΔE (Color Difference)", marker='s')

        # Labels and legend
        plt.xlabel("Frame Index")
        plt.ylabel("Metric Value")
        plt.title("SSIM and Color Difference Across Frames")
        plt.legend()
        plt.grid(True)

        plt.show()
    def pendullum_motion(self,path):
        flow_visual = FlowVisualizer()
        eval_im = Evaluation()
        sample_frames = 20
        batch_size = 12
        from_index = 0
        ref = []
        targ = []
        
        reg = []
        ssim_final = []
        color_final = []
        ref_final = []
        reg_final = []
        target_final = []
        flow_final = []
        roi = False
        for i in range(sample_frames):
            ref = []
            targ=[]
            reg = []
            images = self.run_on_camera_capture_color(batch_size,from_index,path)
             
            self.error_over_target(images[2])

            ref.extend([i.detach().cpu().permute(1, 2, 0).numpy() for i in images[0]])
            targ.extend([i.detach().cpu().permute(1, 2, 0).numpy() for i in images[1]])
            reg.extend([i.detach().cpu().permute(1, 2, 0).numpy() for i in images[2]])

            


            flow_blue = images[3]
            flow_red = images[4]
           
            flow_blue = flow_blue.detach().cpu().numpy()
            flow_equ_im_red = flow_visual.flows_to_numpy_images(flow_red)

            # if not roi:
            #     roi_val = cv2.selectROI("Select ROI", ref[3].astype(np.uint8))
            #     roi = True
            # x,y,w,h = roi_val


            # ref_c = [img[y:y+h, x:x+w] for img in ref]
            # targ_c = [img[y:y+h, x:x+w] for img in targ]
            # reg_c = [img[y:y+h, x:x+w] for img in reg]  # fixed

            # ref = ref_c
            # targ = targ_c
            # reg = reg_c

            from_index = i*batch_size
            ssim_final.extend(eval_im.get_structure_similarity(reg,targ))
            color_final.extend(eval_im.compute_del_e_new(np.array(ref),np.array(targ)))
            target_final.extend([i for i in targ])
            flow_final.extend([i for i in flow_equ_im_red])

            ref_final.extend([i for i in ref])
            reg_final.extend([i for i in reg])
        self.save_comparison_video(reg_final,ref_final,ssim_final,color_final)
        print("This is completed",i)

        return ssim_final,color_final
        
        #self.graph(ssim_final,color_final)
        
    


        # for i,j in zip(ref_final, reg):        

            
        #         # Convert tensors to numpy [H,W,3]
        #         i_np = i            
        #         j_np = j
        #         # Scale to uint8 [0,255]
        #         if i_np.dtype != np.uint8:
        #             i_np = np.clip(i_np, 0, 255).astype(np.uint8) 
        #         if j_np.dtype != np.uint8: 
        #             j_np = np.clip(j_np, 0, 255).astype(np.uint8)
            
        #     # print(j_np)
            
        #         # Ensure both images are same size
        #         if i_np.shape[:2] != j_np.shape[:2]:
        #             j_np = cv2.resize(j_np, (i_np.shape[1], i_np.shape[0]))
    
        #         # Side-by-side stacking
            
        #         split_screen = cv2.hconcat([i_np, j_np])

        #         # Display
        #         cv2.imshow("Unregistered (Left)  |  Registered (Right)", split_screen)
        #         key = cv2.waitKey(0)
        #         if key == 27:  # ESC to break early
        #             break

        
    def save_comparison_video(self,ref_images, reg_images, ssim_list, deltaE_list, out_path="comparison.mp4", fps=10):
        assert len(ref_images) == len(reg_images) == len(ssim_list) == len(deltaE_list), "List lengths must match"

        # Ensure all images are uint8
        ref_images = [cv2.convertScaleAbs(img) for img in ref_images]
        reg_images = [cv2.convertScaleAbs(img) for img in reg_images]

        # Resize all images to the same size (use the reference image size)
        h, w, _ = ref_images[0].shape
        reg_images = [cv2.resize(img, (w, h)) for img in reg_images]

        # Frame size for side-by-side (width doubled)
        out_size = (w * 2, h)

        # Video writer
        fourcc = cv2.VideoWriter_fourcc(*"mp4v")
        writer = cv2.VideoWriter(out_path, fourcc, fps, out_size)

        for idx, (ref, reg, ssim_val, dE) in enumerate(zip(ref_images, reg_images, ssim_list, deltaE_list)):
            # Horizontally stack the images for split-screen
            split_screen = np.hstack((ref, reg))

            # Overlay text on the top-left corner
            text = f"Frame {idx} | SSIM: {ssim_val:.4f} | delta_E: {dE:.2f}"
            cv2.putText(split_screen, text, (10, 30),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2, cv2.LINE_AA)

            # Write the combined frame
            writer.write(split_screen)

        writer.release()
        print(f"Video saved to {out_path}")

    def d_focus_experiment(self):
        obj = raft_tetst()
        path = "src/defocus_Exp/"
        structural_sim = []
        color_diff = []
        for i in range(9):
            path_eff = path + str(i)+".h5"
            print("")
            print("")
            print(path_eff)
            print("")
            print("")
            s_sim,deltaE = obj.pendullum_motion(path_eff)
            structural_sim.append(s_sim)
            color_diff.append(deltaE)
        df_ssim = pd.DataFrame(structural_sim).T
        df_deltaE = pd.DataFrame(color_diff).T

        # Rename columns
        df_ssim.columns = [f"ssim_{i}" for i in range(len(structural_sim))]
        df_deltaE.columns = [f"deltaE_{i}" for i in range(len(color_diff))]

        # Combine both into a single DataFrame (side by side)
        df_final = pd.concat([df_ssim, df_deltaE], axis=1)

        # Export to Excel
        df_final.to_excel("defocus_experiment_results.xlsx", index=False)

        return df_final
    def time_period_Exp(self):
        obj = raft_tetst()
        path = "src/time_period_exp/"
        structural_sim = []
        color_diff = []
        for i in range(1):
            path_eff = path + str(i)+".h5"
            print("")
            print("")
            print(path_eff)
            print("")
            print("")
            s_sim,deltaE = obj.pendullum_motion(path_eff)
            structural_sim.append(s_sim)
            color_diff.append(deltaE)
        df_ssim = pd.DataFrame(structural_sim).T
        df_deltaE = pd.DataFrame(color_diff).T

        # Rename columns
        df_ssim.columns = [f"ssim_{i}" for i in range(len(structural_sim))]
        df_deltaE.columns = [f"deltaE_{i}" for i in range(len(color_diff))]

        # Combine both into a single DataFrame (side by side)
        df_final = pd.concat([df_ssim, df_deltaE], axis=1)

        # Export to Excel
        df_final.to_excel("time_period_experiment_results.xlsx", index=False)

        return df_final
    def __sample(self,path, sample_from=300,batch_size=10,jump = 1,resize = True):
        """
        Sample batch of frames from HDF5 and return tensor.

        Args:
            sample_from (int): Starting index inside the HDF5 file.

        Returns:
            frames: Tensor [M, H, W, C] on self.device,
                    where M <= batch_size depending on available frames.
        """
        images = []
        
        with h5py.File(path, "r") as f:
            total_frames = len(f.keys())  # total number of images stored
            for i in range(batch_size):
                idx = i + sample_from
                if idx >= total_frames:   # stop if we exceed dataset length
                    break
                frame = f[str(idx)][:]    # numpy array (H, W, C)
                images.append(frame)

        if not images:  # no frames available
            print("No frames availebal")
            return None
        images_np = np.stack(images, axis=0)
        
        frames = torch.tensor(images_np, dtype=torch.float32, device="cuda")
        

        return frames
    def error_over_target(self,corrected:torch.tensor):
        """Get the refrece image of batch size m this will be standstill image of pendulum
           corrected images are the images after channel missallignment correction

        """
        
        b,c,h,w=corrected.shape
        resize = True
        target_path = "image.h5"
        target = self.__sample(target_path,sample_from=400,batch_size=b,jump = 1)
        self.resize = ()

       
        print("this is target shape = = =  =",target.shape)
        if resize == True:
            temp =[]
            for i in target:
               H_new, W_new = (384,512)
            # permute to [C,H,W] for interpolate
               
               i = i.permute(2, 0, 1).unsqueeze(0).float()
               i = F.interpolate(i, size=(H_new, W_new), mode='bilinear', align_corners=True)[0].permute(1, 2, 0)
               temp.append(i)
            target = torch.stack(temp, dim=0).permute(0, 3, 1, 2)
        print("this is target shape = = =  =",target.shape)
        reg = ChannelReg()
        flow = reg.compute_flow(target,corrected)
        warped = reg.warp_batch(corrected,flow)   
        self.__disp(target,warped,corrected)


    def __disp(self, target, warped, real):
        for i, j, k in zip(target, warped, real):
            # Move tensors to CPU and convert to numpy
            i = i.detach().cpu().numpy()
            j = j.detach().cpu().numpy()
            k = k.detach().cpu().numpy()

            # If tensors are (C, H, W), convert to (H, W, C)
            if i.ndim == 3 and i.shape[0] in [1, 3]:
                i = np.transpose(i, (1, 2, 0))
                j = np.transpose(j, (1, 2, 0))
                k = np.transpose(k, (1, 2, 0))

            # Convert to uint8 (assumes already scaled 0–255)
            if i.dtype != np.uint8:
                i = np.clip(i, 0, 255).astype(np.uint8)
            if j.dtype != np.uint8:
                j = np.clip(j, 0, 255).astype(np.uint8)
            if k.dtype != np.uint8:
                k = np.clip(k, 0, 255).astype(np.uint8)

            # Combine side-by-side: Target | Warped | Real
            combined = np.hstack((i, j, k))
            cv2.imshow("Target | Warped | Real", combined)

            key = cv2.waitKey(0)
            if key == 27:  # ESC to exit
                break

        cv2.destroyAllWindows()





obj = raft_tetst()
obj.roi = (229, 33, 526, 478) 
obj.pendullum_motion(path="src/time_period_exp/1.h5")

                  