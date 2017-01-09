import socket
import time

host = 'localhost'
port = 8002
run = True

def connect():
  while True:
    time.sleep(5)
    try:
      client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
      client.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)
      client.connect((host, port))
      return client
    except socket.error as e:
      print e

client = connect()
while True:
  time.sleep(1)
  try:
    data = client.recv(1024)
    if len(data) == 0:
      print 'connection lost'
      client = connect()
    print data.decode()
  except socket.error as e:
    print 'connection lost', e
    client = connect()
