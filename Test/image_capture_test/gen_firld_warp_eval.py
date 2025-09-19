from processing_using_raft.gen_field import PerlinCrush
from processing_using_raft.raft_impl import ChannelReg
import torch
import cv2
import numpy as np
class EvaluateWArpedImagesOnPerlinNoise:
    def __init__(self,scale,magnitude,seed,images):
        self.raft = ChannelReg()
        self.scale = scale
        self.magnitude = magnitude
        self.seed = seed
        self.image_tensor = None
        self.perlin = PerlinCrush(scale= self.scale, magnitude=self.magnitude, seed=10)
        self.image = images

  
        pass 
    def get_images(self):
        aug = []
        
        # _,grey,_ = cv2.split(self.image) 
        # zeros = np.zeros_like(grey)
        # im = cv2.merge([zeros, grey, zeros])
        # im = self.image.copy()
        # im = cv2.resize(im, (512, 512))
       
        for i in self.image: 
            im = cv2.resize(i, (512, 512))
            aug.append(im)
        self.image_tensor  = self.to_tensor(aug)

        warped ,flow= self.perlin.warp_image(self.image_tensor)
        warped_numpy = (warped.permute(0, 2, 3, 1).numpy()*255).astype(np.uint8)  # Convert to numpy array
        ref = [self.__to_tensor(i) for i in aug]
        floating = [self.__to_tensor(i) for i in warped_numpy] 

        return ref, warped_numpy ,floating,flow

    def to_tensor(self,img_list):
        arr = np.stack(img_list)  # [N, H, W] or [N, H, W, C]
        if arr.ndim == 3:  # grayscale: [N, H, W]  
            arr = arr[:, None, :, :]  # add channel dimension
        else:  # RGB: [N, H, W, C]
            arr = arr.transpose(0, 3, 1, 2)  # -> [N, C, H, W] 
        
        return torch.from_numpy(arr).float()/255  # normalize to [0,1]
    def __to_tensor(self, img, batched=False):
        img = img.astype(np.float32)
        if not batched:
            img = torch.from_numpy(img).permute(2, 0, 1).float()[None] / 255.0
        else:
            img = torch.from_numpy(img).permute(0, 3, 1, 2).float() / 255.0
        return img.to(self.raft.device)
    def display_side_by_side(self,img1, img2, window_name="Side-by-Side", resize_to=None):
        # Convert (C, H, W) to (H, W, C) if needed
        if img1.ndim == 3 and img1.shape[0] in [1, 3]:
            img1 = np.transpose(img1, (1, 2, 0))
        if img2.ndim == 3 and img2.shape[0] in [1, 3]:
            img2 = np.transpose(img2, (1, 2, 0))

        # Normalize float images to uint8
        if img1.dtype != np.uint8:
            img1 = (img1 * 255).clip(0, 255).astype(np.uint8)
        if img2.dtype != np.uint8:
            img2 = (img2 * 255).clip(0, 255).astype(np.uint8)

        # Resize if required 
        if resize_to:
            img1 = cv2.resize(img1, resize_to)
            img2 = cv2.resize(img2, resize_to)

        # Ensure same height
        if img1.shape != img2.shape:
            img2 = cv2.resize(img2, (img1.shape[1], img1.shape[0]))

        # Concatenate
        combined = np.hstack((img1, img2))

        # Show
        cv2.imshow(window_name, combined)
        cv2.waitKey(0)
        cv2.destroyAllWindows() 

image = cv2.imread("blob.png")  # Replace with your image path 

images = []
for  i in range(10):
    images.append(image)    
ob1= EvaluateWArpedImagesOnPerlinNoise(5000,75,10,images) 
ref,numpy_float,floating,flow = ob1.get_images()

#flow1 = ob1.raft.compute_flow(ref, floating)
#warped = ob1.raft.reg(numpy_float, flow1)
for fl ,fix in zip(numpy_float, images):
    ob1.display_side_by_side(fl, fix)
 

 