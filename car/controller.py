import car

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

  def __init__(generator, car, camera):
    self._generator = generator
    self._run = True
    self._car = car
    self._camera = camera

  def run(self):
    while self._run:
      for code, value in gen.GetNext():
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
        f = value
      elif code == 'CAR_B':
        b = value
      elif code == 'CAR_R':
        r = value
      elif code == 'CAR_L':
        l = value      

  def ChangeCamera(self, code, value):
    pass

  def ChangeCarSpeed(self, code, value):
    if value == 1:
      if code == 'CAR_U':
        self._car.SpeedUp()
      elif code == 'CAR_D':
        self._car.SlowDown()


