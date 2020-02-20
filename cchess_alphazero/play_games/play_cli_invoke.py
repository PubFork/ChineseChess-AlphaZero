import json
from collections import defaultdict
from logging import getLogger
import paho.mqtt.client as mqtt
from cchess_alphazero.agent.model import CChessModel
from cchess_alphazero.agent.player import CChessPlayer, VisitState
from cchess_alphazero.config import Config
from cchess_alphazero.environment.env import CChessEnv
from cchess_alphazero.environment.lookup_tables import flip_move
from cchess_alphazero.lib.model_helper import load_best_model_weight
from cchess_alphazero.lib.tf_util import set_session_config
from web.config import UserConfigEncoder
from web.network_helper import NetWorkConnection

try:
    import queue
except ImportError:
    import Queue as queue

logger = getLogger(__name__)


class ActionResponse():
    def __init__(self):
        self.id = 0
        self.current_x = 0
        self.current_y = 0
        self.target_x = 0
        self.target_y = 0
        self.action = None
        self.win = -1  # 0 is ai 1 is human


message_queue = queue.LifoQueue()

network_helper = NetWorkConnection()


def start(config: Config, human_move_first=True, user=None):
    set_session_config(per_process_gpu_memory_fraction=1, allow_growth=True, device_list="0")
    play = PlayWithHuman(config)
    play.start(human_move_first, user=user)


class PlayWithHuman:
    def __init__(self, config: Config):
        self.config = config
        self.env = CChessEnv()
        self.model = None
        self.pipe = None
        self.ai = None
        self.chessmans = None
        self.human_move_first = True

    def load_model(self):
        self.model = CChessModel(self.config)
        if self.config.opts.new or not load_best_model_weight(self.model):
            self.model.build()

    def start(self, human_first=True, user=None):
        self.env.reset()
        self.load_model()
        self.pipe = self.model.get_pipes()
        self.ai = CChessPlayer(self.config, search_tree=defaultdict(VisitState), pipes=self.pipe,
                               enable_resign=True, debugging=False)
        self.human_move_first = human_first

        self.env.board.print_to_cl()

        def on_connect(client, userdata, flags, rc):
            print("Connected with result code " + str(rc))
            client.subscribe(network_helper.network_connection_config.mqtt_receive_topic_name)
            print(f"save : {UserConfigEncoder().encode(user)}")
            network_helper.get_redis_client().set(user.token, UserConfigEncoder().encode(user))
            print(network_helper.get_redis_client().get(user.token))

        def on_message(client, userdata, msg):
            print(msg.topic + " " + str(msg.payload))
            if self.env.board.is_end():
                self.ai.close()
                print(f"胜者是 is {self.env.board.winner} !!!")
                self.env.board.print_record()
                client.disconnect()

            data = json.loads(msg.payload)
            self.env.board.calc_chessmans_moving_list()
            is_correct_chessman = False
            is_correct_position = False
            chessman = None
            while not is_correct_chessman:
                x, y = data["current_x"], data["current_y"]
                chessman = self.env.board.chessmans[x][y]
                if chessman is not None and chessman.is_red == self.env.board.is_red_turn:
                    is_correct_chessman = True
                    print(f"当前棋子为{chessman.name_cn}，可以落子的位置有：")
                    for point in chessman.moving_list:
                        print(point.x, point.y)
                else:
                    print("没有找到此名字的棋子或未轮到此方走子")
            while not is_correct_position:
                x, y = data["target_x"], data["target_y"]
                is_correct_position = chessman.move(x, y)
                if is_correct_position:
                    # self.env.board.print_to_cl()
                    self.env.board.clear_chessmans_moving_list()

            action, policy = self.ai.action(self.env.get_state(), self.env.num_halfmoves)
            if not self.env.red_to_move:
                action = flip_move(action)
            if action is None:
                response = {'id': data["id"], "current_x": 0, "current_y": 0, "target_x": 0, "target_y": 1,
                            "win": 1, "action": ""}
                print("AI投降了!")
                client.publish(topic=network_helper.network_connection_config.mqtt_send_topic_name,
                               payload=json.dumps(response), qos=0)
                return
            self.env.step(action)
            print(f"AI选择移动 {action}")
            # self.env.board.print_to_cl()
            response = {'id': data["id"], "current_x": action[0], "current_y": action[1], "target_x": action[2],
                        "target_y": action[3], "win": -1,
                        "action": action}
            client.publish(topic=network_helper.network_connection_config.mqtt_send_topic_name,
                           payload=json.dumps(response), qos=0)

        client = network_helper.get_message_queue_client(on_connect, on_message)
        client.loop_forever()