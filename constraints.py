import sys

FILENAME = "assignment2.lp"



def header():
    return "Minimize\n\tr\nSubject to\n"

def constraints(x, y, z):
    
    constraints = ""
    for i in range(1, x +1):
        #n = i + k
        for k in range(1, z+1):
            for j in range(1, y+1):
                n = i + j
                if j < y:
                    constraints += ("x{}{}{} + ".format(i, j, k))                    
                else:
                    constraints += ("x{}{}{} = {}\n".format(i, j, k, n))
    return constraints                    
     
def bounds(x, y, z):
    
    bounds = "  r >= 0\n"
    for i in range(1, x+1):
        for k in range(1, y+1):
            for j in range(1, z+1):
                bound = "{}{}{}".format(i,k,j)
                bounds += ("  x{} >= 0\n".format(bound))
    for i in range(1, x+1):
        for k in range(1, y+1):
            bounds += ("  x{}{} >= 0\n".format(i, k))
    for k in range(1, y+1):
        for j in range(1, z+1):
            bounds += ("  d{}{} >= 0\n".format(k, j))
    
    return bounds
    

def main(x, y, z):
    lp = header()
    lp += constraints(x, y, z)
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
