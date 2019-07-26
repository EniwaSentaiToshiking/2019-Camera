import cv2

# VideoCapture を作成する。
filepath = 'http://192.168.11.100/?action=stream'
cap = cv2.VideoCapture(filepath)

# while True:
#     # 1フレームずつ取得する。
#     ret, frame = cap.read()
#     if not ret:
#         break  # 映像取得に失敗
    
#     cv2.imshow('Frame', frame)
#     cv2.waitKey(1)

# cap.release()
# cv2.destroyAllWindows()

width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
fps = cap.get(cv2.CAP_PROP_FPS)

# VideoWriter を作成する。
fourcc = cv2.VideoWriter_fourcc('m','p','4','v')
writer = cv2.VideoWriter('output.mp4', fourcc, fps, (width, height))

while True:
    # 1フレームずつ取得する。
    ret, frame = cap.read()
    if not ret:
        break  # 映像取得に失敗
    
    writer.write(frame)  # フレームを書き込む。

writer.release()
cap.release()