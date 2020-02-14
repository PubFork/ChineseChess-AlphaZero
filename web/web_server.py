import json
import multiprocessing as mp
import os
import sys

from flask import Flask, request, Response

from cchess_alphazero.config import Config
from cchess_alphazero.lib.logger import setup_logger

_PATH_ = os.path.dirname(os.path.dirname(__file__))

if _PATH_ not in sys.path:
    sys.path.append(_PATH_)

app = Flask(__name__)

user_map = list()


@app.route('/start', methods=['POST'])
def start():
    content = json.loads(request.data)
    print(content)
    topic_name = "demo"  # 使用一个topic来传递数据
    create_topic(topic_name)

    if content["id"] not in user_map:
        print("not in ")
        user_map.append(content["id"])
        background_process = mp.Process(name='background_process', target=active_game,
                                        args=(content, topic_name, content["id"]))
        background_process.daemon = True
        background_process.start()
    else:
        print("found")
    return Response(json.dumps(content), mimetype='application/json')


def create_topic(topic_name):
    print("create_topic")


def active_game(content=None, topic_name=None, user_id=-1):
    mp.freeze_support()
    sys.setrecursionlimit(10000)
    config_type = 'distribute'
    config = Config(config_type=config_type)
    config.resource.create_directories()
    setup_logger(config.resource.main_log_path)
    config.internet.distributed = False
    config.internet.username = "fcbai"
    config.opts.device_list = 1
    num_cores = mp.cpu_count()
    max_processes = num_cores // 2 if num_cores < 20 else 10
    search_threads = 10
    max_processes = int(max_processes)
    print(f"max_processes = {max_processes}, search_threads = {search_threads}")
    config.play.max_processes = max_processes
    config.play.search_threads = search_threads

    import cchess_alphazero.play_games.play_cli_invoke as play
    play.start(config, user_id=user_id)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
