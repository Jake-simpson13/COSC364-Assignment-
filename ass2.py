import sys

FILENAME = "assignment2.lp"
BOUNDS = []


def header():
    return "Minimize\n\tr\nSubject to\n"

#def constraints(x, y, z):
    
    #constraints = ""
    #for i in range(1, x +1):
        ##n = i + k
        #for k in range(1, z+1):
            #for j in range(1, y+1):
                #n = i + j
                #if j < y:
                    #constraints += ("x{}{}{} + ".format(i, j, k))                    
                #else:
                    #constraints += ("x{}{}{} = {}\n".format(i, j, k, n))
    #return constraints                    
     
""" constraints to represent the amount of
    demand from node i to j
"""
def demandVolumeConstraints(x, y, z):
    global BOUNDS
    constraints = ""
    for i in range(1, x +1):
        #n = i + k
        for j in range(1, z+1):
            constraints += ("DemandVolume{0}{1}: ".format(i, j))
            for k in range(1, y+1):
                n = i + k
                #if k < y:
                if k == 1:
                    constraints += ("x{0}{1}{2}".format(i, k, j))  
                elif k < y:
                    constraints += (" + x{0}{1}{2}".format(i, k, j))                
                else:
                    constraints += (" + x{0}{1}{2} = {3}\n".format(i, k, j, i + j))
                    #BOUNDS.append("DV{0}{1} >= 0".format(i, j))
    return constraints        
     
     
""" constraints to represent the amount of
flow on a given link. These auxiliary variables are given by:
y 12 = x 12 + x 123 + x 213
y 13 = x 13 + x 132 + x 213
y 23 = x 23 + x 132 + x 123
"""
def demandFlowConstraints(x, y, z):
    global BOUNDS
    constraints = ""
    for i in range(1, x +1):
        #n = i + k
        for k in range(1, z+1):
            for j in range(1, y+1):
                constraints += ("DemandFlow{0}{1}{2}: {4} x{0}{1}{2} - {3} u{0}{1}{2} = 0\n".format(i, k, j, i+j, 3))
                #BOUNDS.append("DemandFlow{}{}{} >= 0".format(i, k, j))
    return constraints  
    

""" constraints for the src node """    
def srcNodeConstraints(x, y, z):
    global BOUNDS
    constraints = ""
    for i in range(1, x+1):
        for j in range(1, y+1):
            cons = ""
            for k in range(1, z+1):
                if (k == 1):
                    cons += ("x{0}{1}{2}".format(i, j, k))                    
                elif (k < z):
                    cons += (" + x{0}{1}{2}".format(i, j, k))
                else:
                    cons += (" + x{0}{1}{2}".format(i, j, k))
                    constraints += ("srcConstraint{0}{2}: {3} - c{0}{2} = 0\n".format(i, k, j, cons))
                    #BOUNDS.append("srcConstraint{}{} >= 0".format(i, j))
                    
    return constraints
                
     
     ############### not working
""" constraints for the dst node """ 
def dstNodeConstraints(x, y, z):
    global BOUNDS
    constraints = ""
    for i in range(1, z+1):
        for j in range(1, y+1):
            cons = ""
            for k in range(1, x+1):
                if (k == 1):
                    cons += ("x{2}{1}{0}".format(i, j, k))                    
                elif (k < x):
                    cons += (" + x{2}{1}{0}".format(i, j, k))
                else:
                    cons += (" + x{2}{1}{0}".format(i, j, k))
                    constraints += ("dstConstraint{2}{0}: {3} - d{2}{0} = 0\n".format(i, k, j, cons))
                    #BOUNDS.append("dstConstraint{}{} >= 0".format(j, i))            
                    
    return constraints     
     
     
def transNodeConstraints(x, y, z):
    global BOUNDS
    constraints = ""
    for k in range(1, y+1):
        for i in range(1, x+1):
            for j in range(1, z+1):
                if (j == 1 and i == 1):
                    constraints += ("transConstraint{2}: x{0}{1}{2}".format(i, k, j))
                    #BOUNDS.append("transConstraint{} <= 0".format(k))
                #elif j < z:
                #    constraints += (" + x{}{}{}".format(i, k, j))
                elif (i == x and j == z):
                    constraints += (" + x{}{}{} - r <= 0\n".format(i, k, j))
                else:
                    constraints += (" + x{}{}{}".format(i, k, j))
    return constraints

def utilisationConstraints(x, y, z):
    global BOUNDS
    constraints = ""
    for i in range(1, x+1):
        for j in range(1, z+1):
            constraints += ("utilisation{0}{1}: ".format(i, j))
            #BOUNDS.append("utilisation{0}{1} >= 0".format(i, j))
            for k in range(1, y+1):
                if k == 1:
                    constraints += ("u{}{}{}".format(i, k, j))
                elif k == y:
                    constraints += (" + u{}{}{} = {}\n".format(i, k, j, 3))
                else:
                    constraints += (" + u{}{}{}".format(i, k, j))

            #for k in range(1, y+1):
                #e = (' + ', " = {}\n".format(n))[k == y]
                #print("u{}{}{}".format(i,k,j), end=e)               
                    
                    
    return constraints
     
def bounds(x, y, z):
    
    bounds = "\nBounds\nr >= 0\n"
    
    for bound in BOUNDS:
        bounds += bound+"\n"
        
    for i in range(1, x+1):
        for k in range(1, y+1):
            for j in range(1, z+1):
                bound = "{}{}{}".format(i,k,j)
                bounds += ("  x{} >= 0\n".format(bound))
    for i in range(1, x+1):
        for k in range(1, y+1):
            bounds += ("  c{}{} >= 0\n".format(i, k))
    for k in range(1, y+1):
        for j in range(1, z+1):
            bounds += ("  d{}{} >= 0\n".format(k, j))
    
    return bounds

def binaries(x, y, z):
    binaries = "\nBinary\n"
    for i in range(1, x+1):
        for k in range(1, y+1):
            for j in range(1, z+1):
                binaries += "u{0}{1}{2}\n".format(i,k,j)
    
    return binaries
    

def main(x, y, z):
    lp = header()
    lp += demandVolumeConstraints(x, y, z)
    lp += demandFlowConstraints(x, y, z)
    lp += srcNodeConstraints(x, y, z)
    lp += dstNodeConstraints(x, y, z)
    lp += transNodeConstraints(x, y, z)
    lp += utilisationConstraints(x, y ,z)
    lp += bounds(x, y, z)
    lp += binaries(x, y, z)
    print(lp)
    
    file = open(FILENAME, "w")
    file.write(lp)
    file.close()
    
if __name__ == "__main__":
    if len(sys.argv) == 4:
        x = int(sys.argv[1])
        y = int(sys.argv[2])
        z = int(sys.argv[3])
    else:
        x = int(input("How many src nodes?: "))
        y = int(input("How many trans nodes?: "))
        z = int(input("How many dst nodes?: "))
    main(x, y, z)
