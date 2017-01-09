from inputs import get_gamepad
import atexit
import signal
import time
import RPi.GPIO as GPIO
import threading
import socket
import evdev
import web
from evdev import InputDevice, list_devices
from select import select
import fcntl
import struct
import sys
import Queue

GPIO.cleanup()

GPIO.setmode(GPIO.BOARD)
GPIO.setwarnings(True)

WEB_PORT = 8000

key_w = evdev.ecodes.ecodes['KEY_UP'] # forward
key_s = evdev.ecodes.ecodes['KEY_DOWN'] # backward
key_a = evdev.ecodes.ecodes['KEY_LEFT'] # turn left
key_d = evdev.ecodes.ecodes['KEY_RIGHT'] # turn right
key_j = evdev.ecodes.ecodes['KEY_J'] # slow down
key_k = evdev.ecodes.ecodes['KEY_K'] # speed up
key_l = evdev.ecodes.ecodes['KEY_L'] # terminate
key_left = evdev.ecodes.ecodes['KEY_A'] # camera turn left
key_right = evdev.ecodes.ecodes['KEY_D'] # camera turn right
key_up = evdev.ecodes.ecodes['KEY_W'] # camera up
key_down= evdev.ecodes.ecodes['KEY_S'] # camera down
key_1 = evdev.ecodes.ecodes['KEY_1'] # camera forward
key_2= evdev.ecodes.ecodes['KEY_2'] # camera backward
key_3= evdev.ecodes.ecodes['KEY_3'] # crawl close
key_4= evdev.ecodes.ecodes['KEY_4'] # crawl open

ascii_map = {'38': key_w,
             '37': key_a,
             '39': key_d,
             '40': key_s,
             '49': key_1,
             '50': key_2,
             '51': key_3,
             '52': key_4,
             '87': key_up,
             '83': key_down,
             '65': key_left,
             '68': key_right,
             '74': key_j,
             '75': key_k,
             '76': key_l}

terminate = False

def SigHandler(sig, frame):
  global terminate  
  terminate = True
  print 'control c is pressed'

signal.signal(signal.SIGINT, SigHandler)

def GetIP():
  s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
  return socket.inet_ntoa(fcntl.ioctl(s.fileno(), 0x8915, struct.pack('256s', 'wlan0'))[20:24])

class Camera(threading.Thread):
  def __init__(self, port):
    self._degree = 0    
    self._port = port
    GPIO.setup(port, GPIO.OUT, initial=False)
    self._handler = GPIO.PWM(port, 50) #50HZ  
    self._handler.start(0)
    self._direction = 0
    self._terminate = False
    threading.Thread.__init__(self)

  def Turn(self):
    #degree = 12.5 - 5 * self._degree / 360
    degree = 2.5 + 10 * self._degree / 180
    if degree < 0 or degree > 100:
      return

    self._handler.ChangeDutyCycle(degree)
    time.sleep(0.02)
    self._handler.ChangeDutyCycle(0)
    time.sleep(0.2)


  def TurnLeft(self):
    print self._port, 'turn left'
    if self._degree < 180:
      self._degree += 10
      self.Turn()

  def TurnRight(self):
    print self._port, 'turn right'
    if self._degree > 0:
      self._degree -= 10
      self.Turn()

  def Reset(self):
    self._degree = 0
    self.Turn()

  def Terminate(self):
    self._terminate = True

  def run(self):
    while not self._terminate:
      if self._direction == 1:
        self.TurnLeft()
      elif self._direction == -1:
        self.TurnRight()

class SocketGenerator(threading.Thread):
  def __init__(self):
    
    self._queue = Queue.Queue()
    threading.Thread.__init__(self)

  def connect(self):
    while True:
      time.sleep(5)
      try:
        self._host = '139.196.106.212'
        self._port = 8002
        self._client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._client.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)
        self._client.connect((self._host, self._port))
        print 'connect to', self._host, self._port
        return
      except socket.error as e:
        print e
    
  def run(self):
    self.connect()
    while True:
      try:
        datas = self._client.recv(1024).decode()
        print datas
        if len(datas) == 0:
          print 'connection lost'
          self._queue.put([('STOP', 0)])
          self.connect()
        else:
          for data in datas.split('/'):
            if data.find(' ') <= 0:
              continue
            key, action = data.strip().split(' ')
            action = int(action)
            if key in ascii_map:
              key = ascii_map[key]
              print (key, action)
              self._queue.put([(key, action)])
            elif key == 'STOP':
              self._queue.put([('STOP', 0)])
      except socket.error as e:
        print 'connection lost', e
        self._queue.put([('STOP', 0)])
        self.connect()

  def GetNext(self):
    return self._queue.get()
    
class WebGenerator(object):
  def __init__(self):
    self._queue = web.GetQueue()

  def GetNext(self):
    while True:
      key, action = self._queue.get()
      if key in ascii_map:
        key = ascii_map[key]
        return [(key, action)]
      else:
        continue

class LocalInputGenerator(object):
  def __init__(self, fn):
    self._dev = InputDevice(fn)

  def GetNext(self):
    select([self._dev], [], [])
    ret = []
    for event in self._dev.read():
      ret.append((event.code, event.value))
    return ret

class Wheel:
  _speed = 6
  _min_speed = 5
  _max_speed = 10
  _cycle = 1

  def __init__(self, forward_port, backward_port, enable_port):
    self._forward_port = forward_port
    self._backward_port = backward_port
    self._enable_port = enable_port

    GPIO.setup(forward_port, GPIO.OUT)
    GPIO.setup(backward_port, GPIO.OUT)
    GPIO.setup(enable_port, GPIO.OUT)

    GPIO.output(forward_port, False)
    GPIO.output(backward_port, False)
    GPIO.output(enable_port, True)
    

  def SpeedUp(self):
    if self._speed < self._max_speed:
      self._speed += 1
    print 'Speed up to', self._speed
    time.sleep(0.1)

  def SlowDown(self):
    if self._speed > self._min_speed:
      self._speed -= 1
    print 'Slow down to', self._speed
    time.sleep(0.1)

  def speed_control(self):
    if self._cycle < self._max_speed:
      self._cycle += 1
    else:
      self._cycle = 1
    return self._cycle <= self._speed

  def forward(self):
    if self.speed_control():
      GPIO.output(self._forward_port, True)
      GPIO.output(self._backward_port, False)
    else:
      #print 'stop due to speed'
      self.stop()

  def backward(self):
    if self.speed_control():
      GPIO.output(self._forward_port, False)
      GPIO.output(self._backward_port, True)
    else:
      #print 'stop due to speed'
      self.stop()

  def stop(self):
    GPIO.output(self._forward_port, False)
    GPIO.output(self._backward_port, False)

class Car(threading.Thread):
  def __init__(self, left_wheel, right_wheel):
    self._right_wheel = right_wheel
    self._left_wheel = left_wheel
    self._left_direction = 0
    self._right_direction = 0
    self._terminate = False
    threading.Thread.__init__(self)

  def run(self):
    while not self._terminate:
      time.sleep(0.01)
      # 1 - forward, -1 - backward, 0 - stop
      self.ProcessWheel(self._left_direction, self._left_wheel)
      self.ProcessWheel(self._right_direction, self._right_wheel)
    self._left_wheel.stop()
    self._right_wheel.stop()

  def ProcessWheel(self, d, wheel):
    if d == 0:
      wheel.stop()
    elif d == 1:
      wheel.forward()
    elif d == -1:
      wheel.backward()

  def Stop(self):
    self._left_direction = 0
    self._right_direction = 0
    
  def SpeedUp(self):
    self._left_wheel.SpeedUp()
    self._right_wheel.SpeedUp()

  def SlowDown(self):
    self._left_wheel.SlowDown()
    self._right_wheel.SlowDown()

  def Terminate(self):
    self._terminate = True

# http server
server = None
gen = None

# select input

devices = [InputDevice(fn) for fn in list_devices()]
index = 0
for dev in devices:
  print index, dev.name, dev.phys
  index += 1
try:
  print index, 'From Web: ', '%s:%d' % (GetIP(), WEB_PORT)
except:
  print index, 'From web disabled'
print index + 1, 'From socket server'

while True:
  index = int(raw_input())
  if index >= 0 and index < len(devices):
    gen = LocalInputGenerator(devices[index].fn)
    break
  elif index == len(devices):
    server = web.ControlServer(WEB_PORT)
    server.start()
    gen = WebGenerator()
    break
  elif index == len(devices) + 1:
    gen = SocketGenerator()
    gen.start()
    break
  else:
    print 'Select Again!!!!'
             

w_pressed = 0
s_pressed = 0
a_pressed = 0
d_pressed = 0

right_wheel = Wheel(16, 15, 40)
left_wheel = Wheel(18, 22, 40)
car = Car(left_wheel, right_wheel)
car.start()
camera1 = Camera(12)
camera2 = Camera(11)
#camera3 = Camera(40)
#camera4 = Camera(13)
#camera1.start()
#camera2.start()
#camera3.start()
#camera4.start()
atexit.register(GPIO.cleanup)

def UpdateKeyState():
  global w_pressed
  global s_pressed
  global a_pressed
  global d_pressed
  global gen
  global car
  global terminate
  global camera1
  global camera2
  #global camera3
  #global camera4

  camera_map = {key_left : camera1,
                key_right : camera1,
                key_up : camera2,
                key_down : camera2,
                #key_1 : camera3,
                #key_2 : camera3,
                #key_3 : camera4,
                #key_4 : camera4
                }
  ret = False
  for code, value in gen.GetNext():
    if code == 'STOP':
      car.Stop()
      continue
    if value in [0, 1] and code in [key_a, key_s, key_w, key_d, key_l]:
      ret = True
      if code == key_a:
        a_pressed = value
      elif code == key_d:
        d_pressed = value
      elif code == key_w:
        w_pressed = value
      elif code == key_s:
        s_pressed = value
      elif code == key_l:
        terminate = True
    # TODO(taodao) move this to another function
    if value == 1 and code in [key_j, key_k]:
      if code == key_j:
        car.SlowDown()
      elif code == key_k:
        car.SpeedUp()
    if code in [key_left, key_right, key_up, key_down]:
      if value == 0:
        camera_map[code]._direction = 0
      elif code in [key_left, key_up]:
        camera_map[code].TurnLeft()
        #camera_map[code]._direction = 1
      elif code in [key_right, key_down]:
        camera_map[code].TurnRight()
        #camera_map[code]._direction = -1

  return ret

def ReadDirections():
  global w_pressed
  global s_pressed
  global a_pressed
  global d_pressed

  while not UpdateKeyState():
    continue
  l = 0
  r = 0
  if w_pressed:
    l = 1
    r = 1
  elif s_pressed:
    l = -1
    r = -1
  if d_pressed:
    r = 0
  elif a_pressed:
    l = 0
  return l, r

try:
  while not terminate:
    car._left_direction, car._right_direction = ReadDirections()

  car.Terminate()
  car.join()
  camera1.Terminate()
  #camera1.join()
  camera2.Terminate()
  #camera2.join()
  #camera3.Terminate()
  #camera3.join()
  #camera4.Terminate()
  #camera4.join()
  if server:
    server.StopServer()
    server.join()
except Exception as e:
  print e
