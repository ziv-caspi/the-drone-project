import socket
import traceback
import motor_control

HOST = '0.0.0.0'
PORT = 7777

class Server():
    def __init__(self, HOST, PORT, CONNECTIONS):
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        self.HOST = HOST
        self.PORT = PORT
        self.CONNECTIONS = CONNECTIONS

        self.client_socket = None
        self.client_connected = False

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
        self.server_socket.bind((self.HOST, self.PORT))
        self.server_socket.listen(self.CONNECTIONS)
        print('Remote Control Server is UP! \n WARNING! THIS SERVER IS NOT SECURE!')

    def admit_client(self):
        self.client_socket, addrs = self.server_socket.accept()
        print('New Client Connected... IP: ', addrs)

        try:
            if self.client_authentication():
                self.client_connected = True
                self.serve_client()

        except (ConnectionAbortedError, ConnectionResetError) as error:
            print('Connection with {0} Was Aborted. Listening For New Client...'.format(addrs), error)
            self.client_socket.close()
            self.client_connected = False
            traceback.print_exc()

    def client_authentication(self):
        return True

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


# sock = socket.socket()

def straight(controls, speed, forward):
    controls.straight(speed, forward)


def turn(controls, angle, side):
    print('TURNING')
    if side:
        side = 'RIGHT'
        print(side)
    else:
        side = 'LEFT'
        print(side)
    controls.turn(side, angle)

def breaks(controls, *args):
    controls.stop()

FUNC_KEY = {
    'S': straight,
    'T': turn,
    'B': breaks
}

BOOL = {
    0: False,
    1: True
}

def init_server():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((HOST, PORT))
    server_socket.listen(1)
    print('Remote Control Server is UP! \n WARNING! THIS SERVER IS NOT SECURE!')
    return server_socket


def handle_new_client_authentication(client_socket):
    # authentication - currently mock
    return True


def split_by_rcp(msg_len, client_socket):
    try:
        full_msg = client_socket.recv(msg_len).decode()
        func_key = full_msg[0]
        full_msg = full_msg[1:]
        speed = int(full_msg[:2])
        direction = BOOL[int(full_msg[-1])]
        return FUNC_KEY[func_key], speed, direction
    except:
        raise BufferError('Protocol Invalid')


def command_receiver(client_socket, controls):
    msg_len = int(client_socket.recv(2).decode())
    func, speed, direction = split_by_rcp(msg_len, client_socket)
    print(func, speed, direction)
    func(controls, speed, direction)


def main():
    controls = motor_control.Controls()
    server_socket = init_server()
    while True:
        client_socket, addr = server_socket.accept()
        print('New Client Connected... IP: ', addr)
        try:
            if handle_new_client_authentication(client_socket):
                client_on = True
                while client_on:
                    try:
                        command_receiver(client_socket,controls)
                    except (BufferError, ValueError) as e:
                        # TODO: Decide on handling for bad packets... watch list? logging?
                        print('Packet Not By Protocol... Still Listening', 'ERROR: ', e)
        except:
            print('Client Disconnected/Failed')
            client_on = False
            traceback.print_exc()


if __name__ == '__main__':
    server = Server(HOST, PORT, 1)
