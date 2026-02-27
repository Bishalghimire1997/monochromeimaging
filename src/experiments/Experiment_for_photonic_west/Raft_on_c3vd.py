import os
import torch
from torch.utils.data import Dataset, DataLoader
from PIL import Image
import numpy as np
from processing_using_raft.visualize import FlowVisualizer
import cv2
import glob

class readc3vd_data(Dataset):
    def __init__(self, root_dir, transform=None, n_frames_per_batch=4):
        self.root_dir = root_dir
        self.transform = transform
        self.n_frames = n_frames_per_batch

        # Sort color and flow files
        self.color_files = sorted(glob.glob(os.path.join(root_dir, '*_color.png')))
        self.flow_files = sorted(glob.glob(os.path.join(root_dir, '*_flow.tiff')))

        print(f"Found {len(self.color_files)} color files and {len(self.flow_files)} flow files.")

        # Number of possible sliding windows
        self.num_sequences = (len(self.color_files) - self.n_frames) // self.n_frames


    def __len__(self):
        return self.num_sequences

    def __getitem__(self, idx):
        imgs1, imgs2, flows = [], [], []

        # non-overlapping step
        start_idx = idx * self.n_frames  

        for i in range(self.n_frames):
            im1_path = self.color_files[start_idx + i]
            im2_path = self.color_files[start_idx + i + 1]
            flow_path = self.flow_files[start_idx + i]

            print(f"Loading frame {i}: im1={im1_path}, im2={im2_path}, flow={flow_path}")

            im1 = np.array(Image.open(im1_path), dtype=np.float32)
            im2 = np.array(Image.open(im2_path), dtype=np.float32)
            flow = np.array(Image.open(flow_path), dtype=np.float32)

            # convert to torch tensors
            im1 = torch.from_numpy(im1).permute(2, 0, 1)
            im2 = torch.from_numpy(im2).permute(2, 0, 1)

            # ensure flow has 2 channels
            if flow.ndim == 2:
                flow = torch.stack([torch.from_numpy(flow), torch.zeros_like(torch.from_numpy(flow))])
            else:
                flow = torch.from_numpy(flow[:, :, :2]).permute(2, 0, 1)

            imgs1.append(im1)
            imgs2.append(im2)
            flows.append(flow)

        imgs1 = torch.stack(imgs1)  # [n_frames, 3, H, W]
        imgs2 = torch.stack(imgs2)
        flows = torch.stack(flows)  # [n_frames, 2, H, W]

        return imgs1, imgs2, flows


if __name__ == "__main__":
    root_dir = "C:/Users/SIU856587710/channel_tets/datasets/c4vd/cecum_t2_b/cecum_t2_b"
    dataset = readc3vd_data(root_dir, n_frames_per_batch=4)
    dataloader = DataLoader(dataset, batch_size=1, shuffle=False)
    vis = FlowVisualizer()

for i,(imgs1, imgs2, flows) in enumerate(dataloader):
    # Remove batch dimension
    imgs1 = imgs1.squeeze(0)  # [n_frames, 3, H, W]
    imgs2 = imgs2.squeeze(0)
    flows = flows.squeeze(0)  # [n_frames, 2, H, W]

    # print("imgs1:", imgs1.shape)
    # print("imgs2:", imgs2.shape)
    # print("flows:", flows.shape)

    

    # pick first frame for display
    im1 = imgs1[0].permute(1, 2, 0).cpu().numpy()  # [H,W,C]
    im2 = imgs2[0].permute(1, 2, 0).cpu().numpy()
    flow = vis.flows_to_numpy_images(flows)

    # convert to uint8
    im1 = np.clip(im1, 0, 255).astype(np.uint8)
    im2 = np.clip(im2, 0, 255).astype(np.uint8)
    dataloader = DataLoader(dataset, batch_size=1, shuffle=False)
    # convert RGB -> BGR
    im1_bgr = cv2.cvtColor(im1, cv2.COLOR_RGB2BGR)
    im2_bgr = cv2.cvtColor(im2, cv2.COLOR_RGB2BGR)
    print("MAX FLOW",np.max(flows[0],"MIN FLOW",np.min(flows[0])))

    cv2.imshow("Image 1", im1_bgr)
    cv2.imshow("Image 2", im2_bgr)
    cv2.imshow("Optical Flow", flow[0])  # display first flow
    cv2.waitKey(0)
    cv2.destroyAllWindows()

