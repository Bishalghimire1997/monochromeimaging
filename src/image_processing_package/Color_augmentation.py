import cv2
import numpy as np
from skimage import color
from PIL import Image
import os
class ColorAugmentation:
    def get_avg_std(self,image):
        avg = np.mean(image, axis=(0, 1))
        std = np.std(image, axis=(0, 1))
        return avg, std

    def apply_reinhard_transfer(self,source, target, color_space="LAB"):
        if color_space == "LAB":
            source = cv2.cvtColor(source, cv2.COLOR_BGR2LAB)
            target = cv2.cvtColor(target, cv2.COLOR_BGR2LAB)
        elif color_space == "HSV":
            source = cv2.cvtColor(source, cv2.COLOR_BGR2HSV)
            target = cv2.cvtColor(target, cv2.COLOR_BGR2HSV)
        elif color_space == "HED":
            source = cv2.cvtColor(source, cv2.COLOR_BGR2RGB)
            target = cv2.cvtColor(target, cv2.COLOR_BGR2RGB)
            source = color.rgb2hed(source)
            target = color.rgb2hed(target)
        else:
            raise ValueError("Unsupported color space")

    # Get means and stds
        source_avg, source_std = self.get_avg_std(source)
        target_avg, target_std = self.get_avg_std(target)

    # Perform Reinhard normalization
        result = (target - target_avg) * (source_std / target_std) + source_avg

    # Convert back to uint8
        if color_space == "HED":
            result = color.hed2rgb(result)
            result = (255 * (result - result.min()) / (result.max() - result.min())).astype(np.uint8)
            return cv2.cvtColor(result, cv2.COLOR_RGB2BGR)
        else:
           result = np.clip(result, 0, 255).astype(np.uint8)
           if color_space == "LAB":
                return cv2.cvtColor(result, cv2.COLOR_LAB2BGR)
           elif color_space == "HSV":
                return cv2.cvtColor(result, cv2.COLOR_HSV2BGR)


