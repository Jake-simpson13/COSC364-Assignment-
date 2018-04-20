import socket
from packets import *

UDP_IP = "127.0.0.1"
UDP_PORT = 6215
print("UDP target port:", UDP_PORT)
 
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # Internet, UDP
sock.bind((UDP_IP, 5100))
while True:
    x = Payload(2, 2, 3545, 5)
    z = Payload(32, 3456, 2309, 12)
    y = Packet(2, 2, str(x) + str(z))
    MESSAGE = y
    if MESSAGE != "":
        sock.sendto(str(MESSAGE).encode('utf-8'), (UDP_IP, UDP_PORT))
        MESSAGE = ""
    MESSAGE = str(input())