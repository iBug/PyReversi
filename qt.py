from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *

import reversi
import ai


BOARD_SIZE = 680
GRID_SIZE = 80
PIECE_SIZE = 60
margin = (BOARD_SIZE - 8 * GRID_SIZE) // 2  # Should be some 20
padding = (GRID_SIZE - PIECE_SIZE) // 2  # Should be some 10


class ReversiUI(QWidget):
    def __init__(self):
        self.game = reversi.Reversi()
        self.ai = ai.Reversi_AI()
        self.ai.setLevel(0)
        self.humanSide = 1

        super(ReversiUI, self).__init__()
        self.vbox = QVBoxLayout()
        self.hbox = QHBoxLayout()
        self.infoBar = QHBoxLayout()
        self.score_str = "{1} : {2}"
        self.scoreLabel = QLabel(self.score_str)
        self.painter = PaintArea()
        self.init_ui()

    def init_ui(self):
        self.vbox.addWidget(self.painter)
        self.vbox.addLayout(self.infoBar)
        self.vbox.addLayout(self.hbox)
        self.infoBar.addWidget(self.scoreLabel)

        self.scoreLabel.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.scoreLabel.setAlignment(Qt.AlignCenter)
        self.scoreLabel.setFont(QFont("Arial", 24, QFont.Bold))

        self.reset_button = QPushButton("Reset")
        self.diffBox = QComboBox()
        self.diffBox.addItems([
            "1: Stupid", "2: Easy", "3: Easy+",
            "4: Medium", "5: Medium+", "6: Hard",
            "7: Expert", "8: Extreme", "9: TaoKY"
        ])
        self.hbox.addWidget(self.diffBox)
        self.hbox.addWidget(self.reset_button)

        # Add events
        self.reset_button.clicked.connect(self.resetGame)
        def boardClick(event):
            ex, ey = event.x(), event.y()
            gx, gy = (ex - margin) // GRID_SIZE, (ey - margin) // GRID_SIZE
            rx, ry = ex - margin - gx * GRID_SIZE, ey - margin - gy * GRID_SIZE
            if 0 <= gx < 8 and 0 <= gy < 8 and abs(rx - GRID_SIZE/2) < PIECE_SIZE/2 > abs(ry - GRID_SIZE/2):
                self.onClickBoard((gx, gy))
        self.painter.mouseReleaseEvent = boardClick

        def diffChange(index):
            self.ai.setLevel(index)
            self.resetGame()
        self.diffBox.currentIndexChanged.connect(diffChange)

        self.setLayout(self.vbox)
        self.setWindowTitle("iBug Reversi: PyQt5")
        self.setWindowFlags(Qt.WindowMinimizeButtonHint | Qt.WindowCloseButtonHint | Qt.CustomizeWindowHint)

        self.show()
        self.resetGame()
        self.setFixedSize(self.size())

    def onClickBoard(self, pos):
        if not self.humanTurn:
            return
        x, y = pos
        if not self.game.canPut(x, y):
            return
        self.game.put(x, y)
        self.update_board()
        while not self.humanTurn:
            aiMove = self.ai.findBestStep(self.game)
            if aiMove == ():
                break
            self.game.put(aiMove)
            self.update_board()
        if self.game.over:
            sa, sb, sc = game.chessCount
            if sb > sc:
                QMessageBox.information(self, "iBug Reversi", "You Win!")
            elif sb < sc:
                QMessageBox.information(self, "iBug Reversi", "You Lose!")
            elif sb == sc:
                QMessageBox.information(self, "iBug Reversi", "Tie!")


    @property
    def humanTurn(self):
        return self.humanSide == self.game.current and not self.game.over

    def update_board(self):
        self.scoreLabel.setText(self.score_str.format(*self.game.chessCount))
        self.painter.assignBoard(self.game.board)
        self.painter.update()

    def update_ui(self):
        self.update_board()

    def resetGame(self):
        self.game.reset()
        self.update_ui()


class PaintArea(QWidget):
    def __init__(self, board=None):
        super(PaintArea, self).__init__()
        self.board = board

        self.setPalette(QPalette(Qt.white))
        self.setAutoFillBackground(True)
        self.setMinimumSize(BOARD_SIZE, BOARD_SIZE)

        self.penConfig = Qt.black, 3, Qt.PenStyle(Qt.SolidLine), Qt.PenCapStyle(Qt.RoundCap), Qt.PenJoinStyle(Qt.MiterJoin)
        brushStyle = Qt.SolidPattern
        brushColorFrame = QFrame()
        brushColorFrame.setAutoFillBackground(True)
        brushColorFrame.setPalette(QPalette(Qt.white))
        self.brushConfig = Qt.white, Qt.SolidPattern
        self.update()

    def assignBoard(self, board):
        self.board = [list(i) for i in board]

    def paintEvent(self, QPaintEvent):
        if self.board is None:
            raise ValueError("Cannot paint an empty board!")
        p = QPainter(self)
        p.setPen(QPen(*self.penConfig))
        p.setBrush(QBrush(*self.brushConfig))

        # Draw the grids
        for i in range(9):
            A = QPoint(margin, margin + i * GRID_SIZE)
            B = QPoint(BOARD_SIZE - margin, margin + i * GRID_SIZE)
            p.drawLine(A, B)
            A = QPoint(margin + i * GRID_SIZE, margin)
            B = QPoint(margin + i * GRID_SIZE, BOARD_SIZE - margin)
            p.drawLine(A, B)

        # Draw game pieces
        for i in range(8):
            for j in range(8):
                if self.board[i][j] == 0:
                    continue
                fillColor = [None, Qt.black, Qt.white]
                p.setBrush(QBrush(fillColor[self.board[i][j]], Qt.SolidPattern))
                p.drawEllipse(QRect(
                    margin + padding + i * GRID_SIZE, margin + padding + j * GRID_SIZE,
                    PIECE_SIZE, PIECE_SIZE))
