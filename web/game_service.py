import multiprocessing as mp
import os
import sys
import time

from cchess_alphazero.config import Config
from cchess_alphazero.lib.logger import setup_logger
from web.network_helper import NetWorkConnection

_PATH_ = os.path.dirname(os.path.dirname(__file__))

if _PATH_ not in sys.path:
    sys.path.append(_PATH_)

network_helper = NetWorkConnection()


class GameService:
    def __init__(self):
        self.start_time = time.time()

    def active_game(self, user=None):
        mp.freeze_support()
        sys.setrecursionlimit(10000)
        config_type = 'distribute'
        config = Config(config_type=config_type)
        config.resource.create_directories()
        setup_logger(config.resource.main_log_path)
        config.internet.distributed = False
        config.internet.username = user.user_name
        config.opts.device_list = 1
        num_cores = mp.cpu_count()
        max_processes = num_cores // 2 if num_cores < 20 else 10
        search_threads = 10
        max_processes = int(max_processes)
        print(f"max_processes = {max_processes}, search_threads = {search_threads}")
        config.play.max_processes = max_processes
        config.play.search_threads = search_threads

        import cchess_alphazero.play_games.play_cli_invoke as play
        play.start(config, user=user)

    def is_ready(self, login_user):
        return network_helper.get_redis_client().get(login_user.token) is not None
