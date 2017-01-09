import generator
import evdev
from evdev import InputDevice, list_devices
from select import select

class GeneratorKeyboard(generator.Generator):

  def __init__(self, fn):
    self._dev = InputDevice(fn)

  def run(self):
    while self._run:
      select([self._dev], [], [])
      for event in self._dev.read():
        self.Put((event.code, event.value))
        ret.append((event.code, event.value))
    print 'Generator Terminated'

if __name__ == '__main__':
  gen = None
  print list_devices()
  devices = [InputDevice(fn) for fn in list_devices()]
  index = 0
  for dev in devices:
    print index, dev.name, dev.phys
    index += 1

  index = int(raw_input())
  if index >= 0 and index < len(devices):
    gen = LocalInputGenerator(devices[index].fn)
    for i in range(0, 10):
      print 'get', g.GetNext()
    g.Terminate()
    g.join()
  else:
    print 'Wrong input'

  
