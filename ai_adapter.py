import requests


# This should be the port the Flask server is listening to
# It's recommended to run the server with PyPy for its performance boost
SERVER = "http://127.0.0.1:5000"


def setLevel(level):
    """
    Set difficulty level of AI algorithm
    """
    # Construct POST data
    payload = {
        'action': "set_difficulty",
        'data': {
            'level': level
        }
    }
    response = requests.post(SERVER, json=payload).json()
    try:
        return response['message'] == "success"
    except Exception:
        print(response)


def findBestStep(game):
    """
    Send current board to the server and retrieve the "best move"
    """
    # Construct POST data
    payload = {
        'action': "get_move",
        'data': {
            'board': game.board,
            'current': game.current
        }
    }
    response = requests.post(SERVER, json=payload).json()
    try:
        return response["move"]["x"], response["move"]["y"]
    except KeyError:
        return ()  # Something bad?
