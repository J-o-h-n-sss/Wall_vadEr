import socket
import network
import time
from machine import Pin, Timer, PWM
from MotorFunctions import *

class Servo:
    """ A simple class for controlling a 9g servo with the Raspberry Pi Pico.
        Original code from: https://how2electronics.com/how-to-control-servo-motor-with-raspberry-pi-pico/
     """
 
    def __init__(self, pin: int or Pin or PWM, maxRotationDegrees = 180, zeroDegreesCycle=2500, maxDegreesCycle=7500):
        if isinstance(pin, int):
            pin = Pin(pin, Pin.OUT)
        if isinstance(pin, Pin):
            self.__pwm = PWM(pin)
        if isinstance(pin, PWM):
            self.__pwm = pin
        self.__pwm.freq(50)
        self.zeroDegreesCycle = zeroDegreesCycle
        self.maxDegreesCycle = maxDegreesCycle
        self.period = maxDegreesCycle - zeroDegreesCycle
        self.maxRotationDegrees = maxRotationDegrees
 
    def stop(self):
        """ Stop signal to the servo.
 
        """
        self.__pwm.deinit()
 
    def gotoDegrees(self, degrees: int):
        """ Moves the servo to the specified position in degrees.
        """

        cycle = int(self.zeroDegreesCycle + self.period * degrees / self.maxRotationDegrees)
        self.__pwm.duty_u16(cycle)
 
    def gotoMiddle(self):
        """ Moves the servo to the middle.
        """
        self.gotoDegrees(int(self.maxRotationDegrees / 2))
 
    def free(self):
        """ Allows the servo to be moved freely.
        """
        self.__pwm.duty_u16(0)
        
        
class Servo9GR(Servo):
    """ Specific servo: 9GR """
    def __init__(self, pin):
        super().__init__(pin, 180, 1000, 9000)


# Create a servo object connected to GP0
s = Servo9GR(0)
degree = 90
s.stop();

# This code blinks the onboard LED... useful to know it is alive
# led = Pin("LED", Pin.OUT)
# def blink(timer):
#     led.toggle()
# 
# timer = Timer()
# timer.init(freq=2.5, mode=Timer.PERIODIC, callback=blink)

# Create the led objects on GP1 and GP2 and define conveniet toggle functions
led1 = Pin(1, Pin.OUT)
def b1():
    led1.toggle()
    
led2 = Pin(2, Pin.OUT)
def b2():
    led2.toggle()

# Make sure the index.html file has been uploaded to the board; or you can choose to generate the html on the fly
# Original instructions here: https://www.tomshardware.com/how-to/raspberry-pi-pico-w-web-server
# and here: https://how2electronics.com/raspberry-pi-pico-w-web-server-tutorial-with-micropython/
page = open("index.html", "r")
html = page.read()
page.close()

# Wifi config
SSID = "CYBERTRON"
WIFI_PW = "Mr.LamYo"

# Connect to the wifi and Start the web server
def startWeb():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(SSID, WIFI_PW)
    
    # Wait for connect or fail
    wait = 10
    while wait > 0:
        if wlan.status() < 0 or wlan.status() >= 3:
            break
        wait -= 1
        print('waiting for connection...')
        time.sleep(1)
     
    # Handle connection error
    if wlan.status() != 3:
        raise RuntimeError('wifi connection failed')
    else:
        print('connected')
        ip=wlan.ifconfig()[0]
        print('IP: ', ip)
    
    try:
        if ip is not None:
            connection=open_socket(ip)
            serve(connection)
    except KeyboardInterrupt:
        machine.reset()

# Runs the web server, waiting for requests on port 80        
def serve(connection):
    global s
    global degree
    while True:
        print('waiting for requests')
        client = connection.accept()[0]
        request = client.recv(1024)
        request = str(request)
        try:
            request = request.split()[1]
        except IndexError:
            pass
        
        print(request)
        if request == '/Drive':
            move_forward()
        elif request == '/Left':
            turn_left()
        elif request == '/Right':
            turn_right()
            s.gotoDegrees(degree)
        elif request == '/Reverse':
            move_backward()
        elif request == '/Stop':
            stop()
        
        client.send(html)
        client.close()

# The underlying socket communication for the web server
def open_socket(ip):
    # Open a socket
    address = (ip, 80)
    connection = socket.socket()
    connection.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    connection.bind(address)
    connection.listen(1)
    print(connection)
    return(connection)
