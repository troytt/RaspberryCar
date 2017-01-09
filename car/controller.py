import time
import car
import os
import threading
# valide cmd:
# Car directions : CAR_F, CAR_B, CAR_L, CAR_R
# Car speeds     : CAR_U, CAR_D
# Camera control : CM_L, CM_R, CM_U, CM_D
# Car control    : STOP
class Controller(object):
  _car_direction = ['CAR_F', 'CAR_B', 'CAR_L', 'CAR_R']
  _car_speed = ['CAR_U', 'CAR_D']
  _camera_control = ['CM_L', 'CM_R', 'CM_U', 'CM_D']
  _car_control = ['STOP']

  def __init__(self, generator, car, camera):
    self._generator = generator
    self._run = True
    self._car = car
    self._camera = camera

    self._car_f = 0
    self._car_b = 0
    self._car_l = 0
    self._car_r = 0

  def run(self):
    self._generator.start()
    self._car.start()
    while self._run:
      for data in gen.GetNext():
        print data
        code = data[0]
        value = data[1]
      #for code, value in gen.GetNext():
        if code in self._car_control:
          self.ChangeCar(code, value)
        elif code in self._car_direction:
          self.ChangeCarDirection(code, value)
        elif code in self._camera_control:
          self.ChangeCamera(code, value)
        elif code in self._car_speed:
          self.ChangeCarSpeed(code, value)

  def ChangeCar(self, code, value):
    if code == 'STOP':
      self._car.Stop()

  def ChangeCarDirection(self, code, value):
    if value in [0, 1]:
      if code == 'CAR_F':
        self._car_f = value
      elif code == 'CAR_B':
        self._car_b = value
      elif code == 'CAR_R':
        self._car_r = value
      elif code == 'CAR_L':
        self._car_l = value
    l = 0
    r = 0
    if self._car_f:
      l = 1
      r = 1
    elif self._car_b:
      l = -1
      r = -1
    if self._car_r:
      r = 0
    elif self._car_l:
      l = 0
    print code, value, l, r
    self._car._left_direction = l
    self._car._right_direction = r

  def ChangeCamera(self, code, value):
    pass

  def ChangeCarSpeed(self, code, value):
    if value == 1:
      if code == 'CAR_U':
        self._car.SpeedUp()
      elif code == 'CAR_D':
        self._car.SlowDown()

  def Terminate(self):
    self._run = False
    self._generator.Terminate()
    self._car.Terminate()
    self._generator.join()
    self._car.join()

def EnableCamera():
  while True:
    print 'Open camera live'
    os.system("""gst-launch-1.0 -v v4l2src ! 'video/x-raw, width=640, height=480, framerate=30/1' ! queue ! videoconvert ! omxh264enc !  h264parse ! flvmux ! rtmpsink location='rtmp://139.196.106.212/rtmp/live live=1'""")
    time.sleep(1)

if __name__ == '__main__':
  import generator_socket
  gen = generator_socket.GeneratorSocket()
  car = car.Car((11, 12, 10), (13, 14, 10), True)

  live = threading.Thread(target = EnableCamera)
  live.start()
  c = Controller(gen, car, None)
  c.run()

