import socket, traceback

HOST = '0.0.0.0'
PORT = 7777

FUNC_KEY = {
    'S': 'STRAIGHT',
    'A': 'ANGLE'
}

BOOL = {
    0: False,
    1: True
}

def init_server():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((HOST, PORT))
    server_socket.listen(1)
    print('Remote Control Server is UP! \n WARNING! THIS SERVER IS NOT SECURE!')
    return server_socket


def handle_new_client_authentication(client_socket):
    # authentication - currently mock
    return True


def split_by_rcp(msg_len, client_socket):
    try:
        full_msg = client_socket.recv(msg_len)
        func_key = full_msg[0]
        full_msg = full_msg[1:]
        speed = int(full_msg[:2])
        forward = BOOL[int([-1])]
        return func_key, speed, forward
    except:
        raise BufferError('Protocol Invalid')


def command_receiver(client_socket):
    msg_len = client_socket.recv(2)
    func_key, speed, forward = split_by_rcp(msg_len, client_socket)
    print(func_key, speed, forward)


def main():
    server_socket = init_server()
    while True:
        client_socket = server_socket.accept()
        print('New Client Connected...')
        try:
            if handle_new_client_authentication(client_socket):
                command_receiver(client_socket)
        except:
            print('Client Disconnected')
            traceback.print_tb()


if __name__ == '__main__':
    main()
