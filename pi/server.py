import socket
import hashlib, base64
import traceback
import time
import motor_control

HOST = '0.0.0.0'
PORT = 7777

class Server():
    def __init__(self, HOST, PORT, CONNECTIONS, HOLD_DURATION):
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
            if self.verify_client_hold_list_and_password(addrs):
                print('New Client Connected... IP:', addrs)
                self.client_connected = True
                self.add_to_wrong_password_list(addrs, True)
                print('Correct Password, Welcome!')
                self.serve_client()
            else:
                self.add_to_wrong_password_list(addrs, False)


        except (ConnectionAbortedError, ConnectionResetError, ConnectionRefusedError) as error:
            print('Connection with {0} Was Aborted. Listening For New Client...'.format(addrs), error)
            self.client_socket.close()
            self.client_connected = False
            # self.controls.stop()
            traceback.print_exc()

    def client_authentication(self):
        try:
            msg_len = int(self.client_socket.recv(2).decode())
            password = self.client_socket.recv(msg_len)
            return self.check_password(password)

        except:
            return False

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

    def check_password(self, password):
        m = hashlib.sha256()
        m.update(password)
        hashed = m.digest()
        encoded = base64.b64encode(hashed)
        with open('hashed_password.txt', 'rb') as file:
            password_hash = file.read()
            return password_hash == encoded

    def verify_client_hold_list_and_password(self, addrs):
        for holder in self.on_hold_list:
            ip = holder[0]
            start_time = holder[1]
            required_hold_time = holder[2]
            if ip == addrs[0]:
                cur_time = time.time()
                diff = cur_time - start_time
                if diff > required_hold_time:
                    if self.client_authentication():
                        self.on_hold_list.remove(holder)
                        return True
                    # for wrong_password_ip in self.wrong_password_ip_list:
                    #     if holder[0] == wrong_password_ip[0][0]:
                    #         self.wrong_password_ip_list.remove(wrong_password_ip)
                else:
                    print('Client{0} On Hold For {1} More Seconds'.format(addrs, required_hold_time - diff))
                    raise ConnectionRefusedError('Client is On hold list.')
        return self.client_authentication()

    def add_to_wrong_password_list(self, addrs, correct_password):
        if not correct_password:
            for index in range(len(self.wrong_password_ip_list)):
                member = self.wrong_password_ip_list[index]
                member_addrs = member[0]
                wrong_attempt_counter = member[1]

                if member_addrs[0] == addrs[0]:
                    self.wrong_password_ip_list[index] = (
                    member_addrs, wrong_attempt_counter + 1)
                    wrong_attempt_counter += 1
                    print('Wrong Attempt from this IP: ', wrong_attempt_counter)

                    if wrong_attempt_counter >= 3:
                        hold =  self.HOLD_DURATION ** (wrong_attempt_counter -2)
                        print('Putting Client On Hold for {0} Seconds.'.format(hold))

                        list = [index for index in range(len(self.on_hold_list)) if self.on_hold_list[index][0] == member_addrs[0]]
                        print(list, self.on_hold_list)
                        if len(list) > 0:
                            self.on_hold_list[index] = (self.on_hold_list[index][0], self.on_hold_list[index][1], hold)

                        else:
                            self.on_hold_list.append((member_addrs[0], time.time(), self.HOLD_DURATION))
    
                    raise ConnectionAbortedError('Wrong Password')
    
            self.wrong_password_ip_list.append((addrs, 1))
            print('Wrong Attempt from this IP: ', self.wrong_password_ip_list[0][1])
            raise ConnectionAbortedError('Wrong Password')
        for ip in self.wrong_password_ip_list:
            if ip[0][0] == addrs[0]:
                self.wrong_password_ip_list.remove(ip)


if __name__ == '__main__':
    server = Server(HOST, PORT, 0, 5)
    server.start()
