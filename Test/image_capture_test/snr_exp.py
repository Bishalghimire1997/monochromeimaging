import os
import h5py
import numpy as np
import argparse
import numpy as np
import torch
import cv2
from matplotlib import pyplot as plt
import torch.nn.functional as F
from processing_using_raft.raft import RAFT
from processing_using_raft.utils import InputPadder


class RAFTRegistration:
    def __init__(self,
                 model_path="raft-things.pth",
                 use_small=False,
                 device=None):

        self.device = (
            torch.device(device)
            if device is not None
            else torch.device(
                "cuda" if torch.cuda.is_available() else "cpu"
            )
        )

        self.model = self._load_model(
            model_path,
            use_small
        )

    def _load_model(self, model_path, use_small):
        args = argparse.Namespace(
            small=use_small,
            mixed_precision=True,
            alternate_corr=False
        )

        model = RAFT(args)
        model = torch.nn.DataParallel(model)

        checkpoint = torch.load(
            model_path,
            map_location=self.device
        )

        model.load_state_dict(checkpoint)

        return model.module.to(self.device).eval()

    def _to_tensor(self, images):
        """
        images:
            (B, H, W)
            (B, H, W, 1)
            (B, H, W, 3)

        returns:
            [B, 3, H, W]
        """

        images = np.asarray(images)

        if images.ndim == 3:
            images = images[..., None]

        if images.shape[-1] == 1:
            images = np.repeat(images, 3, axis=-1)

        images = images.astype(np.float32)


        images = torch.from_numpy(images)
        images = images.permute(0, 3, 1, 2)

        return images.to(self.device)

    def _warp(self, images, flow):
        """
        images: [B, 1, H, W]
        flow:   [B, 2, H, W]
        """

        B, C, H, W = images.shape

        grid_y, grid_x = torch.meshgrid(
            torch.linspace(-1, 1, H, device=images.device),
            torch.linspace(-1, 1, W, device=images.device),
            indexing="ij"
        )

        base_grid = torch.stack(
            (grid_x, grid_y),
            dim=-1
        )

        base_grid = base_grid.unsqueeze(0).expand(
            B, -1, -1, -1
        )

        flow_x = flow[:, 0] / ((W - 1) / 2)
        flow_y = flow[:, 1] / ((H - 1) / 2)

        flow_norm = torch.stack(
            (flow_x, flow_y),
            dim=-1
        )

        warp_grid = base_grid + flow_norm

        warped = F.grid_sample(
            images,
            warp_grid,
            mode="bilinear",
            padding_mode="border",
            align_corners=True
        )

        return warped

    @torch.no_grad()
    def register(self, source, target):
        """
        Parameters
        ----------
        source : np.ndarray
            Shape (B,H,W) or (B,H,W,1) or (B,H,W,3)

        target : np.ndarray
            Shape (B,H,W) or (B,H,W,1) or (B,H,W,3)

        Returns
        -------
        registered : np.ndarray
            Shape (B,H,W)
        """

        source_t = self._to_tensor(source)
        target_t = self._to_tensor(target)

        padder = InputPadder(source_t.shape)
        source_t, target_t = padder.pad(
            source_t,
            target_t
        )

        _, flow = self.model(
            source_t,
            target_t,
            iters=32,
            test_mode=True
        )

        moving_gray = target_t[:, :1]

        registered = self._warp(
            moving_gray,
            flow
        )

        registered = padder.unpad(
            registered
        )

        registered = (
            registered[:, 0]
            .detach()
            .cpu()
            .numpy()
        )

        return registered

class ImagePSNR:

    def __init__(self):
        self.roi = None

    def select_roi(self, image):
        """
        Ask the user to select an ROI only once.
        """
        if self.roi is not None:
            return self.roi

        display = image.copy()

        # Convert for display if necessary
        if display.dtype != np.uint8:
            disp = display.astype(np.float32)
            disp -= disp.min()
            if disp.max() > 0:
                disp /= disp.max()
            disp = (disp * 255).astype(np.uint8)
        else:
            disp = display.copy()

        roi = cv2.selectROI(
            "Select ROI and press ENTER",
            disp,
            showCrosshair=True,
            fromCenter=False,
        )
        cv2.destroyWindow("Select ROI and press ENTER")

        self.roi = roi
        return roi

    def crop(self, image):
        x, y, w, h = self.select_roi(image)
        return image[y:y + h, x:x + w]

    @staticmethod
    def compute_psnr(reference, target):
        """
        Compute PSNR between two images.
        """

        ref = reference.astype(np.float64)
        tgt = target.astype(np.float64)

        mse = np.mean((ref - tgt) ** 2)

        if mse == 0:
            return np.inf

        data_range = max(ref.max(), tgt.max()) - min(ref.min(), tgt.min())

        if data_range == 0:
            data_range = 1.0

        psnr = 20 * np.log10(data_range / np.sqrt(mse))

        return psnr

    @staticmethod
    def prepare(img):
        img = img.astype(np.float32)
        img -= img.min()

        if img.max() > 0:
            img /= img.max()

        return img

    def compare(self, reference, target1, target2):

        # If images are RGB/BGR, use the second channel only
        if reference.ndim == 3 and reference.shape[-1] == 3:
            reference = reference[:, :, 1]

        if target1.ndim == 3 and target1.shape[-1] == 3:
            target1 = target1[:, :, 1]

        if target2.ndim == 3 and target2.shape[-1] == 3:
            target2 = target2[:, :, 1]

        ref = self.crop(reference)
        tar1 = self.crop(target1)
        tar2 = self.crop(target2)

        psnr1 = self.compute_psnr(ref, tar1)
        psnr2 = self.compute_psnr(ref, tar2)

        fig, ax = plt.subplots(1, 3, figsize=(15, 5))

        titles = [
            "Reference",
            f"Target 1\nPSNR = {psnr1:.2f} dB",
            f"Target 2\nPSNR = {psnr2:.2f} dB",
        ]

        images = [ref, tar1, tar2]

        for a, img, title in zip(ax, images, titles):

            img = self.prepare(img)
            a.imshow(img, cmap="gray")
            a.set_title(title)
            a.axis("off")

        plt.tight_layout()
        plt.show()

        print(f"Target 1 PSNR : {psnr1:.2f} dB")
        print(f"Target 2 PSNR : {psnr2:.2f} dB")

        return psnr1, psnr2
    
class H5ImageLoader:

    def __init__(self, directory):
        self.directory = directory

        self.reference_file = "position_0.h5"
        self.other_files = [
            f"position_{i}_{side}.h5"
            for i in range(1, 6)
            for side in ("L", "R")
        ]

        self.roi = None  # (x, y, w, h)

    # =========================
    # ROI HANDLING
    # =========================

    def display_three_images(self,img1, img2, img3,titles=("Image 1", "Image 2", "Image 3"), figsize=(18, 6)):
   

        def prepare_image(img):
            img = np.asarray(img)

            # Convert to float for normalization
            img = img.astype(np.float32)

            # Handle NaNs/Infs
            img = np.nan_to_num(img)

            # Normalize independently for visualization
            mn = img.min()
            mx = img.max()

            if mx > mn:
                img = (img - mn) / (mx - mn)
            else:
                img = np.zeros_like(img)

            return img

        images = [prepare_image(img1),
                prepare_image(img2),
                prepare_image(img3)]

        fig, axes = plt.subplots(1, 3, figsize=figsize)

        for ax, img, title in zip(axes, images, titles):
            if img.ndim == 2:
                ax.imshow(img, cmap='gray')
            elif img.ndim == 3:
                ax.imshow(img)
            else:
                raise ValueError(f"Unsupported image shape: {img.shape}")

            ax.set_title(title)
            ax.axis("off")

        plt.tight_layout()
        plt.show()


    def select_roi(self, img):
        """
        Scaled-safe ROI selector (prevents screen overflow)
        """
        h, w = img.shape[:2]

        scale = min(1000 / h, 1000 / w, 1.0)
        disp = cv2.resize(img, (int(w * scale), int(h * scale)))

        x, y, rw, rh = cv2.selectROI("Select ROI", disp, fromCenter=False)
        cv2.destroyAllWindows()

        # map back
        x = int(x / scale)
        y = int(y / scale)
        rw = int(rw / scale)
        rh = int(rh / scale)

        return (x, y, rw, rh)

    def apply_roi(self, img):
        x, y, w, h = self.roi
        return img[y:y+h, x:x+w]

    # =========================
    # H5 LOADER
    # =========================

    def _load_h5(self, filename, use_roi=True):
        filepath = os.path.join(self.directory, filename)

        with h5py.File(filepath, "r") as f:
            keys = sorted(f.keys(), key=lambda x: int(x))
            images = [f[k][:] for k in keys]

        images = np.stack(images)

        # =========================
        # FORCE ROI FROM REFERENCE FILE FIRST
        # =========================
        if self.roi is None:
            first_img = images[0]
            self.roi = self.select_roi(first_img)
            print("ROI selected:", self.roi)

        # =========================
        # APPLY ROI
        # =========================
        if use_roi:
            images = np.stack([self.apply_roi(img) for img in images])

        return images

    # =========================
    # API FUNCTIONS
    # =========================

    def load_reference_stack(self):
        return self._load_h5(self.reference_file)

    def get_reference_image(self):
        images = self.load_reference_stack()
        return images.mean(axis=0)

    def get_image1(self, n_images=10):
        images = self.load_reference_stack()
        return images[:n_images], images[:n_images].mean(axis=0)

    def get_sampled_images(self, step=5):
        sampled_images = []

        for filename in self.other_files:
            images = self._load_h5(filename)
            sampled_images.extend(images[::step])

        return np.stack(sampled_images)

    def get_single_image_from_each(self, index=5):
        images_list = []

        for filename in self.other_files:
            images = self._load_h5(filename)
            images_list.append(images[index])

        return np.stack(images_list)
    

     

loader = H5ImageLoader("SNR_test_data")
print("loading_ref")

reference_image = loader.get_reference_image() # average of 10000 static images 
ten_static_images,image1_average = loader.get_image1(n_images=10) #average of 10 static images

# Gives 20 images if each file has 10 frames
sampled_images = loader.get_sampled_images(step=5)

# Gives exactly 10 images (one from each file)
print("loading moving")
ten_moving_images = loader.get_single_image_from_each(index=5) # 10 moving Images 




print("loaded all")
print(ten_moving_images.shape)
print(ten_static_images.shape)



reg = RAFTRegistration()
rej_list = []
for i, j in zip(ten_static_images, ten_moving_images):
    i = i[None, ...]
    j = j[None, ...]

    registered = reg.register(i, j)
    rej_list.append(registered[0])
regestered_image = np.array(rej_list)
regestered_image_average = regestered_image.mean(axis=0)
loader.display_three_images(regestered_image_average,reference_image,image1_average)
psnr = ImagePSNR()
psnr1,psnr2 = psnr.compare(reference_image,regestered_image_average,image1_average)
    


