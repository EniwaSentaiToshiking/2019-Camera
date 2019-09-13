import cv2 as cv
import numpy as np
import copy
from yolo import YOLO

class GUI ():
    # 初期化
    winName = 'ET Robo'
    # 交点サークル(初期にブロックが配置されている所のみ)の座標を管理する配列
    first_set_block_positions = []
    # ブロックサークルの座標を管理する配列
    block_circle_positions = []
    # 交点サークル上における初期に配置されているブロックの色を管理する配列(indexは座標を表す)
    first_set_block_colors = []
    # ブロックサークル上に配置されたブロックの色を管理する配列(indexは座標を表し、9はブロックが配置されていないことを表す)
    block_circle_colors = []

    # 描画を行う上での初期設定
    def make_window(self):
        cv.namedWindow(self.winName, cv.WINDOW_NORMAL)
        cv.setWindowProperty(self.winName, cv.WND_PROP_FULLSCREEN, cv.WINDOW_FULLSCREEN)
        wname = "MouseEvent"
        
    # クリックした箇所をサークルと判定する 最初に交点サークル(初期にブロックが配置されている部分のみ)を8回 次にブロックサークルを8回
    def mouse_event(self, event, x, y, flags, params):
        if event == cv.EVENT_LBUTTONUP:
            if len(self.first_set_block_positions) < 8:
                self.first_set_block_positions.append([x, y])
            elif len(self.block_circle_positions) < 8:
                self.block_circle_positions.append([x, y])

    def nothing(val):
        pass

    # クリックした地点を表示する 初期ブロック位置は赤点 ブロックサークルは青点
    def display_click_point(self, frame):
        for i in self.first_set_block_positions:
            cv.circle(frame, (i[0], i[1]), 3, (0, 0, 255), 3)
        
        for i in self.block_circle_positions:
            cv.circle(frame, (i[0], i[1]), 3, (255, 0, 0), 3)

    # トラックバーを作成する
    def create_trackbar(self, frame):
        cv.createTrackbar('hoge', self.winName, 150, 300, self.nothing)
        cv.createTrackbar('hige', self.winName, 0, 2, self.nothing)

        cv.imshow(self.winName, frame)


# if __name__ == "__main__":
#     print("gggggg")