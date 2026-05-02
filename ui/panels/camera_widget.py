import cv2
from PyQt5 import QtWidgets, QtGui, QtCore

class CameraWidget(QtWidgets.QFrame):
    def __init__(self, cfg, parent=None):
        super().__init__(parent)
        self.cfg = cfg
        self.cap = cv2.VideoCapture(
            cfg['camera']['device_path'],
            cv2.CAP_V4L2
        )
        self.cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
        self._build_ui()
        self.cam_timer = QtCore.QTimer()
        self.cam_timer.timeout.connect(self.update_frame)
        self.cam_timer.start(30)

    def _build_ui(self):
        cam_layout = QtWidgets.QVBoxLayout()
        cam_layout.setContentsMargins(12, 12, 12, 12)
        cam_layout.setSpacing(10)
        self.setLayout(cam_layout)

        cam_title = QtWidgets.QLabel("📷  LIVE CAM — BOX DETECTION")
        cam_title.setStyleSheet("""
            font-size: 10px;
            color: #64748b;
            font-weight: 600;
            padding-left: 4px;
        """)
        cam_title.setAlignment(QtCore.Qt.AlignLeft)
        cam_layout.addWidget(cam_title)

        self.video_label = QtWidgets.QLabel("🔌 MENUNGGU KAMERA...")
        self.video_label.setAlignment(QtCore.Qt.AlignCenter)
        self.video_label.setMinimumHeight(280)
        self.video_label.setStyleSheet("""
            background: #020617;
            border: 1px dashed #334155;
            border-radius: 10px;
            font-size: 11px;
            color: #475569;
        """)
        cam_layout.addWidget(self.video_label, 1)

    def update_frame(self):
        ret, frame = self.cap.read()
        if ret:
            frame = cv2.flip(frame, 1)
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            h, w = frame.shape[:2]
            qt_img = QtGui.QImage(frame.data, w, h, 3 * w,
                                  QtGui.QImage.Format_RGB888)
            pixmap = QtGui.QPixmap.fromImage(qt_img).scaled(
                self.video_label.size(),
                QtCore.Qt.KeepAspectRatio,
                QtCore.Qt.SmoothTransformation
            )
            self.video_label.setPixmap(pixmap)
        else:
            self.video_label.setText("🔌 KAMERA TERPUTUS")

    def reconnect_camera(self):
        self.cap.open(self.cfg['camera']['device_path'], cv2.CAP_V4L2)
        self.cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)

    def release(self):
        self.cam_timer.stop()
        self.cap.release()