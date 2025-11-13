import cv2
import h5py
import numpy as np
from matplotlib import pyplot as plt 
import torch
from torchvision import transforms as transform
import pandas as pd
from processing_using_raft.evaluation_new import Evaluation
from skimage.metrics import structural_similarity as ssim
from experiments.Experiment_for_photonic_west.sample import RGBMisalignmentSimulator
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
        #path = "image.h5" 
        batch = 4
        reg = ChannelReg() 
        sim = RGBMisalignmentSimulator(batch_size=6)
        #sim.video_to_h5("HyperK.avi","Hyper_k.h5")
              
        # sseb = []
        # ssea=[]
        # sscb=[] 
        # ssca =[]   
        # sscrb=[]
        # sscra=[] 
        # sscbb=[]
        # sscba=[]
        # sscgb=[] 
        # sscga=[] 
        # ssclb=[]
        # sscla=[]  
        ssim_before = []
        ssim_after = []
        delta_e_before = []
        delta_e_after = []
       
        roi = (177, 37, 444, 475)        # Hyper Kvasir
        #roi = (5, 440, 1071, 850) sterio mis

        
        
#         offset = 0 
#         from_ind = 200 # deforamtion 700
        

#         ref,target = sim.generate("Hyper_k.h5",from_index=from_ind,jump=4,crop =roi,batch= batch)  
#         img = ref[0].permute(1, 2, 0).cpu().numpy()
#         img = (img).astype(np.uint8)

# # OpenCV ROI selector
#         roi = cv2.selectROI("Select ROI", img, showCrosshair=True, fromCenter=False)
#         print("Selected ROI:", roi)
#         cv2.destroyAllWindows()

#         files = ["Scanning.h5","Surgery.h5","Breathing.h5","Deformation.h5"]

        files = ["Hyper_k.h5"]
        ssim_b0 = []
        ssim_a0 = []
        deltaE_b0 = []
        deltaE_a0 = []
        all_results = []  # to store all file results
        for file in files:
            print("Processing file:",file)
            ssim_b = []
            ssim_a = []
            deltaE_b = []   
            deltaE_a = []   
            for ju in range (10):
                print("Jump value is :",ju)
                
                from_ind = 200
                for i in range (100):
                    ref,target = sim.generate(file,from_index=from_ind,jump = ju+1,crop =roi,batch= batch)  
                    from_ind = from_ind+ batch              # list of tensors
                    print(file, from_ind)
                    similarity_edge_before = np.mean(eval_im.edge_structural_similarity(  ref, target))
                
                    structural_similarity_color_before_r = np.mean(eval_im.get_structure_similarity(ref, target,channel = "r"))
                    structural_similarity_color_before_g = np.mean(eval_im.get_structure_similarity(ref, target,channel = "g"))
                    structural_similarity_color_before_b = np.mean(eval_im.get_structure_similarity(ref, target,channel = "b"))
                    structural_similarity_color_before_l = np.mean(eval_im.get_structure_similarity(ref, target,channel = "all")) 
                    color_index_before = np.mean(eval_im.compute_del_e(ref, target))   

                    ssim_before.append(structural_similarity_color_before_l)
                    delta_e_before.append(color_index_before)


                    flow_b,flow_R,regestered = reg.register_channels_gpu(ref)
                    im = regestered[0]  
                    
                    refer= ref[0]

                    re_np = refer.detach().cpu().permute(1, 2, 0).numpy() 
                    reg_np = im.detach().cpu().permute(1,2,0).numpy()

                    # Convert to uint8 if needed
                    if re_np.max() <= 1.0:
                        re_np = (re_np * 255).astype('uint8')
                        reg_np = (reg_np * 255).astype('uint8')
                    else:
                        re_np = re_np.astype('uint8')
                        reg_np = reg_np.astype('uint8')
                    re_np = re_np[..., ::-1]
                    reg_np = reg_np[..., ::-1]

                    cv2.imshow("before",re_np)
                    cv2.imshow("after",reg_np)
                    cv2.waitKey(0)
                    cv2.destroyAllWindows()

                    structural_similarity_edge_after = np.mean(eval_im.edge_structural_similarity(regestered, target))
                    
                    structural_similarity_color_after_r = np.mean(eval_im.get_structure_similarity(regestered, target,channel = "r"))
                    structural_similarity_color_after_g = np.mean(eval_im.get_structure_similarity(regestered, target,channel = "g"))
                    structural_similarity_color_after_b = np.mean(eval_im.get_structure_similarity(regestered, target,channel = "b"))
                    structural_similarity_color_after_l = np.mean(eval_im.get_structure_similarity(regestered, target,channel = "all"))
                    color_index_after = np.mean(eval_im.compute_del_e(regestered, target)) 

                    ssim_after.append(structural_similarity_color_after_l)
                    delta_e_after.append(color_index_after)

                average_ssim_before = np.mean(ssim_before).item()
                average_ssim_after = np.mean(ssim_after).item()
                average_deltaE_before = np.mean(delta_e_before).item()
                average_deltaE_after = np.mean(delta_e_after).item()

                all_results.append({
                    "File": file,
                    "Jump": ju,
                    "SSIM_Before": average_ssim_before,
                    "SSIM_After": average_ssim_after,
                    "DeltaE_Before": average_deltaE_before,
                    "DeltaE_After": average_deltaE_after,
                    
                })
        df_all = pd.DataFrame(all_results)

    # Save to Excel
        output_excel = "Endoscopy_Registration_Results.xlsx"
        df_all.to_excel(output_excel, index=False)

        print(f"\n✅ Results saved to {output_excel}")
        print(df_all.head())

        return df_all






    # Combine all into one DataFrame
       



            


        # ssim_b0.append(ssim_b1)
        # ssim_a0.append(ssim_a1)
        # deltaE_b0.append(deltaE_b1)
        # deltaE_a0.append(deltaE_a1)

        



    # def run_on_endoscopy_dataset(self):       
    #     eval_im = Evaluation()
    #     reg = ChannelReg() 
    #     sim = RGBMisalignmentSimulator(batch_size=6)

    #     files = ["Surgery.h5", "Breathing.h5", "Deformation.h5", "Scanning.h5"]

    #     roi = (5, 440, 1071, 850)
    #     from_ind = 100
    #     batch = 4

    #     all_results = []  # to store all file results

    #     for file in files:
    #         print(f"\nProcessing file: {file}")

    #         for ju in range(10):
    #             print(f"  Jump value: {ju}")

    #             ssim_before = []
    #             ssim_after = []
    #             delta_e_before = []
    #             delta_e_after = []

    #             for i in range(100):  # repeat for robustness
    #                 ref, target = sim.generate(file, from_index=from_ind, jump=ju, crop=roi, batch=batch)
    #                 from_ind += batch

    #                 # --- Before registration ---
    #                 ssim_l_before = np.mean(eval_im.get_structure_similarity(ref, target, channel="all"))
    #                 deltaE_before = np.mean(eval_im.compute_del_e(ref, target))

    #                 # --- Register channels ---
    #                 _, _, registered = reg.register_channels_gpu(ref)

    #                 # --- After registration ---
    #                 ssim_l_after = np.mean(eval_im.get_structure_similarity(registered, target, channel="all"))
    #                 deltaE_after = np.mean(eval_im.compute_del_e(registered, target))

    #                 # Collect
    #                 ssim_before.append(ssim_l_before)
    #                 ssim_after.append(ssim_l_after)
    #                 delta_e_before.append(deltaE_before)
    #                 delta_e_after.append(deltaE_after)

    #             # Compute averages for this jump value
    #             avg_ssim_b = np.mean(ssim_before)
    #             avg_ssim_a = np.mean(ssim_after)
    #             avg_dE_b = np.mean(delta_e_before)
    #             avg_dE_a = np.mean(delta_e_after)

    #             # Add record
    #             all_results.append({
    #                 "File": file,
    #                 "Jump": ju,
    #                 "SSIM_Before": avg_ssim_b,
    #                 "SSIM_After": avg_ssim_a,
    #                 "DeltaE_Before": avg_dE_b,
    #                 "DeltaE_After": avg_dE_a,
    #                 "SSIM_Improvement": avg_ssim_a - avg_ssim_b,
    #                 "DeltaE_Improvement": avg_dE_b - avg_dE_a
    #             })

    #     # Combine all results into one DataFrame
    #     df_all = pd.DataFrame(all_results)

    #     # Save to Excel
    #     output_excel = "Endoscopy_Registration_Results.xlsx"
    #     df_all.to_excel(output_excel, index=False)

    #     print(f"\n✅ Results saved to {output_excel}")
    #     print(df_all.head())

    #     return df_all



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
        
            sim = RGBMisalignmentSimulator(batch_size = batch_size)
            

            ref, target = sim.generate(path,from_index,jump,batch_size)                   # list of tensors
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
            for i in range(3):
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
        

        


obj = raft_tetst()
obj.roi = (229, 33, 526, 478) 
obj.run_on_endoscopy_dataset()
 