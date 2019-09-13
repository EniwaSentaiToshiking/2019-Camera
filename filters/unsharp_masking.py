import cv2 as cv
import numpy as np

def unsharp_masking(image):
    # 4近傍
    # kernel = np.array([[-1,-1,-1], [-1,9,-1], [-1,-1,-1]], np.float32)
    # 8近傍
    kernel = np.array([[0,-1,0], [-1,5,-1], [0,-1,0]], np.float32)
    dst = cv.filter2D(image, -1, kernel)

    return  dst