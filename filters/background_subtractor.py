import cv2 as cv
import numpy as np

# def background_subtractor(background_image ,image):
#     fgbg = cv.bgsegm.createBackgroundSubtractorMOG()
#     fgmask = fgbg.apply(background_image)
#     fgmask = fgbg.apply(image)

#     cv.imshow('frame',fgmask)

#     return image

BG_COLOR = (255, 255, 255)


def mask_processing(image, mask):
    masked_image = cv.bitwise_and(image, image, mask=mask)

    return masked_image


def background_subtractor(image):
    fgbg = cv.bgsegm.createBackgroundSubtractorMOG()
    background_image = cv.imread("backgroung_image/backgroung_image.png", 1)
    fgmask = fgbg.apply(background_image)
    fgmask = fgbg.apply(image)

    image = mask_processing(image, fgmask)
    cv.imshow("frame", image)

    return image
