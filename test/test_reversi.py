import pytest

import reversi
from reversi import Reversi


def test_globals():
    assert reversi.BS == 8
    assert (reversi.EMPTY, reversi.BLACK, reversi.WHITE) == (0, 1, 2)


def test_reversi_reset():
    game = Reversi()
    game.reset()
    assert game.current == reversi.BLACK
    assert len(game.history) == 0
    assert len(game.board) == 8
    assert all(len(col) == 8 for col in game.board)
    # Ignoring board content. They may change some day


def test_reversi_toggle():
    game = Reversi()
    assert game.current == reversi.BLACK
    assert game.toggle() is None
    assert game.current == reversi.WHITE


@pytest.mark.parametrize("x, y, dx, dy, player, expected", [
    (2, 4, 1, 0, reversi.BLACK, True),
    (2, 4, 1, 0, reversi.WHITE, False),
    (3, 2, 0, 1, reversi.BLACK, False),
    (3, 2, 0, 1, reversi.WHITE, True),
    (2, 4, 1, 0, None, True),
])
def test_reversi_check(x, y, dx, dy, player, expected):
    game = Reversi()
    game.reset()
    assert game.check(x, y, dx, dy, player) == expected


@pytest.mark.parametrize("x, y, player, expected", [
    (2, 4, reversi.BLACK, True),
    (2, 4, reversi.WHITE, False),
    (2, 4, None, True),
])
def test_reversi_canPut(x, y, player, expected):
    game = Reversi()
    game.reset()
    assert game.canPut(x, y, player) == expected


def test_reversi_getAvailables():
    game = Reversi()
    game.reset()
    assert sorted(game.getAvailables()) == sorted([(2, 4), (3, 5), (4, 2), (5, 3)])
    game.toggle()
    assert sorted(game.getAvailables()) == sorted([(2, 3), (4, 5), (3, 2), (5, 4)])


def test_reversi_any():
    game = Reversi()
    game.reset()
    assert game.any()
    assert game.any(reversi.BLACK)
    assert game.any(reversi.WHITE)
    game.board[3][3] = game.board[3][4] = game.board[4][3] = game.board[4][4] = reversi.EMPTY
    assert not game.any(reversi.BLACK)
    assert not game.any(reversi.WHITE)


def test_reversi_over():
    game = Reversi()
    game.reset()
    assert not game.over
    game.board[3][3] = game.board[3][4] = game.board[4][3] = game.board[4][4] = reversi.EMPTY
    assert game.over


@pytest.mark.parametrize("x, y, expected", [
    (3, 3, reversi.BLACK),
    (3, 4, reversi.WHITE),
    (3, 5, reversi.EMPTY),
])
def test_reversi_at(x, y, expected):
    game = Reversi()
    game.reset()
    assert game.at(x, y) == expected


def test_reversi_lastChess():
    game = Reversi()
    game.reset()
    assert game.lastChess is None
    game.put(2, 4)
    assert game.lastChess == (2, 4)


def test_reversi_chessCount():
    game = Reversi()
    game.reset()
    assert game.chessCount == [60, 2, 2]


def test_reversi_put():
    game = Reversi()
    game.reset()
    assert game.put(2, 4)
    assert game.history[-1] == [(3, 4), (2, 4)]
    assert not game.put(2, 4)
    assert not game.put(0, 0)
    assert not game.put((0, 0))  # Tuple unpacking test
    assert game.put((2, 3))


def test_reversi_skipPut():
    game = Reversi()
    game.reset()
    assert not game.skipPut()
    game.board[3][3] = game.board[3][4] = game.board[4][3] = game.board[4][4] = reversi.EMPTY
    assert game.skipPut()
    assert game.history[-1] == []


def test_reversi_undo():
    game_1, game_2 = Reversi(), Reversi()
    game_1.reset()
    game_2.reset()
    assert game_1.board == game_2.board
    assert game_1.history == game_2.history == []
    assert game_1.undo() == (False, 0)
    game_1.put(2, 4)
    assert game_1.board != game_2.board
    assert game_1.history != game_2.history
    assert game_1.undo() == (True, 2)
    assert game_1.board == game_2.board
    assert game_1.history == game_2.history

    game_1.history.append([])
    game_1.toggle()
    assert game_1.undo() == (True, 0)


def test_reversi_copy():
    game = Reversi()
    game.reset()
    game.put(2, 4)
    other = game.copy()
    assert game is not other
    assert game.board == other.board
    assert all(a is not b for a, b in zip(game.board, other.board))
    assert game.current == other.current
    assert game.history == other.history
    assert all(a is not b for a, b in zip(game.history, other.history))


def test_reversi_hash():
    import random
    game = Reversi()
    s = set()
    s.add(game)
    assert len(s) == 1
    for i in range(12):
        game.put(random.choice(game.getAvailables()))
        assert game not in s
        s.add(game)


def test_reversi_repr():
    game = Reversi()
    game.reset()
    assert str(game)
    assert repr(game)
