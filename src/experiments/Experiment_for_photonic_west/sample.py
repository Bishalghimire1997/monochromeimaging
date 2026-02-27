import torch
import h5py
import numpy as np
import torch.nn.functional as F
import os
import cv2
class RGBMisalignmentSimulator:
    def __init__(self, batch_size=12, device="cuda"):
        self.batch_size = batch_size
        self.device = device
        self.resize_flag = True
        self.resize = (384,512)

    def __sample(self,path, sample_from=0,jump = 1):
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
            for i in range(self.batch_size):
                idx = i*jump + sample_from
                if idx >= total_frames:   # stop if we exceed dataset length
                    break
                frame = f[str(idx)][:]    # numpy array (H, W, C)
                images.append(frame)

        if not images:  # no frames available
            print("No frames availebal")
            return None
        images_np = np.stack(images, axis=0)
        frames = torch.tensor(images_np, dtype=torch.float32, device=self.device)
        return frames
    def video_to_h5(self,video_path:str, output_filename="converted.h5"):
        """
        Extracts frames from an .mp4 video and saves them as individual datasets
        inside an .h5 file, each named by its frame index ("0", "1", "2", ...).

        Args:
            video_path (str): Path to input .mp4 file.
            output_dir (str): Directory to save the .h5 file.
        """

        

        # Create output file name
        
        h5_path = output_filename
        print(f"🎬 Converting {video_path} to {h5_path}...")
       

        # Open video
        cap = cv2.VideoCapture(video_path,cv2.CAP_ANY)
        success, frame = cap.read()
        idx = 0
        with h5py.File(h5_path, "w") as f:
            while success:
                # Convert frame from BGR → RGB
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                
                # Optional: normalize to [0,1]
                # frame_rgb = frame_rgb.astype(np.float32) / 255.0
                
                # Save each frame as its own dataset
                f.create_dataset(str(idx), data=frame_rgb, compression="gzip")
                
                idx += 1
                success, frame = cap.read()

        cap.release()
        print(f"✅ Saved {idx} frames to {h5_path}")

    def generate(self, path, from_index:int = 0, jump: int = 1, batch:int = 6, crop: tuple = None):
        """
        Generate reference (misaligned) and target tensors.

        Args:
            jump (int): Frame spacing between channels. Default = 1.
            crop (tuple, optional): (x, y, width, height) to crop frames before resizing.

        Returns: 
            references: [M, C, H, W] tensor (misaligned images).
            targets:    [M, C, H, W] tensor (true images).
        """
        self.frames = self.__sample(path, from_index, jump)
        N, H, W, C = self.frames.shape
        assert C == 3, "Frames must have 3 channels (RGB)."

        refs = []
        targs = []

        for i in range(N - 2):
            blue  = self.frames[i, :, :, 2]         # B from frame i
            green = self.frames[i + 1, :, :, 1]  # G from frame i+jump
            red   = self.frames[i + 2 , :, :, 0]  # R from frame i+2*jump

            # stack back into RGB
            ref = torch.stack([red, green, blue], dim=-1)
            target = self.frames[i + 1]

            # Apply crop if provided
            if crop is not None:
                x, y, w, h = crop
                ref = ref[y:y+h, x:x+w, :]
                target = target[y:y+h, x:x+w, :]

            # Resize if needed
            if self.resize_flag:
                H_new, W_new = self.resize
                # permute to [1, C, H, W] for interpolate
                ref = ref.permute(2, 0, 1).unsqueeze(0).float()  # [1,C,H,W]
                target = target.permute(2, 0, 1).unsqueeze(0).float()
                ref = F.interpolate(ref, size=(H_new, W_new), mode='bilinear', align_corners=True)[0].permute(1, 2, 0)
                target = F.interpolate(target, size=(H_new, W_new), mode='bilinear', align_corners=True)[0].permute(1, 2, 0)

            refs.append(ref)
            targs.append(target)

        references = torch.stack(refs, dim=0).permute(0, 3, 1, 2)  # [M, C, H, W]
        targets = torch.stack(targs, dim=0).permute(0, 3, 1, 2)

        return references, targets
