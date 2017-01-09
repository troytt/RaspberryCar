import generator
import socket
import time

class GeneratorSocket(generator.Generator):
  _cmd_map = {
    '38' : 'CAR_F',  # forward
    '40' : 'CAR_B',  # backward
    '37' : 'CAR_L',  # turn left
    '39' : 'CAR_R',  # turn right
    '74' : 'CAR_D',  # slow down
    '75' : 'CAR_U',  # speed up
    '76' : 'STOP',   # terminate
    '65' : 'CM_L',  # camera turn left
    '68' : 'CM_R',  # camera turn right
    '87' : 'CM_U',  # camera up
    '83' : 'CM_D',  # camera down
  }
  _host = '139.196.106.212'
  _port = 8002

  def __init__(self):
    generator.Generator.__init__(self)

  def Connect(self):
    while True:
      #time.sleep(5)
      try:
        self._client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._client.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)
        self._client.connect((self._host, self._port))
        print 'connect to', self._host, self._port
        return
      except socket.error as e:
        print e

  def run(self):
    self.Connect()
    while self._run:
      try:
        datas = self._client.recv(1024).decode()
        if len(datas) == 0:
          print 'connection lost'
          self.Put('STOP', 1)
          self.Connect()
        else:
          for data in datas.split('/'):
            if data.find(' ') <= 0:
              continue
            key, action = data.strip().split(' ')
            action = int(action)
            if key in self._cmd_map:
              key = self._cmd_map[key]
              self.Put(key, action)
      except socket.error as e:
        print 'connection lost', e
        self.Put('STOP', 1)
        self.Connect()
    print 'Generator Terminated'

if __name__ == '__main__':
  gen = GeneratorSocket()
  gen.start()
  for i in range(0, 100):
    print gen.GetNext()
  gen.Terminate()
  gen.join()
