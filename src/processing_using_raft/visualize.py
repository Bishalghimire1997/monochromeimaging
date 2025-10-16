import matplotlib.pyplot as plt
import numpy as np
import torch

from processing_using_raft import flow_viz


class FlowVisualizer:
    def __init__(self, save_path=None):
        """
        Args:
            save_path (str or None): if provided, will save visualizations to this path instead of just showing.
        """
        self.save_path = save_path

    def _to_numpy_img(self, img):
        """Convert image tensor or numpy -> [H,W,3] float in [0,1]"""
        if isinstance(img, torch.Tensor):
            if img.dim() == 4:  # [B,C,H,W]
                img = img[0]
            if img.dim() == 3:  # [C,H,W]
                img = img.permute(1,2,0)
            img = img.detach().cpu().numpy()
        img = img.astype(np.float32)
        if img.max() > 1.0:   # scale 0–255 to 0–1
            img = img / 255.0
        return img

    def _to_numpy_flow(self, flow):
        """Convert flow tensor or numpy -> [H,W,2] numpy"""
        if isinstance(flow, torch.Tensor):
            if flow.dim() == 4:  # [B,2,H,W]
                flow = flow[0]
            if flow.dim() == 3:  # [2,H,W]
                flow = flow.permute(1,2,0)
            flow = flow.detach().cpu().numpy()
        return flow

    # def visualize(self, image1, image2, flow_pred, flow_gt, title_suffix=""):
    #     """
    #     Show or save image1, image2, predicted flow, and ground truth flow in one figure.
    #     """
    #     # Convert inputs
        
    #     image1 = self._to_numpy_img(image1)
    #     image2 = self._to_numpy_img(image2)
    #     flow_pred = self._to_numpy_flow(flow_pred)
    #     flow_gt   = self._to_numpy_flow(flow_gt)

    #     # Convert flows to color images (uint8 RGB)
    #     flow_pred_img = flow_viz.flow_to_image(flow_pred)
    #     flow_gt_img   = flow_viz.flow_to_image(flow_gt)

    #     # Plot
    #     fig, axes = plt.subplots(2, 2, figsize=(10,8))
    #     axes[0,0].imshow(image1); axes[0,0].set_title("Image 1")
    #     axes[0,1].imshow(image2); axes[0,1].set_title("Image 2")
    #     axes[1,0].imshow(flow_pred_img); axes[1,0].set_title("Predicted Flow")
    #     axes[1,1].imshow(flow_gt_img); axes[1,1].set_title("Ground Truth Flow")

    #     for ax in axes.flat:
    #         ax.axis("off")
    #     plt.tight_layout()

    #     # Save or show
    #     if self.save_path:
    #         fname = f"{self.save_path}/flow_vis{title_suffix}.png"
    #         plt.savefig(fname)
    #         plt.close(fig)
    #         print(f"[FlowVisualizer] Saved visualization to {fname}")
    #     else:
    #         plt.show()
    def visualize(self, image1, image2, flow_pred, flow_gt, mask=None, title_suffix=""):
        """
            Show or save image1, image2, predicted flow, ground truth flow, 
            and optionally occlusion / consistency mask.

            Args:
                image1, image2: [B,3,H,W] or [3,H,W] tensors / numpy arrays
                flow_pred, flow_gt: [B,2,H,W] or [2,H,W] tensors / numpy arrays
                mask: [B,1,H,W] or [H,W] tensor / numpy array (optional)
                title_suffix: string for saving filename
        """
        # Convert inputs
        image1 = self._to_numpy_img(image1)
        image2 = self._to_numpy_img(image2)
        flow_pred = self._to_numpy_flow(flow_pred)
        flow_gt   = self._to_numpy_flow(flow_gt)

        # Convert flows to color
        flow_pred_img = flow_viz.flow_to_image(flow_pred)
        flow_gt_img   = flow_viz.flow_to_image(flow_gt)

        # Set up subplots
        if mask is not None:
            # Convert mask to numpy [H,W]
            if isinstance(mask, torch.Tensor):
                if mask.dim() == 4:  # [B,1,H,W]
                    mask_np = mask[0,0].detach().cpu().numpy()
                elif mask.dim() == 3:  # [1,H,W]
                    mask_np = mask[0].detach().cpu().numpy()
                else:  # [H,W]
                    mask_np = mask.detach().cpu().numpy()
            else:
                mask_np = mask
            # Ensure mask is 0-1 float
            mask_np = np.clip(mask_np, 0, 1)

            fig, axes = plt.subplots(2, 3, figsize=(15,8))
            axes[0,0].imshow(image1); axes[0,0].set_title("Image 1")
            axes[0,1].imshow(image2); axes[0,1].set_title("Image 2")
            axes[0,2].imshow(flow_pred_img); axes[0,2].set_title("Predicted Flow")
            axes[1,0].imshow(flow_gt_img); axes[1,0].set_title("Ground Truth Flow")
            im = axes[1,1].imshow(mask_np, cmap='gray'); axes[1,1].set_title("Occlusion / Consistency Mask")
            #fig.colorbar(im, ax=axes[1,1])
            #axes[1,2].axis("off")
        else:
            fig, axes = plt.subplots(2, 2, figsize=(10,8))
            axes[0,0].imshow(image1); axes[0,0].set_title("Image 1")
            axes[0,1].imshow(image2); axes[0,1].set_title("Image 2")
            axes[1,0].imshow(flow_pred_img); axes[1,0].set_title("Predicted Flow")
            axes[1,1].imshow(flow_gt_img); axes[1,1].set_title("Ground Truth Flow")

        for ax in axes.flat:
            ax.axis("off")
        plt.tight_layout()

        # Save or show
        if self.save_path:
            fname = f"{self.save_path}/flow_vis{title_suffix}.png"
            plt.savefig(fname)
            plt.close(fig)
            print(f"[FlowVisualizer] Saved visualization to {fname}")
        else:
            plt.show()
    def flows_to_numpy_images(self,flow_tensor):
        """
        Convert a batch of flow fields into list of numpy RGB images.

        Args:
            flow_tensor: [N,2,H,W] torch.Tensor or numpy.ndarray

        Returns:
            List[np.ndarray] where each element is [H,W,3] uint8 flow visualization
        # """
        # if isinstance(flow_tensor, torch.Tensor):
        #     flow_tensor = flow_tensor.detach().cpu().numpy()  # [N,2,H,W]

        imgs = []
        for flow in flow_tensor:  # each flow is [2,H,W]
            flow_hw2 = flow.clone().permute(1, 2, 0).cpu().numpy()
            print("Here is the flow shape = ################",flow_hw2.shape)
            flow_img = flow_viz.flow_to_image(flow_hw2)  # -> [H,W,3], uint8
            imgs.append(flow_img)

        return imgs

    
    