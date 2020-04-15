import socket
import keyboard_fly
PI = '10.0.0.16'
HOME = '127.0.0.1'
HOST = PI
PORT = 7777

UP = 72
DOWN = 80
LEFT = 75
RIGHT = 77

SPEED = '70'
ANGLE = '50'

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
        pass

    else:
        pass
    return str(len(pkt)).zfill(2) + pkt


def main():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    print(sock)
    sock.connect((HOST, PORT))
    while True:
        pkt = create_pkt()
        if pkt != '' and pkt != '00':
            print(pkt)
            sock.send(pkt.encode())


if __name__ == '__main__':
    main()
