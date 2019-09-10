import cv2 as cv

def equalize_hist_color(image):
    # YCbCrに変換してYを取りたい
    image_yuv = cv.cvtColor(image, cv.COLOR_BGR2YUV)
    # ヒストグラム平坦化
    image_yuv[:,:,0] = cv.equalizeHist(image_yuv[:,:,0])
    # BRGに戻す
    image = cv.cvtColor(image_yuv, cv.COLOR_YUV2BGR)

    return image