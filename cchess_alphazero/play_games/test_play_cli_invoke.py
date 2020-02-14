import multiprocessing as mp
import os
import sys

import cchess_alphazero.environment.static_env as senv
from cchess_alphazero.config import Config
from cchess_alphazero.lib.logger import setup_logger

_PATH_ = os.path.dirname(os.path.dirname(__file__))

if _PATH_ not in sys.path:
    sys.path.append(_PATH_)


def test_invoke():
    user_map = dict()
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

    user_map["1"] = senv.INIT_STATE
    state = user_map["1"]
    state = senv.step(state, "0001")

    import cchess_alphazero.play_games.play_cli_invoke as play
    play.start(config)
    # response = engine_server.start(config, state)
    # print(response)


if __name__ == "__main__":
    # test_ucci()
    # test_static_env()
    test_invoke()
