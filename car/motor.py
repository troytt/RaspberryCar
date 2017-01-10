import motor_base
import RPi.GPIO as GPIO
import time

class Motor(motor_base.MotorBase):

  def __init__(self, port):
    GPIO.setup(port, GPIO.OUT, initial=False)
    self._handler = GPIO.PWM(port, 50) #50HZ  
    self._handler.start(0)
    threading.Thread.__init__(self, port)

  def Turn(self):
    signal = 2.5 + 10 * self._degree / 180
    if signal < 0 or signal > 100:
      return
    self._handler.ChangeDutyCycle(signal)
    time.sleep(0.02)
    self._handler.ChangeDutyCycle(0)
    time.sleep(0.2)

if __name__ == '__main__':
  m = Motor(10)
  for i in range(0, 20):
    m.TurnLeft()
  for i in range(0, 20):
    m.TurnRight()
  m.Reset()
