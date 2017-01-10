import threading

class Camera(threading.Thread):
  def __init__(self, motor1, motor2):
    self._motor1 = motor1
    self._motor2 = motor2
    self._move1 = 0
    self._move2 = 1
  
  def run(self):
    pass
  def ProcessMotor(self):
    pass

if __name__ == '__main__':
  import motor_base
  m1 = motor_base.MotorBase(2)
  m2 = motor_base.MotorBase(6)
  c = Camera
  
  pass
