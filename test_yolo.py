import cv2 as cv
import numpy as np
# import ulid
import os

# 初期化
confThreshold = 0.6
nmsThreshold = 0.4
inpWidth = 416
inpHeight = 416

# VideoCapture を作成する。
# camera_url = 'video/output_1_a.mp4'
camera_url = 'http://192.168.11.100/?action=stream'
cap = cv.VideoCapture(camera_url)

# VideoWriter を作成する。
width = int(cap.get(cv.CAP_PROP_FRAME_WIDTH))
height = int(cap.get(cv.CAP_PROP_FRAME_HEIGHT))
fps = cap.get(cv.CAP_PROP_FPS)
fourcc = cv.VideoWriter_fourcc('m','p','4','v')

# Yolo関連のモデルの読み込み
modelConfiguration = "yolo/learning_v1.cfg"
modelWeights = "yolo/learning_26000.weights"

net = cv.dnn.readNetFromDarknet(modelConfiguration, modelWeights)
net.setPreferableBackend(cv.dnn.DNN_BACKEND_OPENCV)
net.setPreferableTarget(cv.dnn.DNN_TARGET_CPU)

# クラス名の読み込み
classesFile = "yolo/learning_v1.names"
classes = None
with open(classesFile, 'rt') as f:
    classes = f.read().rstrip('\n').split('\n')

# ブロック位置に関する配列の初期化
color_position = []
black_position = []

color_block_position = []
black_block_position = []

send_color_data = []
send_black_data = []

rbyg = []
black = []

pos_array = []

# レイヤーの出力名を取得する
def getOutputsNames(net):
    layersNames = net.getLayerNames()
    return [layersNames[i[0] - 1] for i in net.getUnconnectedOutLayers()]

# 前フレームの描画情報を削除し，新しい描画情報に置き換える
def postprocess(frame, outs):
    frameHeight = frame.shape[0]
    frameWidth = frame.shape[1]
    classIds = []
    confidences = []
    boxes = []
    # rbyg.clear()
    # black.clear()
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
    # save_root_path = "result/" + ulid.new().str
    save_root_path = "result/"

    # Yoloで出力されるボックスの位置を出す
    for i in indices:
        if not os.path.exists(save_root_path):
            os.mkdir(save_root_path)
            # try:
            #     cv.imwrite(save_root_path + '/' + 'root' + '.png', frame)
            # except Exception as e:
            #     print(e)
        i = i[0]
        box = boxes[i]
        left = box[0]
        top = box[1]
        width = box[2]
        height = box[3]

        drawPred(classIds[i], confidences[i], left, top, left + width, top + height, frame, save_root_path)

# 該当するブロックを四角で囲み，ラベルを付ける
def drawPred(classId, conf, left, top, right, bottom, frame, save_root_path):
    # Draw a bounding box.
    cv.rectangle(frame, (left, top), (right, bottom), (255, 178, 50), 3)

    label = '%.2f' % conf
    if classes:
        assert (classId < len(classes))
        label = '%s:%s' % (classes[classId], label)

    if classes[classId] == 'red':
        rbyg.append([left, top, right, bottom, 1])
    elif classes[classId] == 'blue':
        rbyg.append([left, top, right, bottom, 2])
    elif classes[classId] == 'yellow':
        rbyg.append([left, top, right, bottom, 3])
    elif classes[classId] == 'green':
        rbyg.append([left, top, right, bottom, 4])
    elif classes[classId] == 'black':
        black.append([left, top, right, bottom])

    # Display the label at the top of the bounding box
    print(label)
    labelSize, baseLine = cv.getTextSize(label, cv.FONT_HERSHEY_SIMPLEX, 0.5, 1)
    top = max(top, labelSize[1])
    cv.rectangle(frame, (left, top - round(1.5 * labelSize[1])), (left + round(1.5 * labelSize[0]), top + baseLine),
                 (255, 255, 255), cv.FILLED)
    cv.putText(frame, label, (left, top), cv.FONT_HERSHEY_SIMPLEX, 0.75, (0, 0, 0), 1)

    try:
        cv.imwrite(save_root_path + '/' + label + '.png', frame)
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
    if frame_count % 4 == 0:
        blob = cv.dnn.blobFromImage(frame, 1 / 255, (inpWidth, inpHeight), [0, 0, 0], 1, crop=False)
        net.setInput(blob)
        outs = net.forward(getOutputsNames(net))
        postprocess(frame, outs)
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