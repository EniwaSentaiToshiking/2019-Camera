# -*- coding: UTF-8 -*- 
 
import cv2 as cv
import math 
import numpy as np

# nフレームの平均画像を作成して，フリッカーノイズ対策をする
# 一度保存してあげないと何かが合わなくて，blobFromImageの中でエラー吐いた
def create_average_image(images):
    length = len(images)
    average_image = np.empty(1)
    for index, image in enumerate(images):
        if index == 0:
            average_image = image / length
        else:
            average_image += image / length
    
    cv.imwrite('average_image/ave_image.jpg', average_image)
    average_image = cv.imread("average_image/ave_image.jpg", 1)
    return average_image