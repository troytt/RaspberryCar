import time

class MotorBase():
  def __init__(self, port):
    self._degree = 0
    self._min_degree = 0
    self._max_degree = 180
    self._step = 10
    self._port = port

  def Turn(self):
    signal = 2.5 + 10 * self._degree / 180
    if signal < 0 or signal > 100:
      return
    #print 'Send signal', signal
    time.sleep(0.02)
    #print 'Send signal', 0
    time.sleep(0.2)

  def TurnLeft(self):
    if self._degree < self._max_degree:
      print self._port, 'Turn left to', self._degree
      self._degree += self._step
      self.Turn()

  def TurnRight(self):
    if self._degree > self._min_degree:
      self._degree -= self._step
      print self._port, 'Turn right to', self._degree
      self.Turn()

  def Reset(self):
    self._degree = 0
    self.Turn()

  def ReportDegree(self):
    print 'Motor', self._port, 'at', self._degree

if __name__ == '__main__':
  m = MotorBase(10)
  for i in range(0, 20):
    m.TurnLeft()
  for i in range(0, 20):
    m.TurnRight()
  m.Reset()
