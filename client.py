import socket

HOST = '127.0.0.1'
PORT = 7777


def main():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    print(sock)
    sock.connect((HOST, PORT))
    sock.send('04S701'.encode())


if __name__ == '__main__':
    main()
