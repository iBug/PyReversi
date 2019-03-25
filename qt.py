from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *

import reversi
import ai_adapter


# Constants that will affect how it looks
BOARD_SIZE = 520  # Side length of whole board, including margin
GRID_SIZE = 60  # Side length of a grid, 8x8
PIECE_SIZE = 45  # Diameter of circle that represents a piece
DOT_SIZE = 10  # Dot indicator of possible moves
IND_SIZE = 128  # The score indicator on the left, diameter of circle
IND_BOARD_SIZE = 150  # Same as above, side length of canvas

margin = (BOARD_SIZE - 8 * GRID_SIZE) // 2  # Should be some 20
padding = (GRID_SIZE - PIECE_SIZE) // 2  # Should be some 10
d_padding = (GRID_SIZE - DOT_SIZE) // 2  # Should be some 25
ind_margin = (IND_BOARD_SIZE - IND_SIZE) // 2


class ReversiUI(QWidget):
    def __init__(self):
        self.game = reversi.Reversi()
        self.ai = ai_adapter
        self.ai.setLevel(0)
        self.humanSide = reversi.BLACK

        # Create layout
        super(ReversiUI, self).__init__()
        self.master = QHBoxLayout()
        self.controlBar = QVBoxLayout()
        self.infoBar = QVBoxLayout()
        self.score_str = "{}"
        self.scoreLabelA = ScoreIndicator(reversi.BLACK)
        self.scoreLabelB = ScoreIndicator(reversi.WHITE)
        self.painter = PaintArea()
        self.painter.setFocusPolicy(Qt.StrongFocus)
        self.init_ui()

    def init_ui(self):
        # Insert elements into layout
        self.master.addLayout(self.controlBar)
        self.master.addWidget(self.painter)
        self.controlBar.addLayout(self.infoBar)
        self.infoBar.addWidget(self.scoreLabelA)
        self.infoBar.addWidget(self.scoreLabelB)

        self.reset_button = QPushButton("New Game")
        self.undo_button = QPushButton("Undo")
        self.diffBox = QComboBox()
        self.diffBox.addItems([
            "1: Novice", "2: Easy", "3: Easy+",
            "4: Medium", "5: Medium+", "6: Hard",
            "7: Hard+", "8: Extreme", "9: Zhao JX"
        ])
        self.modeBox = QComboBox()
        self.modeBox.addItems(["I go first", "AI goes first"])
        self.controlBar.addWidget(self.modeBox)
        self.controlBar.addWidget(QSplitter())
        self.controlBar.addWidget(QLabel("Difficulty"))
        self.controlBar.addWidget(self.diffBox)
        self.controlBar.addWidget(self.undo_button)
        self.controlBar.addWidget(self.reset_button)

        # Add events
        def boardClick(event):
            """
            Event handler of mouse click on the "game board" canvas
            """
            ex, ey = event.x(), event.y()
            gx, gy = (ex - margin) // GRID_SIZE, (ey - margin) // GRID_SIZE
            rx, ry = ex - margin - gx * GRID_SIZE, ey - margin - gy * GRID_SIZE
            if 0 <= gx < 8 and 0 <= gy < 8 and \
                    abs(rx - GRID_SIZE / 2) < PIECE_SIZE / 2 > abs(ry - GRID_SIZE / 2):
                self.onClickBoard((gx, gy))

        def diffChange(index):
            """
            Event handler on "Difficulty" cascade menu changes
            """
            self.ai.setLevel(index)
            self.resetGame()

        def modeChange(index):
            """
            Event handler on "Who goes first" cascade menu changes
            """
            self.humanSide = [reversi.BLACK, reversi.WHITE][index]
            self.resetGame()

        self.reset_button.clicked.connect(self.resetGame)
        self.undo_button.clicked.connect(self.undoGame)
        self.painter.mouseReleaseEvent = boardClick
        self.diffBox.currentIndexChanged.connect(diffChange)
        self.modeBox.currentIndexChanged.connect(modeChange)

        self.setLayout(self.master)
        self.setWindowTitle("iBug Reversi: PyQt5")
        self.setWindowFlags(Qt.WindowMinimizeButtonHint | Qt.WindowCloseButtonHint | Qt.CustomizeWindowHint)

        self.show()
        self.resetGame()
        self.setFixedSize(self.size())

    def aiMove(self):
        """
        To perform an AI move
        """
        if self.humanTurn:
            return
        # print("ai moving:")
        aiMove = self.ai.findBestStep(self.game)
        # print("aiMove: {}".format(aiMove))
        if aiMove == ():
            return
        self.game.put(aiMove)
        self.update_ui(True)

    def onClickBoard(self, pos):
        """
        Game event handler on clicking the board
        """
        if not self.humanTurn:
            return  # Not your move, shouldn't respond
        x, y = pos
        if not self.game.canPut(x, y):
            return  # Bad move, ignore it
        self.game.put(x, y)
        self.update_ui(True)
        while not self.humanTurn and not self.game.over:
            if self.game.skipPut():
                break
            self.aiMove()
        # Check if game is over
        if self.game.over:
            sa, sb, sc = self.game.chessCount
            if self.humanSide == reversi.WHITE:
                sb, sc = sc, sb
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
        """
        Wrapped function to update the appearance of the board

        Primarily, setting data for the actual painter function to process
        """
        _, ccBlack, ccWhite = self.game.chessCount
        self.scoreLabelA.setNumber(ccBlack)
        self.scoreLabelB.setNumber(ccWhite)
        self.scoreLabelA.update()
        self.scoreLabelB.update()
        self.painter.assignBoard(self.game.board)
        if self.humanTurn:
            self.painter.assignDots(self.game.getAvailables())
            lastChess = self.game.lastChess
            if lastChess is not None:
                self.painter.assignSpecialDots([lastChess])
            else:
                self.painter.assignSpecialDots(None)
        else:
            self.painter.assignDots(None)
            self.painter.assignSpecialDots(None)
        self.painter.update()

    def update_ui(self, force=False):
        """
        Workaround of UI getting stuck at waiting AI calculation

        See: https://stackoverflow.com/q/49982509/5958455
        """
        self.update_board()
        if force:
            QApplication.instance().processEvents()

    def resetGame(self):
        """
        Start over the game
        """
        self.game.reset()
        self.update_ui()
        while not self.humanTurn and not self.game.over:
            if self.game.skipPut():
                break
            self.aiMove()

    def undoGame(self):
        """
        Undo the last move
        """
        while True:
            r, c = self.game.undo()
            if c == 0 and r:
                # The last operation is a skip
                continue
            if self.humanTurn or not r:
                break
        self.update_ui(True)


class PaintArea(QWidget):
    """
    The class that handles the drawing of the game board
    """

    def __init__(self, board=None):
        super(PaintArea, self).__init__()
        self.board = board
        self.dots = None
        self.spdots = None

        self.setPalette(QPalette(Qt.white))
        self.setAutoFillBackground(True)
        self.setMinimumSize(BOARD_SIZE, BOARD_SIZE)

        self.penConfig = \
            [Qt.black, 2, Qt.PenStyle(Qt.SolidLine), Qt.PenCapStyle(Qt.RoundCap), Qt.PenJoinStyle(Qt.MiterJoin)]
        self.noPen = \
            QPen(Qt.black, 2, Qt.PenStyle(Qt.NoPen), Qt.PenCapStyle(Qt.RoundCap), Qt.PenJoinStyle(Qt.MiterJoin))
        brushColorFrame = QFrame()
        brushColorFrame.setAutoFillBackground(True)
        brushColorFrame.setPalette(QPalette(Qt.white))
        self.brushConfig = Qt.white, Qt.SolidPattern
        self.update()

    def assignBoard(self, board):
        # Copy the board to avoid accidental change to original board
        self.board = [list(i) for i in board]

    def assignDots(self, dots):
        # This one won't change, no need to copy
        self.dots = dots

    def assignSpecialDots(self, dots):
        # This one won't change, no need to copy
        self.spdots = dots

    def paintEvent(self, QPaintEvent):
        """
        Called by QWidget (superclass) when an update event arrives
        """
        if self.board is None:
            raise ValueError("Cannot paint an empty board!")
        p = QPainter(self)

        self.penConfig[0] = Qt.blue
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

        self.penConfig[0] = Qt.black
        p.setPen(QPen(*self.penConfig))
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

        # Draw dot indicators if available
        if self.dots is not None:
            p.setPen(self.noPen)
            p.setBrush(QBrush(Qt.blue, Qt.SolidPattern))
            for x, y in self.dots:
                p.drawEllipse(QRect(
                    margin + d_padding + x * GRID_SIZE, margin + d_padding + y * GRID_SIZE,
                    DOT_SIZE, DOT_SIZE))

        # Draw special dots if available
        if self.spdots is not None:
            p.setPen(self.noPen)
            p.setBrush(QBrush(Qt.red, Qt.SolidPattern))
            for x, y in self.spdots:
                p.drawEllipse(QRect(
                    margin + d_padding + x * GRID_SIZE, margin + d_padding + y * GRID_SIZE,
                    DOT_SIZE, DOT_SIZE))


class ScoreIndicator(QWidget):
    """
    The class that handles the drawing of the score indicator on the left
    """

    def __init__(self, color):
        super(ScoreIndicator, self).__init__()
        self.color = color
        self.number = None
        self.borderPen = \
            QPen(Qt.black, 3, Qt.PenStyle(Qt.SolidLine), Qt.PenCapStyle(Qt.RoundCap), Qt.PenJoinStyle(Qt.MiterJoin))

        self.setAutoFillBackground(False)
        self.setMinimumSize(IND_BOARD_SIZE, IND_BOARD_SIZE)

    def setNumber(self, n):
        self.number = n

    def paintEvent(self, event):
        p = QPainter(self)

        b = QRect(ind_margin, ind_margin, IND_SIZE, IND_SIZE)
        # Draw background circles
        if self.color == reversi.BLACK:
            p.setBrush(QBrush(Qt.black, Qt.SolidPattern))
        elif self.color == reversi.WHITE:
            p.setBrush(QBrush(Qt.white, Qt.SolidPattern))
        else:
            raise ValueError("Invalid color set!")
        p.setPen(self.borderPen)
        p.drawEllipse(b)

        # Add numbers (text)
        if self.color == reversi.BLACK:
            p.setPen(QPen(Qt.white, 48))
        elif self.color == reversi.WHITE:
            p.setPen(QPen(Qt.black, 48))
        p.setFont(QFont("Arial", 48, QFont.Bold))
        p.drawText(b, Qt.AlignCenter, str(self.number))
