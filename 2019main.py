import cv2 as cv
import numpy as np
import os
import copy

from average_image import *
from yolo import *
from filters.equalize_hist_color import *
from filters.gamma_ccorrection import *
from calibration import Calibration, State
from filters.unsharp_masking import *
from filters.background_subtractor import *

# VideoCapture を作成する。
# camera_url = 'video/pre2/output2_bad.mp4'
# camera_url = 'http://192.168.11.100/?action=stream'
# R
camera_url = "http://169.254.16.205/?action=stream"
# L
# camera_url = 'http://169.254.161.93/?action=stream'


# VideoCapture を作成する。
# camera_url = "output7.mp4"

cap = cv.VideoCapture(camera_url)

# VideoWriter を作成する。
width = int(cap.get(cv.CAP_PROP_FRAME_WIDTH))
height = int(cap.get(cv.CAP_PROP_FRAME_HEIGHT))
fps = cap.get(cv.CAP_PROP_FPS)
fourcc = cv.VideoWriter_fourcc("m", "p", "4", "v")

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
yolo_number = YOLO(
    number_model_cfg_pass, number_model_weiight_pass, number_model_names_pass, 0.1
)

# 録画周りの変数
frame_count = 0
record_flag = False
# 平均画像を作るようの配列
images = []

# 取得動画からサークルの座標を取得することに関するクラス
calibration = Calibration()

winName = calibration.winName

# 描画を行う上での初期設定
calibration.make_window()
frame_count = 1

while True:
    # ビデオ情報の読み込み
    hasFrame, frame = cap.read()

    if not hasFrame:
        print("エラー：ビデオカメラの情報がありません")
        cv.waitKey(3000)
        break  # 映像取得に失敗

    # if frame_count == 0:
    #     cv.imwrite("backgroung_image/backgroung_image.png", frame)

    if frame_count < 10:
        images.append(frame)
        # copy.deepcopy()を使って値渡しにしないと，打った点が検出の邪魔になる
        calibration.draw_click_points(copy.deepcopy(frame))

    # 10フレームごとに行う
    if frame_count == 10:
        input_image = create_average_image(images)
        # 最後の微調整用
        for_adjustment_iamge = copy.deepcopy(input_image)
        # 処理能力が足りないと詰むので
        # if input_image == None:
        #     input_image = frame
        input_image = equalize_hist_color(input_image)
        # input_image = gamma_ccorrection(input_image, 0.8)
        # input_image = unsharp_masking(input_image)
        # input_image = background_subtractor(input_image)

        # カラーブロック
        drawed_image, object_models = yolo.postprocess(input_image)
        deduplication_object_models = yolo.deduplication(object_models)

        # for hoge in deduplication_object_models:
        #     img = hoge.clip_image
        #     label = hoge.label
        #     try:
        #         print(label, img[int(img.shape[0] * 0.5), int(img.shape[1] * 0.5)])
        #     except Exception as e:
        #         print(e)

        fixed_color_object_models = yolo.fix_color(deduplication_object_models)

        # ボーナスナンバー
        _, number_models = yolo_number.postprocess(input_image)
        deduplication_number_models = yolo_number.deduplication(number_models)

        for number_model in number_models:
            frame = yolo_number.draw_BBBox(frame, number_model)

        for fixed_color_object_model in fixed_color_object_models:
            frame = yolo.draw_BBBox(frame, fixed_color_object_model)

        # copy.deepcopy()を使って値渡しにしないと，打った点が検出の邪魔になる
        calibration.draw_click_points(copy.deepcopy(frame))

        # 平均画像周り
        frame_count = -1
        images.clear()

        # yoloの結果とcalibrationのstateから判断して，対応付に向かう
        if len(fixed_color_object_models) > 8 and calibration.state == State.wait_yolo:
            color_object_models = copy.deepcopy(fixed_color_object_models)
            print("try association")
            calibration.state = State.in_association
            for color_object_model in color_object_models:
                calibration.association(color_object_model)

            if len(fixed_color_object_models) != 10:
                calibration.state = State.in_adjustment
                calibration.adjustment(for_adjustment_iamge)
            else:
                calibration.state = State.finish

            for i, hoge in enumerate(calibration.intersection_circle_positions):
                if hoge.model == None:
                    print("none", i)
                else:
                    print(i, hoge.model.label)

            for i, hoge in enumerate(calibration.block_circle_positions):
                if hoge.model == None:
                    print("none", i)
                else:
                    print(i, hoge.model.label)

    frame_count += 1

    cv.setMouseCallback(winName, calibration.click_point)

    # ボタン押下時のイベント作成
    key = cv.waitKey(1) & 0xFF

    # 録画開始
    if key == ord("r"):
        writer = cv.VideoWriter("output.mp4", fourcc, fps, (width, height))
        record_flag = True
    if record_flag:
        writer.write(frame)
    # 録画終了
    if key == ord("s"):
        writer.release()
    if key == ord("f"):
        calibration.finish_display_click_point()
    if key == ord("c"):
        calibration.clear_display_click_point()
    # システム終了
    if key == ord("q"):
        cv.destroyAllWindows()

cap.release()
