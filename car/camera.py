import threading
import Queue
import time

class Camera(threading.Thread):
  def __init__(self, motor_port1, motor_port2, debug = False):
    if debug:
      import motor_base
      self._motor1 = motor_base.MotorBase(2)
      self._motor2 = motor_base.MotorBase(6)
    else:
      import motor
      self._motor1 = motor.Motor(2)
      self._motor2 = motor.Motor(6)
    self._action = Queue.Queue()
    self._run = True
    threading.Thread.__init__(self)
  
  def run(self):
    while self._run:
      time.sleep(0.01)
      d1, d2 = self._action.get()
      self.ProcessMotor(self._motor1, d1)
      self.ProcessMotor(self._motor2, d2)
    print 'Reset camera'

  def ProcessMotor(self, motor, direction):
    if direction == 1:
      motor.TurnRight()
    elif direction == -1:
      motor.TurnLeft()

  def TurnLeft(self):
    print 'Camera turn left'
    self._action.put((-1, 0))

  def TurnRight(self):
    print 'Camera turn right'
    self._action.put((1, 0))

  def TurnUp(self):
    print 'Camera turn up'
    self._action.put((0, -1))

  def TurnDown(self):
    print 'Camera turn down'
    self._action.put((0, 1))

  def Terminate(self):
    self._run = False
    self._action.put((0, 0))

  def ReportPosition(self):
    self._motor1.ReportDegree()
    self._motor2.ReportDegree()

if __name__ == '__main__':
  
  c = Camera(3, 6, True)
  c.start()
  for i in range(0, 3):
    c.TurnRight()
    for j in range(0, 3):
      c.TurnUp()
      time.sleep(0.2)
      c.ReportPosition()
      print ' ===== '
  for i in range(0, 3):
    c.TurnLeft()
    for j in range(0, 3):
      c.TurnDown()
      time.sleep(0.2)
      c.ReportPosition()
      print ' ===== '
  c.Terminate()
  print 'end'
  c.join()
