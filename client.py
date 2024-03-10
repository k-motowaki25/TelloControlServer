import socket
import threading
import yaml


class Client:
    def __init__(self, device_type, device_id):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.device_type = device_type
        self.device_id = device_id

        with open('config.yaml') as file:
            config = yaml.safe_load(file)
        self.host = config['host_ip']
        self.port = config['host_port']

    def listen(self):
        while True:
            data, address = self.sock.recvfrom(1024)
            data = data.decode()
            print(f'{address}: {data}')

    def send(self):
        while True:
            message = input('Enter message: ')
            message = f'{self.device_type}:{self.device_id}:{message}'
            self.sock.sendto(message.encode(), (self.host, self.port))


if __name__ == '__main__':
    device_type = input('Enter device type: ')
    device_id = input('Enter device id: ')
    client = Client(device_type, device_id)
    listen_thread = threading.Thread(target=client.listen)
    listen_thread.start()
    client.send()