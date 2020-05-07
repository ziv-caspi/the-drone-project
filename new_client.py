import socket
import random
import hashlib

random.seed(92760325)
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
PI = 'raspberrypi.local'
HOME = '127.0.0.1'
sock.connect((PI, 7777))

password = input('PASSWORD:')

iters = int(sock.recv(1024).decode())
print(iters)
if iters == 1:
    salt = random.randint(0, 99999999)
else:
    for i in range(iters):
        salt = random.randint(0, 99999999)

while True:
    print(salt)
    command = input('COMMAND:')
    string = password + str(salt) + command
    m = hashlib.sha256()
    m.update(string.encode())
    hsh = m.digest()
    hsh_len = str(len(hsh))
    sock.send(hsh_len.encode())
    sock.send(hsh)
    salt += 1
