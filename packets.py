""" 
a class for the packet header, compplete with a field for 'payload'
which is the router information to be used in the router table
"""
class Packet:
    # command = command (1) (1 = request, 2 = response)
    # version = version (1) (version of the rip protocol used - always 2)
    # payload = RIP entries (20) (between 1 - 25 inc, otherwise multiple packets)   

    def __init__(self, command=None, version=None, p_payload=None):
        self.command = command
        self.version = version
        self.must_be_0 = '00'
        self.p_payload = p_payload
        

    def __str__(self):
        string = str(self.command) + str(self.version) + str(self.must_be_0)
        string += str(self.p_payload)
        return string
        
    
    def packet(self):
        value = str(self.command) + str(self.version)
        for pay in self.p_payload:
            value += str(pay.addr_fam_id)
            value += str(pay.must_be_0_2)
            value += str(pay.ipv4_addr)
            value += str(pay.must_be_0_4)
            value += str(pay.metric)
        return value
        
""" 
a class for the packet payload, which gets included in the 
class packet as payload. Between 1 and 25 payload objects to one packet object        
"""
class Payload:
    # addr_fam_id = address family identifier (2)
    # ipv4_addr = IPv4 address (4)
    # metric = metric (4) (cost - must be between 1 - 15 inc, 16 = inf / unreachable)
 
    def __init__(self, addr_fam_id=None, ipv4_addr=None, metric=None):
        self.addr_fam_id = addr_fam_id
        self.must_be_0_2 = '00'
        self.ipv4_addr = ipv4_addr
        self.must_be_0_4 = '0000'
        self. metric = metric
        
    
    def __str__(self):
        return str(self.addr_fam_id) + str(self.must_be_0_2) + str(self.ipv4_addr) + str(self.must_be_0_4) + str(self.metric)
        
        
    def payload(self):
        return str(self.addr_fam_id), self.must_be_0_2, str(self.ipv4_addr), self.must_be_0_4, str(self.metric)
    



'''
#Test data

x = Payload(2, 40, 7)
print(x.payload())
y = Payload(4, 30, 5)
print(y.payload())
ppayload = x,y
z = Packet(1, 2, ppayload)
print(z.packet())
'''