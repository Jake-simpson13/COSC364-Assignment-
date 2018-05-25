import sys
import subprocess
from datetime import datetime

# filename to write the .lp file to, and for the cplex optimizer to read 
LP_FILENAME = "assignment2.lp"
TXT_FILENAME = "assignment2.txt"


""" returns header text """
def header():
    return "Minimize\n\tr\nSubject to\n"
                  
     
""" demand volume from node i to j"""
def demandVolumeConstraints(x, y, z):
    constraints = ""
    for i in range(1, x +1):
        for j in range(1, z+1):
            constraints += ("DemandVolume{0}{1}: ".format(i, j))
            for k in range(1, y+1):
                n = i + k
                if k == 1:
                    constraints += ("x{0}{1}{2}".format(i, k, j))  
                elif k < y:
                    constraints += (" + x{0}{1}{2}".format(i, k, j))                
                else:
                    constraints += (" + x{0}{1}{2} = {3}\n".format(i, k, j, i + j))
    return constraints        
     
     
""" demand flow from node i to j """
def demandFlowConstraints(x, y, z):
    constraints = ""
    for i in range(1, x +1):
        for k in range(1, z+1):
            for j in range(1, y+1):
                constraints += ("DemandFlow{0}{1}{2}: {4} x{0}{1}{2} - {3} u{0}{1}{2} = 0\n".format(i, k, j, i+j, 3))
                
    return constraints  
    

""" constraints for the src node """    
def srcNodeConstraints(x, y, z):
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
                    constraints += ("SrcConstraint{0}{2}: {3} - c{0}{2} = 0\n".format(i, k, j, cons))                    
    return constraints
                
     
""" constraints for the dst node """ 
def dstNodeConstraints(x, y, z):
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
                    constraints += ("DstConstraint{2}{0}: {3} - d{2}{0} = 0\n".format(i, k, j, cons))                    
    return constraints     
     

""" constriants for the trans node """     
def transNodeConstraints(x, y, z):
    constraints = ""
    for k in range(1, y+1):
        for i in range(1, x+1):
            for j in range(1, z+1):
                if (j == 1 and i == 1):
                    constraints += ("TransConstraint{1}: x{0}{1}{2}".format(i, k, j))
                elif (i == x and j == z):
                    constraints += (" + x{}{}{} - r <= 0\n".format(i, k, j))
                else:
                    constraints += (" + x{}{}{}".format(i, k, j))
    return constraints


""" utilisation constraints for the trans nodes"""
def utilisationConstraints(x, y, z):
    constraints = ""
    for i in range(1, x+1):
        for j in range(1, z+1):
            constraints += ("Utilisation{}{}: ".format(i, j))
            for k in range(1, y+1):
                if k == 1:
                    constraints += ("u{}{}{}".format(i, k, j))
                elif k == y:
                    constraints += (" + u{}{}{} = {}\n".format(i, k, j, 3))
                else:
                    constraints += (" + u{}{}{}".format(i, k, j))            
    return constraints


""" bounds for .lp file. All links >= 0 """     
def bounds(x, y, z):   
    bounds = "\nBounds\nr >= 0\nr <= 1\n"        
    for i in range(1, x+1):
        for k in range(1, y+1):
            for j in range(1, z+1):
                bound = "{}{}{}".format(i,k,j)
                bounds += ("x{} >= 0\n".format(bound))
    for i in range(1, x+1):
        for k in range(1, y+1):
            bounds += ("c{}{} >= 0\n".format(i, k))
    for k in range(1, y+1):
        for j in range(1, z+1):
            bounds += ("d{}{} >= 0\n".format(k, j))    
    return bounds


""" binaries for .lp file """
def binaries(x, y, z):
    binaries = "\nBinary\n"
    for i in range(1, x+1):
        for k in range(1, y+1):
            for j in range(1, z+1):
                binaries += "u{0}{1}{2}\n".format(i,k,j) 
    binaries += "\nEND"            
    return binaries


""" utilises the command line function calls to run cplex, using the newly created 
    .lp file as a parameter to get an optimization result """
def cplex():
    path = "/home/cosc/student/jli231/Documents/COSC364/CPLEX/cplex/bin/x86-64_linux/cplex"
    params = ["-c", "read /home/cosc/student/jli231/Documents/COSC364/COSC364-Assignment-/"+LP_FILENAME, "optimize", "display solution variables -"]
        
    result = subprocess.Popen([path]+params, stdout=subprocess.PIPE)
    output = result.communicate()[0] 
    return output


""" main """
def main(x, y, z):
    # build .lp file
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
    
    # write .lp file so cplex can read it
    file = open(LP_FILENAME, "w")
    file.write(lp)
    file.close()
    
    # start timer, run cplex script, stop timer
    start = datetime.now()
    results = cplex()
    time_taken = datetime.now() - start
    print('Time elapsed (hh:mm:ss.ms) {}'.format(time_taken))
    
    # write optimization result to a text file, so we can read a formatted version of the results
    resultfile = open(TXT_FILENAME, "w")
    resultfile.write(results.decode("utf-8"))
    resultfile.close()
    
    
    
    
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
