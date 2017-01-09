import time
class WheelBase:
  _speed = 8
  _min_speed = 5
  _max_speed = 10
  _cycle = 1

  def __init__(self, name, ports):
    forward_port, backward_port, enable_port = ports
    self._forward_port = forward_port
    self._backward_port = backward_port
    self._enable_port = enable_port
    self._name = name
    self._direction = 0
    self.Stop()

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

  def SpeedControl(self):
    if self._cycle < self._max_speed:
      self._cycle += 1
    else:
      self._cycle = 1
    return self._cycle <= self._speed

  def Forward(self):
    self._direction = 1
    if self.SpeedControl():
      #print self._name, 'forward'
      pass
    else:
      self.Pause()

  def Backward(self):
    self._direction = -1
    if self.SpeedControl():
      #print self._name, 'backward'
      pass
    else:
      self.Pause()

  def Stop(self):
    self._direction = 0
    #print self._name, 'stop'
    pass

  def Pause(self):
    pass

  def ReportDirection(self):
    print self._name, self._direction
    
