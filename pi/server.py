import socket
import traceback
import motor_control

HOST = '0.0.0.0'
PORT = 7777


def straight(controls, speed, forward):
    controls.straight(speed, forward)


def turn(controls, angle, side):
    if side:
        side = 'RIGHT'
    else:
        side = 'LEFT'
    controls.turn(side, angle)


FUNC_KEY = {
    'S': straight,
    'T': turn
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
        full_msg = client_socket.recv(msg_len).decode()
        func_key = full_msg[0]
        full_msg = full_msg[1:]
        speed = int(full_msg[:2])
        direction = BOOL[int(full_msg[-1])]
        return FUNC_KEY[func_key], speed, direction
    except:
        raise BufferError('Protocol Invalid')


def command_receiver(client_socket, controls):
    msg_len = int(client_socket.recv(2).decode())
    func, speed, direction = split_by_rcp(msg_len, client_socket)
    print(func, speed, direction)
    func(controls, speed, direction)




def main():
    controls = motor_control.Controls()
    server_socket = init_server()
    while True:
        client_socket, addr = server_socket.accept()
        print('New Client Connected... IP: ', addr)
        try:
            if handle_new_client_authentication(client_socket):
                client_on = True
                while client_on:
                    command_receiver(client_socket,controls)
        except:
            print('Client Disconnected')
            client_on = False
            traceback.print_exc()


if __name__ == '__main__':
    main()
