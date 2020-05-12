import socket
import random
import hashlib
import motor_control
import time
import logging

class Server():
    def __init__(self, PORT, PASSWORD):
        self.PASSWORD = PASSWORD
        self.DELAY = 0.2
        self.controls = motor_control.Controls()

        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.server_socket.bind(('0.0.0.0', PORT))
        print('Server Is Listening On Port', PORT)
        self.server_up = True

        self.RANDOM_LIMIT = 99999999
        self.salt = str(random.randint(0, self.RANDOM_LIMIT))
        self.used_salts = [self.salt]
        
        self.COMMANDS = ['S991', 'S990', 'T991', 'T990', 'B000']
        
        self.PROTOCOL = {
            'SALT': self.send_salt_to_addrs
        }

        self.FUNCTIONS = {
            'S': self.straight,
            'T': self.turn,
            'B': self.breaks
        }

        self.last_ip_wrong = None


    def straight(self, speed, forward):
        self.controls.straight(speed, forward)
        print('Straight', speed, forward)

    def turn(self, side, angle):
        self.controls.turn(side, angle)
        print('Turn', side, angle)

    def breaks(self, *args):
        self.controls.stop()
        print('Breaks')

    def gen_new_salt(self):
        salt = str(random.randint(0, self.RANDOM_LIMIT))
        while salt in self.used_salts:
            salt = str(random.randint(0, self.RANDOM_LIMIT))

        self.used_salts.append(salt)
        self.salt = salt

    def send_salt_to_addrs(self, addrs):
        self.server_socket.sendto(self.salt.encode(), addrs)
    
    def start_server(self):
        while self.server_up:
            self.handle_commands()

    def handle_commands(self):
        try:
            msg_len, addrs = self.server_socket.recvfrom(2)

            if addrs[0] == self.last_ip_wrong:
                time.sleep(self.DELAY)

            msg = self.server_socket.recv(int(msg_len))
            print(msg, 'From:', addrs)
            if msg == b'SALT':
                self.send_salt_to_addrs(addrs)
                return

            self.check_hash_for_commands(msg)


        except PermissionError:
            try:
                print('Password or Command From {0} Are Invalid. Discarding.'.format(addrs))
                self.last_ip_wrong = addrs[0]
            except:
                print('Password or Command Are Invalid. Discarding.')

        except (BufferError, ValueError, OSError):
            try:
                print('Packet From {0} Not By Protocol, Discarding'.format(addrs))
            except:
                print('Packet Not By Protocol, Discarding')



    def calc_hash(self, string):
        m = hashlib.sha256()
        m.update(string.encode())
        return m.digest()

    def check_hash_for_commands(self, hash):
        for command in self.COMMANDS:
            if self.calc_hash(self.PASSWORD + self.salt + command) == hash:
                self.gen_new_salt()
                self.parse_and_execute_command(command)
                return
        raise PermissionError('Password Incorrect or Bad Command, Discarding')

    def parse_and_execute_command(self, command):
        try:
            function = self.FUNCTIONS[command[0]]
            param1 = int(command[1:3])
            param2 = int(command[-1])
            function(param1, param2)
        except:
            raise ValueError

class Security():
    class Endpoint():
        def __init__(self, ip):
            self.ip = ip
            self.time = time.time()
            self.recent_requests = []
            self.valid_requests_count = 0
            self.invalid_requests_count = 0

    def __init__(self):
        logging.basicConfig(filename='data/suspicious_activity.log', level=logging.WARNING)
        self.active_endpoints = []

    def new_ip_connected(self, ip):
        self.active_endpoints.append(self.Endpoint(ip))

    def get_index_of_endpoint(self, ip):
        for i, endpoint in enumerate(self.active_endpoints):
            if endpoint.ip == ip:
                return i

    def new_request_from_ip(self, ip, request, valid):
        endpoint = self.active_endpoints[self.get_index_of_endpoint(ip)]
        if valid:
            endpoint.valid_requests_count += 1
        else:
            endpoint.invalid_requests_count += 1

        endpoint.recent_requests.append(request)



def main():
    server = Server(7777, 'drone')
    server.start_server()


if __name__ == '__main__':
    main()