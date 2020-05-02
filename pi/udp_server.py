import socket
import random
import hashlib

class Server():
    def __init__(self, PORT, PASSWORD):
        self.PASSWORD = PASSWORD

        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.server_socket.bind(('127.0.0.1', PORT))
        print('Server Is Listening On Port', PORT)
        self.server_up = True
        self.salt = str(random.randint(0, 999999))
        
        self.COMMANDS = ['04S991', '04S990', '04T991', '04T990']
        
        self.PROTOCOL = {
            'SALT': self.send_salt_to_addrs
        }

    def send_salt_to_addrs(self, addrs):
        self.server_socket.sendto(self.salt.encode(), addrs)
    
    def start_server(self):
        while self.server_up:
            self.handle_commands()

    def handle_commands(self):
        msg_len, addrs = self.server_socket.recvfrom(2)
        msg = self.server_socket.recv(int(msg_len))
        print(msg, 'From:', addrs)
        # self.server_socket.sendto(msg.encode(), addrs)
        if msg == b'SALT':
            self.send_salt_to_addrs(addrs)
        else:
            print(self.check_hash_for_commands(msg))

    def calc_hash(self, string):
        m = hashlib.sha256()
        m.update(string.encode())
        return m.digest()

    def check_hash_for_commands(self, hash):
        for command in self.COMMANDS:
            if self.calc_hash(self.PASSWORD + self.salt + command) == hash:
                self.salt = str(random.randint(0, 999999))
                return command
        return 'Who Are You??'




def main():
    server = Server(7777, 'drone')
    server.start_server()


if __name__ == '__main__':
    main()