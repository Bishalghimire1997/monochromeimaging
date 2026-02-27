import torch
import torch.nn.functional as F
import numpy as np
import skimage
from skimage.metrics import structural_similarity as ssim
from skimage import color, filters
from skimage.color import deltaE_ciede2000, rgb2xyz, xyz2lab
from skimage import filters
import cv2

class Evaluation():
    def __init__(self):
        pass

    # -----------------------------
    # Structural Similarity
    # -----------------------------
    def get_structure_similarity(self, ref_images: torch.Tensor, target_images: torch.Tensor, channel="all"):
        """
        Compute SSIM between reference and target images.

        Args:
            ref_images: [B, C, H, W] torch tensor, values 0-255
            target_images: same shape as ref_images
            channel: "r", "g", "b", or "all" (use L channel in Lab for "all")
        Returns:
            List of SSIM values for each image
        """
        d_type = np.uint8
        ref_images = ref_images.detach().cpu().permute(0, 2, 3, 1).numpy().astype(d_type)
        tar_images = target_images.detach().cpu().permute(0, 2, 3, 1).numpy().astype(d_type)
        ref_images_np = ref_images[..., ::-1]
        target_images_np= tar_images[..., ::-1]


        

        ssim_list = []
        # print("Image shape for SSIM:", ref_images_np.shape)
        # print("Image shape target for SSIM:", target_images_np.shape )

        for ref, targ in zip(ref_images_np, target_images_np):
            if channel in ["r", "g", "b"]:
                ch_idx = {"b": 0, "g": 1, "r": 2}[channel]
                ssim_val = ssim(ref[..., ch_idx], targ[..., ch_idx], data_range=255)
            else:
                # compute over all channels
                #ref = np.transpose(ref, (2, 0, 1))  # [C,H,W]
                #targ = np.transpose(targ, (2, 0, 1))  # [C,H,W]

                # print("Image shape for SSIM:", ref.shape)
                # print("Image shape target for SSIM:", targ.shape )
                ssim_val = ssim(ref, targ,channel_axis=-1, data_range=255)
            ssim_list.append(ssim_val)


        return ssim_list

    # -----------------------------
    # Delta E CIEDE2000
    # -----------------------------
    def compute_del_e(self, ref_images, tar_images):
        """
        Compute average Delta E (CIEDE2000) color difference between reference and target images.
        Args:
            ref_images (torch.Tensor): Reference images, shape (B, C, H, W)
            tar_images (torch.Tensor): Target images, shape (B, C, H, W)
        Returns:
            np.ndarray: Average Delta E per image, shape (B,)
        """
        # Convert to numpy with shape (B, H, W, C)
        d_type = np.uint8
        ref_images = ref_images.detach().cpu().permute(0, 2, 3, 1).numpy().astype(d_type)
        tar_images = tar_images.detach().cpu().permute(0, 2, 3, 1).numpy().astype(d_type)
        ref_images = ref_images[..., ::-1]
        tar_images = tar_images[..., ::-1]

        # cv2.imshow("ref",ref_images[0])
        # cv2.waitKey(0)
        # cv2.destroyAllWindows()

        ref_images =  filters.gaussian(ref_images, (0,1,1,0), preserve_range=True).astype(d_type)
        tar_images = filters.gaussian(tar_images,(0,1,1,0),preserve_range=True).astype(d_type)     
        xyz_ref = skimage.color.rgb2xyz(ref_images)
        xyz_target = skimage.color.rgb2xyz(tar_images)
        lab_ref = skimage.color.xyz2lab(xyz_ref)
        lab_targ = skimage.color.xyz2lab(xyz_target)
        delta_e=deltaE_ciede2000(lab_ref,lab_targ)
        avg = np.mean(delta_e,axis =(1,2) )

        print(f"The value of Delta E per image: {avg}")
        return avg

    # -----------------------------
    # Edge-based SSIM / MSE
    # -----------------------------
    def edge_structural_similarity(self, ref_images: torch.Tensor, target_images: torch.Tensor):
        """
        Compute SSIM between edge maps of tensor images
        """
        ref_np = ref_images.permute(0, 2, 3, 1).cpu().numpy().astype(np.uint8)
        targ_np = target_images.permute(0, 2, 3, 1).cpu().numpy().astype(np.uint8)

        edge_ssim_list = []

        for ref, targ in zip(ref_np, targ_np):
            # Convert to grayscale
            ref_gray = cv2.cvtColor(ref, cv2.COLOR_RGB2GRAY)
            targ_gray = cv2.cvtColor(targ, cv2.COLOR_RGB2GRAY)

            ref_edges = cv2.Canny(ref_gray, 100, 200)
            targ_edges = cv2.Canny(targ_gray, 100, 200)

            ssim_val = ssim(ref_edges, targ_edges, data_range=255)
            edge_ssim_list.append(ssim_val)

        return edge_ssim_list

    def Mse_edges(self, ref_images: torch.Tensor, target_images: torch.Tensor):
        """
        Compute MSE between edge masks of tensor images
        """
        ref_np = ref_images.permute(0, 2, 3, 1).cpu().numpy().astype(np.uint8)
        targ_np = target_images.permute(0, 2, 3, 1).cpu().numpy().astype(np.uint8)

        mse_list = []

        for ref, targ in zip(ref_np, targ_np):
            ref_gray = cv2.cvtColor(ref, cv2.COLOR_RGB2GRAY)
            targ_gray = cv2.cvtColor(targ, cv2.COLOR_RGB2GRAY)

            _, ref_mask = cv2.threshold(cv2.Canny(ref_gray, 100, 200), 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
            _, targ_mask = cv2.threshold(cv2.Canny(targ_gray, 100, 200), 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

            mse_val = np.mean((ref_mask - targ_mask) ** 2)
            mse_list.append(mse_val)

        return mse_list
