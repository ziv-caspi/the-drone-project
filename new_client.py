import socket
import random
import hashlib
import keyboard_fly


UP = 72
DOWN = 80
LEFT = 75
RIGHT = 77
ENTER = 13

SPEED = '99'
ANGLE = '99'
REPS_LIMIT = 1000000

def create_command():
    c = ord(keyboard_fly.read_key())
    command = ''
    if c == UP:
        command = 'S' + SPEED + '1'

    elif c == DOWN:
        command = 'S' + SPEED + '0'

    elif c == RIGHT:
        command = 'T' + ANGLE + '1'

    elif c == LEFT:
        command = 'T' + ANGLE + '0'

    elif c == 32:
        print('space')
        command = 'B' + '000'

    else:
        pass
    return command



def enter_seq():
    print('Enter Car Sequence:')
    key = 0
    seed = ''
    while key != ENTER:
        key = ord(keyboard_fly.read_key())
        if key == LEFT:
            seed += 0
        if key == RIGHT:
            seed += 1
    print(seed)
    return int(seed, 2)




def main():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    PI = '10.0.0.16'
    HOME = '127.0.0.1'
    sock.connect((PI, 7777))
    seed = enter_seq()
    password = input('PASSWORD:')
    iters_len = int(sock.recv(3))
    iters = int(sock.recv(iters_len).decode())
    print(iters)
    if iters >= REPS_LIMIT:
        print('MAX REPS EXCEEDED.')
        random.seed(seed ** 2)
        iters = iters - REPS_LIMIT + 1
    else:
        random.seed(seed)

    assert iters >= 1
    for i in range(iters):
        salt = random.randint(0, 99999999)

    while True:
        print(salt)
        command = create_command()
        if command != '' and command != '00':
            string = password + str(salt) + command
            m = hashlib.sha256()
            m.update(string.encode())
            hsh = m.digest()
            hsh_len = str(len(hsh))
            sock.send(hsh_len.encode())
            sock.send(hsh)
            salt += 1

if __name__ == '__main__':
    main()