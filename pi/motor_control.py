from sys import platform
if platform != 'win32':
    import RPi.GPIO as gpio
    platform = True
else:
    platform = False
import time

freq = 50 # 50 Hz
proportions = 1.11111111111
class Board:
    def __init__(self, left_wheel, right_wheel):
        self.left_pwm = None
        self.right_pwm = None

        if platform:

            gpio.setmode(gpio.BOARD)
            gpio.setup(left_wheel.power_pin, gpio.OUT)
            gpio.setup(left_wheel.direction_pin, gpio.OUT)
            gpio.setup(right_wheel.power_pin, gpio.OUT)
            gpio.setup(right_wheel.direction_pin, gpio.OUT)

            self.left_pwm = gpio.PWM(left_wheel.power_pin, freq)
            self.right_pwm = gpio.PWM(right_wheel.power_pin, freq)

            self.left_pwm.start(0)
            self.right_pwm.start(0)

class Wheel:
    def __init__(self, side):
        if side == 'LEFT':
            self.direction_pin = 33
            self.power_pin = 31
            self.forward = True
            self.driving = False
        self.speed = 0
        if side == 'RIGHT':
            self.direction_pin = 37
            self.power_pin = 35

    def asssign_pwm(self, pwm):
        self.pwm = pwm

    def set_direction(self, forward):
        if platform:
            gpio.output(self.direction_pin, forward)
        self.forward = forward

    def go(self, power = 100):
        if power == 0:
            self.driving = False

        if 0 > power > 100:
            return
            

        self.pwm.ChangeDutyCycle(power)
        self.speed = power

    def stop(self):
        self.pwm.ChangeDutyCycle(0)
        self.driving = False
        self.speed = 0



class Controls:
    def __init__(self):
        self.speed = 70
        self.direction = True
        self.turning = False
        self.left_wheel = Wheel('LEFT')
        self.right_wheel = Wheel('RIGHT')

        self.board = Board(self.left_wheel, self.right_wheel)

        self.left_pwm = self.board.left_pwm
        self.right_pwm = self.board.right_pwm

        self.left_wheel.asssign_pwm(self.left_pwm)
        self.right_wheel.asssign_pwm(self.right_pwm)

    def allign_direction(self, forward = None):
        if forward == None:
            forward = self.direction

        self.left_wheel.set_direction(forward)
        self.right_wheel.set_direction(forward)
        self.direction = forward

    def allign_wheels(self):
        self.left_wheel.go(self.speed)
        self.right_wheel.go(self.speed)
        self.turning = False

    def straight(self, speed = None, forward = None):
        if not speed:
            speed = self.speed
        if forward == None:
            forward = self.direction

        self.allign_direction(forward)
        self.left_wheel.go(speed)
        self.right_wheel.go(speed)
        self.speed = speed
        self.direction = forward
        self.turning = False

    def stop(self, side = None):
        if side:
            if side == 'LEFT':
                self.left_wheel.stop()
            else:
                self.right_wheel.stop()

        self.left_wheel.stop()
        self.right_wheel.stop()

    def turn(self, side, angle):
        # as for now side slows down ---- vary well may be changed
        power = angle * proportions

        if self.turning:
            self.allign_wheels()

        if side == 'LEFT':
            power = self.left_wheel.speed - power
            if power < 0:
                power = 0
            if power > 100:
                power = 100
            self.left_wheel.go(power)
        if side == 'RIGHT':
            power = self.right_wheel.speed - power
            if power < 0:
                power = 0
            if power > 100:
                power = 100
            self.right_wheel.go(power)
        self.turning = True

    # def drive_forward(self, duration = None, power = None):
    #
    #     allign_direction(True)
    #
    #     self.left_wheel.drive(True)
    #     self.right_wheel.drive(True)
    #
    #     if duration:
    #         time.sleep(duration)
    #         self.left_wheel.drive(False)
    #         self.right_wheel.drive(False)
    #
    # def drive_backward(self, duration):
    #     self.left_wheel.set_direction(False)
    #     self.right_wheel.set_direction(False)
    #     self.left_wheel.drive(True)
    #     self.right_wheel.drive(True)
    #     if duration:
    #         time.sleep(duration)
    #         self.left_wheel.drive(False)
    #         self.right_wheel.drive(False)
