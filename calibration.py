import cv2 as cv
import numpy as np
from enum import Enum

from yolo_object_model import YoloObjectModel as model


class State(Enum):
    in_calibration = "in_calibration"
    wait_yolo = "wait_yolo"
    in_association = "in_association"
    in_adjustment = "in_adjustment"
    finish = "finish"


class CircleType(Enum):
    intersection_circle = "intersection_circle"
    block_circle = "block_circle"


class ColorList(Enum):
    white = 0
    red = 1
    blue = 2
    yellow = 3
    green = 4
    black = 5


class AdjustColor:
    white = [255, 255, 255]
    red = [5, 22, 81]
    blue = [72, 51, 25]
    yellow = [0, 88, 120]
    green = [39, 57, 24]

    colors = [white, red, blue, yellow, green]


class CalibrationModel:
    # YoloObjectModel or AdjustObjectModel
    model = None

    def __init__(self, position_x, position_y):
        self.position_x = position_x
        self.position_y = position_y


class AdjustObjectModel:
    def __init__(self, class_id, label):
        self.class_id = class_id
        self.label = label


class Calibration:
    # 初期化
    winName = "ET Robo"
    # 交点サークル(初期にブロックが配置されている所のみ)の座標を管理する配列
    intersection_circle_positions = []
    # ブロックサークルの座標を管理する配列
    block_circle_positions = []
    # 交点サークル上における初期に配置されているブロックの色を管理する配列(indexは座標を表す)
    first_set_block_colors = []
    # ブロックサークル上に配置されたブロックの色を管理する配列(indexは座標を表し、9はブロックが配置されていないことを表す)
    block_circle_colors = []
    # 状態
    state = State.in_association
    # 最後のあがき用
    to_adjust_color = AdjustColor()

    # 描画を行う上での初期設定
    def make_window(self):
        cv.namedWindow(self.winName, cv.WINDOW_NORMAL)
        cv.setWindowProperty(self.winName, cv.WND_PROP_FULLSCREEN, cv.WINDOW_FULLSCREEN)
        wname = "MouseEvent"

    # クリックした箇所をサークルと判定する 最初に交点サークル(初期にブロックが配置されている部分のみ)を8回 次にブロックサークルを8回
    def click_point(self, event, x, y, flags, params):
        if event == cv.EVENT_LBUTTONUP:
            calibration_model = CalibrationModel(x, y)
            if len(self.intersection_circle_positions) < 8:
                self.intersection_circle_positions.append(calibration_model)
            elif len(self.block_circle_positions) < 8:
                self.block_circle_positions.append(calibration_model)

    # クリックした地点を表示する 初期ブロック位置は赤点 ブロックサークルは青点
    def draw_click_points(self, frame):
        for position in self.intersection_circle_positions:
            cv.circle(
                frame, (position.position_x, position.position_y), 3, (0, 0, 255), 3
            )

        for position in self.block_circle_positions:
            cv.circle(
                frame, (position.position_x, position.position_y), 3, (255, 0, 0), 3
            )

        cv.imshow(self.winName, frame)

    # 点打ち終わり
    def finish_display_click_point(self):
        self.state = State.wait_yolo

    # 点打ちやり直し
    def clear_display_click_point(self):
        self.intersection_circle_positions.clear()
        self.block_circle_positions.clear()

    # 対応付け
    def association(self, color_object_model):
        for calibration_model in self.intersection_circle_positions:
            # YOLOで検出したオブジェクトを囲む短形を作成
            rect = np.array(
                [
                    [color_object_model.left, color_object_model.top],
                    [color_object_model.left, color_object_model.bottom],
                    [color_object_model.right, color_object_model.bottom],
                    [color_object_model.right, color_object_model.top],
                ]
            )

            if (
                # 座標が四角形の内側にあるかどうか
                cv.pointPolygonTest(
                    rect,
                    (calibration_model.position_x, calibration_model.position_y),
                    False,
                )
                >= 0
            ):
                calibration_model.model = color_object_model

        for calibration_model in self.block_circle_positions:
            # YOLOで検出したオブジェクトを囲む短形を作成
            rect = np.array(
                [
                    [color_object_model.left, color_object_model.top],
                    [color_object_model.left, color_object_model.bottom],
                    [color_object_model.right, color_object_model.bottom],
                    [color_object_model.right, color_object_model.top],
                ]
            )

            if (
                # 座標が四角形の内側にあるかどうか
                cv.pointPolygonTest(
                    rect,
                    (calibration_model.position_x, calibration_model.position_y),
                    False,
                )
                >= 0
            ):
                calibration_model.model = color_object_model

    @classmethod
    def _color_id(self, colorList):
        if colorList == ColorList.red:
            return 0, "red"
        if colorList == ColorList.blue:
            return 1, "blue"
        if colorList == ColorList.yellow:
            return 2, "yellow"
        if colorList == ColorList.green:
            return 3, "green"

    @classmethod
    def _adjustment_Logic(self, calibration_model, frame, circle_type):
        # ブロックサークル上には2つしかない 調整して検出したいのは1つ
        block_circle_ajust_count = 0

        if calibration_model.model != None:
            return calibration_model
        else:
            try:
                # opencvはbgr
                b = frame[calibration_model.position_y, calibration_model.position_x][0]
                r = frame[calibration_model.position_y, calibration_model.position_x][2]
                g = frame[calibration_model.position_y, calibration_model.position_x][1]

                # たぶんnumpy型なはず そのまま計算すると桁あふれ？がおきる．intにキャスト
                r_g = int(r) - int(g)
                r_b = int(r) - int(b)
                g_r = int(g) - int(r)

                # 黒(数字の色)扱い 数字の色
                if abs(r_g) < 20 and abs(r_b) < 20 and abs(g_r) < 20:
                    # 交点サークルだけ黒の補完をする
                    if circle_type == CircleType.block_circle:
                        calibration_model.model = AdjustObjectModel(
                            self._color_id(ColorList.black)[0],
                            self._color_id(ColorList.black)[1],
                        )

                    return calibration_model

                vec_a = np.array([b, g, r])
                distance = 10000000
                adjustment_color = None

                for index, color in enumerate(self.to_adjust_color.colors):
                    vec_b = np.array(color)
                    calc_distance = np.linalg.norm(vec_a - vec_b)
                    if distance > calc_distance:
                        distance = calc_distance
                        # 白はスルー
                        if index > 0:
                            adjustment_color = ColorList(index)
                        else:
                            continue

                if adjustment_color != None and block_circle_ajust_count < 1:
                    calibration_model.model = AdjustObjectModel(
                        self._color_id(adjustment_color)[0],
                        self._color_id(adjustment_color)[1],
                    )
                    if circle_type == CircleType.block_circle:
                        block_circle_ajust_count += 1

            except Exception as e:
                # IndexError: index 39 is out of bounds for axis 1 with size 32でコケる
                print(e)

    # 最後の悪あがき
    def adjustment(self, frame):

        for calibration_model in self.intersection_circle_positions:
            calibration_model = self._adjustment_Logic(
                calibration_model, frame, CircleType.intersection_circle
            )

        for calibration_model in self.block_circle_positions:
            calibration_model = self._adjustment_Logic(
                calibration_model, frame, CircleType.block_circle
            )


def hoge():
    a = 59
    b = 57
    print(2 - 4)
    print(abs(2 - 4))
    print(abs(a - b))
    print(abs(b - a))


if __name__ == "__main__":
    hoge()
