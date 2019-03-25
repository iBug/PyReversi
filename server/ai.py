# File: ai.py
# Author: iBug

import random

# import some constants
from reversi import BS, EMPTY, BLACK, WHITE

inf = 999999  # Don't use math.inf
MIN_NODES = 10000
MIN_TICK = 1000

# flake8 ............
SCORE = [
    [  500, -150, 30, 10, 10, 30, -150,  500],  # noqa: E201, E241
    [ -150, -250,  0,  0,  0,  0, -250, -150],  # noqa: E201, E241
    [   30,    0,  1,  2,  2,  1,    0,   30],  # noqa: E201, E241
    [   10,    0,  2, 16, 16,  2,    0,   30],  # noqa: E201, E241
    [   10,    0,  2, 16, 16,  2,    0,   30],  # noqa: E201, E241
    [   30,    0,  1,  2,  2,  1,    0,   30],  # noqa: E201, E241
    [ -150, -250,  0,  0,  0,  0, -250, -150],  # noqa: E201, E241
    [  500, -150, 30, 10, 10, 30, -150,  500],  # noqa: E201, E241
]

BONUS = 30
LIBERTY = 8
STABILITY = [2, 4, 6, 10, 15]

AICONFIG = [
    (1, 22, 0),
    (2, 6, 1),
    (3, 6, 1),
    (3, 8, 2),
    (4, 10, 2),
    (4, 12, 3),
    (6, 14, 3),
    (6, 16, 4),
    (8, 18, 4)
]

DIRECTIONS = [(x - 1, y - 1) for i in range(3) for y, x in enumerate([i] * 3)]


class ReversiAI:
    def __init__(self):
        self.nodeCount = 0
        self.depth = 6
        self.maxDepth = None
        self.final = 16
        self.aiLevel = 8
        self.saveState = dict()
        self.setLevel()

    # Heuristic Reversi game evaluation methods, chosen at different difficulties
    # Some are more complex than others!
    #
    # Reference implementations:
    # https://yshan.github.io/othello/ (see JavaScript source code)
    # http://www.codeceo.com/article/android-reversi-game.html

    def heuristicEval_0(self, game, player):
        _, s1, s2 = game.chessCount
        return s1 - s2

    def heuristicEval_1(self, game, player):
        s = [0, 0, 0]
        for x in range(BS):
            for y in range(BS):
                if (x == 0 or x == BS - 1) and (y == 0 or y == BS - 1):
                    s[game.board[x][y]] += 5
                elif (x == 0 or x == BS - 1) or (y == 0 or y == BS - 1):
                    s[game.board[x][y]] += 2
                else:
                    s[game.board[x][y]] += 1
        return s[1] - s[2]

    def heuristicEval_2(self, game, player):
        return self.heuristicEval_1(game, player) * 2 + len(game.getAvailables(BLACK)) - len(game.getAvailables(WHITE))

    def heuristicEval_3(self, game, player):
        s = [0, 0, 0]
        for x in range(BS):
            for y in range(BS):
                s[game.board[x][y]] += STABILITY[self.stability(game, (x, y))]
        s[1] += len(game.getAvailables(BLACK))
        s[2] += len(game.getAvailables(WHITE))
        return s[1] - s[2]

    def heuristicEval_4(self, game, player):
        self.nodeCount += 1
        c1, c2, s1, s2 = 0, 0, 0, 0
        board = game.board
        for x in range(BS):
            for y in range(BS):
                chess = board[x][y]
                if chess == EMPTY:
                    continue
                liberty = 0
                for dx, dy in DIRECTIONS:
                        tx, ty = x + dx, y + dy
                        if 0 <= tx < BS and 0 <= ty < BS and board[tx][ty] == EMPTY:
                            liberty += 1
                if chess == BLACK:
                    c1 += 1
                    s1 += SCORE[x][y] - liberty * LIBERTY
                else:
                    c2 += 1
                    s2 += SCORE[x][y] - liberty * LIBERTY

        if c1 == 0:
            return -inf
        if c2 == 0:
            return inf
        if c1 + c2 == BS ** 2:
            if c1 > c2:
                return inf
            if c2 > c1:
                return -inf

        def checkCorner(pos, adjacents, dpos):
            nonlocal s1, s2

            x, y = pos
            dx, dy = dpos
            chess = board[x][y]
            if chess != EMPTY:
                for cx, cy in adjacents:
                    chess = board[cx][cy]
                    if chess == EMPTY:
                        continue
                    if chess == BLACK:
                        s1 -= SCORE[cx][cy]
                    else:
                        s2 -= SCORE[cx][cy]

                tx, ty = x, y
                for i in range(0, BS - 2):
                    tx += dx
                    if board[tx][ty] != chess:
                        break
                    if chess == BLACK:
                        s1 += BONUS
                    else:
                        s2 += BONUS

                tx, ty = x, y
                for i in range(0, BS - 2):
                    ty += dy
                    if board[tx][ty] != chess:
                        break
                    if chess == BLACK:
                        s1 += BONUS
                    else:
                        s2 += BONUS

        checkCorner((0, 0), [(0, 1), (1, 0), (1, 1)], (1, 1))
        checkCorner((BS - 1, 0), [(BS - 2, 0), (BS - 2, 1), (BS - 1, 1)], (-1, 1))
        checkCorner((0, BS - 1), [(0, BS - 2), (1, BS - 2), (1, BS - 1)], (1, -1))
        checkCorner((BS - 1, BS - 1), [(BS - 2, BS - 2), (BS - 2, BS - 1), (BS - 1, BS - 2)], (-1, -1))

        return s1 - s2

    def stability(self, game, pos):
        board = game.board
        x, y = pos
        chess = board[x][y]
        if chess == EMPTY:
            return 0
        other = [None, WHITE, BLACK]
        dx = [(0, 0), (-1, 1), (-1, 1), (1, -1)]
        dy = [(-1, 1), (0, 0), (-1, 1), (-1, 1)]

        degree = 0
        for k in range(4):
            tx = [x, x]
            ty = [y, y]
            for i in range(2):
                while 0 <= tx[i] + dx[k][i] < 8 and 0 <= ty[i] + dy[k][i] < 8 and \
                        board[tx[i] + dx[k][i]][ty[i] + dy[k][i]] == chess:
                    tx[i] += dx[k][i]
                    ty[i] += dy[k][i]
            if not (0 <= tx[0] + dx[k][0] < 8 and 0 <= ty[0] + dy[k][0] < 8) or \
                    not (0 <= tx[1] + dx[k][1] < 8 and 0 <= ty[1] + dy[k][1] < 8):
                degree += 1
            elif board[tx[0] + dx[k][0]][ty[0] + dy[k][0]] == other[chess] and \
                    board[tx[1] + dx[k][1]][ty[1] + dy[k][1]] == other[chess]:
                degree += 1
        return degree

    def exactScore(self, game, player):
        self.nodeCount += 1
        _, ccBlack, ccWhite = game.chessCount
        score = 0
        if ccBlack > ccWhite:
            score = inf
        elif ccBlack < ccWhite:
            score = -inf
        return score

    def getHeuristicScore(self, game, player, step):
        game.put(step)
        try:
            score = self.saveState[game]
        except KeyError:
            score = self.heuristicScore(game, player)
            self.saveState[game] = score
        game.undo()
        return score

    def heuristicSearch(self, game, player, depth, alpha, beta):
        if depth <= 0:
            try:
                return self.saveState[game]
            except KeyError:
                score = self.heuristicScore(game, player)
                self.saveState[game] = score
                return score

        maxMode = (game.current == BLACK)
        score = -inf - 1 if maxMode else inf + 1
        steps = game.getAvailables()
        bestStep = ()

        if len(steps) > 0:
            hValue = {}
            for step in steps:
                hValue[step] = self.getHeuristicScore(game, player, step)
            steps = sorted(steps, key=lambda s: hValue[s], reverse=maxMode)

            if depth == 1:
                step = steps[0]
                return hValue[step], step

            for step in steps:
                game.put(step)
                rscore, rstep = self.heuristicSearch(game, player, depth - 1, alpha, beta)
                game.undo()
                if maxMode:
                    if rscore > score:
                        score, bestStep = rscore, step
                    alpha = max(alpha, score)
                    if alpha >= beta:
                        # print("%d alpha cut: %d, %d" % (depth ,alpha, beta))
                        break
                else:
                    if rscore < score:
                        score, bestStep = rscore, step
                    beta = min(beta, score)
                    if alpha >= beta:
                        # print("%d beta cut: %d, %d" % (depth, alpha, beta))
                        break
        else:
            if not game.over:
                game.skipPut()
                rscore, rstep = self.heuristicSearch(game, player, depth, alpha, beta)
                game.undo()
                return rscore, ()
            else:
                return self.exactScore(game, player), ()
        return score, bestStep

    def exactSearch(self, game, player, depth, alpha, beta):
        if depth <= 0:
            return self.exactScore(game, player), ()

        maxMode = (game.current == BLACK)
        score = -inf - 1 if maxMode else inf + 1
        steps = game.getAvailables()
        bestStep = ()

        if len(steps) > 0:
            for step in steps:
                game.put(step)
                rscore, rstep = self.exactSearch(game, player, depth - 1, alpha, beta)
                game.undo()

                if maxMode:
                    if rscore > score:
                        score, bestStep = rscore, step
                    alpha = max(alpha, score)
                    if alpha >= beta:
                        break
                else:
                    if rscore < score:
                        score, bestStep = rscore, step
                    beta = min(beta, score)
                    if alpha >= beta:
                        break
        else:
            if not game.over:
                game.skipPut()
                rscore, rstep = self.exactSearch(game, player, depth, alpha, beta)
                game.undo()
                return rscore, ()
            else:
                return self.exactScore(game, player), ()
        return score, bestStep

    def setLevel(self, level=None):
        if level is None:
            level = self.aiLevel

        self.aiLevel = level
        self.depth, self.final, evalLevel = AICONFIG[level]
        self.heuristicScore = getattr(self, "heuristicEval_" + str(evalLevel))

        # Clear saved states
        self.saveState.clear()

    def findBestStep(self, game):
        player = game.current
        steps = game.getAvailables()
        _, ccBlack, ccWhite = game.chessCount
        cc = ccBlack + ccWhite
        if len(steps) <= 0:
            return ()

        # Random mode
        if cc <= (BS - 4) ** 2:
            randSteps = [(x, y) for x, y in steps
                         if 2 <= x < BS - 2 and 2 <= y < BS - 2]
            if len(randSteps) > 0:
                return random.choice(randSteps)

        # Final mode: exact search
        if cc >= BS ** 2 - self.final:
            self.maxDepth = BS ** 2 - cc
            self.nodeCount = 0
            rscore, rstep = self.exactSearch(game, player, self.maxDepth, -inf, inf)
            if rscore != -inf:
                return rstep

        # Heuristic search
        self.nodeCount = 0
        self.maxDepth = self.depth
        rscore, rstep = self.heuristicSearch(game, player, self.maxDepth, -inf, inf)
        return rstep
