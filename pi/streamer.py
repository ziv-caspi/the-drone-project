import cv2
from imutils.video import VideoStream
from imutils import resize
from Cryptodome.Cipher import AES
import threading
import socket

class Streamer():
    def __init__(self, timeout):
        self.timeout = timeout
        self.client_addrs = None
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.key = None

    def start_streaming_to_client(self, client_addrs):
        self.client_addrs = client_addrs
        self.client_socket.settimeout(self.timeout)
        try:
            self.vs = VideoStream(src=0).start()
            self.streaming_loop()

        except socket.timeout:
            print('Socket Time Out Exceeded, Closing Streaming Connection')
            self.client_addrs = None

        except socket.error:
            print('Lost Streaming Connection.')
            self.client_addrs = None

    def stop_streaming_to_client(self):
        self.client_addrs = None

    def streaming_loop(self):
        while self.client_addrs:
            frame = self.vs.read()
            frame = resize(frame, width=320)
            frame = frame.tobytes()
            self.client_socket.sendto(str(len(frame)).encode(), self.client_addrs)
            self.client_socket.sendto(frame, self.client_addrs)