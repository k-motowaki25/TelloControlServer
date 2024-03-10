from devices.operation import OperationDevice
from devices.coord import CoordDevice
from devices.tello import TelloDevice
import socket
import threading
import datetime


class Server:
    def __init__(self, host, port):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind((host, port))
        self.devices = {'operation': {}, 'coord': {}, 'tello': {}}

    def listen(self):
        print('*** Server started ***')
        while True:
            data, address = self.sock.recvfrom(1024)
            device_type, device_id, payload = data.decode().split(':')
            asctime = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            print(f'[{asctime}] [{address[0]}:{address[1]}] [{device_type}:{device_id}] - {payload}')

            if device_type not in self.devices:
                print(f'Invalid device type: {device_type}')
                continue

            if device_id not in self.devices[device_type]:
                if device_type == 'operation':
                    device = OperationDevice(self, address)
                elif device_type == 'coord':
                    device = CoordDevice(self, address)
                elif device_type == 'tello':
                    device = TelloDevice(self, address, device_id)

                self.devices[device_type][device_id] = device

            device = self.devices[device_type][device_id]
            device.process_recv_data(payload)


if __name__ == '__main__':
    server = Server('0.0.0.0', 12345)
    server_connection_thread = threading.Thread(target=server.listen)
    server_connection_thread.start()