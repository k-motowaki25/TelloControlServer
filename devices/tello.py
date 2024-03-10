from devices.device import Device
import time
import threading
import yaml


class TelloDevice(Device):
    def __init__(self, server, address, device_id):
        super().__init__(server, address)
        self.device_id = device_id
        self.coords = {'curt': {}, 'goal': {}}
        self.is_moving = False
        
        with open('config.yaml') as file:
            config = yaml.safe_load(file)
        self.DEFAULT_GOAL_COORD = config['set_curt_cmd']['init'][device_id]
        self.coords['curt'] = self.DEFAULT_GOAL_COORD.copy()
        self.coords['goal'] = self.DEFAULT_GOAL_COORD.copy()
    
    def moving_start(self):
        self.is_moving = True
        self.moving_thread = threading.Thread(target=self.moving)
        self.moving_thread.start()
    
    def moving_stop(self):
        self.goal_coord = self.DEFAULT_GOAL_COORD.copy()
        time.sleep(5) # 初期位置に戻るのを待つ
        self.is_moving = False
        self.moving_thread.join()
    
    def moving(self):
        TH = 0.1
        while self.is_moving:
            move = [1024] * 4
            diff_x = self.coords['goal']['x'] - self.coords['curt']['x']
            diff_y = self.coords['goal']['y'] - self.coords['curt']['y']
            diff_z = self.coords['goal']['z'] - self.coords['curt']['z']

            # [回転左右-+, 上下+-, 前後+-, 左右-+]
            if abs(diff_x) > TH:
                move[3] += 600 * diff_x
            if abs(diff_y) > TH:
                move[2] += 600 * diff_y
            if abs(diff_z) > TH:
                move[1] += 600 * diff_z

            message = f'stick,{",".join(map(str, map(int, move)))}'
            self.send(message)
            time.sleep(0.03)
    
    def set_goal_coord(self, coord):
        COEF = 0.9 # ゴール座標を中央寄せするための係数
        coord = {k: v*COEF + (1-COEF)/2 for k, v in coord.items()}
        self.coords['goal'] = coord
    
    def send(self, message):
        self.sock.sendto(message.encode(), self.address)