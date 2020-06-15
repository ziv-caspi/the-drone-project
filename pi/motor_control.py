from sys import platform
if platform != 'win32':
    import RPi.GPIO as gpio
    platform = True
else:
    platform = False

freq = 50 # 50 Hz
proportions = 1.11111111111
class Board:
    """
        Board class. responsible for initializing the correct gpio pins with matching motors/controller.
    """
    def __init__(self, left_wheel, right_wheel):
        """
            initializes Board class. sets correct current to each pin according to wheels specified pins.
        :param left_wheel: Left Wheel Object
        :type left_wheel: Wheel
        :param right_wheel: Right Wheel Object
        :type right_wheel: Wheel
        """
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
    """
        Wheel class. responsible for giving direction to its motors, and controlling wheel.
    """
    def __init__(self, side):
        """
            initializes wheel. assigns gpio pins number to specific wheel
        :param side: which wheel is this
        :type side: str
        """
        if side == 'LEFT':
            self.direction_pin = 33
            self.power_pin = 31
            self.forward = True
            self.driving = False
        self.speed = 0
        if side == 'RIGHT':
            self.direction_pin = 37
            self.power_pin = 35

    def assign_pwm(self, pwm):
        """
`           sets wheel's pwm value to specified param.
        :param pwm: wanted pwm value
        :type pwm: int
        """
        self.pwm = pwm

    def set_direction(self, forward):
        """
            sets the wheel movement direction- True for forward and False for backward
        :param forward: movement direction
        :type forward: bool
        """
        if platform:
            gpio.output(self.direction_pin, forward)
        self.forward = forward

    def go(self, power = 100):
        """
            tells wheel to go, with specified power as pwm value.
        :param power: pwm value
        :type power: int  0-100
        :return: exits function if power not 0-100
        :rtype: None
        """
        if power == 0:
            self.driving = False

        if 0 > power > 100:
            return


        self.pwm.ChangeDutyCycle(power)
        self.speed = power

    def stop(self):
        """
            tells wheel to stop moving.
        """
        self.pwm.ChangeDutyCycle(0)
        self.driving = False
        self.speed = 0



class Controls:
    """
        Controls class- provides abstraction for movement actions.
         this is used by the server to execute movement commands.
    """
    def __init__(self):
        """
            Initializes the entire car- creates wheel objects and assigns to board.
        """
        self.speed = 70
        self.direction = True
        self.turning = False
        self.left_wheel = Wheel('LEFT')
        self.right_wheel = Wheel('RIGHT')

        self.board = Board(self.left_wheel, self.right_wheel)

        self.left_pwm = self.board.left_pwm
        self.right_pwm = self.board.right_pwm

        self.left_wheel.assign_pwm(self.left_pwm)
        self.right_wheel.assign_pwm(self.right_pwm)
        print('Controls Initialized')

    def align_direction(self, forward = None):
        """
            align wheels to be both the same direction
        :param forward: controls the direction
        :type forward: bool True for forward and False for backward
        """
        if forward == None:
            forward = self.direction

        self.left_wheel.set_direction(forward)
        self.right_wheel.set_direction(forward)
        self.direction = forward

    def align_wheels(self, speed = None):
        """
            align wheels to move at the same speed.
        """
        if not speed:
            speed = self.speed

        self.left_wheel.go(speed)
        self.right_wheel.go(speed)
        self.turning = False

    def straight(self, speed = None, forward = None):
        """
            makes both wheels to go straight at same speed
        :param speed: value for pwm
        :type speed: int 0-100, default is class speed.
        :param forward: True for forward False for backward, default is class direction.
        :type forward: bool
        """
        if not speed:
            speed = self.speed
        if forward == None:
            forward = self.direction

        self.align_direction(forward)
        self.align_wheels(speed)
        self.speed = speed
        self.direction = forward

    def stop(self, side = None):
        """
            makes wheels stop.
        :param side: optional, if you want only one side to stop.
        :type side: str
        """
        if side:
            if side == 'LEFT':
                self.left_wheel.stop()
            else:
                self.right_wheel.stop()
            return

        self.left_wheel.stop()
        self.right_wheel.stop()

    def turn(self, side, angle):
        """
            slows down one wheel so that turning is achieved
        :param side: which side to turn to
        :type side: bool
        :param angle: angle of the turn means how hard the turn is, ratio between the two wheels speeds.
        :type angle: int 0-99
        """
        power = angle * proportions

        if self.turning:
            self.align_wheels()

        if not side:
            print('LEFT')
            power = self.left_wheel.speed - power
            if power < 0:
                power = 0
            if power > 100:
                power = 100
            self.left_wheel.go(power)
        elif side:
            print('RIGHT')
            power = self.right_wheel.speed - power
            if power < 0:
                power = 0
            if power > 100:
                power = 100
            self.right_wheel.go(power)
        self.turning = True

if __name__ == '__main__':
    controls = Controls()
