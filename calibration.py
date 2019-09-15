import cv2 as cv
import numpy as np
from enum import Enum


class State(Enum):
    in_calibration = "in_calibration"
    wait_yolo = "wait_yolo"
    in_association = "in_association"
    in_adjustment = "in_adjustment"
    in_setting_serial = "in_setting_serial"
    finish = "finish"


class CircleType(Enum):
    intersection_circle = "intersection_circle"
    block_circle = "block_circle"


class NomberList(Enum):
    one = 0
    two = 1
    three = 2
    four = 3
    five = 4
    six = 5
    seven = 6
    eight = 7


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
    # 交点サークル上における初期に配置されているブロックの色を管理する配列(indexは座標を表す,中身はclassid)
    serial_list_as_intersection_circle = []
    # ブロックサークル上に配置されたブロックの色を管理する配列([数字,クラスid]黒は無視)
    serial_list_as_block_circle = []
    # ボーナスナンバー
    bonus_number = 0
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

    @classmethod
    # 対応付け
    def _association_logic(self, color_object_model, calibration_model):
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

    # 対応付け
    def association(self, color_object_model):
        for calibration_model in self.intersection_circle_positions:
            self._association_logic(color_object_model, calibration_model)

        for calibration_model in self.block_circle_positions:
            self._association_logic(color_object_model, calibration_model)

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
        if colorList == ColorList.black:
            return 4, "black"

    @classmethod
    def _number_id(self, numberlist):
        if numberlist == NomberList.one:
            return 1
        if numberlist == NomberList.two:
            return 2
        if numberlist == NomberList.three:
            return 3
        if numberlist == NomberList.four:
            return 4
        if numberlist == NomberList.five:
            return 5
        if numberlist == NomberList.six:
            return 6
        if numberlist == NomberList.seven:
            return 7
        if numberlist == NomberList.eight:
            return 8

    @classmethod
    # 最後の悪あがき
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

    # シリアル通信の準備をする
    def set_serial_list(self, bonus_number_models):
        if len(bonus_number_models) == 0:
            self.bonus_number = 0
        else:
            # スコアが高い順にソート
            bonus_number_models = sorted(bonus_number_models)
            # 一番高いやつを信用する
            bonus_number_model = bonus_number_models[0]
            self.bonus_number = self._number_id(bonus_number_model.class_id)

        # 交点サークル
        for intersection_circle_position in self.intersection_circle_positions:
            self.serial_list_as_intersection_circle.append(
                intersection_circle_position.model.class_id
            )

        # ブロックサークル
        for index, block_circle_position in enumerate(self.block_circle_positions):
            # 無検出と黒は無視
            if (
                block_circle_position.model != None
                and block_circle_position.model.class_id != 4
            ):
                # ブロックサークルの数字として送りたい. index == 0ならブロックサークルの数字は1
                self.serial_list_as_block_circle.append(index + 1)
                self.serial_list_as_block_circle.append(
                    block_circle_position.model.class_id
                )


def hoge():
    calibration = Calibration()
    print(calibration._number_id(NomberList(0)))


if __name__ == "__main__":
    hoge()
