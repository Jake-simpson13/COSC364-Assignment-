""" 
a class for the packet header, complete with a field for 'payload'
which is the router information to be used in the router table
"""
class Packet:
    # command = command (1) (1 = request, 2 = response)
    # version = version (1) (version of the rip protocol used - always 2)
    # generating_router_id = Router that generates this RIP packet
    # payload = RIP entries (20) (between 1 - 25 inc, otherwise multiple packets)   

    
    def __init__(self, command=None, version=None, generating_routerID=None, p_payload=None):
        
        # Command
        if len(str(command)) == 1:
            self.command = command
        
        # Version
        if len(str(version)) == 1:    
            self.version = version
        
        # Generating Router ID    
        if len(str(generating_routerID)) == 2:
            self.generating_routerID = str(generating_routerID)
        elif len(str(generating_routerID)) == 1:
            self.generating_routerID = "0" + str(generating_routerID)
        
        # Payload
        self.p_payload = p_payload
        


    def __str__(self):
        string = str(self.command) + str(self.version) + str(self.generating_routerID)
        string += str(self.p_payload)
        return string
       


""" 
a class for the packet payload, which gets included in the 
class packet as payload. Between 1 and 25 payload objects to one packet object        
"""
class Payload:
    # addr_fam_id = address family identifier (2)
    # ipv4_addr = IPv4 address (4)
    # routerID = the router that the Generating Router is describing
    # metric = metric (4) (cost - must be between 1 - 15 inc, 16 = inf / unreachable)
 
    def __init__(self, addr_fam_id=None, ipv4_addr=None, routerID=None, metric=None):
        
        # Address Family Identifer
        if len(str(addr_fam_id)) == 2:
            self.addr_fam_id = str(addr_fam_id)
        elif len(str(addr_fam_id)) == 1:
            self.addr_fam_id = "0" + str(addr_fam_id)
            
        # 00    
        self.must_be_0_2 = '00'
        
        # IPv4 Address
        if len(str(ipv4_addr)) == 4:
            self.ipv4_addr = str(ipv4_addr)
        elif len(str(ipv4_addr)) == 3:
            self.ipv4_addr = "0" + str(ipv4_addr)
        elif len(str(ipv4_addr)) == 2:
            self.ipv4_addr = "00" + str(ipv4_addr) 
        elif len(str(ipv4_addr)) == 1:
            self.ipv4_addr = "000" + str(ipv4_addr)         
        
        # Router ID
        if len(str(routerID)) == 4:
            self.routerID = str(routerID)
        elif len(str(routerID)) == 3:
            self.routerID = "0" + str(routerID)
        elif len(str(routerID)) == 2:
            self.routerID = "00" + str(routerID) 
        elif len(str(routerID)) == 1:
            self.routerID = "000" + str(routerID)         
        
        # 0000
        self.must_be_0_4 = '0000'
        
        # Metric
        if len(str(metric)) == 4:
            self.metric = str(metric)
        elif len(str(metric)) == 3:
            self.metric = "0" + str(metric)
        elif len(str(metric)) == 2:
            self.metric = "00" + str(metric) 
        elif len(str(metric)) == 1:
            self.metric = "000" + str(metric) 

    
    def __str__(self):
        return str(self.addr_fam_id) + str(self.must_be_0_2) + str(self.ipv4_addr) + str(self.routerID) + str(self.must_be_0_4) + str(self.metric)
        
    



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
'''
ppayload = []
x = Payload(2, 40, 7, 3)
#print(x.payload())
y = Payload(4, 30, 5, 3)
#print(y.payload())
ppayload.append(x)
ppayload.append(y)
#z = Packet(1, 2, 35, None)
#print(z.packet())
z = Packet(1, 2, 35, ppayload)
print(z.packet())
'''
