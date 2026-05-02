import cv2
import rclpy
from PyQt5 import QtWidgets, QtCore
from config import ConfigManager
from core.ros_node import ROSNode
from ui.panels.camera_widget import CameraWidget
from ui.panels.checkpoint_panel import CheckpointPanel
from ui.panels.left_panel import LeftPanel
from ui.panels.right_panel import RightPanel
from ui.styles import get_global_styles
from core.robot_state import RobotState


config = ConfigManager()

class RobotGUI(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.setStyleSheet(get_global_styles())
        # ── Komponen inti ──
        self.state    = RobotState()
        self.ros_node = ROSNode(config.config)

        # ── ROS timer ──
        self.ros_timer = QtCore.QTimer()
        self.ros_timer.timeout.connect(self.spin_ros)
        self.ros_timer.start(config.config['ros2']['spin_interval_ms'])

        # ── Window setup ──
        self.setWindowTitle(config.config['gui']['title'])
        self.setGeometry(100, 100, 1400, 800)
        self.setMinimumSize(1200, 700)

        central_widget = QtWidgets.QWidget()
        self.setCentralWidget(central_widget)
        self.setStyleSheet(get_global_styles())
        # ── Buat semua panel ──
        self.cam_widget = CameraWidget(config.config)
        self.cp_panel   = CheckpointPanel()
        self.left_panel = LeftPanel(self.cam_widget, self.cp_panel)
        self.right_panel = RightPanel()

        # ── Layout ──
        root = QtWidgets.QHBoxLayout()
        root.setContentsMargins(16, 16, 16, 16)
        root.setSpacing(16)
        central_widget.setLayout(root)
        root.addWidget(self.left_panel, 7)
        root.addWidget(self.right_panel, 3)

        # ── Hubungkan semua signal ──
        self._connect_signals()

    def _connect_signals(self):
        self.cp_panel.checkpoint_toggled.connect(self._on_checkpoint_toggle)
        self.right_panel.start_requested.connect(self.start_robot)
        self.right_panel.stop_requested.connect(self.stop_robot)
        self.right_panel.reset_requested.connect(self.reset_robot)
        self.right_panel.color_changed.connect(self._on_color_change)
        self.right_panel.retry_requested.connect(self.retry_connection)

    # ── Event handlers — semua aksi ada di sini ──
    def _on_checkpoint_toggle(self, idx, checked):
        self.state.toggle_checkpoint(idx, checked)
        self.state.set_cmd("CHECKPOINT_UPDATE")
        self._publish()

    def _on_color_change(self, color):
        self.state.set_color(color)
        self.state.set_cmd("COLOR_CHANGE")
        self._publish()

    def start_robot(self):
        self.state.set_status("OTONOM")
        self.state.set_cmd(config.config['ros2']['commands']['start'])
        self.right_panel.update_status("🟢  STATUS: OTONOM", "#10b981", "#059669")
        self.right_panel.set_action_state("start")
        self._publish()

    def stop_robot(self):
        self.state.set_status("STOPPED")
        self.state.set_cmd(config.config['ros2']['commands']['stop'])
        self.right_panel.update_status("🔴  STATUS: STOPPED", "#ef4444", "#dc2626")
        self.right_panel.set_action_state("stop")
        self._publish()

    def reset_robot(self):
        self.state.reset()
        self.right_panel.update_status("🟡  STATUS: RESET", "#f59e0b", "#d97706")
        self.right_panel.set_action_state(None)
        self.cp_panel.reset_all()
        self._publish()

    def retry_connection(self):
        self.state.set_cmd(config.config['ros2']['commands']['retry'])
        self.right_panel.flash_retry()
        self._publish()
        QtCore.QTimer.singleShot(500, self.cam_widget.reconnect_camera)

    def _publish(self):
        packet = self.state.to_packet()
        self.ros_node.send_packet(packet)
        self.left_panel.update_packet_display(packet)

    def spin_ros(self):
        rclpy.spin_once(self.ros_node, timeout_sec=0)

    def closeEvent(self, event):
        self.cam_widget.release()
        self.ros_timer.stop()
        try:
            cv2.destroyAllWindows()
        except cv2.error:
            # GTK2 support not available on this system
            pass
        rclpy.shutdown()
        event.accept()

    