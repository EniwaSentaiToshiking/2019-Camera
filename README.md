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

- データセット作成で注意すべきこと

  - [機械学習のデータセットの重要性](https://qiita.com/nonbiri15/items/b29fe079d359d531bf85)
  - [darknet](https://github.com/AlexeyAB/darknet#how-to-improve-object-detection)
  - 実際に検出する環境を想定すること
  - 汎化性能を上げるために，マルチアングル，拡大・縮小を意識すること
  - 照明条件の変化を考慮すること
  - 用意する画像の種類はまんべんなく集めること．偏りがあると，過学習を招くことになる

- auto_annotation.py

  - 自動データセット作成ツール
  - 2018 の優秀なモデルを使用し，データセットを自動で作成する
  - annotation_images/下にクラス名ごとのフォルダが作成される
  - 各クラス/BBimages に BB 付き画像が保存されるので，ノイズを検出して対応するファイルを削除すること

- tin-out-nnotation-images.py

  - 自動的にアノテーションされた画像を間引くツール
  - 画像と BBbox のテキストが削除される
  - ウィンドウには，txt に基づいた BB 付きが表示される
  - 別途 各クラス/BBimages を表示して，比較することを推奨する
  - ファイルの構成は BBbox と同じ
    - target-dir
      - 001
      - 002
      - labels
        - 001
        - 002
  - next や back で画像を表示し，delete ボタンで削除する

- 画像の配置
  - images 元画像
  - labels-fist 元ラベル
  - rotation_block_images 回転後のカラーブロック画像
  - inflate_block_labels 回転後のカラーブロックラベル
  - rotation_numbers_images 回転後の数字画像
  - inflate_numbers_labels 回転後の数字ラベル
  - dataset 回転+フィルター処理後の画像
  - final_labels 回転+フィルター処理後のラベル
- BBox-Label-Tool.py を用いてバウンティングボックスを付与
- inflate_images.py を用いて
  - [かさ増し](https://qiita.com/bohemian916/items/9630661cd5292240f8c7)
  - [水増しの注意点](https://products.sint.co.jp/aisia/blog/vol1-7)
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
- 手順
  - ブロック
    - python inflate_block.py data
    - python inflate_block_filter.py data
  - 数字
    - python inflate_number.py data
    - python inflate_number_filter.py data
  - python convert.py data dataset 0.7

## ハイパーパラメータ

- フィルター数：(n+5)\*3

| 項目                 | 値          |
| -------------------- | ----------- |
| クラス数             | 13          |
| フィルター数         | 90          |
| 最大イテレーション数 | 26000       |
| バッチサイズ         | 64          |
| 訓練とバリッドの比率 | 7:3         |
| 学習率               | 0.001       |
| step                 | 20800,23400 |
| 学習率を変化させる値 | .1,.1       |

## モデルの作り方

- darknet はよしなに準備する alex ver 推奨
- 初期重みは weight/にある
  - v2 は 19
  - v3 は 53
- ./darknet detector train data/config/learning.data data/config/learning.cfg 初期重み -gpus 0,1 -map >> log.txt
- 途中経過は backup/
- 推移は chart.png
- ./darknet detector test data/config/learning.data data/config/learning.cfg 重み -gpus 0,1 任意の画像のパス

## fine tuning

- [転移学習とファインチューニングの違い](https://www.quora.com/What-is-the-difference-between-transfer-learning-and-fine-tuning)
  - 出力層以外を使うのは同じ
  - 重みを再学習してチューニングするかどうかが異なる
  - yolo の作者や alex さんは，転移学習の代わりに finetuning をと書いてた [github](https://github.com/AlexeyAB/darknet#how-to-improve-object-detection)
- 重みの切り出し方
- ./darknet partial yolo/yolov3.cfg weights/yolov3.weights 2018robo.conv.81 81
- 予め yolov3.cfg の 548 行目に、stopbacward=1 を記入して出力層以外を切り出すこと
- 学習方法
  - 通常どおり行う。初期重みをさっき作った奴にする

## モデルの評価方法

- alex ver darknet では，loss 関数の推移と共に map を描画してくれる
- [【物体検出】vol.3 ：YOLOv3 の独自モデル学習の勘](https://www.nakasha.co.jp/future/ai/yolov3train.html)
- [【入門者向け】機械学習の分類問題評価指標解説(正解率・適合率・再現率など)](https://qiita.com/FukuharaYohei/items/be89a99c53586fa4e2e4)
- ./darknet detector map data/config/learning.data data/config/learning.cfg 初期重み -gpus 0,1 >> map.txt
- map オプションによって，対象のイテレーション時点での下記がわかる
  - map
  - iou
  - f
  - tp
  - fp
  - fn
- あくまで所感
  - map は 50 以上はないとゴミ．70 後半~80 前半がよさそう．90 はたぶん過学習
  - iou は深く気にしない．あくまで BB がどれだけ合ってる？って値．60 もあれば御の字
  - los 関数の値は，0.1 を下回っていたいところ
  - 採用する重みは，tp と fp をプロットして交差する箇所を探すこと
  - map だけじゃなくて，ap も見ること．さらに tp，fp も見ながらヤバそうなクラスを割り出すこと
  - 評価指標による数値はあくまで数字．しっかりテストすること
