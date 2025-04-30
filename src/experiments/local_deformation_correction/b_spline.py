# Non-Rigid Image Registration (Simplified Implementation of Multi-level Deformable Model)

import cv2
from matplotlib import pyplot as plt
import numpy as np
from h5_file_format_package.h5_format import H5FormatRead
from skimage.transform import PiecewiseAffineTransform, warp
import SimpleITK as sitk
from scipy.interpolate import RectBivariateSpline
from skimage import img_as_float
from skimage.registration import optical_flow_tvl1

# Step 1: Global Homography Registration using SIFT + RANSAC

def estimate_global_homography(ref_img, float_img):
    sift = cv2.SIFT_create()
    kp1, des1 = sift.detectAndCompute(ref_img, None)
    kp2, des2 = sift.detectAndCompute(float_img, None)

    bf = cv2.BFMatcher()
    matches = bf.knnMatch(des1, des2, k=2)
    good_matches = []
    for m, n in matches:
        if m.distance < 0.75 * n.distance:
            good_matches.append(m)

    src_pts = np.float32([kp1[m.queryIdx].pt for m in good_matches])
    dst_pts = np.float32([kp2[m.trainIdx].pt for m in good_matches])

    H, mask = cv2.findHomography(dst_pts, src_pts, cv2.RANSAC, 5.0)
    aligned = cv2.warpPerspective(float_img, H, (ref_img.shape[1], ref_img.shape[0]))
    return aligned, H

# Step 2: Coarse Local Registration using Piecewise Affine Mesh (Simplified)
def coarse_mesh_registration(ref_img, float_img, grid_size=2):
    rows, cols = ref_img.shape
    src_cols = np.linspace(0, cols, grid_size)
    src_rows = np.linspace(0, rows, grid_size)
    src_rows, src_cols = np.meshgrid(src_rows, src_cols)
    src = np.dstack([src_cols.flat, src_rows.flat])[0]

    v, u = optical_flow_tvl1(np.copy(ref_img), np.copy(float_img))
    dst = src + np.stack([u.flat, v.flat], axis=-1)[:src.shape[0]]

    tform = PiecewiseAffineTransform()
    tform.estimate(src, dst)
    warped = warp(float_img, tform, output_shape=ref_img.shape)
    return warped


# Step 3: Fine Registration using B-Spline-like Interpolation (Simplified Optical Flow)
def fine_registration(ref_img, float_img):
     
        # frame1 = cv2.cuda_GpuMat()
        # frame2 = cv2.cuda_GpuMat()
        # frame1.upload(ref_img.astype(np.float32))
        # frame2.upload(warped.astype(np.float32))
        # tvl1 = cv2.cuda.OpticalFlowDual_TVL1.create()
        # flow = tvl1.calc(frame1, frame2, None)
        # flow = flow.download()
        # u = flow[..., 0]
        # v = flow[..., 1]
        v, u = optical_flow_tvl1(ref_img, float_img)
        nr, nc = ref_img.shape
        row_coords, col_coords = np.meshgrid(np.arange(nr), np.arange(nc), indexing='ij')
        warped = cv2.remap(float_img.astype(np.float32),
                       (col_coords + u).astype(np.float32),
                       (row_coords + v).astype(np.float32),
                       interpolation=cv2.INTER_LINEAR)
        #computing the histogram of the orginal image 


        return warped

def optical_flow_impl():
    img = cv2.imread('test.png')
    ref = img[:, :, 0]  # Reference image (first channel)
    compute_histogram(ref,"ref")
    print(ref.shape)
    print(ref.dtype)
    floating1 = img[:, :, 1]  # Floating image (second channel)
    compute_histogram(floating1,"green_before")
    floating2 = img[:, :, 2]  # Floating image (third channel)
    compute_histogram(floating2,"red_before")
    cv2.imshow('ref', ref)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

    aligned_global1, H1 = estimate_global_homography(ref, floating1)
    aligned_global2, H2 = estimate_global_homography(ref, floating2)

    aligned_coarse1 = coarse_mesh_registration(np.copy(ref), np.copy(aligned_global1))
    aligned_coarse2 = coarse_mesh_registration(np.copy(ref), np.copy(aligned_global2))

    aligned_fine1 = fine_registration(ref, aligned_coarse1)
    aligned_fine2 = fine_registration(ref, aligned_coarse2)
    aligned_fine1 =  (aligned_fine1 * 255).clip(0, 255).astype(np.uint8)
    aligned_fine2 = (aligned_fine2 * 255).clip(0, 255).astype(np.uint8)
    compute_histogram(aligned_fine1,"green_after")
    compute_histogram(aligned_fine2,"red_after")

    
    cv2.imshow('aligned_coarse1', aligned_coarse1)
    cv2.imshow('aligned_coarse2', aligned_coarse2)
    cv2.imshow('aligned_fine1', aligned_fine1)
    cv2.imshow('aligned_fine2', aligned_fine2)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

    img =cv2.merge([ref, aligned_fine1, aligned_fine2])
    cv2.imshow('aligned_fine', img)
    cv2.waitKey(0)
    cv2.destroyAllWindows()


def compute_histogram(image,title = 'Grayscale Histogram'):
    # Convert the image to grayscale if it is not already
    if len(image.shape) == 3:
        image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    hist = cv2.calcHist([image], [0], None, [256], [0, 256])
    hist = hist.flatten()
    # Compute the histogram
    plt.figure()
    plt.bar(range(256), hist, width=1.0, edgecolor='black')  # <- this draws distinct bars
    plt.title(title)
    plt.xlabel('Pixel Value')
    plt.ylabel('Frequency')
    plt.xlim([0, 255])  # Pixel values between 0-255
    plt.show()

    return hist

if __name__ == "__main__":
    # img = cv2.imread('test.png')
    # ref = img[:, :, 0]  # Reference image (first channel)
    # floating1 = img[:, :, 1]  # Floating image (second channel)
    # floating2 = img[:, :, 2]  # Floating image (third channel)
    # g=coarse_mesh_registration_sift(ref, floating1)
    # r =coarse_mesh_registration_sift(ref, floating2)
    # g_im =  (g * 255).clip(0, 255).astype(np.uint8)
    # r_im =  (r * 255).clip(0, 255).astype(np.uint8)
    # img = cv2.merge([ref, g_im, r_im])
    # cv2.imshow('aligned_fine', img)
    # cv2.waitKey(0)  
    optical_flow_impl()


    