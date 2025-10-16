import torch
import h5py
import numpy as np
import torch.nn.functional as F

class RGBMisalignmentSimulator:
    def __init__(self, path, batch_size=12, device="cuda"):
        self.path = path
        self.batch_size = batch_size
        self.device = device
        self.resize_flag = True
        self.resize = (384,512)

    def __sample(self, sample_from=0):
        """
        Sample batch of frames from HDF5 and return tensor.

        Args:
            sample_from (int): Starting index inside the HDF5 file.

        Returns:
            frames: Tensor [M, H, W, C] on self.device,
                    where M <= batch_size depending on available frames.
        """
        images = []
        with h5py.File(self.path, "r") as f:
            total_frames = len(f.keys())  # total number of images stored
            for i in range(self.batch_size):
                idx = i + sample_from
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

    def generate(self, from_index:int = 0,jump: int = 1):
        """
        Generate reference (misaligned) and target tensors.

        Args:
            jump (int): Frame spacing between channels. Default = 1.

        Returns: 
            references: [M, H, W, 3] tensor (misaligned images).
            targets:    [M, H, W, 3] tensor (true images).
        """
        self.frames = self.__sample(from_index)
        N, H, W, C = self.frames.shape
        assert C == 3, "Frames must have 3 channels (RGB)."

        refs = []
        targs = []

        for i in range(N - 2 * jump):
            blue  = self.frames[i, :, :, 2]       # B from frame i
            green = self.frames[i + jump, :, :, 1] # G from frame i+jump
            red   = self.frames[i + 2 * jump, :, :, 0] # R from frame i+2*jump

            # stack back into RGB
            ref = torch.stack([red, green, blue], dim=-1)

            # target = the full color frame from where green came
            target = self.frames[i + jump]

            if self.resize_flag is True:
                H_new, W_new = self.resize
                # permute to [C,H,W] for interpolate
                ref = ref.permute(2, 0, 1).unsqueeze(0).float()  # [1,C,H,W]
                target = target.permute(2, 0, 1).unsqueeze(0).float()
                ref = F.interpolate(ref, size=(H_new, W_new), mode='bilinear', align_corners=True)[0].permute(1, 2, 0)
                target = F.interpolate(target, size=(H_new, W_new), mode='bilinear', align_corners=True)[0].permute(1, 2, 0)

            refs.append(ref)
            targs.append(target)

        references = torch.stack(refs, dim=0).permute(0, 3, 1, 2)
        targets = torch.stack(targs, dim=0).permute(0, 3, 1, 2)
        print("Refrence shape", references.shape,"Target Shape",targets.shape)   

        return references, targets
