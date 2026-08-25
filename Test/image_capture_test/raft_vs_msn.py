import torch
import numpy as np
import cv2
import torch.nn.functional as F
import argparse
import h5py
import os 
import pandas as pd
from processing_using_raft.evaluation import Evaluation
from processing_using_raft.raft import RAFT
from processing_using_raft.utils import InputPadder


class RAFTChannelRegistration:
    def __init__(self, model_path="raft-things"
    ".pth", small=False):
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.model = self._load_model(model_path, small)
        self.roi = (218,58,513,438)
        self.model_path = model_path

    def _load_model(self, model_path, use_small):
        args = argparse.Namespace(
            small=use_small,
            mixed_precision=True,
            alternate_corr=False
        )
        model = RAFT(args)
        model = torch.nn.DataParallel(model)

        checkpoint = torch.load(model_path, map_location=self.device)
        model.load_state_dict(checkpoint)

        return model.module.to(self.device).eval()

    @torch.no_grad()
    def compute_flow(self, img1, img2):
        """
        img1, img2: [B, 3, H, W]
        returns: flow [B, 2, H, W]
        """
        padder = InputPadder(img1.shape)
        img1, img2 = padder.pad(img1, img2)

        _, flow = self.model(img1, img2, iters=20, test_mode=True)
        flow = padder.unpad(flow)

        return flow

    def warp(self, image, flow):
        """
        image: [B, 1, H, W]
        flow:  [B, 2, H, W]
        """
        B, C, H, W = image.shape

        # create normalized grid
        grid_y, grid_x = torch.meshgrid(
            torch.linspace(-1, 1, H, device=image.device),
            torch.linspace(-1, 1, W, device=image.device),
            indexing="ij"
        )
        base_grid = torch.stack((grid_x, grid_y), dim=-1)
        base_grid = base_grid.unsqueeze(0).repeat(B, 1, 1, 1)

        # normalize flow
        flow_x = flow[:, 0] / ((W - 1) / 2)
        flow_y = flow[:, 1] / ((H - 1) / 2)
        flow_norm = torch.stack((flow_x, flow_y), dim=-1)

        sampling_grid = base_grid + flow_norm

        warped = F.grid_sample(
            image,
            sampling_grid,
            mode="bilinear",
            padding_mode="border",
            align_corners=True
        )

        return warped

    @torch.no_grad()
    def register(self, images):
        """
        images: [B, 3, H, W] (RGB, normalized 0-1)
        returns:
            registered_images [B, 3, H, W]
            flow_red
            flow_blue
        """

        images = images.to(self.device)

        # Extract channels
        red   = images[:, 0:1]
        green = images[:, 1:2]
        blue  = images[:, 2:3]

        # Repeat to 3 channels for RAFT
        green_3 = green.repeat(1, 3, 1, 1)
        red_3   = red.repeat(1, 3, 1, 1)
        blue_3  = blue.repeat(1, 3, 1, 1)

        # Compute flows
        flow_red  = self.compute_flow(green_3, red_3)
        flow_blue = self.compute_flow(green_3, blue_3)

        # Warp single-channel images
        warped_red  = self.warp(red, flow_red)
        warped_blue = self.warp(blue, flow_blue)

        # Reconstruct RGB
        registered = torch.cat(
            [warped_red, green, warped_blue],
            dim=1
        )

        return registered, flow_red, flow_blue
    
    def read_sample(self,file_path,dataset_name = "reference",number_of_frames = 10, esc= 0,crop =False): 

          image1 = []     
          image2 = []          
          offset = 10+esc 
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
                    print(self.roi)
                for ref,targ in zip(image1,image2):
                    ref = ref[self.roi[1]:self.roi[1]+self.roi[3],self.roi[0]:self.roi[0]+self.roi[2]]
                    targ = targ[self.roi[1]:self.roi[1]+self.roi[3],self.roi[0]:self.roi[0]+self.roi[2]]
                    image1_crop.append(ref)
                    image2_crop.append(targ)
                return image1_crop,image2_crop 
          else:
                return image1,image2
    def list_to_tensor(self, image_list):
        tensor = torch.from_numpy(np.stack(image_list))  # [B,H,W,3]
        tensor = tensor.permute(0, 3, 1, 2).float() / 255.0
        return tensor
    def tensor_to_list(self, tensor):
        """
        tensor: [B, 3, H, W] float (0–1)

        returns:
            list of numpy arrays [H, W, 3] uint8
        """
        if tensor.is_cuda:
            tensor = tensor.detach().cpu()

        tensor = tensor.clamp(0, 1)

        # [B, 3, H, W] → [B, H, W, 3]
        tensor = tensor.permute(0, 2, 3, 1)

        numpy_images = (tensor.numpy() * 255.0).astype(np.uint8)

        return [img for img in numpy_images]

    def run_on_endoscopy_dataset(self):

        eval_im = Evaluation()


        path = "video090.h5"
        offset = 0

        # Store metrics cleanly
        metrics = {
            "ssim_before":[],
            "ssim_after":[],
            "deltaE_before": [],
            "deltaE_after": []
        }

        ref, target = self.read_sample(path, crop=True)
        results_rows = []

        for j in range(10):

            # ===================== BEFORE REGISTRATION =====================

           
            ssim_before = np.mean(eval_im.get_structure_similarity(ref, target, channel="all"))
            deltaE_before = np.mean(eval_im.compute_del_e(ref, target))

            # ===================== REGISTRATION =====================

            
            image_batch_ref = self.list_to_tensor(ref)
            images_reg,_,_ = self.register(image_batch_ref)

            # ===================== AFTER REGISTRATION =====================
            
            reg = self.tensor_to_list(images_reg)
            ssim_after = np.mean(eval_im.get_structure_similarity(reg, target, channel="all"))
            deltaE_after = np.mean(eval_im.compute_del_e(reg, target))

            # ===================== VISUALIZATION =====================

            # for unreg, reg_img in zip(image_batch, reg):
            #     if unreg.shape != reg_img.shape:
            #         reg_img = cv2.resize(reg_img, (unreg.shape[1], unreg.shape[0]))

            #     split_screen = cv2.hconcat([unreg, reg_img])
            #     cv2.imshow("Unregistered | Registered", split_screen)

            #     key = cv2.waitKey(0)
            #     cv2.destroyAllWindows()
            #     if key == 27:
            #         break

            # ===================== STORE METRICS =====================


            metrics["ssim_before"].append(ssim_before)
            metrics["ssim_after"].append(ssim_after)
        
            metrics["deltaE_before"].append(deltaE_before)
            metrics["deltaE_after"].append(deltaE_after)

            # ===================== PRINT ITERATION RESULT =====================

            print(f"\nIteration {j+1}")
            
            print(f"DeltaE: {deltaE_before:.4f} → {deltaE_after:.4f}")
            print(f"SSIM: {ssim_before:.4f} → {ssim_after:.4f}")
           
            print("-" * 50)

            offset += 10
            ref, target = self.read_sample(path, esc=offset, crop=True)

        
            results_rows.append({
            "Model": self.model_path,
            "Iteration": j+1,
            "SSIM_Before": ssim_before,
            "SSIM_After": ssim_after,
            "DeltaE_Before": deltaE_before,
            "DeltaE_After": deltaE_after
        })

        df_new = pd.DataFrame(results_rows)

        # Excel file path
        excel_path = "endoscopy_results_raft.xlsx"

        # If file exists → append
        if os.path.exists(excel_path):
            df_existing = pd.read_excel(excel_path)
            df_final = pd.concat([df_existing, df_new], ignore_index=True)
        else:
            df_final = df_new

        # Save back to Excel
        df_final.to_excel(excel_path, index=False)

        print(f"Results saved to {excel_path}")

    

       
obj = RAFTChannelRegistration()
obj.run_on_endoscopy_dataset()