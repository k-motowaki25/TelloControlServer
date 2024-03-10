import threading


class Device:
    def __init__(self, server, address):
        self.server = server
        self.sock = server.sock
        self.address = address

    def process_recv_data(self, data):
        pass