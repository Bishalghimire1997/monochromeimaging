from image_processing_package.Color_augmentation import ColorAugmentation
import cv2
def test_color_augmentation():
    boaring = cv2.imread("boaring_sunset.PNG")
    cv2.imshow('boaring', boaring)
    cv2.waitKey(0)
    interesting1 = cv2.imread("interesting_sunset.PNG")
    cv2.imshow('interesting1', interesting1)
    cv2.waitKey(0)
    ca = ColorAugmentation()

    interesting2 = cv2.imread("int1.PNG")
    cv2.imshow('interesting2', interesting2)
    cv2.waitKey(0)
    ca = ColorAugmentation()
    # Apply Reinhard transfer in LAB color space
    augmented_image1 = ca.apply_reinhard_transfer(interesting1, boaring, color_space="LAB")
    augmented2 = ca.apply_reinhard_transfer(interesting2, boaring, color_space="LAB")
    cv2.imshow('Augmented Image1', augmented_image1)
    cv2.waitKey(0)
    cv2.imshow('Augmented Image2', augmented2)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
if __name__ == "__main__":
    test_color_augmentation()