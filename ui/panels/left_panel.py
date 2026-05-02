from PyQt5 import QtWidgets
import json


class LeftPanel(QtWidgets.QFrame):
    def __init__(self, cam_widget, cp_panel, parent=None):
        super().__init__(parent)

        self.cam_widget = cam_widget
        self.cp_panel = cp_panel

        self._build_ui()

    def _build_ui(self):
        # style panel kiri
        self.setFrameShape(QtWidgets.QFrame.StyledPanel)

        layout = QtWidgets.QVBoxLayout()
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(12)

        # 1. Camera Widget
        layout.addWidget(self.cam_widget, 5)

        # 2. Checkpoint Panel
        layout.addWidget(self.cp_panel, 2)

        # 3. Packet Label
        self.packet_label = QtWidgets.QLabel("📡 LAST PACKET:")
        self.packet_label.setWordWrap(True)
        self.packet_label.setStyleSheet("""
            QLabel {
                background: rgba(59,130,246,0.08);
                border: 1px solid #3b82f6;
                border-radius: 10px;
                padding: 10px;
                font-size: 12px;
            }
        """)

        layout.addWidget(self.packet_label, 1)

        self.setLayout(layout)

    def _build_packet(self):
        return {
            "status": "default"
        }

    def update_packet_display(self, packet: dict):
        if packet is None:
            packet = self._build_packet()

        pretty = json.dumps(packet, indent=2)
        self.packet_label.setText(f"📡 LAST PACKET:\n{pretty}")