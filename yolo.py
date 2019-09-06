import cv2 as cv
import numpy as np

from yolo_object_model import YoloObjectModel as model

class YOLO():

    # 初期化
    confThreshold = 0.2
    nmsThreshold = 0.4
    inpWidth = 416
    inpHeight = 416
    rbyg = []
    black = []

    def __init__(self, model_cfg_pass, model_weiight_pass, model_names_pass):
        # Yolo関連のモデルの読み込み
        self.modelConfiguration = model_cfg_pass
        self.modelWeights = model_weiight_pass
        # クラス名の読み込み
        self.classesFile = model_names_pass
        self.classes = None
        #
        self.net = cv.dnn.readNetFromDarknet(self.modelConfiguration, self.modelWeights)
        self.net.setPreferableBackend(cv.dnn.DNN_BACKEND_OPENCV)
        self.net.setPreferableTarget(cv.dnn.DNN_TARGET_CPU)
        with open(self.classesFile, 'rt') as f:
            self.classes = f.read().rstrip('\n').split('\n')
    
    # レイヤーの出力名を取得する
    def getOutputsNames(self):
        layersNames = self.net.getLayerNames()
        return [layersNames[i[0] - 1] for i in self.net.getUnconnectedOutLayers()]

    # 前フレームの描画情報を削除し，新しい描画情報に置き換える
    def postprocess(self, frame):
        # 結果を格納したインスタンスの配列
        object_models = []
        drawed_image = np.empty(1)

        blob = cv.dnn.blobFromImage(frame, 1 / 255, (self.inpWidth, self.inpHeight), [0, 0, 0], 1, crop=False)
        self.net.setInput(blob)
        outs = self.net.forward(self.getOutputsNames())
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
                if confidence > self.confThreshold:
                    center_x = int(detection[0] * frameWidth)
                    center_y = int(detection[1] * frameHeight)
                    width = int(detection[2] * frameWidth)
                    height = int(detection[3] * frameHeight)
                    left = int(center_x - width / 2)
                    top = int(center_y - height / 2)
                    classIds.append(classId)
                    confidences.append(float(confidence))
                    boxes.append([left, top, width, height])

        indices = cv.dnn.NMSBoxes(boxes, confidences, self.confThreshold, self.nmsThreshold)

        # Yoloで出力されるボックスの位置を出す
        for i in indices:
            i = i[0]
            box = boxes[i]
            left = box[0]
            top = box[1]
            width = box[2]
            height = box[3]

            drawed_image, object_model = self.drawPred(classIds[i], confidences[i], left, top, left + width, top + height, frame)
            object_models.append(object_model)
        
        return drawed_image, object_models
    
    def clip(self, image, left, right, top, bottom):

        # トリミングする範囲 y:y+height,x:x+width
        cliped_image = image[top:bottom+1, left:right+1]

        return cliped_image

    # 該当するブロックを四角で囲み，ラベルを付ける
    def drawPred(self, classId, conf, left, top, right, bottom, frame):
        # Draw a bounding box.
        cv.rectangle(frame, (left, top), (right, bottom), (255, 178, 50), 3)

        label = '%.2f' % conf
        score = 0.0
        if self.classes:
            assert (classId < len(self.classes))
            score = label
            # label = '%s:%s' % (self.classes[classId], label)
            label = self.classes[classId]

        # modelのインスタンス
        clip_image = self.clip(frame, left, right, top, bottom)
        object_model = model(label, score, left, right, top, bottom, clip_image)
        # print(object_model.label)

        if self.classes[classId] == 'red':
            self.rbyg.append([left, top, right, bottom, 1])
        elif self.classes[classId] == 'blue':
            self.rbyg.append([left, top, right, bottom, 2])
        elif self.classes[classId] == 'yellow':
            self.rbyg.append([left, top, right, bottom, 3])
        elif self.classes[classId] == 'green':
            self.rbyg.append([left, top, right, bottom, 4])
        elif self.classes[classId] == 'black':
            self.black.append([left, top, right, bottom])

        # Display the label at the top of the bounding box
        labelSize, baseLine = cv.getTextSize(label, cv.FONT_HERSHEY_SIMPLEX, 0.5, 1)
        top = max(top, labelSize[1])
        cv.rectangle(frame, (left, top - round(1.5 * labelSize[1])), (left + round(1.5 * labelSize[0]), top + baseLine),
                    (255, 255, 255), cv.FILLED)
        cv.putText(frame, label, (left, top), cv.FONT_HERSHEY_SIMPLEX, 0.75, (0, 0, 0), 1)

        return frame, object_model
    
    def debugDraw(self, image, model):
        # Draw a bounding box.
        cv.rectangle(image, (model.left, model.top), (model.right, model.bottom), (255, 178, 50), 3)
        # Display the label at the top of the bounding box
        labelSize, baseLine = cv.getTextSize(model.label, cv.FONT_HERSHEY_SIMPLEX, 0.5, 1)
        top = max(model.top, labelSize[1])
        cv.rectangle(image, (model.left, top - round(1.5 * labelSize[1])), (model.left + round(1.5 * labelSize[0]), top + baseLine),
                    (255, 255, 255), cv.FILLED)
        cv.putText(image, model.label, (model.left, top), cv.FONT_HERSHEY_SIMPLEX, 0.75, (0, 0, 0), 1)
    
        return image

    # 重複を削除する
    # 比較先の中心が比較元の短形の内側にあるかどうかで判断
    def deduplication(self, object_models):
        # scoreが高い順にソート
        sorted_object_models = sorted(object_models)
        if len(object_models) == 1:
            return sorted_object_models

        deleteObjectModels = []
        for index, objectModel in enumerate(sorted_object_models):
            for comparisonIndex in range(index + 1, len(sorted_object_models)):
                rect = np.array([[objectModel.left, objectModel.top],
                                    [objectModel.left, objectModel.bottom],
                                    [objectModel.right, objectModel.bottom],
                                    [objectModel.right, objectModel.top]])

                centralCoordinate = sorted_object_models[comparisonIndex].calcCcntralCoordinate()
            if cv.pointPolygonTest(rect, (centralCoordinate["x"], centralCoordinate["y"]), False) >= 0:
                deleteObjectModels.append(sorted_object_models[comparisonIndex])

        for target in set(deleteObjectModels):
            sorted_object_models.remove(target)

        return sorted_object_models
    
    # 色の誤識別を修正する
    def fix_color(self, object_models):
        for object_model in object_models:
            # 中心位置取得
            center = tuple(np.array([int(object_model.clip_image.shape[1] * 0.5), int(object_model.clip_image.shape[0] * 0.5)]))
            # opencvはbgr
            r = object_model.clip_image[center][2]
            g = object_model.clip_image[center][1]
            b = object_model.clip_image[center][0]
            # 赤と緑の差に注目する
            if (abs(r - g) >= 40 ) and object_model.label == "yellow":
                object_model.label = "red"
            if (abs(r - g) < 40) and object_model.label == "red":
                object_model.label = "yellow"
        
        return object_models

if __name__ == '__main__':
    model_cfg_pass = "yolo/0903/etrobo2019_block.cfg"
    model_weiight_pass = "yolo/0903/etrobo2019_block_800.weights"
    model_names_pass = "yolo/0902/learning.names"
    yolo = YOLO(model_cfg_pass, model_weiight_pass, model_names_pass)