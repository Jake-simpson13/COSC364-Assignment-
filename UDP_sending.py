import socket
from packets import *

UDP_IP = "127.0.0.1"
UDP_PORT = 6215
print("UDP target port:", UDP_PORT)
 
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # Internet, UDP
sock.bind((UDP_IP, 5100))
while True:
    pyld = ''
    x = Payload(2, 2, 3545, 5)
    pyld += str(x)
    z = Payload(32, 3456, 2309, 12)
    pyld += str(z)
    
    
    y = Packet(2, 2, 36, pyld)
    MESSAGE = y
    if MESSAGE != "":
        sock.sendto(str(MESSAGE).encode('utf-8'), (UDP_IP, UDP_PORT))
        MESSAGE = ""
    MESSAGE = str(input())
    
    
'''
#Test data

x = Payload(2, 40, 7, 3)
print(x.payload())
y = Payload(4, 30, 5, 3)
print(y.payload())
ppayload = [x,y]
z = Packet(1, 2, ppayload)
print(z.packet())
'''