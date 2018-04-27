import os
import sys
import re
import socket
import time


from multiprocessing import *
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
        outputPorts = re.findall('[0-9]+', lines)
        
        if outputPorts != []:
            if len(outputPorts) == 3:
                portnum = outputPorts[0]
                metric = outputPorts[1]
                router_id = outputPorts[2]
                OUTPUTS.append([int(portnum), int(metric), int(router_id)]) 
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
    
    finally:
        sys.exit(0)


########################## PROCESS FUNCTIONS ##########################

""" a function that takes the data from a socket as a string, then creates 
    a new packet, and fills it with data to analyse """
def openData(packet, queue):
    global USED_ROUTER_IDS
    global FORWARDING_TABLE
    
    i = 4
    pay = ''    
    # turn Packet object into string and strip off byte indicators
    data_unstripped = str(packet)
    data = data_unstripped[2:-1]
    
    packet_info = []
    
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

        # create a new object to insert into our routing table, or update if already inserted
        graph_data = [int(p_routerID), int(p_metric), int(generating_routerID), 0]            
        packet_info.append(graph_data)
        
    # put object into queue to be sorted by main programme    
    queue.put(packet_info)  
       


""" a function called for the receive thread instead of run(). an infinite 
loop that checks incoming sockets, and forwards accordingly or drops """
def receive(socket, queue):
    
    while True:
        data, addr = socket[1].recvfrom(1024) # buffer size is 1024 bytes
        openData(data, queue)
        
        
########################## FORWARDING FUNCTIONS ##########################
        
""" a function that makes a packet to send to the output links """    
def make_message(output):
    command = 2
    version = 2    
    payld = ''

    # make a specialised packet for each output
    for router in FORWARDING_TABLE:
        #if the router we learnt a link from is the router we are making a packet for
        if int(output[2]) == int(router[2]):
            # set metric to 16
            route_payload = Payload(2, 2, str(router[0]), 16)       
            
        else:              
            k = 0
            while  k < len(OUTPUTS):
                # if the router we are sending the data to is a router we learnt the link for
                if router[0] == OUTPUTS[k][2]:
                    # set metric to the link cost
                    router[1] = OUTPUTS[k][1] 
                    break
                k+=1            
            
            # turn the variables into an Payload object
            route_payload = Payload(2, 2, str(router[0]), str(router[1]))
        # turn the payload to a string and add to a string
        payld += str(route_payload)
    #create a Packet object to send
    pac = Packet(command, version, ROUTER_ID, payld)    
    return pac



""" a function called by the receive function, to forward a packet to the 
next destination """    
def send():
    # create UDP socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    # for each output - make a packet and send using a UDP port
    for output in OUTPUTS:
        message = make_message(output)
        sock.sendto(str(message).encode('utf-8'), ("127.0.0.1", int(output[0])))
    


""" prints the forwarding table """   
def print_table(table):
    print("Forwarding table:")
    print("ID, Metric, Learnt From, TTL(x30sec)")
    for line in FORWARDING_TABLE:
        print(line)
    print()
   
   
   
""" a function to take an individual link and process it, by adding it to the 
    FORWARDING_TABLE if not present, otherwise reset counter to 0 """
def process_link(link):
    global FORWARDING_TABLE
    j = 0
    while j < len(FORWARDING_TABLE):
        #if the recieved link routerID equals an entry in the forwarding table
        if link[0] == FORWARDING_TABLE[j][0]:
            # reset the time to live to 0
            FORWARDING_TABLE[j][3] = 0
            
            # if the recieved link has a lesser cost to the router
            '''
            if (rcvd_link[1] < FORWARDING_TABLE[j][1]):
                # if the received routerID is in the list of directly connected routers
                if rcvd_link[0] in [item[3] for item in OUTPUTS]:
                    # update the link with the new cost
                    FORWARDING_TABLE[j][1] = rcvd_link[1]
                    FORWARDING_TABLE[j][2] = rcvd_link[2]                        
            '''
            break
        j+=1
    # if the link has not yet been discovered    
    if j >= len(FORWARDING_TABLE):
        got_from = link[0]
        link_cost = 0
      
        FORWARDING_TABLE.append(link)
        
        
         
""" a function that monitors the queues that act as pipes, from the individual 
   processes. to the main programme. When a link or an array of links has been 
   discovered, we split them up to individual links and pass to the process link
   function """
def update(queue):
    global FORWARDING_TABLE
    global USED_ROUTER_IDS
    while True:
        try:
            # recieve a list of links from a process
            while True:
                rcvd_link = queue.get(False)
                # if only one link has been posted
                for link in rcvd_link:
                    # see if we recieved multiple links in one packet
                    try:
                        for li in link:
                            # process multiple links
                            process_link(li)
                    except:
                        # process the one link
                        process_link(link)
        # no data waiting for us from the queue - move on            
        except:
            #print("no new data")
            i = 1      
        
        # go through all lists in the forwarding table
        for route in FORWARDING_TABLE:
            # dont increment TTL feild in FORWARDING TABLE if we are looking at ourself
            if route[0] == ROUTER_ID:
                continue
            
            # increment time to live counter
            route[3] = route[3] + 1
            # if the link is 6 rotations old without an update, set cost to 16
            if route[3] >= 6:
                index = FORWARDING_TABLE.index(route)
                route[1] = 16
                FORWARDING_TABLE[index][1] = 16
            # or if the link has expired, delete link    
            if route[3] >= 10:
                FORWARDING_TABLE = delete_link(route, FORWARDING_TABLE)
        # print table        
        print_table(FORWARDING_TABLE)        
        # create new packets to send
        send()
        # wait
        time.sleep(TIME_TO_SLEEP)



""" delete a dead link out of the FORWARDING TABLE """    
def delete_link(route, table):
    USED_ROUTER_IDS.remove(route[2])
    table.remove(route)
    return table
    
    
########################## MAIN ##########################
        
def main():
    configFile = getInputFile()
    setupData = readInputFile(configFile)
    incomingSocketSetUp()  

    print("\nRouter ID =", ROUTER_ID)
    
    # add ourself to the forwarding table
    FORWARDING_TABLE.append([ROUTER_ID, 0, ROUTER_ID,0])    
    # start a queue for the processes to pass links back to the main programme
    queue = Queue()
    
    for socket in INCOMING_SOCKETS:
        process = Process(target=receive, args=(socket, queue, ))
        process.start() 
    update(queue)

    closeSockets()


if __name__ == "__main__":
    main()