import cv2

for i in range(5):
    cap = cv2.VideoCapture(i, cv2.CAP_V4L2)
    if cap.isOpened():
        print(f"Kamera aktif di index {i}")
        cap.release()