from flask import Flask, render_template, request
import socket
import random
import hashlib

SPEED = '99'
ANGLE = '99'
REPS_LIMIT = 1000000
PI = '10.0.0.16'
HOME = '127.0.0.1'

class Client():
    def __init__(self):

        self.SEED = None
        self.PASSWORD = None

        self.salt = None

        self.initialized = False



    def up(self):
        if not self.SEED or not self.PASSWORD:
            return
        if not self.initialized:
            self.initialize_connection()

        command = 'S991'

        self.hash_and_send(command)




    def down(self):
        if not self.SEED or not self.PASSWORD:
            return
        if not self.initialized:
            self.initialize_connection()

        command = 'S990'

        self.hash_and_send(command)

    def left(self):
        if not self.SEED or not self.PASSWORD:
            return
        if not self.initialized:
            self.initialize_connection()

        command = 'T990'

        self.hash_and_send(command)

    def right(self):
        if not self.SEED or not self.PASSWORD:
            return
        if not self.initialized:
            self.initialize_connection()

        command = 'T991'

        self.hash_and_send(command)

    def initialize_connection(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((PI, 7777))

        iters_len = int(self.sock.recv(3))
        iters = int(self.sock.recv(iters_len).decode())

        print(iters)
        if iters >= REPS_LIMIT:
            print('MAX REPS EXCEEDED.')
            random.seed(self.SEED ** 2)
            iters = iters - REPS_LIMIT + 1
        else:
            random.seed(self.SEED)

        assert iters >= 1
        for i in range(iters):
            self.salt = random.randint(0, 99999999)

        print(iters, self.salt)

        if self.sock and self.salt:
            self.initialized = True

    def hash_and_send(self, command):
        string = self.PASSWORD + str(self.salt) + command
        m = hashlib.sha256()
        m.update(string.encode())
        hsh = m.digest()
        hsh_len = str(len(hsh))
        self.sock.send(hsh_len.encode())
        self.sock.send(hsh)
        print(self.salt)
        self.salt += 1



app = Flask(__name__)

my_client = Client()



@app.route('/')
def index():
    return render_template('index.html')

@app.route('/left')
def left():
    print('left')
    my_client.left()
    return '200'

@app.route('/right')
def right():
    print('right')
    my_client.right()
    return '200'

@app.route('/up')
def up():
    print('up')
    my_client.up()
    return '200'

@app.route('/down')
def down():
    print('down')
    my_client.down()
    return '200'

@app.route('/seed/<seed>')
def get_seed( seed):
    if seed:
        my_client.SEED = seed
        return '200'
    return '204'

@app.route('/password/<password>')
def get_password(password):
    if password:
        my_client.PASSWORD = password
        return '200'
    return '204'


if __name__ == '__main__':
    app.run()