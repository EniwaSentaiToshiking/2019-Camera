#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# usage: ./increase_picture.py hogehoge.jpg
#

import cv2
import numpy as np
import sys
import os
from shutil import copyfile
from PIL import Image

# ヒストグラム均一化
def equalizeHistRGB(src):
    
    RGB = cv2.split(src)
    Blue   = RGB[0]
    Green = RGB[1]
    Red    = RGB[2]
    for i in range(3):
        cv2.equalizeHist(RGB[i])

    img_hist = cv2.merge([RGB[0],RGB[1], RGB[2]])
    return img_hist

# ガウシアンノイズ
def addGaussianNoise(src):
    row,col,ch= src.shape
    mean = 0
    var = 0.1
    sigma = 15
    gauss = np.random.normal(mean,sigma,(row,col,ch))
    gauss = gauss.reshape(row,col,ch)
    noisy = src + gauss
    
    return noisy

def main(data_dir, file_name, class_num, class_name, out_dir):
    # ルックアップテーブルの生成
    min_table = 50
    max_table = 205
    diff_table = max_table - min_table
    gamma = 10
    
    LUT_HC = np.arange(256, dtype = 'uint8' )
    LUT_LC = np.arange(256, dtype = 'uint8' )
    
    LUTs = []
    
    # 平滑化用
    average_square = (10,10)
    
    # ハイコントラストLUT作成
    for i in range(0, min_table):
        LUT_HC[i] = 0
    
    for i in range(min_table, max_table):
        LUT_HC[i] = 255 * (i - min_table) / diff_table
    
    for i in range(max_table, 255):
        LUT_HC[i] = 255
    
    # その他LUT作成
    for i in range(256):
        LUT_LC[i] = min_table + i * (diff_table) / 255
    
    LUTs.append(LUT_HC)
    LUTs.append(LUT_LC)

    # ガンマ補正
    for index in range(7, 16):
        LUT_G = np.arange(256, dtype = 'uint8' )
        for i in range(256):
            LUT_G[i] = 255 * pow(float(i) / 255, 1.0 / (index/gamma))
        LUTs.append(LUT_G)

    # 画像の読み込み
    img_src = cv2.imread(
        "{0}/rotation_images/{1}/{2}".format(data_dir, class_num, file_name), 1)
    trans_img = []

    # LUT変換
    for i, LUT in enumerate(LUTs):
        trans_img.append( cv2.LUT(img_src, LUT))

    # 平滑化      
    trans_img.append(cv2.blur(img_src, average_square))      

    # ヒストグラム均一化
    trans_img.append(equalizeHistRGB(img_src))

    # ノイズ付加
    trans_img.append(addGaussianNoise(img_src))

    # 保存
    base = os.path.splitext(os.path.basename(file_name))[0] + "_"
    img_src.astype(np.float64)

    for i, img in enumerate(trans_img):
        if not os.path.exists("{0}/{1}/{2}".format(data_dir, out_dir, class_name)):
            os.makedirs("{0}/{1}/{2}".format(data_dir, out_dir, class_name))
        if not os.path.exists("{0}/final_labels/{1}".format(data_dir, class_name)):
            os.makedirs("{0}/final_labels/{1}".format(data_dir, class_name))
        new_file_name = base + str(i)
        text_file_name = file_name.replace(".jpg", ".txt")
        cv2.imwrite(
            "{0}/{1}/{2}/{3}".format(data_dir, out_dir, class_name, new_file_name + ".jpg"), img)
        copyfile("{0}/inflated_labels/{1}/{2}".format(data_dir, class_num, text_file_name),
                     "{0}/final_labels/{1}/{2}".format(data_dir, class_name, new_file_name + ".txt"))

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("please set data directory path.")
        print("python inflate_images.py [input_dir] [out_dir]")
        exit(-1)

    # 増幅するフォルダ名の決定
    out_dir = "dataset"
    if len(sys.argv) > 2:
        out_dir = sys.argv[2]

    data_dir = sys.argv[1]

    # クラス名のファイルの読み込み
    classes = []
    classes = [line.rstrip() for line in open('{0}/classes.txt'.format(data_dir), 'r')]

    print('class name = ', end='')
    for i in classes:
        print(i, end=' ')
    print("")

    for _, dirs, _ in os.walk("{0}/rotation_images/".format(data_dir)):
        for class_name in classes:
            for class_num in dirs:
                if class_num == class_name:
                    print("{0}/rotation_images/{1}".format(data_dir, class_name))
                    for _, _, files in os.walk("{0}/rotation_images/{1}".format(data_dir, class_num)):
                        for file_name in files:
                            try:
                                main(data_dir, file_name, class_num, class_name, out_dir)
                            except:
                                continue