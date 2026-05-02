import sys
import os
import rclpy

sys.path.insert(0, os.path.dirname(__file__))

from PyQt5 import QtWidgets
from ui.main_window import RobotGUI


if __name__ == "__main__":
    rclpy.init()  # ← WAJIB sebelum membuat ROSNode

    app = QtWidgets.QApplication(sys.argv)
    app.setStyle("Fusion")

    window = RobotGUI()
    window.showMaximized()

    sys.exit(app.exec_())