import requests


SERVER = "http://127.0.0.1:5000"


def setLevel(level):
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
        return ()
