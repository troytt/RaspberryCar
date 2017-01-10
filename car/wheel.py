import time
import RPi.GPIO as GPIO
import wheel_base

class Wheel(wheel_base.WheelBase):
  _speed = 8
  _min_speed = 5
  _max_speed = 10
  _cycle = 1

  def __init__(self, name, ports):
    forward_port, backward_port, enable_port = ports
    GPIO.setup(forward_port, GPIO.OUT)
    GPIO.setup(backward_port, GPIO.OUT)
    GPIO.setup(enable_port, GPIO.OUT)

    GPIO.output(forward_port, False)
    GPIO.output(backward_port, False)
    GPIO.output(enable_port, True)
    wheel_base.WheelBase.__init__(self, name, ports)

  def Forward(self):
    if self.SpeedControl():
      GPIO.output(self._forward_port, True)
      GPIO.output(self._backward_port, False)
    else:
      self.Stop()

  def Backward(self):
    if self.SpeedControl():
      GPIO.output(self._forward_port, False)
      GPIO.output(self._backward_port, True)
    else:
      self.Stop()

  def Stop(self):
    GPIO.output(self._forward_port, False)
    GPIO.output(self._backward_port, False)
