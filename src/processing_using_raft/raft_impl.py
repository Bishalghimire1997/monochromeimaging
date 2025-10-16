import numpy as np
import argparse
import torch
import torch.nn.functional as F
import cv2
from processing_using_raft.utils import InputPadder, forward_interpolate
from processing_using_raft.raft import RAFT
class ChannelReg():
    def __init__(self):
        self.__model_path ="z.pth"
        self.__use_small = False
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.model = self.__load_model(self.__model_path, self.__use_small)
    def register_channels_gpu(self,image:torch.tensor):
       
        val = self.__split_rgb_channels(image.clone())

       


        blue = val["blue"]
        green = val["green"]
        red = val["red"]
       
        flow_blue = self.compute_flow(green,blue)
        flow_red = self.compute_flow(green,red)
        warped_blue = self.warp_batch(blue,flow_blue)
        warped_red = self.warp_batch(red,flow_red)  

        warped_blue = warped_blue[:,1,:,:]
        warped_red = warped_red[:,1,:,:]
        green = green[:,1,:,:]

        warped_red = warped_red.unsqueeze(1)   # [B,1,H,W]
        green     = green.unsqueeze(1)         # [B,1,H,W]
        warped_blue= warped_blue.unsqueeze(1)  # [B,1,H,W]


        #print("***************************Warped blue max",torch.max(warped_blue))
     
        #print("***************************Warped blue max",torch.max(warped_blue))

       
        registered = torch.cat([warped_red, green, warped_blue], dim=1)  # [B,3,H,W]

        #registered = registered.permute(0, 3, 1, 2)  # [B,H,W,3]

        
        return flow_blue,flow_red,registered

    
    def __split_rgb_channels(self,image: torch.Tensor):
        """
        Given a tensor [B, H, W, 3], create separate 3-channel images for each channel
        with other channels set to zero.
        Returns a dict { 'red': red_img, 'green': green_img, 'blue': blue_img }
        where each has shape [B, H, W, 3].
        """
        B, C, H, W = image.shape
        assert C == 3, "Input must have 3 channels"

        # Zero tensor
        zeros = torch.zeros_like(image)

        # Red [R,0,0]
        red_img = zeros.clone()
        red_img[:,1,:,:] = image[:, 0, :, :]

        # Green [0,G,0]
        green_img = zeros.clone()
        green_img[:,1,:,:] = image[:, 1, :, :]

        # Blue [0,0,B]
        blue_img = zeros.clone()
        blue_img[:,1,:,:] = image[:, 2, :, :]

        return {
            "red": red_img,
            "green": green_img,
            "blue": blue_img
        }
    
    def display_bchw_images(self,batch_tensor, window_name="Images", wait_time=0):
        """
        Display a batch of images stored as BCHW tensor using OpenCV.
        - batch_tensor: [B, C, H, W] (C=3)
        - Automatically converts to HWC, scales to 0-255 uint8
        - Displays each image one by one
        """
        if not isinstance(batch_tensor, torch.Tensor):
            raise TypeError("Input must be a torch.Tensor")

        B, C, H, W = batch_tensor.shape
        if C != 3:
            raise ValueError("Only 3-channel RGB images are supported")

        for i in range(B):
            img = batch_tensor[i].detach().cpu()

            # Convert to HWC
            img = img.permute(1, 2, 0).numpy()

            # Scale to uint8 if needed
            min_val = img.min()
            max_val = img.max()
            if max_val > 1.0:
                # Assume already in 0-255
                img_disp = np.clip(img, 0, 255).astype(np.uint8)
            else:
                # Scale from [0,1] to [0,255]
                img_disp = np.clip(img * 255.0, 0, 255).astype(np.uint8)

            # Convert RGB to BGR for OpenCV
            img_disp = cv2.cvtColor(img_disp, cv2.COLOR_RGB2BGR)

            cv2.imshow(f"{window_name} - Image {i}", img_disp)
            key = cv2.waitKey(wait_time)
            if key == 27:  # ESC to exit early
                break

    cv2.destroyAllWindows()
    def register_channels(self,image_batch):
        fix_g,float_b,float_r,green,blue,red = self.__get_ref_floating_batch(image_batch)
        flow_b = self.compute_flow(fix_g,float_b)
        flow_r = self.compute_flow(fix_g,float_r)
        registered_b = self.reg(blue,flow_b)
        registered_r = self.reg(red,flow_r)
        registered_image = [cv2.merge([b,g,r]) for b,g,r in zip(registered_b,green,registered_r)]
        return registered_image
     
        
    def reg(self,floating_image_list,flow_list):
        registered_images = []
        for image,flow in zip(floating_image_list,flow_list):
            registered_image = self.fine_reg_using_stn(image,flow)
            registered_images.append(registered_image)
        return registered_images

    @torch.no_grad()
    def __load_model(self, model_path, use_small):
        args = argparse.Namespace(small=use_small, mixed_precision=True, alternate_corr=False)
        model = RAFT(args)
        model = torch.nn.DataParallel(model)
        checkpoint = torch.load(model_path, map_location=self.device)
        model.load_state_dict(checkpoint)
        return model.module.to(self.device).eval()
    

    def __get_ref_floating_batch(self,image_batch):
        """Get the reference and floating images from the batch"""
        blue_batch = []
        green_batch = []
        red_batch = []
        green_to_return = []
        blue_to_return = []
        red_to_return = []
        blue,_,_ = cv2.split(image_batch[0])
        h, w = blue.shape
        zeros = np.zeros((h, w),dtype=np.uint8)
        
        for i in image_batch:
            # cv2.imshow("input",i)
            # cv2.waitKey(0)
            # cv2.destroyAllWindows()
            b,g,r =cv2.split(i)
            blue_batch.append(cv2.merge([zeros,b,zeros]))
            green_batch.append(cv2.merge([zeros,g,zeros]))
            red_batch.append(cv2.merge([zeros,r,zeros]))
            green_to_return.append(g)
            blue_to_return.append(b)
            red_to_return.append(r)
        fixed = [self.__to_tensor(img,batched = False) for img in green_batch]
        floating_blue = [self.__to_tensor(img,batched = False) for img in blue_batch]
        floating_red = [self.__to_tensor(img,batched = False) for img in red_batch]
        return fixed,floating_blue,floating_red,green_to_return,blue_to_return,red_to_return

    def __to_tensor(self, img,batched = False ):
        img = img.astype(np.float32)
        if not(batched):
            img = torch.from_numpy(img).permute(2, 0, 1).float()[None] / 255.0
        else:
            img  = torch.from_numpy(img).permute(0, 3, 1, 2).float() / 255.0
        return img.to(self.device) 
    
    @torch.no_grad()
    def fine_reg_using_stn(self,floating_image, flow):
            if floating_image.ndim == 2:
                floating_image = np.expand_dims(floating_image, axis=-1)
            image = torch.from_numpy(floating_image).permute(2, 0, 1).unsqueeze(0).float() / 255.0  # (B=1, C, H, W)
            flow = torch.from_numpy(flow).permute(2, 0, 1).unsqueeze(0).float()  # (B=1, 2, H, W)
            B,C,H,W = image.size()
            grid_y, grid_x = torch.meshgrid(torch.linspace(-1, 1, H, device=image.device),
                                    torch.linspace(-1, 1, W, device=image.device))
            grid = torch.stack((grid_x, grid_y), dim=2)  # (H, W, 2)
            grid = grid.unsqueeze(0).repeat(B, 1, 1, 1)  # (B, H, W, 2)

    # Normalize flow from pixel space to [-1, 1]
    # flow_x is flow[:, 0, :, :]
            flow_x = flow[:, 0, :, :] / ((W - 1) / 2)
            flow_y = flow[:, 1, :, :] / ((H - 1) / 2)
            flow_norm = torch.stack((flow_x, flow_y), dim=3)  # (B, H, W, 2)

    # Add flow to base grid
            sampling_grid = grid + flow_norm  # displaced sampling grid

        # Sample the floating image at the new grid locations
            warped_image = F.grid_sample(image, sampling_grid, mode='bilinear', padding_mode='border', align_corners=True)
            warped_np = (warped_image[0].permute(1, 2, 0).cpu().numpy() * 255).astype(np.uint8)
            if warped_np.ndim == 3 and warped_np.shape[2] == 1:
               warped_np = warped_np.squeeze(-1)
            # print(warped_np)
            # cv2.imshow("warped",warped_np)
            # cv2.waitKey(0)
            # cv2.destroyAllWindows()
            return warped_np


    def warp_batch(self,images:torch.tensor, flows:torch.tensor,pad_mode = "border"):
        print("This is flow type ################################# ",type(flows[0]))
       

        B, C, H, W = images.size()
        # Create normalized mesh grid
        grid_y, grid_x = torch.meshgrid(
            torch.linspace(-1, 1, H, device=images.device),
            torch.linspace(-1, 1, W, device=images.device),
            indexing='ij'
        )
        base_grid = torch.stack((grid_x, grid_y), dim=-1)  # [H, W, 2]
        base_grid = base_grid.unsqueeze(0).expand(B, -1, -1, -1)  # [B, H, W, 2]

        # Normalize flow to [-1, 1]
        flow_x = flows[:, 0, :, :] / ((W - 1) / 2)
        flow_y = flows[:, 1, :, :] / ((H - 1) / 2)
        flow_norm = torch.stack((flow_x, flow_y), dim=-1)  # [B, H, W, 2]

        # Final warp grid
        warp_grid = base_grid + flow_norm  # [B, H, W, 2]
         # Warp

        warped = F.grid_sample(images, warp_grid, mode='bilinear', padding_mode=pad_mode, align_corners=True)
        print("################################################################ This is the shape immidaitely after warping #################################  =  ",warped.shape)
       
        return warped
    


    @torch.no_grad()
       
    def compute_flow(self, fix_batch, floating_batch):
        """
        Compute optical flow for a batch of image pairs.

        Args:
            fix_batch (List[np.ndarray] or np.ndarray): List or array of N images [H, W, 3].
            floating_batch (List[np.ndarray] or np.ndarray): List or array of N images [H, W, 3].

        Returns:
            List[np.ndarray]: List of flow outputs [H, W, 2] for each pair.
        """
        assert len(fix_batch) == len(floating_batch), "Mismatch in batch sizes"
        batch_size = len(fix_batch)

        # # Convert each image to tensor and stack into batch
        # img1_list = [self.__to_tensor(img,batched = False) for img in fix_batch]
        # img2_list = [self.__to_tensor(img,batched = False) for img in floating_batch]

        img1_batch = fix_batch # [B, 3, H, W]
        img2_batch = floating_batch  # [B, 3, H, W]
        print("Refrence shape in compute flow  :",img1_batch.shape,"Target Shape in compute flow ", img2_batch.shape)

        padder = InputPadder(img1_batch.shape)
        img1_batch, img2_batch = padder.pad(img1_batch, img2_batch)
       

        # Inference
        _, flow_preds = self.model(img1_batch, img2_batch, iters=100  , test_mode=True)

        # Unpad and convert to list of numpy arrays
        # flows = [] 
        # for b in range(batch_size):
        #     flow = padder.unpad(flow_preds[b]).permute(1, 2, 0).detach().cpu().numpy()
        #     flows.append(flow)
        return flow_preds


