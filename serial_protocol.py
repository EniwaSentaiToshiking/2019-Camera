import serial
from timeout_decorator import timeout, TimeoutError
import time
from enum import Enum

# [4, 0, 2, 2, 3, 0, 3, 1]
# [2, 3, 3, 2]
class SerialProtocol:
    # シリアル通信
    ser = None
    # BlueToothでロボットから送られてくるデータの読み込み
    line = ""
    # 送る文字列
    send_data = ""
    # 交点サークル上における初期に配置されているブロックの色を管理する配列(indexは座標を表す,中身はclassid)
    serial_list_as_intersection_circle = []
    # ブロックサークル上に配置されたブロックの色を管理する配列([数字,クラスid]黒は無視)
    serial_list_as_block_circle = []
    # ボーナスナンバー
    bonus_number = 0

    def __init__(self, path, port):
        self.path = path
        self.port = port
        # BlueToothの初期化
        try:
            self.ser = serial.Serial(
                self.path, self.port
            )  # tty.MindstormsEV3-SerialPor or tty.Mindstorms-SerialPortPr
            print("connection done")
        except:
            ser = ""
            print("can not connect")

    # BlueToothでロボットから送られてくるデータの読み込み
    def catch_serial(self):
        try:
            self.line = self.serial_read(self.ser)
            print("receive", self.line)
        except TimeoutError:
            # print("TimeoutError")
            pass
        except Exception as e:
            # print("failed", e)
            pass

    def send_serial(self):
        # BlueToothで座標データの送信
        if self.line:  # ロボットからシグナルが来ている場合
            print("bonus_number", self.bonus_number)
            print("intersection_circle", self.serial_list_as_intersection_circle)
            print("block_circle", self.serial_list_as_block_circle)

            # ボーナスナンバー
            self.send_data += str(self.bonus_number)

            # 交点サークル
            for val in self.serial_list_as_intersection_circle:
                self.send_data += str(val)

            # ブロックサークル
            for val in self.serial_list_as_block_circle:
                self.send_data += str(val)

            # BlueToothで送信
            self.ser.write(self.send_data.encode("ascii"))
            self.ser.close()

    @timeout(0.1)
    def serial_read(self, robo):
        return robo.readline().decode("ascii")


if __name__ == "__main__":
    serial = SerialProtocol("/dev/tty.MindstormsEV3-SerialPor", 9600)
    serial.serial_list_as_intersection_circle = [4, 0, 2, 2, 3, 0, 3, 1]
    serial.serial_list_as_block_circle = [2, 3]
    serial.bonus_number = 4
    time.sleep(5)
    serial.catch_serial()
    time.sleep(2)
    serial.send_serial()
