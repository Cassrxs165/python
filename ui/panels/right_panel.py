# ui/panels/right_panel.py
from PyQt5 import QtWidgets, QtCore
from PyQt5.QtCore import pyqtSignal

class RightPanel(QtWidgets.QFrame):

    # ── Signal ── panel hanya "teriak", main_window yang dengar
    start_requested = pyqtSignal()
    stop_requested  = pyqtSignal()
    reset_requested = pyqtSignal()
    color_changed   = pyqtSignal(str)
    retry_requested = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._build_ui()

    # ── _build_right_panel() dipindah ke sini ──
    def _build_ui(self):
        layout = QtWidgets.QVBoxLayout()
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(16)
        self.setLayout(layout)

        # STATUS LABEL
        self.status_label = QtWidgets.QLabel("🟢  STATUS: READY")
        self.status_label.setAlignment(QtCore.Qt.AlignCenter)
        self.status_label.setStyleSheet(self._status_style("#10b981", "#059669"))
        layout.addWidget(self.status_label)

        # WARNA TOGGLE
        layout.addWidget(self._build_color_toggle())

        # RETRY
        self.btn_retry = QtWidgets.QPushButton("🔄  RETRY KAMERA")
        self.btn_retry.setStyleSheet(self._btn_retry_dim())
        self.btn_retry.clicked.connect(self.retry_requested.emit)  # ← emit
        layout.addWidget(self.btn_retry)

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

        layout.addWidget(self._build_action_buttons())

    # ── Pindah dari testGUI.py, hanya ganti .connect() ──
    def _build_action_buttons(self):
        self.btn_start = QtWidgets.QPushButton("▶  START OTONOM")
        self.btn_start.setStyleSheet(self._btn_start_dim())
        self.btn_start.clicked.connect(self.start_requested.emit)  # ← emit

        self.btn_stop = QtWidgets.QPushButton("⛔  EMERGENCY STOP")
        self.btn_stop.setStyleSheet(self._btn_stop_dim())
        self.btn_stop.clicked.connect(self.stop_requested.emit)    # ← emit

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
        self.btn_reset.clicked.connect(self.reset_requested.emit)  # ← emit

        frame = QtWidgets.QWidget()
        col = QtWidgets.QVBoxLayout()
        col.setSpacing(8)
        col.setContentsMargins(0, 0, 0, 0)
        frame.setLayout(col)
        col.addWidget(self.btn_start)
        col.addWidget(self.btn_stop)
        col.addWidget(self.btn_reset)
        return frame

    # right_panel.py — ganti _build_color_toggle() yang rusak ini:
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
        self.btn_merah.toggled.connect(
            lambda checked: self._on_color_toggle("MERAH", checked)
        )

        self.btn_biru = QtWidgets.QPushButton("🔵  MODE BIRU")
        self.btn_biru.setCheckable(True)
        self.btn_biru.setStyleSheet(self._color_btn_style("blue", False))
        self.btn_biru.toggled.connect(
            lambda checked: self._on_color_toggle("BIRU", checked)
        )

        layout.addWidget(self.btn_merah)
        layout.addWidget(self.btn_biru)
        return frame
    
    def _on_color_toggle(self, color, checked):
        if not checked:
            return
        # ← style tombol tetap di sini (tampilan)
        if color == "MERAH":
            self.btn_merah.setStyleSheet(self._color_btn_style("red", True))
            self.btn_biru.setChecked(False)
            self.btn_biru.setStyleSheet(self._color_btn_style("blue", False))
        else:
            self.btn_biru.setStyleSheet(self._color_btn_style("blue", True))
            self.btn_merah.setChecked(False)
            self.btn_merah.setStyleSheet(self._color_btn_style("red", False))
        # ← TIDAK ada color_mode, cmd_current, publish — hanya emit
        self.color_changed.emit(color)

    # ── Dipanggil dari main_window untuk update tampilan ──
    def update_status(self, text: str, c1: str, c2: str):
        self.status_label.setText(text)
        self.status_label.setStyleSheet(self._status_style(c1, c2))

    def set_action_state(self, active):
        # ← pindah dari _set_action_state() di testGUI.py, tidak ada yang berubah
        if active == "start":
            self.btn_start.setStyleSheet(self._btn_start_active())
            self.btn_stop.setStyleSheet(self._btn_stop_dim())
        elif active == "stop":
            self.btn_stop.setStyleSheet(self._btn_stop_active())
            self.btn_start.setStyleSheet(self._btn_start_dim())
        else:
            self.btn_start.setStyleSheet(self._btn_start_dim())
            self.btn_stop.setStyleSheet(self._btn_stop_dim())

    def flash_retry(self):
        # ← logika glow retry pindah ke sini dari testGUI.py
        self.btn_retry.setStyleSheet(self._btn_retry_active())
        QtCore.QTimer.singleShot(
            800, lambda: self.btn_retry.setStyleSheet(self._btn_retry_dim())
        )

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
    def _color_btn_style(self, color, active):
        if color == "red":
            if active:
                return "QPushButton { background: #dc2626; color: white; border: 2px solid #ef4444; border-radius: 8px; font-size: 13px; font-weight: 700; min-height: 40px; }"
            return "QPushButton { background: rgba(239,68,68,0.1); color: #fca5a5; border: 1px solid #7f1d1d; border-radius: 8px; font-size: 13px; min-height: 40px; }"
        else:
            if active:
                return "QPushButton { background: #1d4ed8; color: white; border: 2px solid #3b82f6; border-radius: 8px; font-size: 13px; font-weight: 700; min-height: 40px; }"
            return "QPushButton { background: rgba(59,130,246,0.1); color: #93c5fd; border: 1px solid #1e3a5f; border-radius: 8px; font-size: 13px; min-height: 40px; }"

    def _status_style(self, c1, c2):
        return f"""
            background: qlineargradient(x1:0,y1:0,x2:1,y2:1,stop:0 {c1},stop:1 {c2});
            border-radius: 12px; padding: 14px;
            font-size: 16px; font-weight: 700;
        """

