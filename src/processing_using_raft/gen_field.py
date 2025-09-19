import numpy as np
import torch.nn.functional as F
import torch
import cv2
import noise

class PerlinCrush:
    def __init__(self, scale=100.0, magnitude=50.0, seed=None):
        self.scale = scale
        self.magnitude = magnitude
        self.seed = seed
        self.roi = None
    def generate_perlin_flow_2d_from_3d(self, img):
        B, C, H, W = img.shape
        if self.seed is not None:
            np.random.seed(self.seed)

        freq = 1.0 / self.scale
        flow_batch = []

        for _ in range(B):
            flow_x = np.zeros((H, W), dtype=np.float32)
            flow_y = np.zeros((H, W), dtype=np.float32)
            flow_z = np.zeros((H, W), dtype=np.float32)
            binary_mask = np.ones((H, W), dtype=bool)


            offset = np.random.randint(0, 100)
            z_shift = 100.0  # change to separate the x and y noise directions
            if self.roi is None: 
                    binary_mask = np.ones((H,W),dtype=bool)
            else:    
                    binary_mask = np.zeros((H, W), dtype=bool)
                    x1, y1, x2, y2 = self.roi
                    binary_mask[y1:y2, x1:x2] = True
                    print(binary_mask[y1:y2,x1:x2])

            for i in range(H):
                for j in range(W):
                    if binary_mask[i,j]:
                        
                        fx = noise.pnoise3( 
                            i * freq,
                            j * freq,
                            offset,
                            octaves=8,
                            repeatx = 1024,
                            repeaty=1024,
                            repeatz=1024,
                            base=0
                        )
                        fy = noise.pnoise3(
                            i * freq,
                            j * freq,
                            offset + z_shift,
                            octaves=8,
                            repeatx=1024,
                            repeaty=1024,
                            repeatz=1024,
                            base=1
                        )

                        fz = noise.pnoise3(
                            i * freq,
                            j * freq,
                            offset ,
                            octaves=8,
                            repeatx=1024,
                            repeaty=1024,
                            repeatz=1024,
                            base=2
                        )

                    
                        flow_x[i, j] = fx
                        flow_y[i, j] = fy
                        flow_z[i, j] = fz  # Not used in 2D flow

            # Normalize and scal




            flow_x = torch.from_numpy(flow_x)
            flow_y = torch.from_numpy(flow_y)
            flow_x = (flow_x+flow_z)/2
            flow_y = (flow_y+flow_z)/2
            flow_x = flow_x / (flow_x.abs().max() + 1e-8) * self.magnitude
            flow_y = flow_y / (flow_y.abs().max() + 1e-8) * self.magnitude
            
            

            flow = torch.stack([flow_x, flow_y], dim=0)  # [2, H, W]
            flow_batch.append(flow)

        flow_tensor = torch.stack(flow_batch, dim=0)  # [B, 2, H, W]
        return flow_tensor


    def generate_perlin_flow_GPU(self,image,  device='cuda'):
        """
        Generate a batch of 2D Perlin-like flow fields on GPU.

        Args:
            B (int): Batch size
            H (int): Image height
            W (int): Image width
            scale (float): Controls frequency of noise
            magnitude (float): Maximum flow magnitude
            device (str): 'cuda' or 'cpu'
            seed (int, optional): Random seed

        Returns:
            Tensor: Flow tensor of shape [B, 2, H, W]
        """
        B, C, H, W = image.shape
        if self.seed is not None:
            torch.manual_seed(self.seed)

        # Create normalized coordinate grid
        y = torch.linspace(0, 1, H, device=device)
        x = torch.linspace(0, 1, W, device=device)
        yy, xx = torch.meshgrid(y, x, indexing='ij')  # [H, W]

        # Scale coordinates
        freq = 1.0 / self.scale
        xx = xx * freq * W
        yy = yy * freq * H

        # Random offsets per batch
        offsets = torch.randint(0, 100, (B, 1, 1), device=device, dtype=torch.float32)
        z_shift = 10.0  # separate x and y directions

        # Create batch of grids
        xx_batch = xx.unsqueeze(0).repeat(B, 1, 1) + offsets
        yy_batch = yy.unsqueeze(0).repeat(B, 1, 1) + offsets

        # Smooth sinusoidal approximation of Perlin noise
        flow_x = torch.sin(xx_batch + yy_batch) + torch.cos(xx_batch * 0.5 + yy_batch * 0.5)
        flow_y = torch.sin(xx_batch + yy_batch + z_shift) + torch.cos(xx_batch * 0.5 + yy_batch * 0.5 + z_shift)

        # Normalize to [-1, 1] and scale by magnitude
        flow_x = flow_x / (flow_x.abs().amax(dim=[1,2], keepdim=True) + 1e-8) * self.magnitude
        flow_y = flow_y / (flow_y.abs().amax(dim=[1,2], keepdim=True) + 1e-8) * self.magnitude

        flow = torch.stack([flow_x, flow_y], dim=1)  # [B, 2, H, W]
        return flow


    def warp_image(self, img):
        """
        Warp a BCHW image tensor using generated Perlin flow in one direction (e.g., vertical only).

        Args:
            img: torch.Tensor of shape [B, C, H, W]

        Returns:
            warped: torch.Tensor of shape [B, C, H, W]
            flow: torch.Tensor of shape [B, 1, H, W]
        """
        B, C, H, W = img.shape
        device = img.device

        # [B, 1, H, W] — single-channel flow (e.g., vertical offset only)
        single_flow = self.generate_perlin_flow_2d_from_3d(img).to(device)

        # Expand to [B, 2, H, W] for grid warping
        flow = torch.zeros((B, 2, H, W), device=device)
        flow[:, 1, :, :] = single_flow[:, 0, :, :]  # Apply as vertical flow (Y-axis only)

        # Generate base grid
        grid_y, grid_x = torch.meshgrid(
            torch.arange(H, device=device),
            torch.arange(W, device=device),
            indexing='ij'
        )
        grid = torch.stack((grid_x, grid_y), dim=0).float()  # [2, H, W]
        grid = grid.unsqueeze(0).repeat(B, 1, 1, 1)  # [B, 2, H, W]

        # Apply flow
        vgrid = grid + flow  # [B, 2, H, W]

        # Normalize grid to [-1, 1]
        vgrid[:, 0, :, :] = 2.0 * vgrid[:, 0, :, :] / max(W - 1, 1) - 1.0
        vgrid[:, 1, :, :] = 2.0 * vgrid[:, 1, :, :] / max(H - 1, 1) - 1.0

        # Rearrange for grid_sample
        vgrid = vgrid.permute(0, 2, 3, 1)  # [B, H, W, 2]

        warped = F.grid_sample(img, vgrid, align_corners=True, mode='bilinear', padding_mode='border')

        return warped, single_flow 
    # def warp_image_with_intensity(self, img):
    #     """
    #     Warp a BCHW image tensor using generated Perlin flow in one direction (e.g., vertical only).

    #     Args:
    #         img: torch.Tensor of shape [B, C, H, W]

    #     Returns:
    #         warped: torch.Tensor of shape [B, C, H, W]
    #         flow: torch.Tensor of shape [B, 1, H, W]
    #     """
    #     B, C, H, W = img.shape
    #     device = img.device

    #     # [B, 1, H, W] — single-channel flow (e.g., vertical offset only)
    #     single_flow = self.generate_perlin3d(img).to(device)

    #     # Expand to [B, 2, H, W] for grid warping
    #     flow = torch.zeros((B, 2, H, W), device=device)
    #     flow[:, 1, :, :] = single_flow[:, 0, :, :]  # Apply as vertical flow (Y-axis only)

    #     # Generate base grid
    #     grid_y, grid_x = torch.meshgrid(
    #         torch.arange(H, device=device),
    #         torch.arange(W, device=device),
    #         indexing='ij'
    #     )
    #     grid = torch.stack((grid_x, grid_y), dim=0).float()  # [2, H, W]
    #     grid = grid.unsqueeze(0).repeat(B, 1, 1, 1)  # [B, 2, H, W]

    #     # Apply flow
    #     vgrid = grid + flow  # [B, 2, H, W]

    #     # Normalize grid to [-1, 1]
    #     vgrid[:, 0, :, :] = 2.0 * vgrid[:, 0, :, :] / max(W - 1, 1) - 1.0
    #     vgrid[:, 1, :, :] = 2.0 * vgrid[:, 1, :, :] / max(H - 1, 1) - 1.0

    #     # Rearrange for grid_sample
    #     vgrid = vgrid.permute(0, 2, 3, 1)  # [B, H, W, 2]

    #     warped = F.grid_sample(img, vgrid, align_corners=True,   mode='bilinear', padding_mode='border')

    #     return warped, single_flow 