# While these are written as constants, there's no guarantee that the program will work if any of them is changed

BS = 8  # Board size

EMPTY = 0
BLACK = 1
WHITE = 2
HASH_KEY = 18446744073709551557


class Reversi:
    def __init__(self):
        self.board = None
        self.current = None
        self.history = None
        self.reset()

    def reset(self):
        self.board = [[EMPTY for _ in range(BS)] for _ in range(BS)]
        self.board[3][3] = self.board[4][4] = BLACK
        self.board[3][4] = self.board[4][3] = WHITE
        self.current = BLACK
        self.history = []

    def toggle(self):
        self.current = [BLACK, WHITE][self.current == BLACK]

    def check(self, x, y, dx, dy, player=None, operate=False, func=lambda *a: None):
        if player is None:
            player = self.current

        found = False
        c = 0
        while True:
            x += dx
            y += dy
            if not (0 <= x < BS and 0 <= y < BS):
                break
            chess = self.board[x][y]
            if chess == EMPTY:
                break
            elif chess == player:
                found = True
                break
            else:
                c += 1

        if c > 0 and found:
            if operate:
                while c > 0:
                    x -= dx
                    y -= dy
                    self.board[x][y] = player
                    func(x, y)
                    c -= 1
            return True
        return False

    def canPut(self, x, y, player=None):
        if player is None:
            player = self.current

        if self.board[x][y] != EMPTY:
            return False
        return self.check(x, y, -1, -1, player) or self.check(x, y, 1, 1, player) or \
            self.check(x, y, -1, 0, player) or self.check(x, y, 1, 0, player) or \
            self.check(x, y, -1, 1, player) or self.check(x, y, 1, -1, player) or \
            self.check(x, y, 0, -1, player) or self.check(x, y, 0, 1, player)

    def getAvailables(self, player=None):
        if player is None:
            player = self.current

        return [(x, y) for x in range(BS) for y in range(BS) if self.canPut(x, y, player)]

    def any(self, player=None):
        if player is None:
            player = self.current

        return any(self.canPut(x, y, player) for x in range(BS) for y in range(BS))

    @property
    def over(self):
        return (not self.any(BLACK)) and (not self.any(WHITE))

    def at(self, x, y):
        return self.board[x][y]

    @property
    def lastChess(self):
        try:
            return self.history[-1][-1]
        except IndexError:
            return None

    @property
    def chessCount(self):
        # Relies on EMPTY, BLACK, WHITE == 0, 1, 2
        cc = [0, 0, 0]

        for x in range(BS):
            for y in range(BS):
                cc[self.board[x][y]] += 1
        return cc

    def put(self, x, y=None, player=None):
        if y is None:
            # Unpack the tuple
            x, y = x
        if self.board[x][y] != EMPTY:
            return False
        if player is None:
            player = self.current

        changes = []

        def saveChange(x, y):
            changes.append((x, y))

        self.check(x, y, -1, -1, player, True, saveChange)
        self.check(x, y, 1, 1, player, True, saveChange)
        self.check(x, y, -1, 0, player, True, saveChange)
        self.check(x, y, 1, 0, player, True, saveChange)
        self.check(x, y, -1, 1, player, True, saveChange)
        self.check(x, y, 1, -1, player, True, saveChange)
        self.check(x, y, 0, -1, player, True, saveChange)
        self.check(x, y, 0, 1, player, True, saveChange)

        if len(changes) == 0:
            return False

        self.board[x][y] = player
        changes.append((x, y))
        self.history.append(changes)
        self.toggle()
        self.skipPut()
        return True

    def skipPut(self):
        if self.any(self.current):
            return False

        self.history.append([])
        self.toggle()
        return True

    def undo(self):
        if len(self.history) == 0:
            return False, 0

        lastPlayer = [WHITE, BLACK][len(self.history) % 2]
        lastFlip = [BLACK, WHITE][lastPlayer == BLACK]
        lastOp = self.history.pop()
        if len(lastOp) == 0:
            self.toggle()
            return True, self.undo()[1]

        for x, y in lastOp:
            self.board[x][y] = lastFlip
        x, y = lastOp[-1]
        self.board[x][y] = EMPTY
        self.toggle()
        return True, len(lastOp)

    def copy(self):
        game = Reversi()
        game.board = [list(col) for col in self.board]
        game.history = [list(h) for h in self.history]
        game.current = self.current
        return game

    def __str__(self):
        return "\n".join(" ".join([".", "O", "X"][self.board[x][y]] for x in range(BS)) for y in range(BS))

    def __hash__(self):
        res = 0
        for x in range(8):
            for y in range(8):
                res = (3 * res + self.board[x][y]) % HASH_KEY
        return res ^ (1 + self.current)
