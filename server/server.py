import socket
import os

from support.functions import *

format_to_function = {
    "NATIVE": get_native,
    "JSON": get_json,
    "XML": get_xml,
    "PROTO": get_proto,
    "AVRO": get_avro,
    "YAML": get_yaml,
    "MSGPACK": get_msg_pack
}

host = os.environ.get("HOST_NAME")
port = int(os.environ.get("PORT", 2001))
addr = (host,port)

s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.bind(addr)
print("Started")
while True:
    conn, addr = s.recvfrom(1024)
    if not conn:
        break
    f, ser_time, deser_time = format_to_function[host]()
    s.sendto((str(f) + "\nSerialization time: " + str(ser_time) + "\nDeserialization time: " + str(deser_time) + "\n").encode(), addr)
s.close()