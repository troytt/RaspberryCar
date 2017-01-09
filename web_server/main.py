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
import socket

http_port = 8001
#socket_addr = '139.196.106.212'
socket_addr = 'localhost'
socket_port = 8002
queue = Queue.Queue()
last_ping_time = 0
client_active = False


class TestHTTPHandler(BaseHTTPRequestHandler):
  def do_GET(self):
    global queue
    global last_ping_time
    global client_active


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
      last_ping_time = time.time()

    if path == '/action':
      client_active = True
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

class SocketServer(threading.Thread):
  def __init__(self, addr, port):
    self._queue = GetQueue()
    self._server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    self._server.bind((addr, port))
    self._server.listen(1)
    self._run = True
    threading.Thread.__init__(self)
    print 'Socket server started'

  def WaitClient(self):
    client, address = self._server.accept()
    print 'Client', address, ' connect'
    return client

  def StopServer(self):
    self._queue.put(('TERMINATE', 1))
    self._run = False

  def run(self):
    client = self.WaitClient()
    while self._run:
      try:
        key, action = self._queue.get()
        data = '%s %d/' % (key, action)
        if key == 'TERMINATE':
          client.close()
          self._server.close()
          break
        else:
          client.send(data.encode())
      except socket.error as e:
        client = self.WaitClient()
    print 'Socket Server stopped'


class ControlServer(threading.Thread):
  """ Control server has two opponents:
      A web server to recieve commands from user,
      A socket server to send commands to raspberry.
  """
  def __init__(self):
    self._http_server = None
    self._socket_server = None
    self._run = False
    threading.Thread.__init__(self)

  def run(self):
    os.chdir('static')
    self._run = True
    self._socket_server = SocketServer(socket_addr, socket_port)
    self._http_server = HTTPServer(('', http_port), TestHTTPHandler)
    self._socket_server.start()
    while self._run:
      self._http_server.handle_request()
    print 'HTTP server stopped'

  def CheckLive(self):
    global client_active
    global last_ping_time
    print 'Start check client live'
    while self._run:
      if client_active:
        if time.time() - last_ping_time > 1:
          print 'Client leave, stop'
          client_active = False
          self.SendStopCommand()
      time.sleep(0.1)

  def SendStopCommand(self):
    print 'Send STOP'
    GetQueue().put(('STOP', 1))

  def StopServer(self):
    print 'Stop all servers'
    self._run = False
    self._socket_server.StopServer()
    self._socket_server.join()

def GetQueue():
  global queue
  return queue



server = ControlServer()
server.start()
try:
  server.CheckLive()
except:
  print 'error, stop servers'
  server.StopServer()

server.join()



