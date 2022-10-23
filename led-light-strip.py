"""MagicHome Python API.
Copyright 2016, Adam Kempenich. Licensed under MIT.
It currently supports:
- Bulbs (Firmware v.4 and greater)
- Legacy Bulbs (Firmware v.3 and lower)
- RGB Controllers
- RGB+WW Controllers
- RGB+WW+CW Controllers
"""
import socket
import struct
import datetime
import time


class MagicHomeApi:
    def __init__(self, device_ip, keep_alive=True):
        self.device_ip = device_ip
        self.keep_alive = keep_alive
        self.API_PORT = 5577

        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s.settimeout(3)
        self.latest_connection = datetime.datetime.now()

        try:
            print("[CONNECTING]")
            self.s.connect((self.device_ip, self.API_PORT))
            print("[CONNECTED]")
            self.turn_on()
            self.update_device(r=0, g=0, b=0, white1=255)
            time.sleep(0.2)
            self.update_device(r=0, g=0, b=0, white1=0)

        except socket.error as exc:
            print(f"[ERROR CONNECTING] {exc}")
            if self.s:
                self.s.close()
        

    def turn_on(self):
        self.send_bytes(0x71, 0x23, 0x0F, 0xA3)

    def turn_off(self):
        self.send_bytes(0x71, 0x24, 0x0F, 0xA4)

    def get_status(self):
        self.send_bytes(0x81, 0x8A, 0x8B, 0x96)
        return self.s.recv(14)

    def update_device(self, r=0, g=0, b=0, white1=None):
        white1 = self.check_number_range(white1)
        message = [0x31, g, r, b, white1, 0, 0, 0]
        self.send_bytes(*(message + [self.calculate_checksum(message)]))

    def check_number_range(self, number):
        if number < 0:
            return 0
        elif number > 255:
            return 255
        else:
            return number

    def send_preset_function(self, preset_number, speed): # Presets can range from 0x25 (int 37) to 0x38 (int 56)
        if preset_number < 37:
            preset_number = 37
        if preset_number > 56:
            preset_number = 56
        if speed < 0:
            speed = 0
        if speed > 100:
            speed = 100

        if type == 4:
            self.send_bytes(0xBB, preset_number, speed, 0x44)
        else:
            message = [0x61, preset_number, speed, 0x0F]
            self.send_bytes(*(message + [self.calculate_checksum(message)]))

    def calculate_checksum(self, bytes):
        return sum(bytes) & 0xFF

    def send_bytes(self, *bytes):
        check_connection_time = (datetime.datetime.now() - self.latest_connection).total_seconds()
        try:
            if check_connection_time >= 290:
                print("[CONNECTION TIMED OUT]")
                self.s.connect((self.device_ip, self.API_PORT))
            message_length = len(bytes)
            self.s.send(struct.pack("B" * message_length, *bytes))
            # Close the connection unless requested not to
            if self.keep_alive is False:
                self.s.close()
        except socket.error as exc:
            print(f"[CONNECTION ERROR] {exc}")
            if self.s:
                self.s.close()


# home = MagicHomeApi('10.10.123.3')
# home.turn_on()
# home.update_device(r=255, g=50, b=0, white1=0)

# #home.turn_off()





