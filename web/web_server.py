import json
import multiprocessing as mp
import os
import sys
import time
import uuid

from flask import Flask, request, Response
from flask import abort

from web.config import UserConfigEncoder, UserConfig
from web.game_service import GameService
from web.user_service import UserService

_PATH_ = os.path.dirname(os.path.dirname(__file__))

if _PATH_ not in sys.path:
    sys.path.append(_PATH_)

app = Flask(__name__)

user_service = UserService()
game_service = GameService()


@app.route('/start', methods=['POST'])
def start():
    content = json.loads(request.data)
    print(content)
    user = UserConfig(id=content['id'], user_name=content['user_name'], token=content['token'])

    if not user_service.verify_token(user.token):
        abort(401)

    if game_service.is_ready(user):
        return Response(json.dumps(content), mimetype='application/json')

    background_process = mp.Process(name='background_process',
                                    target=game_service.active_game,
                                    args=[user])
    background_process.daemon = True
    background_process.start()
    while not game_service.is_ready(user):
        print("waiting init game house")
        time.sleep(3)
    return Response(json.dumps(content), mimetype='application/json')



@app.route('/login', methods=['POST'])
def login():
    content = json.loads(request.data)
    user = user_service.login(content['user_name'], content['password'])
    if user is not None:
        return Response(init_user_game_info(user), mimetype='application/json')
    else:
        abort(404)


def init_user_game_info(user):
    user_info = UserConfigEncoder().encode(UserConfig(
        id=user.id,
        user_name=user.user_name,
        token=user.token))
    return user_info


@app.route('/register', methods=['POST'])
def register():
    content = json.loads(request.data)
    user = user_service.register(content['user_name'], content['password'])
    return Response(init_user_game_info(user), mimetype='application/json')


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
