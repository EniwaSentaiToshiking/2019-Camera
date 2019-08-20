import cv2
import os

def save_all_frames(video_path, dir_path, basename, ext='jpg'):
    cap = cv2.VideoCapture(video_path)

    if not cap.isOpened():
        return

    os.makedirs(dir_path, exist_ok=True)
    base_path = os.path.join(dir_path, basename)

    digit = len(str(int(cap.get(cv2.CAP_PROP_FRAME_COUNT))))

    n = 0

    while True:
        ret, frame = cap.read()
        if ret:
            cv2.imwrite('{}-{}.{}'.format(base_path, str(n).zfill(digit), ext), frame)
            n += 1
        else:
            return

# How to
# save_all_frames('data/temp/sample_video.mp4', 'data/temp/result', 'sample_video_img')
save_all_frames('video/output_1_r.mp4', 'images/001', '1-r-video', 'jpg')
save_all_frames('video/output_2_r.mp4', 'images/002', '2-r-video', 'jpg')
save_all_frames('video/output_3_r.mp4', 'images/003', '3-r-video', 'jpg')
save_all_frames('video/output_4_r.mp4', 'images/004', '4-r-video', 'jpg')
save_all_frames('video/output_5_r.mp4', 'images/005', '5-r-video', 'jpg')
save_all_frames('video/output_6_r.mp4', 'images/006', '6-r-video', 'jpg')
save_all_frames('video/output_7_r.mp4', 'images/007', '7-r-video', 'jpg')
save_all_frames('video/output_8_r.mp4', 'images/008', '8-r-video', 'jpg')
