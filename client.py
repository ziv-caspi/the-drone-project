import socket
import keyboard_fly
PI = '192.168.10.105'
HOME = '127.0.0.1'
HOST = PI
PORT = 7777

UP = 65
DOWN = 66
LEFT = 67
RIGHT = 68

SPEED = 70
ANGLE = 30

def create_pkt():
    c = ord(keyboard_fly.read_key())
    pkt = ''
    if c == UP:
        pkt = 'S' + SPEED + 1

    elif c == DOWN:
        pkt = 'S' + SPEED + 0

    elif c == RIGHT:
        pkt = 'T' + ANGLE + 1

    elif c == LEFT:
        pkt = 'T' + SPEED + 0

    elif c == 32:
        pass

    else:
        print('INVALID KEY, ONLY ARROW KEYS')

    return str(len(pkt)).zfill(2) + pkt
def main():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    print(sock)
    sock.connect((HOST, PORT))
    while True:
        pkt = create_pkt()
        sock.send(pkt.encode())


if __name__ == '__main__':
    main()
