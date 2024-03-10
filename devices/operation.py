from devices.device import Device


class OperationDevice(Device):
    def __init__(self, server, address):
        super().__init__(server, address)
    
    def process_recv_data(self, data):        
        parts = data.split(' ')
        command, params = parts[0], parts[1:]
        match command:
            case 'start':
                self.apply_func_all_tellos('send', 'takeoff')
            case 'stop':
                self.apply_func_all_tellos('send', 'land')
            case 'speed_switch':
                self.apply_func_all_tellos('send', 'speed_switch')
            case 'move_start':
                self.apply_func_all_tellos('moving_start')
            case 'move_stop':
                self.apply_func_all_tellos('moving_stop')
            case 'set_goal':
                sub_command, sub_params = params[0], params[1:]
                coord = dict(zip(['x', 'y', 'z'], map(float, sub_params)))
                match sub_command:
                    case 'all':
                        self.apply_func_all_tellos('set_goal_coord', coord)
                    case '0' | '1' | '2':
                        if sub_command in self.server.devices['tello']:
                            self.server.devices['tello'][sub_command].set_goal_coord(coord)
                    case _:
                        print(f"Unknown sub command: {sub_command}")
            case _:
                print(f"Unknown command: {command}")
    
    def apply_func_all_tellos(self, func, *args, **kwargs):
        for tello in self.server.devices['tello'].values():
            getattr(tello, func)(*args, **kwargs)