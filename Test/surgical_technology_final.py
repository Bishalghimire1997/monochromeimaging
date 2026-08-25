import os
import cv2
import torch
import numpy as np
from processing_using_raft.raft import RAFT
from processing_using_raft.visualize import FlowVisualizer
import argparse
from processing_using_raft.utils import InputPadder

class ImagePairReader:
    def __init__(self, folder_path):
        self.folder_path = folder_path
        self.resize = True

        # Supported extensions
        valid_exts = ('.tif', '.tiff', '.png', '.jpg', '.jpeg')

        # Sorted list of image files
        self.files = sorted([
            f for f in os.listdir(folder_path)
            if f.lower().endswith(valid_exts)
        ])

        if len(self.files) < 2:
            raise ValueError("Need at least 2 images to form pairs.")

        self.num_pairs = len(self.files) - 1

    def read_pair(self, i):
        if i < 0 or i >= self.num_pairs:
            raise IndexError(f"Index {i} out of range (0 to {self.num_pairs - 1})")

        img1_path = os.path.join(self.folder_path, self.files[i])
        img2_path = os.path.join(self.folder_path, self.files[i + 1])

        img1 = cv2.imread(img1_path, cv2.IMREAD_UNCHANGED)
        img2 = cv2.imread(img2_path, cv2.IMREAD_UNCHANGED)

        if self.resize:
            img1 = cv2.resize(img1,(560,320))
            img2 = cv2.resize(img2,(560,320))



        if img1 is None or img2 is None:
            raise ValueError("Error reading one of the images.")

        # Ensure 3-channel (important for models like RAFT)
        if len(img1.shape) == 2:  # grayscale
            img1 = cv2.merge([img1, img1, img1])
        if len(img2.shape) == 2:
            img2 = cv2.merge([img2, img2, img2])

        return img1, img2
class opt_flow():
  
    def __init__(self, model_path="blood_cell"
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
class Tracking_impl():
    def __init__(self):
        self.reader = ImagePairReader("rbc")
        self.fl = opt_flow()
        self.viz = FlowVisualizer()

        

        pass
    def impl(self):
        for i in range (self.reader.num_pairs):
           
            im1,im2 = self.reader.read_pair(i)
            
            image1 = self.list_to_tensor([im1,im1,im1])
            image2 = self.list_to_tensor([im2,im2,im2])

           

            flow = self.fl.compute_flow(image1,image2)

            fl = self.viz.flows_to_numpy_images(flow)
            save_path = os.path.join( self.reader.folder_path, f"flow_{i:04d}.png")
            self.save_flow_image(fl[2],save_path)
           
            
            
    def list_to_tensor(self, image_list):
        ten = torch.from_numpy(np.stack(image_list))  # [B,H,W,3]
        ten = ten.permute(0, 3, 1, 2).float() 
        ten = ten.to(self.fl.device)
        return ten
    def save_flow_image(self,image, file_path):
        """
        Saves an image as PNG.
        Automatically creates directory if it doesn't exist.
        """
        # Get directory from path
        directory = os.path.dirname(file_path)

        # Create directory if needed
        if directory and not os.path.exists(directory):
            os.makedirs(directory)

        # Save image
        success = cv2.imwrite(file_path, image)

        if not success:
            raise IOError(f"Failed to save image at {file_path}")

  
obj = Tracking_impl()

obj.impl()
