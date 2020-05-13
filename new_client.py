import socket
import random
import hashlib
import keyboard_fly


UP = 72
DOWN = 80
LEFT = 75
RIGHT = 77

SPEED = '99'
ANGLE = '99'
REPS_LIMIT = 10

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


def main():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    PI = 'raspberrypi.local'
    HOME = '127.0.0.1'
    sock.connect((PI, 7777))

    password = input('PASSWORD:')

    iters = int(sock.recv(1024).decode())
    print(iters)
    if iters >= REPS_LIMIT:
        print('MAX REPS EXCEEDED.')
        random.seed(92760325 ** 2)
        iters = 1
    else:
        random.seed(92760325)

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