import qt
import sys
from PyQt5.QtWidgets import QApplication


if __name__ == "__main__":
    app = QApplication(sys.argv)
    ui = qt.ReversiUI()
    sys.exit(app.exec_())
