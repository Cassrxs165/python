import sys
import cv2
import rclpy
from rclpy.node import Node
from std_msgs.msg import String
from PyQt5 import QtWidgets, QtGui, QtCore


# ================= ROS2 NODE =================
class ROSNode(Node):
    def __init__(self):
        super().__init__('gui_node')
        self.publisher = self.create_publisher(String, 'robot_command', 10)

    def send(self, text):
        msg = String()
        msg.data = text
        self.publisher.publish(msg)
        self.get_logger().info(f'GUI → ROS2: {text}')


# ================= GUI =================
class RobotGUI(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()

        # ===== ROS2 INIT =====
        rclpy.init()
        self.ros_node = ROSNode()

        # Timer untuk ROS spin (non-blocking)
        self.ros_timer = QtCore.QTimer()
        self.ros_timer.timeout.connect(self.spin_ros)
        self.ros_timer.start(10)

        # ===== GUI SETUP (IDENTIK DENGAN SEBELUMNYA) =====
        self.setWindowTitle("Robocon 2026 - Vision Control")
        self.setGeometry(100, 100, 1400, 800)
        self.setMinimumSize(1200, 700)

        central_widget = QtWidgets.QWidget()
        self.setCentralWidget(central_widget)

        # CYBERPUNK THEME (100% SAMA)
        self.setStyleSheet(self.get_global_styles())

        # CAMERA (SAMA PERSIS)
        self.cap = cv2.VideoCapture(
            "/dev/v4l/by-id/usb-046d_C922_Pro_Stream_Webcam_8E3AFE4F-video-index0",
            cv2.CAP_V4L2
        )
        self.cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)

        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.update_frame)
        self.timer.start(30)

        self.setup_ui(central_widget)
        self.status = "READY"

    def get_global_styles(self):
        return """
        QMainWindow {
            background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                stop:0 #0a0f1e, stop:1 #1a2332);
            color: #e2e8f0;
        }
        QLabel {
            color: #e2e8f0;
            font-weight: 500;
        }
        QFrame {
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 #1e293b, stop:1 #0f172a);
            border: 1px solid #334155;
            border-radius: 16px;
        }
        QPushButton {
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 #3b82f6, stop:1 #1d4ed8);
            color: white;
            border: 2px solid #1e40af;
            border-radius: 12px;
            padding: 12px 24px;
            font-size: 15px;
            font-weight: 600;
            min-height: 48px;
        }
        QPushButton:hover {
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 #60a5fa, stop:1 #3b82f6);
        }
        QPushButton:pressed {
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 #2563eb, stop:1 #1d4ed8);
        }
        """

    # ===== ROS2 SPIN (BARU) =====
    def spin_ros(self):
        """Non-blocking ROS2 spin"""
        rclpy.spin_once(self.ros_node, timeout_sec=0)

    # ===== UI (100% IDENTIK) =====
    def setup_ui(self, central_widget):
        main_layout = QtWidgets.QHBoxLayout()
        main_layout.setContentsMargins(24, 24, 24, 24)
        main_layout.setSpacing(24)
        central_widget.setLayout(main_layout)

        # LEFT PANEL - VIDEO
        left_panel = self.create_video_panel()
        main_layout.addWidget(left_panel, 7)

        # RIGHT PANEL - CONTROLS
        right_panel = self.create_control_panel()
        main_layout.addWidget(right_panel, 3)

    def create_video_panel(self):
        panel = QtWidgets.QFrame()
        panel.setObjectName("videoPanel")
        layout = QtWidgets.QVBoxLayout()
        layout.setSpacing(20)
        layout.setContentsMargins(24, 24, 24, 24)
        panel.setLayout(layout)

        # HEADER
        header = QtWidgets.QLabel("🎥 LIVE VISION")
        header.setStyleSheet("""
            font-size: 22px; 
            font-weight: 700; 
            color: #38bdf8;
            padding: 8px 0;
            background: rgba(56, 189, 248, 0.1);
            border-radius: 8px;
            border-left: 4px solid #38bdf8;
        """)
        header.setAlignment(QtCore.Qt.AlignCenter)
        layout.addWidget(header)

        # VIDEO LABEL
        self.video_label = QtWidgets.QLabel("🔌 MENUNGGU KAMERA...")
        self.video_label.setAlignment(QtCore.Qt.AlignCenter)
        self.video_label.setMinimumHeight(300)
        self.video_label.setStyleSheet("""
            background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                stop:0 #000000, stop:1 #1a1a1a);
            border: 2px dashed #475569;
            border-radius: 12px;
            font-size: 18px;
        """)
        
        video_container = QtWidgets.QWidget()
        video_layout = QtWidgets.QVBoxLayout()
        video_layout.setContentsMargins(0, 0, 0, 0)
        video_container.setLayout(video_layout)
        video_layout.addWidget(self.video_label, 1)
        layout.addWidget(video_container, 1)

        # TARGET STATUS
        self.target_label = QtWidgets.QLabel("🎯 Target: TIDAK TERDETEKSI")
        self.target_label.setStyleSheet("""
            background: rgba(239, 68, 68, 0.2);
            border: 1px solid #7f1d1d;
            border-radius: 10px;
            padding: 12px;
            font-size: 16px;
            font-weight: 600;
        """)
        self.target_label.setAlignment(QtCore.Qt.AlignCenter)
        layout.addWidget(self.target_label)

        return panel

    def create_control_panel(self):
        panel = QtWidgets.QFrame()
        layout = QtWidgets.QVBoxLayout()
        layout.setSpacing(20)
        layout.setContentsMargins(24, 24, 24, 24)
        panel.setLayout(layout)

        # STATUS HEADER
        self.status_label = QtWidgets.QLabel("🟢 STATUS: READY")
        self.status_label.setAlignment(QtCore.Qt.AlignCenter)
        self.status_label.setStyleSheet("""
            background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                stop:0 #10b981, stop:1 #059669);
            border-radius: 12px;
            padding: 16px;
            font-size: 18px;
            font-weight: 700;
        """)
        layout.addWidget(self.status_label)

        # CONTROL BUTTONS (ROS2 INTEGRATED)
        self.btn_start = QtWidgets.QPushButton("▶️ START OTONOM")
        self.btn_start.clicked.connect(self.start_robot)
        layout.addWidget(self.btn_start)

        self.btn_retry = QtWidgets.QPushButton("🔄 RETRY KAMERA")
        self.btn_retry.clicked.connect(self.retry_connection)
        layout.addWidget(self.btn_retry)

        self.btn_stop = QtWidgets.QPushButton("⛔ EMERGENCY STOP")
        self.btn_stop.clicked.connect(self.stop_robot)
        layout.addWidget(self.btn_stop)

        layout.addStretch()

        # INFO PANEL (TAMBAH ROS2 STATUS)
        info_label = QtWidgets.QLabel("🤖 Robocon 2026\nROS2 Vision Control v2.0")
        info_label.setAlignment(QtCore.Qt.AlignCenter)
        info_label.setStyleSheet("""
            background: rgba(59, 130, 246, 0.1);
            border: 1px solid #3b82f6;
            border-radius: 10px;
            padding: 12px;
            font-size: 14px;
            opacity: 0.8;
        """)
        layout.addWidget(info_label)

        return panel

    # ===== CAMERA (SAMA PERSIS) =====
    def update_frame(self):
        ret, frame = self.cap.read()
        if ret:
            frame = cv2.flip(frame, 1)
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            h, w = frame.shape[:2]
            bytes_per_line = 3 * w

            qt_image = QtGui.QImage(frame.data, w, h, bytes_per_line, 
                                  QtGui.QImage.Format_RGB888)
            
            pixmap = QtGui.QPixmap.fromImage(qt_image)
            scaled_pixmap = pixmap.scaled(
                self.video_label.size(),
                QtCore.Qt.KeepAspectRatio,
                QtCore.Qt.SmoothTransformation
            )
            self.video_label.setPixmap(scaled_pixmap)
        else:
            self.video_label.setText("🔌 KAMERA TERPUTUS")

    # ===== ROS2 BUTTON ACTIONS =====
    def start_robot(self):
        self.status = "OTONOM"
        self.status_label.setText("🟢 STATUS: OTONOM")
        self.status_label.setStyleSheet("""
            background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                stop:0 #10b981, stop:1 #059669);
            border-radius: 12px;
            padding: 16px;
            font-size: 18px;
            font-weight: 700;
        """)
        self.ros_node.send("start")  # 🔥 ROS2 SEND

    def retry_connection(self):
        self.cap.release()
        QtCore.QTimer.singleShot(500, self.reconnect_camera)
        self.ros_node.send("retry")  # 🔥 ROS2 SEND

    def reconnect_camera(self):
        self.cap.open("/dev/v4l/by-id/usb-046d_C922_Pro_Stream_Webcam_8E3AFE4F-video-index0",
                     cv2.CAP_V4L2)
        self.cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)

    def stop_robot(self):
        self.status = "STOPPED"
        self.status_label.setText("🔴 STATUS: STOPPED")
        self.status_label.setStyleSheet("""
            background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                stop:0 #ef4444, stop:1 #dc2626);
            border-radius: 12px;
            padding: 16px;
            font-size: 18px;
            font-weight: 700;
        """)
        self.ros_node.send("stop")  # 🔥 ROS2 SEND

    # ===== CLOSE (ROS2 SHUTDOWN) =====
    def closeEvent(self, event):
        self.timer.stop()
        self.ros_timer.stop()  # STOP ROS TIMER
        self.cap.release()
        cv2.destroyAllWindows()
        rclpy.shutdown()  # 🔥 ROS2 CLEANUP
        event.accept()

    # ===== FULLSCREEN STABIL (SAMA PERSIS) =====
    def resizeEvent(self, event):
        super().resizeEvent(event)
        if hasattr(self, 'video_label') and self.video_label.pixmap():
            pixmap = self.video_label.pixmap()
            if pixmap:
                scaled_pixmap = pixmap.scaled(
                    self.video_label.size(),
                    QtCore.Qt.KeepAspectRatio,
                    QtCore.Qt.SmoothTransformation
                )
                self.video_label.setPixmap(scaled_pixmap)


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    app.setStyle('Fusion')
    
    window = RobotGUI()
    window.showMaximized()
    sys.exit(app.exec_())