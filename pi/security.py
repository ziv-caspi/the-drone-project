import hashlib
import base64
import time

class Security():
    def __init__(self, HOLD_DURATION):
        self.wrong_password_ip_list = []
        self.on_hold_list = []
        self.HOLD_DURATION = HOLD_DURATION

    def check_password(self, password):
        m = hashlib.sha256()
        m.update(password)
        hashed = m.digest()
        encoded = base64.b64encode(hashed)
        with open('hashed_password.txt', 'rb') as file:
            password_hash = file.read()
            return password_hash == encoded

    def wrong_password(self, addrs):
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
                    hold = self.HOLD_DURATION ** (wrong_attempt_counter - 2)
                    print('Putting Client On Hold for {0} Seconds.'.format(hold))

                    list = [index for index in range(len(self.on_hold_list)) if
                            self.on_hold_list[index][0] == member_addrs[0]]
                    print(list, self.on_hold_list)
                    if len(list) > 0:
                        self.on_hold_list[index] = (self.on_hold_list[index][0], self.on_hold_list[index][1], hold)

                    else:
                        self.on_hold_list.append((member_addrs[0], time.time(), self.HOLD_DURATION))

                raise ConnectionAbortedError('Wrong Password')

        self.wrong_password_ip_list.append((addrs, 1))
        print('Wrong Attempt from this IP: ', self.wrong_password_ip_list[0][1])
        raise ConnectionAbortedError('Wrong Password')

    def correct_password(self, addrs):
        for ip in self.wrong_password_ip_list:
            if ip[0][0] == addrs[0]:
                self.wrong_password_ip_list.remove(ip)

    def handle_password_attempt(self, addrs, correct_password):
        if not correct_password:
            self.wrong_password(addrs)

        self.correct_password(addrs)

    def verify_client_hold_list_and_password(self, addrs, client_socket):
        for holder in self.on_hold_list:
            ip = holder[0]
            start_time = holder[1]
            required_hold_time = holder[2]
            if ip == addrs[0]:
                cur_time = time.time()
                diff = cur_time - start_time
                if diff > required_hold_time:
                    if self.client_authentication(client_socket):
                        self.on_hold_list.remove(holder)
                        return True
                    return False
                    # for wrong_password_ip in self.wrong_password_ip_list:
                    #     if holder[0] == wrong_password_ip[0][0]:
                    #         self.wrong_password_ip_list.remove(wrong_password_ip)
                else:
                    print('Client{0} On Hold For {1} More Seconds'.format(addrs, required_hold_time - diff))
                    raise ConnectionRefusedError('Client is On hold list.')
        return self.client_authentication(client_socket)

    def client_authentication(self, client_socket):
        try:
            msg_len = int(client_socket.recv(2).decode())
            password = client_socket.recv(msg_len)
            return self.check_password(password)

        except:
            return False
