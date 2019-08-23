import cv2
import glob
import os

# 画像ファイルの読み込み
file_list = sorted(glob.glob('images/2019/black/*.JPG'))
# リサイズ後の画像名
file_name = 'black'
# 画像の保存先
save_folder = '005'


def resize(image):
    height = image.shape[0]
    width = image.shape[1]
    # 600 * 600 未満にしたい（理想は多分416*416）0.16はiphonexs基準
    resized_image = cv2.resize(image , (int(width*0.16), int(height*0.16)))

    return resized_image

if __name__ == '__main__':
    for index, _ in enumerate(file_list):
        # ファイル名の取得
        file_path = os.path.basename(file_list[index])
        image = cv2.imread(file_list[index])
        print(file_path)
        image = resize(image)

        cv2.imwrite('./images/' + save_folder + '/' + file_name + '_19_' + str(index) + '.jpg', image)