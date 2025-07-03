import sys, os
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

from ui.gui.main_window import OptimizerXWindow
from PyQt5.QtWidgets import QApplication

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = OptimizerXWindow()
    window.show()
    sys.exit(app.exec_())