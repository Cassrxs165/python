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
        print(f"[ROS2] Kirim: {text}")


# ================= GUI =================
class RobotGUI(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()

        # ===== ROS2 INIT =====
        rclpy.init()
        self.ros_node = ROSNode()

        # Timer untuk ROS spin
        self.ros_timer = QtCore.QTimer()
        self.ros_timer.timeout.connect(self.spin_ros)
        self.ros_timer.start(10)

        # ===== GUI SETUP =====
        self.setWindowTitle("Robocon 2026 - Vision Control")
        self.setGeometry(100, 100, 1400, 800)

        central_widget = QtWidgets.QWidget()
        self.setCentralWidget(central_widget)

        # CAMERA
        self.cap = cv2.VideoCapture(0)

        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.update_frame)
        self.timer.start(30)

        self.setup_ui(central_widget)
        self.status = "READY"

    # ===== ROS LOOP =====
    def spin_ros(self):
        rclpy.spin_once(self.ros_node, timeout_sec=0)

    # ===== UI =====
    def setup_ui(self, central_widget):
        layout = QtWidgets.QHBoxLayout()
        central_widget.setLayout(layout)

        self.video_label = QtWidgets.QLabel("Camera")
        self.video_label.setAlignment(QtCore.Qt.AlignCenter)
        layout.addWidget(self.video_label, 3)

        control_layout = QtWidgets.QVBoxLayout()

        self.status_label = QtWidgets.QLabel("STATUS: READY")
        self.status_label.setAlignment(QtCore.Qt.AlignCenter)
        control_layout.addWidget(self.status_label)

        btn_start = QtWidgets.QPushButton("START")
        btn_start.clicked.connect(self.start_robot)
        control_layout.addWidget(btn_start)

        btn_retry = QtWidgets.QPushButton("RETRY")
        btn_retry.clicked.connect(self.retry_connection)
        control_layout.addWidget(btn_retry)

        btn_stop = QtWidgets.QPushButton("STOP")
        btn_stop.clicked.connect(self.stop_robot)
        control_layout.addWidget(btn_stop)

        layout.addLayout(control_layout, 1)

    # ===== CAMERA =====
    def update_frame(self):
        ret, frame = self.cap.read()
        if ret:
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            h, w, ch = frame.shape
            bytes_per_line = ch * w
            qt_image = QtGui.QImage(frame.data, w, h, bytes_per_line,
                                    QtGui.QImage.Format_RGB888)
            self.video_label.setPixmap(QtGui.QPixmap.fromImage(qt_image))

    # ===== BUTTON ACTION =====
    def start_robot(self):
        self.status = "OTONOM"
        self.status_label.setText("STATUS: OTONOM")
        self.ros_node.send("start")

    def retry_connection(self):
        self.cap.release()
        self.cap.open(0)
        self.ros_node.send("retry")

    def stop_robot(self):
        self.status = "STOPPED"
        self.status_label.setText("STATUS: STOPPED")
        self.ros_node.send("stop")

    # ===== CLOSE EVENT =====
    def closeEvent(self, event):
        self.timer.stop()
        self.cap.release()
        rclpy.shutdown()
        event.accept()


# ================= MAIN =================
if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = RobotGUI()
    window.show()
    sys.exit(app.exec_())