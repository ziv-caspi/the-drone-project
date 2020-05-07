import socket
import random
import hashlib

random.seed(92760325)
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect(('raspberrypi.local', 7777))

password = input('PASSWORD:')

iters = int(sock.recv(1024).decode())
if iters == 1:
    salt = random.randint(0, 99999999)
else:
    for i in range(iters - 1):
        salt = random.randint(0, 99999999)

while True:
    command = input('COMMAND:')
    string = password + salt + command
    m = hashlib.sha256()
    m.update(string.encode())
    hsh = m.digest()
    hsh_len = str(len(hsh))
    sock.send(hsh_len.encode())
    sock.send(hsh)
    salt += 1
