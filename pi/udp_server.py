import socket
import random
import hashlib


def main():
    server_socket = socket.socke(socket.AF_INET, socket.SOCK_DGRAM)
    server_socket.bind(('127.0.0.1', 7777))

    while True:
        msg, addrs = server_socket.recvfrom(1024)
        msg = msg.decode()
        print(msg, 'From:', addrs)
