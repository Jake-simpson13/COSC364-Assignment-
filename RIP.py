import os
import re
import socket
import time
import math
import select
import sys

from multiprocessing import *
from threading import *
from packets import *

ROUTER_ID = None
INPUT_PORTS = []
OUTPUTS = []
USED_ROUTER_IDS = []
INCOMING_SOCKETS = []

TIME_TO_SLEEP = 3
LOW_ROUTER_ID_NUMBER = 0
HIGH_ROUTER_ID_NUMBER = 64000
LOW_PORT_NUMBER = 1024
HIGH_PORT_NUMBER = 64000

IP = "127.0.0.1"

# a tuple with the layout (Router ID, Metric Value, Router Learnt From, Time Loop)
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
        USED_ROUTER_IDS.append(ROUTER_ID)

    

""" extract the inport ports to set up UDP sockets. Returns a list of all valid 
    port numbers between 1024 and 64000 """
def extractValidInputPorts(line):
    inputPorts = re.findall('[0-9]+', line)
    for ports in inputPorts:
        if portNumberCheck(ports) == True:
            INPUT_PORTS.append(int(ports))  



""" extract the output ports to set up UDP sockets. returns a list of all valid 
    port numbers between 1024 and 64000 """
def extractValidOutputPorts(line):
    global FORWARDING_TABLE
    global OUTPUTS
    global USED_ROUTER_IDS
    age = 0
    splitline = line.split(" ")
    for lines in splitline:
        #outputPorts = re.findall("[-+]?[.]?[\d]+(?:,\d\d\d)*[\.]?\d*(?:[eE][-+]?\d+)?", lines)
        outputPorts = re.findall('[0-9]+', lines)
        
        if outputPorts != []:
            if len(outputPorts) == 3:
                portnum = outputPorts[0]
                metric = outputPorts[1]
                router_id = outputPorts[2]
                OUTPUTS.append([int(portnum), int(metric), int(router_id)]) 
                FORWARDING_TABLE.append([int(router_id), int(metric), ROUTER_ID, age])
                USED_ROUTER_IDS.append(int(router_id))

        

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
        

""" close all open sockets """
def closeSockets():
    try:
        for sockID, sock in INCOMING_SOCKETS:
            sock.shutdown(socket.SHUT_RDWR)
            sock.close()
        print(INCOMING_SOCKETS)           
            
    except OSError: 
        print("Error closing Sockets")
        sys.exit(1)


########################## THREAD FUNCTIONS ##########################

""" a function that takes the data from a socket as a string, then creates 
    a new packet, and fills it with data to analyse """
def openData(packet, queue, used_id_q):
    global USED_ROUTER_IDS
    global FORWARDING_TABLE
    
    i = 4
    pay = ''    
    # turn Packet object into string and strip off byte indicators
    data_unstripped = str(packet)
    data = data_unstripped[2:-1]
    
    # get packet header information
    command = data[:1]
    version = data[1:2]
    generating_routerID = data[2:4]
    while i < len(data):
        # get packet payload information
        p_addr_fam_id = data[i:i+2]
        p_must_be_0_2 = data[i+2:i+4]
        p_ipv4_addr = data[i+4:i+8]
        p_routerID = data[i+8:i+12]
        p_must_be_0_4 = data[i+12:i+16]
        p_metric = data[i+16:i+20]
        i += 20

        """
        to ressemble packet, uncomment lines below and adjust code
        """
        #payload = Payload(p_addr_fam_id, p_ipv4_addr, p_routerID, p_metric)
        #pay += str(payload)
    #pac = Packet(command, version, generating_routerID)
    
    

        # create a new object to insert into our routing table, or update if already inserted
        graph_data = [int(p_routerID), int(p_metric), int(generating_routerID), 0]            
        print("###########\n",graph_data)
       
        #if int(p_routerID) in [routers[0] for routers in FORWARDING_TABLE]:
        j = 0
        while j < len(USED_ROUTER_IDS):
            if int(p_routerID) == USED_ROUTER_IDS[j]:
                print("MATCH")
                break
            j+=1
            
        # if we havent seen this entry before, add it to our FORWARDING TABLE, and save a copy of its ROUTER ID     
        if j >= len(USED_ROUTER_IDS):
            used_id_q.put(int(p_routerID))
            queue.put(graph_data)                
            
            



""" a function called for the receive thread instead of run(). an infinite 
loop that checks incoming sockets, and forwards accordingly or drops """
def receive(socket, q, q1):
    
    while True:
        data, addr = socket[1].recvfrom(1024) # buffer size is 1024 bytes
        print("SOCKET", socket[0], "received from:", addr, "message:", data)
        openData(data, q, q1)
    
    
def make_message(output):
    command = 2
    version = 2    
    payld = ''

    for router in FORWARDING_TABLE:
        if int(router[2]) == router[2]:
            print("Inserting poison reverse")
            route_payload = Payload(2, 2, str(router[0]), 16)
        else:    
            route_payload = Payload(2, 2, str(router[0]), str(router[1]))
        payld += str(route_payload)

    pac = Packet(command, version, ROUTER_ID, payld)    
    print("Packet =", pac)
    return pac


""" a function called by the receive function, to forward a packet to the 
next destination """    
def send():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    for output in OUTPUTS:

        message = make_message(output)
        sock.sendto(str(message).encode('utf-8'), ("127.0.0.1", int(output[0])))
    
   
        
""" sort nodes in graph to be ordered in terms of router ID from 
    smallest to largest """
def sortGraph(graph):
    return graph.sort(key=lambda tup: tup[0])
   
   
   
def print_table(table):
    print("Forwarding table:\n", table, "\n")
    print("Used router ids", USED_ROUTER_IDS, "\n\n")
    print("Directly connected neighbours", OUTPUTS)

   
   
def update(q, q1):
    global FORWARDING_TABLE
    global USED_ROUTER_IDS
    while True:
        try:
            FORWARDING_TABLE.append(q.get(False))
            USED_ROUTER_IDS.append(q1.get(False))                    
        except:
            print("no new data")      

        for route in FORWARDING_TABLE:
           # for r_id, metric, learnt_from, time_alive in route: 

            route[3] = route[3] + 1
            if route[3] == 6:
                route[1] = 16
            if route[3] >= 10:
                FORWARDING_TABLE = delete_link(route, FORWARDING_TABLE)
                
        print_table(FORWARDING_TABLE)
        send()
        time.sleep(TIME_TO_SLEEP)
    
def delete_link(route, table):
    print("need to remove", route[2], "from", USED_ROUTER_IDS)
    USED_ROUTER_IDS.remove(route[2])
    table.remove(route)
    return table
    
########################## MAIN ##########################
    
        
def main():
    configFile = getInputFile()
    setupData = readInputFile(configFile)
    incomingSocketSetUp()  

    print("\nRouter ID =", ROUTER_ID)


    sortGraph(FORWARDING_TABLE)
  
    print(INCOMING_SOCKETS)
    
    
    q = Queue()
    q1 = Queue()
    
    for socket in INCOMING_SOCKETS:
        process = Process(target=receive, args=(socket, q, q1, ))
        process.start() 
    update(q, q1)

    #closeSockets()


if __name__ == "__main__":
    main()