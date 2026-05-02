import sys
import cv2
import json
import rclpy
from rclpy.node import Node
from std_msgs.msg import String
from PyQt5 import QtWidgets, QtGui, QtCore
from config import ConfigManager

config = ConfigManager()


# ================= ROS2 NODE ==================
class ROSNode(Node):
    def __init__(self, cfg):
        super().__init__(cfg['ros2']['node_name'])
        self.publisher = self.create_publisher(
            String,
            cfg['ros2']['topic'],
            cfg['ros2']['qos_depth']
        )

    def send_packet(self, packet: dict):
        """Kirim semua data sebagai 1 JSON packet"""
        msg = String()
        msg.data = json.dumps(packet)
        self.publisher.publish(msg)
        self.get_logger().info(f'GUI → ROS2 PACKET: {msg.data}')


# ================= GUI =================
class RobotGUI(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()

        # ===== STATE =====
        self.robot_status = "READY"
        self.color_mode   = "MERAH"
        self.checkpoints  = [False] * 12
        self.cmd_current  = "READY"

        # ===== ROS2 INIT =====
        rclpy.init()
        self.ros_node = ROSNode(config.config)
        self.ros_timer = QtCore.QTimer()
        self.ros_timer.timeout.connect(self.spin_ros)
        self.ros_timer.start(config.config['ros2']['spin_interval_ms'])

        # ===== WINDOW =====
        self.setWindowTitle(config.config['gui']['title'])
        self.setGeometry(100, 100, 1400, 800)
        self.setMinimumSize(1200, 700)
        self.setStyleSheet(self.get_global_styles())

        central_widget = QtWidgets.QWidget()
        self.setCentralWidget(central_widget)

        # ===== KAMERA =====
        self.cap = cv2.VideoCapture(
            config.config['camera']['device_path'],
            cv2.CAP_V4L2
        )
        self.cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)

        self.cam_timer = QtCore.QTimer()
        self.cam_timer.timeout.connect(self.update_frame)
        self.cam_timer.start(30)

        # ===== BUILD UI =====
        self.setup_ui(central_widget)

    # ------------------------------------------------------------------
    # STYLES
    # ------------------------------------------------------------------
    def get_global_styles(self):
        return """
        QMainWindow {
            background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                stop:0 #0a0f1e, stop:1 #1a2332);
            color: #e2e8f0;
        }
        QLabel  { color: #e2e8f0; font-weight: 500; }
        QFrame  {
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
            border-radius: 10px;
            padding: 10px 16px;
            font-size: 13px;
            font-weight: 600;
            min-height: 40px;
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

    # ------------------------------------------------------------------
    # LAYOUT UTAMA
    # ------------------------------------------------------------------
    def setup_ui(self, central_widget):
        root = QtWidgets.QHBoxLayout()
        root.setContentsMargins(16, 16, 16, 16)
        root.setSpacing(16)
        central_widget.setLayout(root)

        # KIRI (2/3): kamera + checkpoint + packet
        left_panel = self._build_left_panel()
        root.addWidget(left_panel, 7)

        # KANAN (1/3): status + warna + retry + action buttons
        right_panel = self._build_right_panel()
        root.addWidget(right_panel, 3)

    # ------------------------------------------------------------------
    # PANEL KIRI
    # Urutan: HEADER → [CAMERA | CHECKPOINT] → PACKET → TARGET
    # ------------------------------------------------------------------
    def _build_left_panel(self):
        panel = QtWidgets.QFrame()
        layout = QtWidgets.QVBoxLayout()
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)
        panel.setLayout(layout)

        # ── HEADER ──
        header = QtWidgets.QLabel("🎥  ROBOCON 2026 — VISION CONTROL")
        header.setAlignment(QtCore.Qt.AlignCenter)
        header.setStyleSheet("""
            font-size: 18px; font-weight: 700; color: #38bdf8;
            padding: 6px 12px;
            background: rgba(56,189,248,0.08);
            border-radius: 8px;
            border-left: 4px solid #38bdf8;
        """)
        layout.addWidget(header)

        # ── BARIS ATAS: kamera + 12 checkpoint ──
        top_row = QtWidgets.QHBoxLayout()
        top_row.setSpacing(12)
        top_row.addWidget(self._build_camera_widget(), alignment=QtCore.Qt.AlignTop)
        top_row.addWidget(self._build_checkpoint_panel(), alignment=QtCore.Qt.AlignTop)
        layout.addLayout(top_row)

        # ── PACKET INFO (mengisi ruang di antara top_row dan target) ──
        self.packet_label = QtWidgets.QLabel()
        self.packet_label.setStyleSheet("""
            background: rgba(0,0,0,0.4);
            border: 1px solid #1e293b;
            border-radius: 10px;
            padding: 10px;
            font-size: 11px;
            color: #22d3ee;
            font-family: monospace;
        """)
        self.packet_label.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignTop)
        self.packet_label.setWordWrap(True)
        # stretch=1 → packet mengisi semua ruang kosong antara top_row dan target
        layout.addWidget(self.packet_label, 1)
        self._update_packet_display()

        # ── TARGET STATUS BAR (paling bawah kiri) ──
        self.target_label = QtWidgets.QLabel("🎯  Target: TIDAK TERDETEKSI")
        self.target_label.setAlignment(QtCore.Qt.AlignCenter)
        self.target_label.setStyleSheet("""
            background: rgba(239,68,68,0.2);
            border: 1px solid #7f1d1d;
            border-radius: 10px;
            padding: 10px;
            font-size: 14px;
            font-weight: 600;
            color: #fca5a5;
        """)
        layout.addWidget(self.target_label)

        return panel

    # --- Kamera ---
    def _build_camera_widget(self):
        cam_frame = QtWidgets.QFrame()
        cam_frame.setFixedSize(500, 400)
        cam_frame.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        cam_frame.setStyleSheet("""
            QFrame {
                background: #0f172a;
                border: 1px solid #1e293b;
                border-radius: 12px;
            }
        """)

        cam_layout = QtWidgets.QVBoxLayout()
        cam_layout.setContentsMargins(12, 12, 12, 12)
        cam_layout.setSpacing(10)
        cam_frame.setLayout(cam_layout)

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

        return cam_frame

    # --- 12 Toggle Checkpoint ---
    def _build_checkpoint_panel(self):
        frame = QtWidgets.QFrame()
        layout = QtWidgets.QVBoxLayout()
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(8)
        frame.setFixedHeight(400)
        frame.setLayout(layout)

        title = QtWidgets.QLabel("📍  CHECKPOINT TOGGLE")
        title.setStyleSheet("""
            font-size: 13px; font-weight: 700; color: #38bdf8;
            padding: 4px 0;
            border-bottom: 1px solid #1e293b;
        """)
        title.setAlignment(QtCore.Qt.AlignCenter)
        layout.addWidget(title)

        grid_widget = QtWidgets.QWidget()
        grid = QtWidgets.QGridLayout()
        grid.setSpacing(8)
        grid_widget.setLayout(grid)

        self.cp_buttons = []
        for i in range(12):
            btn = QtWidgets.QPushButton(f"CP {i+1}")
            btn.setCheckable(True)
            btn.setSizePolicy(
                QtWidgets.QSizePolicy.Expanding,
                QtWidgets.QSizePolicy.Expanding
            )
            btn.setStyleSheet(self._cp_style_off())
            btn.toggled.connect(lambda checked, idx=i: self._on_checkpoint_toggle(idx, checked))
            row, col = divmod(i, 6)
            grid.addWidget(btn, row, col)
            self.cp_buttons.append(btn)

        for i in range(6):
            grid.setColumnStretch(i, 1)
        grid.setRowStretch(0, 1)
        grid.setRowStretch(1, 1)

        layout.addWidget(grid_widget, 1)
        return frame

    def _cp_style_off(self):
        return """
            QPushButton {
                background: #1e293b;
                color: #64748b;
                border: 1px solid #334155;
                border-radius: 8px;
                font-size: 12px;
                font-weight: 600;
            }
            QPushButton:hover { border-color: #3b82f6; color: #93c5fd; }
        """

    def _cp_style_on(self):
        return """
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #1d4ed8, stop:1 #1e3a8a);
                color: #bfdbfe;
                border: 2px solid #3b82f6;
                border-radius: 8px;
                font-size: 12px;
                font-weight: 700;
            }
        """

    # ------------------------------------------------------------------
    # PANEL KANAN
    # Urutan: STATUS → COLOR TOGGLE → RETRY → (spacer) → BRANDING → ACTION BUTTONS
    # ------------------------------------------------------------------
    def _build_right_panel(self):
        panel = QtWidgets.QFrame()
        layout = QtWidgets.QVBoxLayout()
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(16)
        panel.setLayout(layout)

        # STATUS
        self.status_label = QtWidgets.QLabel("🟢  STATUS: READY")
        self.status_label.setAlignment(QtCore.Qt.AlignCenter)
        self.status_label.setStyleSheet(self._status_style("#10b981", "#059669"))
        layout.addWidget(self.status_label)

        # WARNA KOTAK — TOGGLE MERAH / BIRU
        layout.addWidget(self._build_color_toggle())

        # RETRY KAMERA
        self.btn_retry = QtWidgets.QPushButton("🔄  RETRY KAMERA")
        self.btn_retry.setStyleSheet(self._btn_retry_dim())
        self.btn_retry.clicked.connect(self.retry_connection)
        layout.addWidget(self.btn_retry)

        # SPACER → dorong tombol aksi ke bawah
        layout.addStretch()

        # BRANDING
        info = QtWidgets.QLabel("🤖  Robocon 2026\nROS2 Vision Control v3.0")
        info.setAlignment(QtCore.Qt.AlignCenter)
        info.setStyleSheet("""
            background: rgba(59,130,246,0.1);
            border: 1px solid #3b82f6;
            border-radius: 10px;
            padding: 10px;
            font-size: 12px;
        """)
        layout.addWidget(info)

        # ACTION BUTTONS — pojok kanan bawah
        layout.addWidget(self._build_action_buttons())

        return panel

    # ------------------------------------------------------------------
    # STYLE HELPERS — action buttons (active glow vs dim)
    # ------------------------------------------------------------------
    def _btn_start_active(self):
        return """
            QPushButton {
                background: rgba(16, 185, 129, 0.35);
                color: #d1fae5;
                border: 2px solid #34d399;
                border-radius: 10px;
                font-size: 14px; font-weight: 700;
                min-height: 48px;
            }
            QPushButton:hover { background: rgba(16, 185, 129, 0.45); }
        """

    def _btn_start_dim(self):
        return """
            QPushButton {
                background: rgba(16, 185, 129, 0.10);
                color: #6ee7b7;
                border: 1px solid #10b981;
                border-radius: 10px;
                font-size: 14px; font-weight: 700;
                min-height: 48px;
            }
            QPushButton:hover { background: rgba(16, 185, 129, 0.20); color: #a7f3d0; }
        """

    def _btn_stop_active(self):
        return """
            QPushButton {
                background: rgba(239, 68, 68, 0.35);
                color: #fee2e2;
                border: 2px solid #f87171;
                border-radius: 10px;
                font-size: 14px; font-weight: 700;
                min-height: 48px;
            }
            QPushButton:hover { background: rgba(239, 68, 68, 0.45); }
        """

    def _btn_stop_dim(self):
        return """
            QPushButton {
                background: rgba(239, 68, 68, 0.10);
                color: #fca5a5;
                border: 1px solid #ef4444;
                border-radius: 10px;
                font-size: 14px; font-weight: 700;
                min-height: 48px;
            }
            QPushButton:hover { background: rgba(239, 68, 68, 0.20); color: #fecaca; }
        """

    def _btn_retry_active(self):
        return """
            QPushButton {
                background: rgba(56, 189, 248, 0.35);
                color: #e0f2fe;
                border: 2px solid #7dd3fc;
                border-radius: 10px;
                font-size: 13px; font-weight: 600;
                min-height: 40px;
            }
        """

    def _btn_retry_dim(self):
        return """
            QPushButton {
                background: rgba(56, 189, 248, 0.10);
                color: #7dd3fc;
                border: 1px solid #38bdf8;
                border-radius: 10px;
                font-size: 13px; font-weight: 600;
                min-height: 40px;
            }
            QPushButton:hover { background: rgba(56, 189, 248, 0.22); color: #bae6fd; }
        """

    # ------------------------------------------------------------------
    # 3 TOMBOL AKSI (vertikal, kanan bawah)
    # ------------------------------------------------------------------
    def _build_action_buttons(self):
        self.btn_start = QtWidgets.QPushButton("▶  START OTONOM")
        self.btn_start.setStyleSheet(self._btn_start_dim())
        self.btn_start.clicked.connect(self.start_robot)

        self.btn_stop = QtWidgets.QPushButton("⛔  EMERGENCY STOP")
        self.btn_stop.setStyleSheet(self._btn_stop_dim())
        self.btn_stop.clicked.connect(self.stop_robot)

        self.btn_reset = QtWidgets.QPushButton("🔄  RESET")
        self.btn_reset.setStyleSheet("""
            QPushButton {
                background: rgba(245, 158, 11, 0.10);
                color: #fcd34d;
                border: 1px solid #f59e0b;
                border-radius: 10px;
                font-size: 14px; font-weight: 700;
                min-height: 48px;
            }
            QPushButton:hover { background: rgba(245, 158, 11, 0.22); color: #fde68a; }
            QPushButton:pressed { background: rgba(245, 158, 11, 0.35); }
        """)
        self.btn_reset.clicked.connect(self.reset_robot)

        # QVBoxLayout → tombol susun vertikal
        frame = QtWidgets.QWidget()
        col = QtWidgets.QVBoxLayout()
        col.setSpacing(8)
        col.setContentsMargins(0, 0, 0, 0)
        frame.setLayout(col)

        col.addWidget(self.btn_start)
        col.addWidget(self.btn_stop)
        col.addWidget(self.btn_reset)

        return frame

    # --- Toggle Merah / Biru ---
    def _build_color_toggle(self):
        frame = QtWidgets.QFrame()
        layout = QtWidgets.QVBoxLayout()
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(8)
        frame.setLayout(layout)

        title = QtWidgets.QLabel("🎨  MODE WARNA KOTAK")
        title.setStyleSheet("font-size: 12px; color: #94a3b8; font-weight: 600;")
        title.setAlignment(QtCore.Qt.AlignCenter)
        layout.addWidget(title)

        self.btn_merah = QtWidgets.QPushButton("🔴  MODE MERAH")
        self.btn_merah.setCheckable(True)
        self.btn_merah.setChecked(True)
        self.btn_merah.setStyleSheet(self._color_btn_style("red", True))
        self.btn_merah.toggled.connect(lambda checked: self._on_color_toggle("MERAH", checked))

        self.btn_biru = QtWidgets.QPushButton("🔵  MODE BIRU")
        self.btn_biru.setCheckable(True)
        self.btn_biru.setStyleSheet(self._color_btn_style("blue", False))
        self.btn_biru.toggled.connect(lambda checked: self._on_color_toggle("BIRU", checked))

        layout.addWidget(self.btn_merah)
        layout.addWidget(self.btn_biru)
        return frame

    def _color_btn_style(self, color, active):
        if color == "red":
            if active:
                return "QPushButton { background: #dc2626; color: white; border: 2px solid #ef4444; border-radius: 8px; font-size: 13px; font-weight: 700; min-height: 40px; }"
            return "QPushButton { background: rgba(239,68,68,0.1); color: #fca5a5; border: 1px solid #7f1d1d; border-radius: 8px; font-size: 13px; min-height: 40px; }"
        else:
            if active:
                return "QPushButton { background: #1d4ed8; color: white; border: 2px solid #3b82f6; border-radius: 8px; font-size: 13px; font-weight: 700; min-height: 40px; }"
            return "QPushButton { background: rgba(59,130,246,0.1); color: #93c5fd; border: 1px solid #1e3a5f; border-radius: 8px; font-size: 13px; min-height: 40px; }"

    # ------------------------------------------------------------------
    # HELPERS STYLE
    # ------------------------------------------------------------------
    def _status_style(self, c1, c2):
        return f"""
            background: qlineargradient(x1:0,y1:0,x2:1,y2:1,stop:0 {c1},stop:1 {c2});
            border-radius: 12px; padding: 14px;
            font-size: 16px; font-weight: 700;
        """

    # ------------------------------------------------------------------
    # ROS2 PACKET
    # ------------------------------------------------------------------
    def _build_packet(self):
        cp_array = [i + 1 for i, v in enumerate(self.checkpoints) if v]
        return {
            "cmd":        self.cmd_current,
            "color":      self.color_mode,
            "checkpoints": cp_array,
            "status":     self.robot_status
        }

    def _publish_packet(self):
        packet = self._build_packet()
        self.ros_node.send_packet(packet)
        self._update_packet_display(packet)

    def _update_packet_display(self, packet=None):
        if packet is None:
            packet = self._build_packet()
        pretty = json.dumps(packet, indent=2)
        self.packet_label.setText(f"📡 LAST PACKET:\n{pretty}")

    # ------------------------------------------------------------------
    # EVENT HANDLERS
    # ------------------------------------------------------------------
    def _on_checkpoint_toggle(self, idx, checked):
        self.checkpoints[idx] = checked
        self.cp_buttons[idx].setStyleSheet(
            self._cp_style_on() if checked else self._cp_style_off()
        )
        self.cmd_current = "CHECKPOINT_UPDATE"
        self._publish_packet()

    def _on_color_toggle(self, color, checked):
        if not checked:
            return
        self.color_mode = color
        if color == "MERAH":
            self.btn_merah.setStyleSheet(self._color_btn_style("red", True))
            self.btn_biru.setChecked(False)
            self.btn_biru.setStyleSheet(self._color_btn_style("blue", False))
        else:
            self.btn_biru.setStyleSheet(self._color_btn_style("blue", True))
            self.btn_merah.setChecked(False)
            self.btn_merah.setStyleSheet(self._color_btn_style("red", False))
        self.cmd_current = "COLOR_CHANGE"
        self._publish_packet()

    def _set_action_state(self, active):
        """Update glow state: 'start', 'stop', atau None (reset/netral)"""
        if active == "start":
            self.btn_start.setStyleSheet(self._btn_start_active())
            self.btn_stop.setStyleSheet(self._btn_stop_dim())
        elif active == "stop":
            self.btn_stop.setStyleSheet(self._btn_stop_active())
            self.btn_start.setStyleSheet(self._btn_start_dim())
        else:  # reset / netral
            self.btn_start.setStyleSheet(self._btn_start_dim())
            self.btn_stop.setStyleSheet(self._btn_stop_dim())

    def start_robot(self):
        self.robot_status = "OTONOM"
        self.cmd_current  = config.config['ros2']['commands']['start']
        self.status_label.setText("🟢  STATUS: OTONOM")
        self.status_label.setStyleSheet(self._status_style("#10b981", "#059669"))
        self._set_action_state("start")
        self._publish_packet()

    def stop_robot(self):
        self.robot_status = "STOPPED"
        self.cmd_current  = config.config['ros2']['commands']['stop']
        self.status_label.setText("🔴  STATUS: STOPPED")
        self.status_label.setStyleSheet(self._status_style("#ef4444", "#dc2626"))
        self._set_action_state("stop")
        self._publish_packet()

    def reset_robot(self):
        self.robot_status = "READY"
        self.cmd_current  = "RESET"
        self.checkpoints  = [False] * 12
        for btn in self.cp_buttons:
            btn.setChecked(False)
            btn.setStyleSheet(self._cp_style_off())
        self.status_label.setText("🟡  STATUS: RESET")
        self.status_label.setStyleSheet(self._status_style("#f59e0b", "#d97706"))
        self._set_action_state(None)
        self._publish_packet()

    def retry_connection(self):
        self.cmd_current = config.config['ros2']['commands']['retry']
        # Glow sebentar → balik dim setelah 800ms
        self.btn_retry.setStyleSheet(self._btn_retry_active())
        QtCore.QTimer.singleShot(800, lambda: self.btn_retry.setStyleSheet(self._btn_retry_dim()))
        self._publish_packet()
        self.cap.release()
        QtCore.QTimer.singleShot(500, self.reconnect_camera)

    def reconnect_camera(self):
        self.cap.open(config.config['camera']['device_path'], cv2.CAP_V4L2)
        self.cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)

    # ------------------------------------------------------------------
    # KAMERA UPDATE
    # ------------------------------------------------------------------
    def update_frame(self):
        ret, frame = self.cap.read()
        if ret:
            frame = cv2.flip(frame, 1)
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            h, w  = frame.shape[:2]
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

    # ------------------------------------------------------------------
    # ROS2 SPIN & CLOSE
    # ------------------------------------------------------------------
    def spin_ros(self):
        rclpy.spin_once(self.ros_node, timeout_sec=0)

    def closeEvent(self, event):
        self.cam_timer.stop()
        self.ros_timer.stop()
        self.cap.release()
        cv2.destroyAllWindows()
        rclpy.shutdown()
        event.accept()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        if hasattr(self, 'video_label') and self.video_label.pixmap():
            pixmap = self.video_label.pixmap()
            if pixmap:
                self.video_label.setPixmap(
                    pixmap.scaled(self.video_label.size(),
                                  QtCore.Qt.KeepAspectRatio,
                                  QtCore.Qt.SmoothTransformation)
                )


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    app.setStyle('Fusion')
    window = RobotGUI()
    window.showMaximized()
    sys.exit(app.exec_())