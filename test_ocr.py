import cv2 as cv
import numpy as np
import os
import ulid
from PIL import Image
import pyocr
import pyocr.builders

# VideoCapture を作成する。
camera_url = 'http://192.168.11.100/?action=stream'
cap = cv.VideoCapture(camera_url)

# VideoWriter を作成する。
width = int(cap.get(cv.CAP_PROP_FRAME_WIDTH))
height = int(cap.get(cv.CAP_PROP_FRAME_HEIGHT))
fps = cap.get(cv.CAP_PROP_FPS)
fourcc = cv.VideoWriter_fourcc('m','p','4','v')

# 録画周りの変数
frame_count = 0
record_flag = False

# OCR Setup
tools = pyocr.get_available_tools()

def cv2pil(image):
    ''' OpenCV型 -> PIL型 '''
    new_image = image.copy()
    if new_image.ndim == 2:  # モノクロ
        pass
    elif new_image.shape[2] == 3:  # カラー
        new_image = cv.cvtColor(image, cv.COLOR_BGR2RGB)
    elif new_image.shape[2] == 4:  # 透過
        new_image = cv.cvtColor(image, cv.COLOR_BGRA2RGBA)
    new_image = Image.fromarray(new_image)
    return new_image

def exportResult(frame, txt):
    save_root_path = "result/ocr/" + ulid.new().str
    if not os.path.exists(save_root_path):
        os.mkdir(save_root_path)
        result_txt = open(save_root_path + '/' + 'result.txt','a')
        try:
            cv.imwrite(save_root_path + '/' + 'root' + '.png', frame)
            result_txt.write(str(txt) + '\n')
        except Exception as e:
            print(e)
        result_txt.close()

while True:
    # ビデオ情報の読み込み
    hasFrame, frame = cap.read()

    if not hasFrame:
        print("エラー：ビデオカメラの情報がありません")
        cv.waitKey(3000)
        break  # 映像取得に失敗
    
    # 8フレームごとに行う
    if frame_count % 8 == 0:
        try:
            tool = tools[0]
            txt = tool.image_to_string(
            cv2pil(frame),
            lang="eng",
            builder=pyocr.builders.TextBuilder()
            )
            if txt != "":
                exportResult(frame, txt)
        except Exception as e:
            print("aa",e)
    frame_count+=1

    cv.imshow('Frame', frame)
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