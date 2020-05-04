import socket
import hashlib
import keyboard_fly

HOME = '127.0.0.1'
PI = '10.0.0.16'
HOST = PI
PORT = 7777

SPEED = '99'
ANGLE = '50'

UP = 72
DOWN = 80
LEFT = 75
RIGHT = 77

def create_pkt():
    c = ord(keyboard_fly.read_key())
    pkt = ''
    if c == UP:
        pkt = 'S' + SPEED + '1'

    elif c == DOWN:
        pkt = 'S' + SPEED + '0'

    elif c == RIGHT:
        pkt = 'T' + ANGLE + '1'

    elif c == LEFT:
        pkt = 'T' + ANGLE + '0'

    elif c == 32:
        pkt = 'B' + '000'
    else:
        pass
    return pkt


def main():
    addrs = (HOST, PORT)

    client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)


    password = input('Password:')
    while True:
        command = create_pkt()
        if command != '' and command != '00':
            client_socket.sendto(b'04', addrs)
            client_socket.sendto(b'SALT', addrs)
            salt = client_socket.recv(1024).decode()
            m = hashlib.sha256()
            m.update((password + salt + command).encode())
            hsh = m.digest()
            client_socket.sendto(str(len(hsh)).encode(), addrs)
            client_socket.sendto(hsh, addrs)



if __name__ == '__main__':
    main()