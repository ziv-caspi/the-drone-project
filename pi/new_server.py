import socket
import random
import hashlib
import motor_control
import time

class Server():
    def __init__(self, PORT, CONNECTIONS, PASSWORD, SALT_SEED):

        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.controls = motor_control.Controls()

        self.HOST = '0.0.0.0'
        self.PORT = PORT
        self.CONNECTIONS = CONNECTIONS

        self.client_socket = None
        self.client_addrs = None
        self.client_connected = False

        self.PASSWORD = PASSWORD
        random.seed(SALT_SEED)
        self.randoms_used = 0
        self.session_salt = None
        self.current_salt = None
        self.RANDOM_LIMIT = 99999999

        self.COMMANDS = ['S991', 'S990', 'T991', 'T990', 'B000']

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
        self.init_server()
        print('Server is Up on PORT %d' % self.PORT)
        while True:
            try:
                self.client_socket, self.client_addrs = self.server_socket.accept()
                print(self.client_addrs)
                self.new_connection()
                while self.client_connected:
                    self.handle_commands()
            except:
                print('Connection Aborted.')
                self.client_socket.close()
                self.client_connected = False
                self.client_addrs = None

    def init_server(self):
        self.server_socket.bind((self.HOST, self.PORT))
        self.server_socket.listen(self.CONNECTIONS)

    def gen_new_session_salt(self):
        self.session_salt = random.randint(0, self.RANDOM_LIMIT)
        self.randoms_used += 1
        self.current_salt = self.session_salt
        print(self.current_salt)

    def send_randoms_used(self):
        self.client_socket.send(str(self.randoms_used).encode())

    def straight(self, speed, forward):
        print(speed, forward)
        self.controls.straight(speed, forward)
        print('STRAIGHT')

    def turn(self, side, angle):
        print(side, angle)
        self.controls.turn(side, angle)
        print('TURN')

    def breaks(self, *args):
        self.controls.stop()
        print('BREAKS')

    def new_connection(self):
        self.gen_new_session_salt()
        try:
            self.client_socket.send(str(self.randoms_used).encode())
            self.client_connected = True
        except (ConnectionAbortedError, ConnectionResetError, ConnectionError, ConnectionRefusedError) as error:
            print(error, self.client_addrs)

    def handle_commands(self):
        try:
            hash_len = int(self.client_socket.recv(2).decode())
            sent_hash = self.client_socket.recv(hash_len)
            found = False
            for command in self.COMMANDS:
                if self.compute_hash(command) == sent_hash:
                    print(command)
                    found = True
                    try:
                        self.execute_command(command)
                    except:
                        print('Car Function Failed.')
            if not found:
                print('Hash Incompatible.', self.current_salt)
            self.current_salt += 1

        except:
            pass

    def compute_hash(self, COMMAND):
        string = self.PASSWORD + str(self.current_salt) + COMMAND
        m = hashlib.sha256()
        m.update(string.encode())
        return m.digest()

    def execute_command(self, command):
        func_key = command[0]
        param1 = command[1:3]
        param2 = self.BOOL[int(command[-1])]
        function = self.FUNC_KEY[func_key]
        print(function)
        function(param1, param2)


if __name__ == '__main__':
    server = Server(7777, 0, 'drone', 92760325)
    server.start()