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
OUTGOING_SOCKETS = []

LOW_ROUTER_ID_NUMBER = 1
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
    splitline = line.split(" ")
    for lines in splitline:
        outputPorts = re.findall("[-+]?[.]?[\d]+(?:,\d\d\d)*[\.]?\d*(?:[eE][-+]?\d+)?", lines)
        if outputPorts != []:
            if portNumberCheck(outputPorts[0]) == True:
                OUTPUTS.append([outputPorts])


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
    (Router ID, Metric Value, router learnt from, counter) 
    in a tuple """    
def directConnectGraph():   
    counter = 0
    for node in OUTGOING_SOCKETS:
        #print("routerID =", node[2], "metricValue =", node[3])
        FORWARDING_TABLE.append([int(node[2]), int(node[3]), ROUTER_ID, counter]) 

    
    
""" sort nodes in graph to be ordered in terms of router ID from 
    smallest to largest """
def sortGraph(graph):
    return graph.sort(key=lambda tup: tup[0])


########################## THREAD FUNCTIONS ##########################

""" a function that takes the data from a socket as a string, then creates 
    a new packet, and fills it with data to analyse """
def openData(data, addr, queue, used_id_q):
    global FORWARDING_TABLE
    global USED_ROUTER_IDS
    i = 4
    recvd_pac = Packet()
    
    recvd_pac.command = data[:1]
    recvd_pac.version = data[1:2]
    recvd_pac.must_be_0 = data[2:4]
    while i < len(data):
        payload = Payload()
        payload.addr_fam_id = data[i:i+2]
        payload.must_be_0_2 = data[i+2:i+4]
        payload.ipv4_addr = data[i+4:i+8]
        payload.routerID = data[i+8:i+12]
        payload.must_be_0_4 = data[i+12:i+16]
        payload.metric = data[i+16:i+20]
        i += 20
        #print(recvd_pac, payload)

        for output_ports in OUTPUTS:
            for input_port_num, metric, router_id in output_ports:
                if int(addr[1]) == int(input_port_num):
                    r_id = abs(int(router_id))
                    graph_data = [int(payload.routerID), int(payload.metric), r_id, 0]
                    if len(FORWARDING_TABLE) > 1:
                        
                        if int(payload.routerID) not in [item[0] for item in FORWARDING_TABLE]:
                            USED_ROUTER_IDS.append(int(payload.routerID))
                            used_id_q.put(int(payload.routerID))
                            FORWARDING_TABLE.append(graph_data)
                            queue.put(graph_data)
                        #else:
                            ##for router in FORWARDING_TABLE:
                            #root = queue.get()
                            #print(root)
                            #print("does", int(payload.routerID), "equal", router[0])
                            #if int(payload.routerID) == router[0]:
                                #router[3] = 0
                                #print("NEW R DETAILS", router)
                                #queue.put(router)
                    else:
                        used_id_q.put(int(payload.routerID))
                        #USED_ROUTER_IDS.append(int(payload.routerID))
                        #FORWARDING_TABLE.append(graph_data)
                        queue.put(graph_data)                        
                        
    print(FORWARDING_TABLE)
    print("Used router ids", USED_ROUTER_IDS)



""" a function called for the receive thread instead of run(). an infinite 
loop that checks incoming sockets, and forwards accordingly or drops """
def receive(socket, q, q1):
    
    while True:
        data, addr = socket[1].recvfrom(1024) # buffer size is 1024 bytes
        print("SOCKET", socket[0], "received from:", addr, "message:", data)
        openData(data, addr, q, q1)
    
    
def make_message():
    command = "2"
    version = "2"
    for router in FORWARDING_TABLE:
        source = router[0]

    pac = Packet(command, version, None)
    
    for router in FORWARDING_TABLE:
        metric = router[1]
    return pac


""" a function called by the receive function, to forward a packet to the 
next destination """    
def send():
    global OUTPUTS
    sock = socket.socket(socket.AF_NET, socket.SOCK_DGRAM)
    for port in OUTPUTS:
        message = make_massage()
        message = message.encode('utf-8')
        
        sock.sendto(message("0.0.0.0", port))
    
   
   
def print_table(table):
    print("Forwarding table: \n", table, "\n\n")
    print("Used router ids", USED_ROUTER_IDS)

   
   
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
            #print("ONE ROUTE + ", route)
            route[3] = route[3] + 1
            if route[3] == 6:
                route[1] = 16
            if route[3] >= 10:
                FORWARDING_TABLE = delete_link(route, FORWARDING_TABLE)
                
        print_table(FORWARDING_TABLE)
        time.sleep(1)
    
def delete_link(route, table):
    #index = table.index(route)
    #print("route to be removed at index", index)
    
    print("need to remove", route[0], "from", USED_ROUTER_IDS)
    USED_ROUTER_IDS.remove(route[0])
    
    table.remove(route)
    return table
    
########################## MAIN ##########################
    
        
def main():
    configFile = getInputFile()
    setupData = readInputFile(configFile)
    incomingSocketSetUp()  

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
    
    
    q = Queue()
    q1 = Queue()
    
    for socket in INCOMING_SOCKETS:
        process = Process(target=receive, args=(socket, q, q1, ))
        current_processes.append(process)
        
    for process in current_processes:
        process.start()   

    update(q, q1)
    #while True:
    #    print("parent pipe recvd", parent_conn.recv())
    
    #closeSockets()

if __name__ == "__main__":
    main()