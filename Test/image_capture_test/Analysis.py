# -*- coding: utf-8 -*-
"""
Created on Thu Oct  9 16:51:43 2025

@author: Steven Blair
"""

import numpy as np
import matplotlib.pyplot as plt

import h5py
from skimage import color
from skimage import filters

#%%


def scale_brightness(n_frames,ref_img):

    target_mean = np.mean(ref_img,axis = (0,1))
    print("Target Mean =",target_mean)
    print("atrget_img.shape:", n_frames.shape)
    ref_mean = np.mean(n_frames,axis =(1,2))
    print("ref_mean = ",ref_mean)
    scaling_f = target_mean/ref_mean
    
    scaling_arr = scaling_f[:,None,None,:]
    scaled = n_frames * scaling_arr
    scaled = scaled.astype(np.uint8)
    scaled_mean = np.mean(scaled,axis = (1,2))
    print("scaled mean = ",scaled_mean)
    print("Scaling_factor = ",scaling_f)
    return scaled


def get_images(filename, n_frames=None, *, flip=False, i_start=30):
    with h5py.File(filename, 'r') as file:
        keys = file.keys()
        keys = [int(key) for key in keys]
        keys.sort()
        keys = [str(key) for key in keys]
        
        if n_frames is not None:
            keys = keys[i_start:i_start+n_frames]
            if len(keys) < n_frames:
                raise IndexError("File does not contain n_frames frames")
        
        frames = np.stack([np.array(file[key]) for key in keys], axis=0)
    
    if flip:
        frames = np.flip(frames, axis=-1)    
    return frames

#%%

filename = 'image_indoor_fl_1000.h5'
n_frames = 10

images = get_images(filename, n_frames, flip=True)
dtype = images.dtype
images = filters.gaussian(images, (0,1,1,0), preserve_range=True).astype(dtype)
ref_image = np.mean(images.copy(),axis =0)
for i in range (20):
    images = scale_brightness(images,ref_image)
image_avg = images[9]#np.mean(images, axis=0).astype(dtype) 

#%%

plt.figure()
plt.imshow(image_avg)
plt.show()

plt.figure()
for i in range(0, n_frames):
    plt.subplot(2,n_frames//2,i+1)
    plt.imshow(images[i,...])
plt.show()

# plt.figure()
# plt.plot(np.mean(images, axis=(1,2)))
# plt.show()

channel_means =np.mean(images,axis=(1,2))

plt.figure()
plt.plot(channel_means[:, 0], color='b', label='Blue')
plt.plot(channel_means[:, 1], color='g', label='Green')
plt.plot(channel_means[:, 2], color='r', label='Red')
plt.xlabel("Image Index")
plt.ylabel("Mean Intensity")
plt.legend()
plt.title("Mean Intensity per Channel")
plt.show()

#%%

offset = np.mean(images, axis=(0,1,2))
noise = np.std(images, axis=(0,1,2), ddof=1)

#%%

print(f'Offset (R): {offset[0]:.2} DN\t| Offset (G): {offset[1]:.2} DN\t| Offset (B): {offset[2]:.2} DN')
print(f'Noise  (R): { noise[0]:.2} DN\t| Noise  (G): { noise[1]:.2} DN\t| Noise  (B): { noise[2]:.2} DN')

log = True

plt.figure(figsize=(6.4,7.2))
plt.subplot(311)
plt.hist(images[...,0].reshape(-1), bins=np.linspace(0, 255, 256), log=log, color='red')
plt.axvline(offset[0], linestyle='--', color='k')
plt.title(f'Red Channel (Offset: {offset[0]:.2} DN & Noise: { noise[0]:.2} DN)')
plt.xlabel('Digital Number (DN)')
plt.ylabel('Count')
plt.subplot(312)
plt.hist(images[...,1].reshape(-1), bins=np.linspace(0, 255, 256), log=log, color='green')
plt.axvline(offset[1], linestyle='--', color='k')
plt.title(f'Green Channel (Offset: {offset[1]:.2} DN & Noise: { noise[1]:.2} DN)')
plt.xlabel('Digital Number (DN)')
plt.ylabel('Count')
plt.subplot(313)
plt.hist(images[...,2].reshape(-1), bins=np.linspace(0, 255, 256), log=log, color='blue')
plt.axvline(offset[2], linestyle='--', color='k')
plt.title(f'Blue Channel (Offset: {offset[2]:.2} DN & Noise: { noise[2]:.2} DN)')
plt.xlabel('Digital Number (DN)')
plt.ylabel('Count')
plt.tight_layout()
plt.show()

#%%

images_xyz = color.rgb2xyz(images) 
images_lab = color.xyz2lab(images_xyz) 
image_avg_xyz = color.rgb2xyz(image_avg)
image_avg_lab = color.xyz2lab(image_avg_xyz)


deltaEs = [color.deltaE_ciede2000(image_avg_lab, image_lab) for image_lab in images_lab]
deltaEs = np.stack(deltaEs, axis=0)

print(f"Delta E = {deltaEs.copy().mean(axis = (1,2))}")

deltaE_avg = np.mean(deltaEs)
deltaE_std = np.std(deltaEs, ddof=1)

#%%

print(f'Mean Delta E: {deltaE_avg:.3} | SD Delta E: {deltaE_std:.3}')

log = True

plt.figure()
plt.hist(np.mean(deltaEs, axis=0).reshape(-1), bins=100, log=log, color='grey')
plt.axvline(deltaE_avg, linestyle='--', color='k')
plt.title(f'Mean Delta E: {deltaE_avg:.3} | SD Delta E: {deltaE_std:.3}')
plt.xlabel('Delta E')
plt.ylabel('Count')
plt.tight_layout()
plt.show()

plt.figure()
plt.imshow(np.mean(deltaEs, axis=0))
plt.colorbar()
plt.tight_layout()
plt.show()


    

