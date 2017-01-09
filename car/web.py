import os
import re
import threading
import urllib
import time
import threading
from urlparse import urlparse, parse_qs
from os import curdir, sep
from BaseHTTPServer import HTTPServer, BaseHTTPRequestHandler
import Queue

queue = Queue.Queue()
lastPingTime = 0
active = False

def CheckLive():
  while True:
    if active:
      if time.time() - lastPingTime > 1:
        print 'Client dead, stop'
        queue.put(('76', 1))
        break
    time.sleep(0.2)
      
class TestHTTPHandler(BaseHTTPRequestHandler):  
  def do_GET(self):
    global queue
    global lastPingTime
    global active
    
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
        lastPingTime = time.time()
        print 'recieve ping at', lastPingTime

    if path == '/action':
      active = True
      parameters = parse_qs(parsed.query)
      action = parameters.get('action', None)
      key = parameters.get('key', None)
      if key and action and len(key) == 1 and len(action) == 1:
        key = key[0]
        action = action[0]
        if action in ['up', 'down']:
          if action == 'up':
            action = 0
          else:
            action = 1
        queue.put((key, action))

      self.send_response(200)
      self.end_headers()
      return

class ControlServer(threading.Thread):
  def __init__(self, port):
    self._http_server = None
    self._port = port
    self._run = False
    threading.Thread.__init__(self)
    
  def run(self):
    os.chdir('static')
    self._run = True
    self._http_server = HTTPServer(('', self._port), TestHTTPHandler)
    while self._run:
      self._http_server.handle_request()

  def StopServer(self):
    self._run = False

def GetQueue():
  global queue
  return queue

t = threading.Thread(target = CheckLive)
t.start()
