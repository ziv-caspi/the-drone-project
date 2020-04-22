import socket

sock = socket.socket()

sock.connect(('127.0.0.1', 7777))

msg = ''
while msg != 'exit':
    msg = input("MSG: ")
    sock.send(msg.encode())
sock.close()