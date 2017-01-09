import time
import Queue
import threading

class Generator(threading.Thread):
  def __init__(self):
    self._queue = Queue.Queue()
    self._run = True
    threading.Thread.__init__(self)

  def run(self):
    while self._run:
      time.sleep(0.1)
    print 'Generator Terminated'

  def GetNext(self):
    return self._queue.get()

  def Put(self, data):
    self._queue.put(data)

  def Terminate(self):
    self._run = False

if __name__ == '__main__':
  g = Generator()
  g.start()
  for i in range(0, 10):
    g.Put(i + 1)
  
  for i in range(0, 10):
    print g.GetNext()
  
  g.Terminate()
  g.join()
