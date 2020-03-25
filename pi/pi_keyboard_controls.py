import motor_control
import keyboard_fly


UP = 65
DOWN = 66
LEFT = 67
RIGHT = 68

controls = motor_control.Controls()
controls.allign_direction(True)

while True:
    c = ord(keyboard_fly.read_key())
    if c == UP:
        controls.straight(forward=True)
    elif c == DOWN:
        controls.straight(forward=False)
    elif c == RIGHT:
        controls.turn(side='RIGHT', angle=70)
    elif c == LEFT:
        controls.turn(side='LEFT', angle=70)
    elif c == 32:
        controls.stop()
    else:
        print('INVALID KEY, ONLY ARROW KEYS')
