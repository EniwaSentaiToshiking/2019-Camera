# 2019-Camera

## 開発環境

Python 3.5.0(共同 PC の関係)

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

## データセットの作り方

- auto_annotation.py

  - 自動データセット作成ツール
  - 2018 の優秀なモデルを使用し，データセットを自動で作成する
  - annotation_images/下にクラス名ごとのフォルダが作成される
  - 各クラス/BBimages に BB 付き画像が保存されるので，ノイズを検出して対応するファイルを削除すること

- 画像の配置
  - images 元画像
  - labels-fist 元ラベル
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
  - ブロック
    - python inflate_block.py data
  - 数字
    - python inflate_number.py data
    - python inflate_number_filter.py data
  - python convert.py data dataset 0.8

## モデルの作り方

- darknet はよしなに準備する alex ver 推奨
- 初期重みは weight/にある
  - v2 は 19
  - v3 は 53
- ./darknet detector train data/config/learning.data data/config/learning.cfg 初期重み -gpus 0,1 -map >> log.txt
- 途中経過は backup/
- 推移は chart.png
- ./darknet detector test data/config/learning.data data/config/learning.cfg 重み -gpus 0,1 任意の画像のパス
- ./darknet detector map data/config/learning.data data/config/learning.cfg 初期重み -gpus 0,1 >> map.txt

## fine tuning

- 重みの切り出し方
- ./darknet partial yolo/yolov3.cfg weights/yolov3.weights 2018robo.conv.81 81
- 予め yolov3.cfg の 548 行目に、stopbacward=1 を記入して出力層以外を切り出すこと
- 学習方法
  - 通常どおり行う。初期重みをさっき作った奴にする
