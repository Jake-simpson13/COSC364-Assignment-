import os
import re
import socket
import time
import math
import select
import sys

from multiprocessing import *
from threading import *

ROUTER_ID = None
INPUT_PORTS = []
OUTPUTS = []
USED_ROUTER_IDS = []
INCOMING_SOCKETS = []
OUTGOING_SOCKETS = []

LOW_ROUTER_ID_NUMBER = 1
HIGH_ROUTER_ID_NUMBER = 64000
LOW_PORT_NUMBER = 1024
HIGH_PORT_NUMBER = 64000

IP = "127.0.0.1"

# a tuple with the layout (Router ID, Metric Value, Router Learnt From)
FORWARDING_TABLE = []


########################## FILE SETUP ##########################

""" ask for filename """
def getInputFile():
    print("Enter a valid configuration file: ")
    configFile = input()
    return configFile



""" check the port number provided is within the allowed parameters """
def routerIdCheck(routerID):
    if int(routerID) > LOW_ROUTER_ID_NUMBER and int(routerID) < HIGH_ROUTER_ID_NUMBER:
        return True



""" check that the port numbers provided from the config file are between 
    the allowed parameters"""
def portNumberCheck(portno):
    if int(portno) > LOW_PORT_NUMBER and int(portno) < HIGH_PORT_NUMBER:
        return True
    
    

""" extract the router ID from the line parsed in the config file.
    If two router IDs are given in the config file, the second one will be
    deemed a correction / will override the first or previous Router IDs """
def extractRouterID(line):
    global ROUTER_ID
    routerID = re.findall(r'\b\d+\b', line)
    if routerIdCheck(int(routerID[-1])) == True:
        ROUTER_ID = (int(routerID[-1]))
        #print("Router ID =", ROUTER_ID)

    

""" extract the inport ports to set up UDP sockets. Returns a list of all valid 
    port numbers between 1024 and 64000 """
def extractValidInputPorts(line):
    inputPorts = re.findall('[0-9]+', line)
    for ports in inputPorts:
        if portNumberCheck(ports) == True:
            INPUT_PORTS.append(int(ports))
    #print("Input Ports =", INPUT_PORTS)    



""" extract the output ports to set up UDP sockets. returns a list of all valid 
    port numbers between 1024 and 64000 """
def extractValidOutputPorts(line):
    splitline = line.split(" ")
    for lines in splitline:
        outputPorts = re.findall("[-+]?[.]?[\d]+(?:,\d\d\d)*[\.]?\d*(?:[eE][-+]?\d+)?", lines)
        if outputPorts != []:
            if portNumberCheck(outputPorts[0]) == True:
                OUTPUTS.append(outputPorts)
    #print("output Ports =", OUTPUTS) 
    


""" read and extract the router-id, input-ports and outputs """
def readInputFile(configFile):
    try:
        infile = open(configFile)
        lines = infile.readlines()
    
        for line in lines:
            if "router-id" in line:
                extractRouterID(line) 

            if "input-ports" in line:
                extractValidInputPorts(line)

            if "outputs" in line:
                extractValidOutputPorts(line)
        
        infile.close()
                
    except FileNotFoundError:
        print("Sorry, the entered file was not found.")
        configFile = getInputFile()
        setupData = readInputFile(configFile)
    
    
########################## UDP SOCKETS ##########################
    
""" Set up a UDP port for all input ports. Acting as server side """
def incomingSocketSetUp():              
    for inputSock in INPUT_PORTS:
        sockID = "IncomingSocket" + str(inputSock)
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.setblocking(True)
        try:
            sock.bind((IP, inputSock))
            INCOMING_SOCKETS.append((sockID,sock))
        except OSError:
            print("Socket already bound \n\n")
            sys.exit(1)
        
        
""" set up a UDP port for all out output ports. Acting as client side """
def outputSocketSetUp():
    for portno, metricValue, routerID in OUTPUTS:
        metricValue = metricValue.strip('-')
        routerID = routerID.strip('-')
        sockID = "OutgoingSocket" + str(routerID)
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        OUTGOING_SOCKETS.append((sockID, portno, routerID, metricValue, sock))        


""" close all open sockets """
def closeSockets():
    try:
        for sockID, sock in INCOMING_SOCKETS:
            sock.shutdown(socket.SHUT_RDWR)
            sock.close()
        for sockID, portno, routerID, metricValue, sock in OUTGOING_SOCKETS: 
            sock.shutdown(socket.SHUT_RDWR)
            sock.close()
        print(INCOMING_SOCKETS)
        print(OUTGOING_SOCKETS)            
            
    except OSError: 
        print("Error closing Sockets")
        sys.exit(1)


        
########################## BELLMAN FORD ALGORITHM ##########################
    
""" a graph from the routers given in the config file that have passed all 
    required tests.
    Format is:
    (Router ID, Metric Value, router learnt from) 
    in a tuple """    
def directConnectGraph():   
    for node in OUTGOING_SOCKETS:
        #print("routerID =", node[2], "metricValue =", node[3])
        FORWARDING_TABLE.append((int(node[2]), int(node[3]), ROUTER_ID)) 

    
    
""" sort nodes in graph to be orderedd in terms of router ID from 
    smallest to largest """
def sortGraph(graph):
    return graph.sort(key=lambda tup: tup[0])


########################## THREAD FUNCTIONS ##########################

""" a function called for the receive thread instead of run(). an infinite 
loop that checks incoming sockets, and forwards accordingly or drops """
def receive(socket):
    
    while True:
        print("current socket id" ,socket[0], "\ncurrent socket", socket[1], "\n")
        print('now waiting for data')
        data, addr = socket[1].recvfrom(1024) # buffer size is 1024 bytes
        print("received from:", addr, "message:", data)
        #break
    
    #receive.terminate() 
    
    

""" a function called by the receive function, to forward a packet to the 
next destination """    
def send():
    i = 1
    
    
    
def create_rip_packet():
    
    
########################## MAIN ##########################
    
        
def main():
    configFile = getInputFile()
    setupData = readInputFile(configFile)
    incomingSocketSetUp()
    outputSocketSetUp()    
    
    print()
    print("Router ID =", ROUTER_ID)

    directConnectGraph()
    sortGraph(FORWARDING_TABLE)
    
    print("Forwarding table \n", FORWARDING_TABLE, "\n")
    print("OUTGOING SOCKETS \n", OUTGOING_SOCKETS)    
    print()

    current_processes = []
    # starts threads, that use two functions receive to receive, then send to forward data
    print(INCOMING_SOCKETS)
    for socket in INCOMING_SOCKETS:
        print("starting process for", socket[0])
        process = Process(target=receive, args=(socket, ))
        #process = Thread(target=receive, args=(socket, ))
        current_processes.append(process)
        
    for process in current_processes:
        process.start()   
        #process.join()
        print(process)
        #receive(socket)

    

    #closeSockets()






'''        
        MESSAGE = "Hello, World!"

        for sid, input_port, cost, router_id, sock in OUTGOING_SOCKETS:
        
           # sock = socket.socket(socket.AF_INET, # Internet
           #          socket.SOCK_DGRAM) # UDP
            sock.sendto(MESSAGE.encode('utf-8'), (IP, int(input_port)))        
'''        
'''
            data, addr = sock.recvfrom(1024) # buffer size is 1024 bytes
            print("received from:", addr, "message:", data)
    

'''

"""
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # Internet, UDP
while True:
    if MESSAGE != "":
        sock.sendto(MESSAGE.encode('utf-8'), (UDP_IP, UDP_PORT))
        MESSAGE = ""
    MESSAGE = str(input())
"""



if __name__ == "__main__":
    main()