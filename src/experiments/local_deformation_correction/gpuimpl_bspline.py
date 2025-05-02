import cv2
import numpy as np
from matplotlib import pyplot as plt
from concurrent.futures import ThreadPoolExecutor
import multiprocessing as mp
from image_processing_package.Color_augmentation import ColorAugmentation
from skimage.transform import PiecewiseAffineTransform, warp

# ---------------- GPU Optical Flow Wrapper ---------------- #
class Flow:
    def __init__(self,numbItterations=2, tau=4, lambda_=0.5, theta=0.06, epsilon=1e-3):
        self.tvl1 = cv2.cuda.OpticalFlowDual_TVL1.create()
        self.tvl1 .setNumIterations(numbItterations)
        self.tvl1 .setTau(tau)
        self.tvl1 .setLambda(lambda_)
        self.tvl1 .setTheta(theta)
        self.tvl1 .setEpsilon(epsilon)   
       

    def compute_flow(self, images):
        fi=cv2.GaussianBlur(images[0], (5, 5), 100)
        fl = cv2.GaussianBlur(images[1], (5, 5), 100)  
        images = [fi, fl]         
        
       
        ref, floating = [i.astype(np.float32) / 255.0 for i in images]

        gpu_ref = cv2.cuda_GpuMat()
        gpu_flt = cv2.cuda_GpuMat()
        gpu_ref.upload(ref)
        gpu_flt.upload(floating)

        flow_gpu = self.tvl1.calc(gpu_ref, gpu_flt, None)
        return flow_gpu.download()

# ---------------- Registration Steps ---------------- #

# def estimate_global_homography(ref_img, float_img):
#     sift = cv2.SIFT_create()
#     kp1, des1 = sift.detectAndCompute(ref_img, None)
#     kp2, des2 = sift.detectAndCompute(float_img, None)

#     matches = cv2.BFMatcher().knnMatch(des1, des2, k=2)
#     good = [m for m, n in matches if m.distance < 0.75 * n.distance]
#     src_pts = np.float32([kp1[m.queryIdx].pt for m in good])
#     dst_pts = np.float32([kp2[m.trainIdx].pt for m in good])

#     H, _ = cv2.findHomography(dst_pts, src_pts, cv2.RANSAC, 5.0)
#     aligned = cv2.warpPerspective(float_img, H, (ref_img.shape[1], ref_img.shape[0]))
#     return aligned, H

def coarse_mesh_registration_gpu(ref_img, float_img, flow, grid_size=2):
    rows, cols = ref_img.shape
    src_cols = np.linspace(0, cols - 1, grid_size)
    src_rows = np.linspace(0, rows - 1, grid_size)
    src_rows, src_cols = np.meshgrid(src_rows, src_cols)
    src = np.dstack([src_cols, src_rows]).reshape(-1, 2)

    u, v = flow[..., 0], flow[..., 1]
    flow_at_points = np.array([
        [u[int(y), int(x)], v[int(y), int(x)]] for x, y in src
    ])
    dst = src + flow_at_points

    tform = PiecewiseAffineTransform()
    tform.estimate(src, dst)
    warped = warp(float_img, tform, output_shape=ref_img.shape)
    return warped

def fine_registration_gpu(ref_img, float_img, flow):
    u, v = flow[..., 0], flow[..., 1]
    h, w = ref_img.shape
    grid_y, grid_x = np.meshgrid(np.arange(h), np.arange(w), indexing='ij')
    map_x = (grid_x + u).astype(np.float32)
    map_y = (grid_y + v).astype(np.float32)

    warped = cv2.remap(float_img.astype(np.float32), map_x, map_y, interpolation=cv2.INTER_CUBIC)
    return warped

# ---------------- Histogram Visualization ---------------- #

def compute_histogram(image, title='Histogram'):
    if len(image.shape) == 3:
        image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    hist = cv2.calcHist([image], [0], None, [256], [0, 256]).flatten()
    plt.figure()
    plt.bar(range(256), hist, width=1.0, edgecolor='black')
    plt.title(title)
    plt.xlabel('Pixel Value')
    plt.ylabel('Frequency')
    plt.xlim([0, 255])
    plt.show()
    return hist
def augment_saturation(image):
    hsv=cv2.cvtColor(image,cv2.COLOR_BGR2HSV)
    hsv[:,:,1]= 0
    gray_bgr=cv2.cvtColor(hsv,cv2.COLOR_HSV2BGR)

    return gray_bgr


# ---------------- Main Pipeline ---------------- #        

def optical_flow_impl_gpu_parallel():
    aug=ColorAugmentation()
    img = cv2.imread('test.png')
    ref =cv2.imread('bw.png')
    augmented_ref= aug.apply_reinhard_transfer(ref, img, color_space="LAB")
    blue_c, green_c, red_c = cv2.split(img)
    blue, green, red = cv2.split(augmented_ref)



    #compute_histogram(blue, "Blue (Ref)")
    #compute_histogram(green, "Green Before")
    #compute_histogram(red, "Red Before")

    flow_engine1 = Flow(numbItterations=1, tau=1, lambda_=0.1, theta=0.06, epsilon=1e-3)
    flow_engine2 = Flow(numbItterations=1, tau=1, lambda_=0.1, theta=0.06, epsilon=1e-5)
    

    with ThreadPoolExecutor(max_workers=2) as executor:
        future_g = executor.submit(flow_engine1.compute_flow, [blue_c, green_c])
        future_r = executor.submit(flow_engine2.compute_flow, [green_c, red_c])

        flow_g = future_g.result()
        flow_r = future_r.result()
  
    #coarse registration
    coarse_g = coarse_mesh_registration_gpu(np.copy(blue_c), np.copy(green_c), flow_g)
    coarse_r = coarse_mesh_registration_gpu(np.copy(blue_c), np.copy(red_c), flow_r)
    # Fine registration
    fine_g = fine_registration_gpu(np.copy(blue_c), coarse_g, flow_g)
    fine_r = fine_registration_gpu(np.copy(blue_c), coarse_r, flow_r)

    fine_g = (fine_g * 255).clip(0, 255).astype(np.uint8)
    fine_r = (fine_r * 255).clip(0, 255).astype(np.uint8)

    #compute_histogram(fine_g, "Green After")
    #compute_histogram(fine_r, "Red After")

    cv2.imshow('Aligned Green', fine_g)
    cv2.imshow('Aligned Red', fine_r)
    cv2.imshow('Final RGB', cv2.merge([blue_c, fine_g, fine_r]))
    cv2.waitKey(0)
    cv2.destroyAllWindows()
def generate_gaussian_noisy_bgr_variants(height, width, mean=127, std=40):
        """
        Generate three noisy BGR images using Gaussian distribution 
        with one color channel set to zero in each.

        Parameters:
            height (int): Image height
            width (int): Image width
            mean (int): Mean of the normal distribution
            std (int): Standard deviation of the normal distribution

        Returns:
            tuple: Three NumPy arrays of shape (H, W, 3) in BGR format
        """
        # Generate noise with normal distribution and clip to [0, 255]
        noise = np.random.normal(loc=mean, scale=std, size=(height, width)).astype(np.float32)
        noise = np.clip(noise, 0, 255).astype(np.uint8)

        # Construct three BGR images with one zeroed channel each
        bgr_red_zero = np.stack([noise, noise, np.zeros_like(noise)], axis=2)   # Red = 0
        bgr_green_zero = np.stack([noise, np.zeros_like(noise), noise], axis=2) # Green = 0
        bgr_blue_zero = np.stack([np.zeros_like(noise), noise, noise], axis=2)  # Blue = 0

        return bgr_red_zero, bgr_green_zero, bgr_blue_zero
def isolate_channel(image, index):
    """
    Given a BGR image and a channel index (0=Blue, 1=Green, 2=Red),
    return a BGR image with only that channel and others dark.

    Parameters:
        image (np.ndarray): Input BGR image.
        index (int): Channel index to preserve (0, 1, or 2).

    Returns:
        np.ndarray: Output image with only the selected channel.
    """
    if index not in [0, 1, 2]:
        raise ValueError("Index must be 0 (Blue), 1 (Green), or 2 (Red).")
    
    # Create a zero image of same shape
    dark_image = np.zeros_like(image)

    # Copy only the selected channel
    dark_image[:, :, 0] = image[:, :, index]

    return dark_image
# ---------------- Run ---------------- #

if __name__ == "__main__":
    optical_flow_impl_gpu_parallel()
