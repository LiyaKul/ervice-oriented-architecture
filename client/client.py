import socketserver
import json
import os
import socket
import struct
import sys

# https://docs.python.org/3/library/socketserver.html

class MyUDPHandler(socketserver.BaseRequestHandler):
    def handle(self):
        data = self.request[0].strip()
        socket_receive = self.request[1]

if __name__ == "__main__":
    print('hello')
    HOST, PORT = "0.0.0.1", 2000
    with socketserver.UDPServer((HOST, PORT), MyUDPHandler) as server:
        server.serve_forever()
