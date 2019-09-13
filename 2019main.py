import cv2 as cv
import numpy as np
import os

from average_image import *
from yolo import *
from filters.equalize_hist_color import *
from filters.gamma_ccorrection import *
from GUI import GUI

# VideoCapture を作成する。
camera_url = 'output7.mp4'
# camera_url = 'http://192.168.11.100/?action=stream'
# R
# camera_url = 'http://169.254.16.205/?action=stream'
# L
# camera_url = 'http://169.254.161.93/?action=stream'

cap = cv.VideoCapture(camera_url)

# VideoWriter を作成する。
width = int(cap.get(cv.CAP_PROP_FRAME_WIDTH))
height = int(cap.get(cv.CAP_PROP_FRAME_HEIGHT))
fps = cap.get(cv.CAP_PROP_FPS)
fourcc = cv.VideoWriter_fourcc('m','p','4','v')

# カラーブロック
block_model_cfg_pass = "yolo/2018/yolov3.cfg"
block_model_weiight_pass = "yolo/2018/yolov3.weights"
# block_model_cfg_pass = "yolo/0905/etrobo2019_block.cfg"
# block_model_weiight_pass = "yolo/0905/etrobo2019_block_1100.weights"
block_model_names_pass = "yolo/0905/learning.names"
yolo = YOLO(block_model_cfg_pass, block_model_weiight_pass, block_model_names_pass, 0.1)

# ボーナスナンバー
number_model_cfg_pass = "yolo/0830/etrobo2019_number.cfg"
number_model_weiight_pass = "yolo/0830/etrobo2019_number_820.weights"
number_model_names_pass = "yolo/0830/learning.names"
yolo_number = YOLO(number_model_cfg_pass, number_model_weiight_pass, number_model_names_pass, 0.1)

# 録画周りの変数
frame_count = 0
record_flag = False
# 平均画像を作るようの配列
images = []

# 取得動画からサークルの座標を取得することに関するクラス
GUI = GUI()

winName = GUI.winName

# 描画を行う上での初期設定
GUI.make_window()
frame_count = 1

while True:
    # ビデオ情報の読み込み
    hasFrame, frame = cap.read()
    original_frame = frame

    if not hasFrame:
        print("エラー：ビデオカメラの情報がありません")
        cv.waitKey(3000)
        break  # 映像取得に失敗

    if frame_count < 10:
        images.append(frame)

    # 4フレームごとに行う
    if frame_count == 10:
        # input_image = create_average_image(images) 
        # input_image = gamma_ccorrection(input_image, 1.5) 
        # input_image = equalize_hist_color(input_image)
        input_image = equalize_hist_color(frame)  

        GUI.display_click_point(frame)

        # カラーブロック
        drawed_image, object_models = yolo.postprocess(input_image)
        deduplication_object_models = yolo.deduplication(object_models)
        fixed_color_object_models = yolo.fix_color(deduplication_object_models)

        # ボーナスナンバー
        _, number_models = yolo_number.postprocess(input_image)
        deduplication_number_models = yolo_number.deduplication(number_models)

        for hoge in number_models:
            original_frame = yolo_number.debugDraw(original_frame, hoge)

        for hoge in fixed_color_object_models:
            # print(i.label)
            original_frame = yolo.debugDraw(original_frame, hoge)
        # print("---------")

        GUI.create_trackbar(frame)
        cv.imshow(winName, original_frame)
        # 平均画像周り
        frame_count = -1
        images.clear()
    frame_count+=1

    cv.setMouseCallback(winName, GUI.mouse_event, [winName, frame])

    # ボタン押下時のイベント作成
    key = cv.waitKey(1) & 0xff

    # 録画開始
    if key == ord('r'):
        writer = cv.VideoWriter('output.mp4', fourcc, fps, (width, height))
        record_flag = True
    if record_flag:
        writer.write(frame)
    # 録画終了
    if key == ord('s'):
        writer.release()
    # システム終了
    if key == ord('q'):
        cv.destroyAllWindows()

cap.release()