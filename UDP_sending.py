import socket

UDP_IP = "127.0.0.1"
UDP_PORT = 6213
#MESSAGE = "Hello, World!"
print("Enter Message: ")
MESSAGE = str(input())
print("UDP target IP:", UDP_IP)
print("UDP target port:", UDP_PORT)
print("message:", MESSAGE)
 
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # Internet, UDP
while True:
    if MESSAGE != "":
        sock.sendto(MESSAGE.encode('utf-8'), (UDP_IP, UDP_PORT))
        MESSAGE = ""
    MESSAGE = str(input())