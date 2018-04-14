import socket
from packets import *

UDP_IP = "127.0.0.1"
UDP_PORT = 6215
#MESSAGE = "Hello, World!"
#print("Enter Message: ")
#MESSAGE = str(input())
print("UDP target IP:", UDP_IP)
print("UDP target port:", UDP_PORT)
#print("message:", MESSAGE)
 
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # Internet, UDP
while True:
    x = Payload(2, 2, 5)
    y = Packet(2, 2, x)
    MESSAGE = y
    if MESSAGE != "":
        sock.sendto(str(MESSAGE).encode('utf-8'), (UDP_IP, UDP_PORT))
        MESSAGE = ""
    MESSAGE = str(input())