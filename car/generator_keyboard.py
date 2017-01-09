import generator
import evdev
from evdev import InputDevice, list_devices
from select import select

class GeneratorKeyboard(generator.Generator):
  _cmd_map = {
    evdev.ecodes.ecodes['KEY_UP']    : 'CAR_F',  # forward
    evdev.ecodes.ecodes['KEY_DOWN']  : 'CAR_B',  # backward
    evdev.ecodes.ecodes['KEY_LEFT']  : 'CAR_L',  # turn left
    evdev.ecodes.ecodes['KEY_RIGHT'] : 'CAR_R',  # turn right
    evdev.ecodes.ecodes['KEY_J']     : 'CAR_D',  # slow down
    evdev.ecodes.ecodes['KEY_K']     : 'CAR_U',  # speed up
    evdev.ecodes.ecodes['KEY_L']     : 'STOP',   # terminate
    evdev.ecodes.ecodes['KEY_A']     : 'CM_L',  # camera turn left
    evdev.ecodes.ecodes['KEY_D']     : 'CM_R',  # camera turn right
    evdev.ecodes.ecodes['KEY_W']     : 'CM_U',  # camera up
    evdev.ecodes.ecodes['KEY_S']     : 'CM_D',  # camera down
  }

  def __init__(self, fn):
    self._dev = InputDevice(fn)
    generator.Generator.__init__(self)

  def run(self):
    while self._run:
      select([self._dev], [], [])
      for event in self._dev.read():
        if event.code in self._cmd_map:
          self.Put((self._cmd_map[event.code], event.value))
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
    g = GeneratorKeyboard(devices[index].fn)
    g.start()
    for i in range(0, 10):
      print 'get', g.GetNext()
    g.Terminate()
    g.join()
  else:
    print 'Wrong input'

  
