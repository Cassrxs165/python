import cv2

cap = cv2.VideoCapture(3, cv2.CAP_V4L2)

while True:
    ret, frame = cap.read()
    if not ret:
        print("kamera gagal")
        break

    cv2.imshow("C922 Camera", frame)

    if cv2.waitKey(1) & 0xFF == 27:
        break

cap.release()
cv2.destroyAllWindows()