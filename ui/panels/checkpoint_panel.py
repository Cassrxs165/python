from PyQt5 import QtWidgets, QtCore
from PyQt5.QtCore import pyqtSignal
from ui.styles import cp_style_off, cp_style_on

class CheckpointPanel(QtWidgets.QFrame):
    checkpoint_toggled = pyqtSignal(int, bool)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.buttons = []
        self._build_ui()

    def _build_ui(self):
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
            btn.setStyleSheet(cp_style_off())
            btn.toggled.connect(lambda checked, idx=i: self.checkpoint_toggled.emit(idx, checked))
            row, col = divmod(i, 6)
            grid.addWidget(btn, row, col)
            self.cp_buttons.append(btn)

        for i in range(6):
            grid.setColumnStretch(i, 1)
        grid.setRowStretch(0, 1)
        grid.setRowStretch(1, 1)

        layout.addWidget(grid_widget, 1)
        return frame
            

    def reset_all(self):
        for btn in self.cp_buttons:   # ← ganti dari self.buttons
            btn.setChecked(False)
            btn.setStyleSheet(cp_style_off())