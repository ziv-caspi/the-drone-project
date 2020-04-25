import socket
import hashlib, base64
import traceback
import time
import motor_control
import security

HOST = '0.0.0.0'
PORT = 7777


class Server():
    def __init__(self, HOST, PORT, CONNECTIONS, HOLD_DURATION):
        self.Security = security.Security(HOLD_DURATION)

        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        self.HOST = HOST
        self.PORT = PORT
        self.CONNECTIONS = CONNECTIONS
        self.HOLD_DURATION = HOLD_DURATION


        self.client_socket = None
        self.client_connected = False
        self.wrong_password_ip_list = []
        self.on_hold_list = []

        self.controls = motor_control.Controls()

        self.FUNC_KEY = {
            'S': self.straight,
            'T': self.turn,
            'B': self.breaks
        }

        self.BOOL = {
            0: False,
            1: True
        }

    def start(self):
        self.initialize_server()
        while True:
            self.admit_client()

    def straight(self, speed, forward):
        self.controls.straight(speed, forward)

    def turn(self, side, angle):
        self.controls.turn(side, angle)

    def breaks(self, *args):
        self.controls.stop()

    def initialize_server(self):
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_socket.bind((self.HOST, self.PORT))
        self.server_socket.listen(3)
        print('Remote Control Server is UP! \n WARNING! THIS SERVER IS NOT SECURE!')

    def admit_client(self):
        self.client_socket, addrs = self.server_socket.accept()

        try:
            if self.Security.verify_client_hold_list_and_password(addrs, self.client_socket):
                print('New Client Connected... IP:', addrs)
                self.client_connected = True
                self.Security.handle_password_attempt(addrs, True)
                print('Correct Password, Welcome!')
                self.serve_client()
            else:
                self.Security.handle_password_attempt(addrs, False)


        except (ConnectionAbortedError, ConnectionResetError, ConnectionRefusedError) as error:
            print('Connection with {0} Was Aborted. Listening For New Client...'.format(addrs), error)
            self.client_socket.close()
            self.client_connected = False
            # self.controls.stop()
            traceback.print_exc()

    def serve_client(self):
        while self.client_connected:

            try:
                self.receive_commands()

            except (BufferError, ValueError) as error:
                # TODO: Decide on handling for bad packets... watch list? logging?
                print('Packet Not By Protocol. ERROR:', error)
                traceback.print_exc()

    def receive_commands(self):
        msg_len = int(self.client_socket.recv(2).decode())
        if not msg_len:
            raise ConnectionResetError('Connection Closed. Empty Message.')

        func, param1, param2 = self.split_by_rcp(msg_len)
        print(func, param1, param2)
        func(param1, param2)

    def split_by_rcp(self, msg_len):
        try:
            full_msg = self.client_socket.recv(msg_len).decode()
            func_key = full_msg[0]
            full_msg = full_msg[1:]
            speed = int(full_msg[:2])
            direction = self.BOOL[int(full_msg[-1])]
            return self.FUNC_KEY[func_key], speed, direction
        except:
            raise BufferError('Protocol Invalid')




if __name__ == '__main__':
    server = Server(HOST, PORT, 0, 5)
    server.start()
