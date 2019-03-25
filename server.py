from flask import *
from reversi import Reversi
from ai import ReversiAI


app = Flask(__name__)


game = Reversi()
ai = ReversiAI()


@app.route("/", methods=["POST"])
def index():
    try:
        data = request.get_json()
        action = data['action']
        data = data['data']
        if action == "set_difficulty":
            return set_difficulty(data)
        elif action == "get_move":
            return get_next_move(data)
    except Exception as e:
        from traceback import format_tb
        import sys
        print("".join(format_tb(sys.exc_info()[2])))
        return jsonify({'error': {'exception': type(e).__name__, 'message': str(e)}}), 400


def set_difficulty(data):
    global ai
    if 0 <= data['level'] < 8:
        print("Set AI level {}".format(data['level']))
        ai.setLevel(data['level'])
        return jsonify({'message': "success"})
    return jsonify({'message': "invalid difficulty level"}), 400


def get_next_move(data):
    global ai, game
    try:
        # Reconstruct game board from incoming data
        game.current = data['current']
        game.board = data['board']
        game.history = []

        # Calculate best move
        x, y = ai.findBestStep(game)
        return jsonify({'move': {'x': x, 'y': y}})
    except Exception as e:
        return jsonify({'error': {'exception': type(e).__name__, 'message': str(e)}}), 400


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
