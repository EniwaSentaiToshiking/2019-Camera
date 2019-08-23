import cv2 as cv
import numpy as np
import os
import random
import string

# 初期化
# 検出する閾値
confThreshold = 0.83
nmsThreshold = 0.4
inpWidth = 416
inpHeight = 416

# VideoCapture を作成する。
camera_url = 'video/output_8_r.mp4'
# camera_url = 'http://192.168.11.100/?action=stream'
cap = cv.VideoCapture(camera_url)

# VideoWriter を作成する。
width = int(cap.get(cv.CAP_PROP_FRAME_WIDTH))
height = int(cap.get(cv.CAP_PROP_FRAME_HEIGHT))
fps = cap.get(cv.CAP_PROP_FPS)
fourcc = cv.VideoWriter_fourcc('m','p','4','v')

# Yolo関連のモデルの読み込み
modelConfiguration = "yolo/2018/yolov3.cfg"
modelWeights = "yolo/2018/yolov3.weights"

net = cv.dnn.readNetFromDarknet(modelConfiguration, modelWeights)
net.setPreferableBackend(cv.dnn.DNN_BACKEND_OPENCV)
net.setPreferableTarget(cv.dnn.DNN_TARGET_CPU)

# クラス名の読み込み
classesFile = "yolo/2018/learning.names"
classes = None
with open(classesFile, 'rt') as f:
    classes = f.read().rstrip('\n').split('\n')

# uuidだと長いから
def random_string(length, seq=string.digits + string.ascii_lowercase):
    sr = random.SystemRandom()
    return ''.join([sr.choice(seq) for i in range(length)])

# 画像のリサイズ
def resize(image):
    height = image.shape[0]
    width = image.shape[1]
    # 600 * 600 未満にしたい（理想は多分416*416）0.5は1280*720基準
    resized_image = cv.resize(image , (int(width*0.5), int(height*0.5)))

    return resized_image

# レイヤーの出力名を取得する
def getOutputsNames(net):
    layersNames = net.getLayerNames()
    return [layersNames[i[0] - 1] for i in net.getUnconnectedOutLayers()]

# 前フレームの描画情報を削除し，新しい描画情報に置き換える
def postprocess(nonBB_image, frame, outs):
    frameHeight = frame.shape[0]
    frameWidth = frame.shape[1]
    classIds = []
    confidences = []
    boxes = []

    for out in outs:
        for detection in out:
            scores = detection[5:]
            classId = np.argmax(scores)
            confidence = scores[classId]
            if confidence > confThreshold:
                center_x = int(detection[0] * frameWidth)
                center_y = int(detection[1] * frameHeight)
                width = int(detection[2] * frameWidth)
                height = int(detection[3] * frameHeight)
                left = int(center_x - width / 2)
                top = int(center_y - height / 2)
                classIds.append(classId)
                confidences.append(float(confidence))
                boxes.append([left, top, width, height])

    indices = cv.dnn.NMSBoxes(boxes, confidences, confThreshold, nmsThreshold)
    # かぶらないかぶらないファイル名を生成するため
    random_path_name = random_string(10)
    save_root_path = "annotation_images/"

    # Yoloで出力されるボックスの位置を出す
    for i in indices:
        i = i[0]
        box = boxes[i]
        left = box[0]
        top = box[1]
        width = box[2]
        height = box[3]
        # 画像とtxtのファイル名
        filename = random_path_name + '_' + str(classes[classIds[i]])
        # クラス名ごとにフォルダを生成する
        save_path = save_root_path + '/' + str(classes[classIds[i]])

        if not os.path.exists(save_root_path):
            os.mkdir(save_root_path)
        if not os.path.exists(save_path):
            os.mkdir(save_path)

        try:
            cv.imwrite(save_path + '/' + filename + '.jpg', nonBB_image)
            # BBtoolsと同じ形式に
            annotation = '1\n' + str(left) + ' ' + str(top) + ' ' + str(left + width) + ' ' + str(top + height) 
            with open(save_path + '/' + filename + '.txt', mode='w') as f:
                f.write(annotation)
            drawPred(classIds[i], confidences[i], left, top, left + width, top + height, frame, save_path, filename)
        except Exception as e:
            print(e)

# 該当するブロックを四角で囲み，ラベルを付ける
def drawPred(classId, conf, left, top, right, bottom, frame, save_root_path, filename):
    # Draw a bounding box.
    cv.rectangle(frame, (left, top), (right, bottom), (255, 178, 50), 3)

    label = '%.2f' % conf
    if classes:
        assert (classId < len(classes))
        label = '%s:%s' % (classes[classId], label)

    # Display the label at the top of the bounding box
    print(label)
    labelSize, baseLine = cv.getTextSize(label, cv.FONT_HERSHEY_SIMPLEX, 0.5, 1)
    top = max(top, labelSize[1])
    cv.rectangle(frame, (left, top - round(1.5 * labelSize[1])), (left + round(1.5 * labelSize[0]), top + baseLine),
                 (255, 255, 255), cv.FILLED)
    cv.putText(frame, label, (left, top), cv.FONT_HERSHEY_SIMPLEX, 0.75, (0, 0, 0), 1)

    save_path = save_root_path + '/' + 'BBimages'
    if not os.path.exists(save_path):
        os.mkdir(save_path)

    try:
        cv.imwrite(save_path + '/' + filename + '.jpg', frame)
    except Exception as e:
        print(e)

# 録画周りの変数
frame_count = 0
record_flag = False

while True:
    # ビデオ情報の読み込み
    hasFrame, frame = cap.read()

    if not hasFrame:
        print("エラー：ビデオカメラの情報がありません")
        cv.waitKey(3000)
        break  # 映像取得に失敗
    
    # 8フレームごとに行う
    if frame_count % 8 == 0:
        # 保存用にBBなしの画像を保持する
        nonBB_image = resize(frame)
        frame = resize(frame)
        blob = cv.dnn.blobFromImage(frame, 1 / 255, (inpWidth, inpHeight), [0, 0, 0], 1, crop=False)
        net.setInput(blob)
        outs = net.forward(getOutputsNames(net))
        postprocess(nonBB_image, frame, outs)
    frame_count+=1

    cv.imshow('Frame', frame)

    # ボタン押下時のイベント作成
    key = cv.waitKey(1) & 0xff
    # システム終了
    if key == ord('q'):
        cv.destroyAllWindows()

cap.release()