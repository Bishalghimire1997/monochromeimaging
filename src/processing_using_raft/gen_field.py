import numpy as np
import torch.nn.functional as F
import torch
import noise

class PerlinCrush:
    def __init__(self, scale=100.0, magnitude=15.0, seed=None):
        self.scale = scale
        self.magnitude = magnitude
        self.seed = seed
    def generate_perlin_flow_2d_from_3d(self, img):
        B, C, H, W = img.shape
        if self.seed is not None:
            np.random.seed(self.seed)

        freq = 1.0 / self.scale
        flow_batch = []

        for _ in range(B):
            flow_x = np.zeros((H, W), dtype=np.float32)
            flow_y = np.zeros((H, W), dtype=np.float32)

            offset = np.random.randint(0, 100)
            z_shift = 10.0  # change to separate the x and y noise directions

            for i in range(H):
                for j in range(W):
                    fx = noise.pnoise3(
                        i * freq,
                        j * freq,
                        offset,
                        octaves=4,
                        repeatx=1024,
                        repeaty=1024,
                        repeatz=1024,
                        base=0
                    )
                    fy = noise.pnoise3(
                        i * freq,
                        j * freq,
                        offset + z_shift,
                        octaves=4,
                        repeatx=1024,
                        repeaty=1024,
                        repeatz=1024,
                        base=0
                    )
                    flow_x[i, j] = fx
                    flow_y[i, j] = fy

            # Normalize and scale
            flow_x = torch.from_numpy(flow_x)
            flow_y = torch.from_numpy(flow_y)
            flow_x = flow_x / (flow_x.abs().max() + 1e-8) * self.magnitude
            flow_y = flow_y / (flow_y.abs().max() + 1e-8) * self.magnitude

            flow = torch.stack([flow_x, flow_y], dim=0)  # [2, H, W]
            flow_batch.append(flow)

        flow_tensor = torch.stack(flow_batch, dim=0)  # [B, 2, H, W]
        return flow_tensor

    def generate_perlin_flow(self, img):
        B, C, H, W = img.shape
        if self.seed is not None:
            np.random.seed(self.seed)

        freq = 1.0 / self.scale  
        flow_batch = []

        for _ in range(B):
            flow = np.zeros((H, W), dtype=np.float32)
            offset = np.random.randint(0, 100)
 
            for i in range(H):
                for j in range(W):
                    # Generate Perlin noise in one direction (e.g., vertical)
                    flow[i, j] = noise.pnoise2(
                        (i + offset) * freq,
                        (j + offset) * freq,
                        octaves=4,
                        repeatx=1024,
                        repeaty=1024,
                        base=0
                    )
            flow = torch.from_numpy(flow)
            flow = flow / (flow.abs().max() + 1e-8) * self.magnitude  # normalize
            flow_batch.append(flow.unsqueeze(0))  # add channel dim: [1, H, W]

        flow_tensor = torch.stack(flow_batch, dim=0)  # [B, 1, H, W]
        return flow_tensor

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