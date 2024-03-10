from devices.device import Device
import re


class CoordDevice(Device):
    def __init__(self, server, address):
        super().__init__(server, address)

    def process_recv_data(self, data):
        # c(id, x1)(id, x2)(id, x3)
        tellos = self.server.devices['tello']

        c, pairs = data[0], data[1:]
        parsed = re.findall(r'\((\d),(-?\d+\.?\d*)\)', pairs)
        for id, value in parsed:
            if id not in tellos: continue
            value = float(value)
            tellos[id].coords['curt'][c] = value