import socket
import random
import hashlib
import time
import motor_control

class Server():
    """
        Server class, responsible for receiving commands and executing them. Uses the Secure Commands Protocol/
    """

    def __init__(self, PORT, CONNECTIONS, PASSWORD, SALT_SEED, TIMEOUT):
        """
        Initializes the Server Class

        :param PORT: port to listen on
        :type PORT: int
        :param CONNECTIONS: max number of queued connection
        :type CONNECTIONS: int
        :param PASSWORD: password required for login
        :type PASSWORD: string
        :param SALT_SEED: number to use as seed for random
        :type SALT_SEED: int
        :param TIMEOUT: max seconds until first command required
        :type TIMEOUT: int
        """
        self.TIMEOUT = TIMEOUT
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # the servers socket object
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.controls = motor_control.Controls() # Controls class instance

        self.HOST = '0.0.0.0'
        self.PORT = PORT
        self.CONNECTIONS = CONNECTIONS

        self.client_socket = None
        self.client_addrs = None
        self.client_connected = False

        self.PASSWORD = PASSWORD
        self.SEED = SALT_SEED
        random.seed(SALT_SEED)
        self.RANDOM_LIMIT = 99999999 # max generated number
        self.REPS_LIMIT = 1000000 # number of random reps before re init seed
        self.reps_file_path = 'random_reps.txt'
        try:

            with open(self.reps_file_path, 'r') as f:
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
            print('SEED is:', self.SEED, 'SALT is:', self.current_salt)


        except (FileNotFoundError, ValueError):
            self.randoms_used = 0
            with open(self.reps_file_path, 'w') as f:
                f.write(str(self.randoms_used))
            self.session_salt = None
            self.current_salt = None

        self.COMMANDS = ['S991', 'S990', 'T991', 'T990', 'B000'] # all knows commands

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
        """
            starts the server, accepts client connections and handles them.
             the client is expected to send a first valid command within TIMEOUT seconds, else the connection
             will be aborted. any invalid command sent will lead to connection aborted.
        """
        self.init_server()
        print('Server is Up on PORT %d' % self.PORT)
        while True:
            try:
                self.client_socket, self.client_addrs = self.server_socket.accept()
                self.client_socket.settimeout(self.TIMEOUT)
                try:
                    print(self.client_addrs)
                    self.new_connection()
                    self.auth_msg()
                    while self.client_connected:
                        self.handle_commands()
                except socket.timeout:
                    print('Connection TimeOut Exceeded. Dumping Session')
                    raise ConnectionAbortedError

            except socket.error as e:
                print('Connection Aborted:', e)
                self.client_socket.close()
                self.client_connected = False
                self.client_addrs = None

    def init_server(self):
        """
            initialize server socket object
        """
        self.server_socket.bind((self.HOST, self.PORT))
        self.server_socket.listen(self.CONNECTIONS)

    def gen_new_session_salt(self):
        """
            this is called when a new connection is accepted.
            generates new random number to be used as this session's salt
        """
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


    def straight(self, speed, forward):
        """
            tells the car to go straight, uses the motor control class
        :param speed: speed for the wheels
        :type speed: int 0-99
        :param forward: True for forward False for backward
        :type forward: bool
        """
        print(speed, forward)
        self.controls.straight(speed, forward)
        print('STRAIGHT')

    def turn(self, angle, side):
        """
            tells the car to turn, uses the motor control class
        :param angle: how hard the turn is 0-99
        :type angle: int
        :param side: True for right, False for left
        :type side: bool
        """
        print(side, angle)
        self.controls.turn(side, angle)
        print('TURN')

    def breaks(self, *args):
        """
            tells the car to stop, uses the motor control class
        :param args: place holder so that function can be called the same way as turn and straight, actually needs no params
        :type args: list placeholder
        """
        self.controls.stop()
        print('BREAKS')

    def new_connection(self):
        """
            called when a new connection is accepted.
            calls gen_new_session_salt, sends number of randoms used to client.


        """
        self.gen_new_session_salt()
        try:
            # try:
            #     self.bin_to_car('{0:b}'.format(self.SEED), 0.5, 0.4)
            # except:
            #     print('Error with car sequence')
            print(self.randoms_used)
            msg = str(len(str(self.randoms_used))).zfill(3) + str(self.randoms_used)
            self.client_socket.send(msg.encode())
            self.client_connected = True
        except (ConnectionAbortedError, ConnectionResetError, ConnectionError, ConnectionRefusedError) as error:
            print(error, self.client_addrs)

    def recv_command(self):
        """
            handles receiving command-hash from client. compares sent hash with self-calculated to find sent command
        :return: command sent(if found match), sent hash
        :rtype: str, bytearray
        """
        try:
            hash_len = int(self.client_socket.recv(2).decode())
            sent_hash = self.client_socket.recv(hash_len)
            for command in self.COMMANDS:
                if self.compute_hash(command) == sent_hash:
                    return command, sent_hash
            print('Excpected Salt:', self.current_salt)
            return None, sent_hash
        except (ValueError) as e:
            print('Packet Not By Protocol', e)
            raise ConnectionAbortedError

    def handle_commands(self):
        """
            gets sent command from recv_command, and tells execute_command to execute it.
            if no legit command was sent connection is aborted.
        """
        try:
            command, sent_hash = self.recv_command()
            self.current_salt += 1
            if command:
                try:
                    self.execute_command(command)
                except:
                    print('Car Function Failed.')
            else:
                self.usage_analysis.request_received(self.client_addrs[0], sent_hash, None)
                print('Hash Incompatible. Dumping Session', self.current_salt)
                raise ConnectionResetError

        except:
            raise ConnectionAbortedError

    def compute_hash(self, COMMAND):
        """
            computes hash for hash(password + salt + COMMAND) and returns it.
        :param COMMAND: command to compute hash for
        :type COMMAND: str
        :return: computed hash
        :rtype: bytearray
        """
        string = self.PASSWORD + str(self.current_salt) + COMMAND
        m = hashlib.sha256()
        m.update(string.encode())
        return m.digest()

    def execute_command(self, command):
        """
            parse command sent by client and calls appropriate function with included params to execute it.
        :param command:
        :type command:
        """
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

    def auth_msg(self):
        """
            waiting for first auth message before timeout ends.
             if gets legit one timeout is reset, else connection aborted
        :return: exits function
        :rtype: None
        """
        print('Waiting On Auth Message...')
        command, sent_hash = self.recv_command()
        self.current_salt += 1
        print('command:', command)
        if command:
            self.client_socket.settimeout(None)
            print('AUTH COMMAND Received:', command)
            return

        raise ConnectionAbortedError



if __name__ == '__main__':
    
    server = Server(7777, 0, 'drone', 92760325, 0.2)
    for start_attempt in range(3):
        try:
            server.start()
            server.start()
        except Exception as e:
            print(f"Attempt {start_attempt+1}/3 has failed")
            print(e)
