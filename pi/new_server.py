import socket
import random
import hashlib
import time

import motor_control
import usage_analysis

class Server():
    def __init__(self, PORT, CONNECTIONS, PASSWORD, SALT_SEED):

        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.controls = motor_control.Controls()
        self.usage_analysis = usage_analysis.UsageAnalysis()

        self.HOST = '0.0.0.0'
        self.PORT = PORT
        self.CONNECTIONS = CONNECTIONS

        self.client_socket = None
        self.client_addrs = None
        self.client_connected = False

        self.PASSWORD = PASSWORD
        self.SEED = SALT_SEED
        random.seed(SALT_SEED)
        self.RANDOM_LIMIT = 99999999
        self.REPS_LIMIT = 1000000
        self.reps_file_path = 'random_reps.txt'
        try:

            f = open(self.reps_file_path, 'r')
            self.randoms_used = int(f.read())
            iters = self.randoms_used

            if self.randoms_used >= self.REPS_LIMIT:
                print('MAX REPS EXCEEDED.')
                random.seed(SALT_SEED ** 2)
                iters = self.randoms_used - self.REPS_LIMIT + 1# Notice Can Cause Repetition
                print(iters)


            for i in range(iters):
                self.session_salt =  random.randint(0, self.RANDOM_LIMIT)
            self.current_salt = self.session_salt


        except:
            self.randoms_used = 0
            self.session_salt = None
            self.current_salt = None

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
                try:
                    self.usage_analysis.save_endpoint(self.client_addrs[0])
                except:
                    print('Failed To Get Client Addres, Data not saved.')

                self.client_socket.close()
                self.client_connected = False
                self.client_addrs = None

    def init_server(self):
        self.server_socket.bind((self.HOST, self.PORT))
        self.server_socket.listen(self.CONNECTIONS)

    def gen_new_session_salt(self):
        if self.randoms_used == self.REPS_LIMIT - 1:
            random.seed(self.SEED ** 2)
            print('MAX REPS EXCEEDED.', self.randoms_used)

        self.session_salt = random.randint(0, self.RANDOM_LIMIT)
        self.randoms_used += 1
        self.current_salt = self.session_salt

        try:
            with open(self.reps_file_path, 'w') as f:
                f.write(str(self.randoms_used))
        except:
            print('Could Not Write To Reps file.')
        print(self.current_salt)

    def send_randoms_used(self):
        self.client_socket.send(str(self.randoms_used).encode())

    def straight(self, speed, forward):
        print(speed, forward)
        self.controls.straight(speed, forward)
        print('STRAIGHT')

    def turn(self, angle, side):
        print(side, angle)
        self.controls.turn(side, angle)
        print('TURN')

    def breaks(self, *args):
        self.controls.stop()
        print('BREAKS')

    def new_connection(self):
        self.gen_new_session_salt()
        try:
            print(self.randoms_used)
            msg = str(len(str(self.randoms_used))).zfill(3) + str(self.randoms_used)
            self.client_socket.send(msg.encode())
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
                    self.usage_analysis.request_received(self.client_addrs[0], sent_hash, command)
                    print(command)
                    found = True
                    try:
                        self.execute_command(command)
                    except:
                        print('Car Function Failed.')
            if not found:
                self.usage_analysis.request_received(self.client_addrs[0], sent_hash, None)
                print('Hash Incompatible.', self.current_salt)
            self.current_salt += 1

        except:
            raise ConnectionAbortedError

    def compute_hash(self, COMMAND):
        string = self.PASSWORD + str(self.current_salt) + COMMAND
        m = hashlib.sha256()
        m.update(string.encode())
        return m.digest()

    def execute_command(self, command):
        func_key = command[0]
        param1 = int(command[1:3])
        param2 = self.BOOL[int(command[-1])]
        function = self.FUNC_KEY[func_key]
        print(function)
        function(param1, param2)

    def bin_to_car(self, bin_string, intervals, pause):
        for val in bin_string:
            self.controls.turn(self.BOOL[int(val)], 99)
            time.sleep(intervals)
            self.controls.stop()
            time.sleep(pause)


if __name__ == '__main__':
    server = Server(7777, 0, 'drone', 92760325)
    server.start()