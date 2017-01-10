import threading
import time

class Car(threading.Thread):
  def __init__(self, left_wheel_ports, right_wheel_ports, debug = False):
    if debug:
      import wheel_base
      self._left_wheel = wheel_base.WheelBase('Left wheel', left_wheel_ports)
      self._right_wheel = wheel_base.WheelBase('Right wheel', right_wheel_ports)
    else:
      import wheel
      self._left_wheel = wheel.Wheel('Left wheel', left_wheel_ports)
      self._right_wheel = wheel.Wheel('Right wheel', right_wheel_ports)

    self._left_direction = 0
    self._right_direction = 0
    self._run = True
    threading.Thread.__init__(self)

  def run(self):
    while self._run:
      time.sleep(0.01)
      self.ProcessWheel(self._left_direction, self._left_wheel)
      self.ProcessWheel(self._right_direction, self._right_wheel)
    self._left_wheel.Stop()
    self._right_wheel.Stop()

  def ProcessWheel(self, d, wheel):
    if d == 0:
      wheel.Stop()
    elif d == 1:
      wheel.Forward()
    elif d == -1:
      wheel.Backward()

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
    self._run = False

  def ReportWheelDirection(self):
    self._left_wheel.ReportDirection()
    self._right_wheel.ReportDirection()


if __name__ == '__main__':
  car = Car((11, 12, 10), (13, 14, 10), True)
  car.start()
  for i in [-1, 0, 1]:
    for j in [-1, 0, 1]:
      print 'Direction', i, j
      car._left_direction = i
      car._right_direction = j
      time.sleep(0.5)
      car.ReportWheelDirection()
      print ' ===== '
  for i in range(1, 6):
    car.SpeedUp()
  for i in range(1, 6):
    car.SlowDown()
  car.Terminate()
  car.join()
