# 2019-Camera

## 開発環境

Python 3.6.0

## 用いるパッケージ

pipenv

## 使い方

weights ファイルをダウンロードし，yolo/に置く．  
[yolov3.weights](https://www.dropbox.com/s/1r2xawzvz0fpd8f/yolov3.weights?dl=0)

`$ pipenv install`  
`$ pipenv run python main.py`

キーボードの r を押下すると録画開始
キーボードの s を押下すると録画終了
キーボードの q を押下すると終了

## モデルの作り方

- 画像の配置
  - images 元画像
  - labels 元ラベル
  - rotation_images 回転後の画像
  - inflate_labels 回転後のラベル
  - dataset 回転+フィルター処理後の画像
  - final_labels 回転+フィルター処理後のラベル
- BBox-Label-Tool.py を用いてバウンティングボックスを付与
- inflate_images.py を用いて[かさ増し](https://qiita.com/bohemian916/items/9630661cd5292240f8c7)
  - 横反転
  - 縦反転
  - 90 度回転
  - 180 回転
  - 270 度回転
  - HIGH コントラスト(50 未満を 0，205 以上を 255)
  - LOW コントラスト(コントラストの差を小さくする)
  - ガンマ補正(0.7~1.5,01 刻み) 9
  - 平滑化
  - ヒストグラム均一化
  - ノイズ付加(ガウシアン)
  - (通常 1 + 通常 1 _ 回転 3 + 反転 2 　+ 反転 2 _ 回転 3) \* フィルター 14 = 168 枚
- 手順
  - inflate_images.py
  - inflate_images_filter.py
