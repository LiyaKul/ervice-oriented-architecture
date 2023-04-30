import os
import socketserver
import socket

hosts = [
    "NATIVE",
    "JSON",
    "XML",
    "PROTO",
    "AVRO",
    "YAML",
    "MSGPACK"
]

class MyUDPHandler(socketserver.BaseRequestHandler):
    def handle(self):
        data = self.request[0].strip().decode().split()
        if data[0] != "get_result" or data[1].upper() not in hosts:
            self.request[1].sendto(b"bad request", self.client_address)
            return
        addr = (data[1].upper(), 2001)
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.sendto(b"get result", addr)
        data = s.recvfrom(1024)[0]
        print(data)
        self.request[1].sendto(data, self.client_address)

if __name__ == "__main__":
    HOST = os.environ.get("PROXY_HOST", "0.0.0.0")
    PORT = int(os.environ.get("PROXY_PORT", 2000))
    with socketserver.UDPServer((HOST, PORT), MyUDPHandler) as server:
        print("Started")
        server.serve_forever()
