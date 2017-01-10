import generator
import os
from urlparse import urlparse, parse_qs
from os import curdir, sep
from BaseHTTPServer import HTTPServer, BaseHTTPRequestHandler
import Queue
import time
import threading

queue = Queue.Queue()
last_ping_time = 0
active = False
cmd_map = {
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

def GetQueue():
  global queue
  return queue

class PiHTTPHandler(BaseHTTPRequestHandler):
  def do_GET(self):
    global last_ping_time
    global active
    global cmd_map
    
    parsed = urlparse(self.path)
    path = parsed.path
    if path == '/':
      f = open(curdir + sep + 'index.html') 
      self.send_response(200)
      self.send_header("Content-type", "text/html")
      self.end_headers()
      self.wfile.write(f.read())
      f.close()
      return
    if path == '/jquery.js':
      f = open(curdir + sep + 'jquery.js') 
      self.send_response(200)
      self.send_header("Content-type", "application/javascript")
      self.end_headers()
      self.wfile.write(f.read())
      f.close()
      return

    if path == '/ping':
      if active:
        last_ping_time = time.time()
      self.send_response(200)
      self.end_headers()
      return

    if path == '/action':
      active = True
      parameters = parse_qs(parsed.query)
      action = parameters.get('action', None)
      key = parameters.get('key', None)
      if key and action and len(key) == 1 and len(action) == 1:
        key = key[0]
        action = action[0]
        if key in cmd_map:
          if action in ['up', 'down']:
            if action == 'up':
              action = 0
            else:
              action = 1
          GetQueue().put([(key, action)])
      self.send_response(200)
      self.end_headers()
      return

class GeneratorWeb(generator.Generator):
  def __init__(self):
    self._http_server = None
    self._daemon = None
    self._port = 8000
    generator.Generator.__init__(self)
  
  def run(self):
    os.chdir('static')
    self._http_server = HTTPServer(('', self._port), PiHTTPHandler)
    self._daemon = threading.Thread(target = self.CheckAlive)
    self._daemon.start()
    while self._run:
      self._http_server.handle_request()
    self._daemon.join()
    

  def GetNext(self):
    return GetQueue().get()

  def CheckAlive(self):
    global active
    global last_ping_time
    while self._run:
      if active:
        if time.time() - last_ping_time > 1:
          active = False
          print 'Client dead, stop'
          queue.put([('STOP', 1)])
      time.sleep(0.2)

if __name__ == '__main__':
  g = GeneratorWeb()
  g.start()
  for i in range(0, 10):
    print g.GetNext()
  g.Terminate()
  g.join()

