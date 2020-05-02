import socket
import hashlib

HOST = '127.0.0.1'
PORT = 7777

def main():
    addrs = (HOST, PORT)

    client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)


    password = input('Password:')
    while True:
        command = input('Command:')
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