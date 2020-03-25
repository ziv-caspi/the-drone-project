import socket
import motor_control

IP = '0.0.0.0'
PORT = 5468


def stop(controls):
    controls.stop()


def up(controls, param1, param2):
    controls.straight(forward=param1)


def down(controls, param1, param2):
    controls.straight(forward=param1)


def left(controls, param1, param2):
    controls.turn(side=param1, angle=param2)


def right(controls, param1, param2):
    controls.turn(side=param1, angle=param2)


FUNCTIONS = {
    0: stop,
    1: up,
    2: down,
    3: right,
    4:left()
}

CONSTANTS = {
    0: False,
    1: True,
    3: 'LEFT',
    4: 'RIGHT'
}


def rc_protocol(command):
    func_key = command[:1]
    func = FUNCTIONS[func_key]
    command = command[1:]

    param1 = command[:1]
    param1 = CONSTANTS[param1]
    command = command[1:]

    param2 = int(command[:3])

    return func, param1, param2


def receiver(sock):
    command_length = sock.recv(2)
    command = sock.recv(command_length)
    return command


def main():
    controls = motor_control.Controls()
    controls.allign_direction(True)
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((IP, PORT))
    print('Remote Control Server is UP! \n WARNING! THIS SERVER IS NOT SECURE!')
    while True:
        server_socket.listen(1)
        client_socket, addrs = server_socket.accept()
        print('New Client Connected, IP is {0}'.format(addrs))
        while True:
            try:
                command = receiver(client_socket)
                func, param1, param2 = rc_protocol(command)
                print(str(func), param1, param2)
                func(controls, param1, param2)
            except:
                print('Something went wrong')


if __name__ ==  '__main__':
    main()
