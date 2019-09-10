import cv2 as cv
import numpy as np

def gamma_ccorrection(image, gamma):
    if isinstance(image, np.ndarray) != True:
        raise Exception('not match type gamma_ccorrection!')

    # gamma = 1.5

    gamma_cvt = np.zeros((256, 1), dtype='uint8')

    for i in range(256):
        gamma_cvt[i][0] = 255 * (float(i) / 255) ** (1.0 / gamma)

    img_gamma = cv.LUT(image, gamma_cvt)

    return img_gamma