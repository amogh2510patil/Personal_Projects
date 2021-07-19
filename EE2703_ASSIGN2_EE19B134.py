#! /usr/bin/env python3

#Amogh Patil
#EE19B134

#Program that takes the input as an argument from the command line
#The input is the name of the file whose contents need to be read and required details are extracted
#Solving the circuit with nodal analysis
#the circuit can handle only sources of single frequncy

import sys
import numpy
from numpy import *

nodes = []      #list to hold nodes
volts = []      #list to hold voltage sources
freq = 0        #variable to hold frequncy of sources 

class Circuit_elements:
    name = ''
    n1 = 0
    n2 = 0
    val = 0 

    def __init__(self, name,n1,n2,val):
        self.name = name
        self.n1 = n1
        self.n2 = n2
        self.val = val
    
#Function to create an object for each element
def parseline(line):
    tokens = line.split()
    #adding a node to the list of nodes
    if tokens[1] not in nodes:  
        nodes.append(tokens[1])
    if tokens[2] not in nodes:
        nodes.append(tokens[2])
    #Converting GND to 0
    if tokens[1] == 'GND':
        tokens[1] = 0 
    if tokens[2] == 'GND':
        tokens[2] = 0 

    if tokens[0][0] == 'C' or tokens[0][0] == 'L' or tokens[0][0] == 'R':
        if tokens[0][0] == 'L'and freq == 0: #To treat an inductor as a 0V voltage source in the dc circuit
            volts.append(tokens[0])

        #Tranforming the impedence values
        if tokens[0][0] == 'L':
            tokens[3] = double(tokens[3]) * 1j*2*pi*freq
        if tokens[0][0] == 'C' and freq != 0.0:
            tokens[3] = 1/(double(tokens[3]) * 1j*2*pi*freq)
        if tokens[0][0] == 'R':
            tokens[3] = double(tokens[3])
        obj1 = Circuit_elements(tokens[0],int(tokens[1]),int(tokens[2]),tokens[3])
        return(obj1)

    if tokens[0][0] == 'V' or tokens[0][0] == 'I' :
        if tokens[0][0] == 'V' and tokens[0] not in volts:
            volts.append(tokens[0]) 
        if freq != 0 and tokens[3] == 'dc' :
            print("Input file contains ac and dc sources, the code is incapable of running it")
            exit(0)
        #Trnaforming the values of the voltage and current sources in ac values
        if freq != 0 :
            tokens[4] = 0.5 * double(tokens[4])*cos(double(tokens[5])) + 0.5 * 1j * double(tokens[4])*sin(double(tokens[5]))
        obj2 = Circuit_elements(tokens[0],int(tokens[1]),int(tokens[2]),tokens[4])
        return(obj2)



#To make sure only 2 arguments are provided: the python executable and the name of the netlist file.
if len(sys.argv) != 2:
    print('\nUsage: %s <inputfile>' % sys.argv[0])
    exit(0)

try:
    #open the reuired file and read the lines in the file and simultaneously removing the comments
    f = open(sys.argv[1])
    lines = [line.split('#')[0] for line in f.readlines()]
    f.close()

    #To store into a variable the words that are to be detected in the file
    CIRCUIT = ".circuit"
    END = ".end"
    AC = ".ac"
    #to store the line number when .circuit and .end is encountered
    start = -1
    finish = -1
    ac = -1

    #iterate through the lines to detect .circuit and .end
    for line in lines :
        if CIRCUIT == line[:len(CIRCUIT)] :
            start = lines.index(line)
        elif END == line[:len(END)] :
            finish = lines.index(line)
        elif AC == line[:len(AC)] :
            ac = lines.index(line)

    #To check whether .cicuit is encountered and if encountered, it should be encountered before .end
    #To check if .ac is detected after .end
    if start >= finish or start == -1 or (ac != -1 and ac <= finish):
        print("INVALID INPUT")
        exit(0)
    #To extract the frequncy of sources in the circuit(Assuming only single frequncy sources are present)
    if ac > finish:
        freq = double(lines[ac].split()[2])
    
    #Total circuit stores all the elements in their respective branches in the form of a table(basically list of lists)
    totalcircuit = []
    for line in lines[(start+1):finish] :
        totalcircuit.append(parseline(line))
    
    #Number of nodes in the ciruit
    n = len(nodes)
    #Number of voltage sources in the circuit along with number of inductors in dc case
    p = len(volts)

    #Creating G(conductance) Matrix
    A = array([[0.0+1j*0.0 for i in range(n+p)] for k in range(n+p)])
    
    #Creating I matrix
    B = array([[0.0+1j*0.0] for k in range(n+p)])
    
    #matrix variable
    q = 0 #for voltage source
    s = 1 #for inductors 

    #Filling G - matrix
    #Iterating through the various elements of the ciruit
    for element in totalcircuit:
        #For resistors and in ac circuits for capacitors and inductors 
        #For the element => the equaition (Vn1 - Vn2)/element.val contributes to the G matrix
        if (element.name[0] == 'C' and freq != 0.0) or (element.name[0] == 'L'and freq != 0.0) or element.name[0] == 'R':
            A[element.n1][element.n1] += 1/element.val
            A[element.n1][element.n2] += -1/element.val
            A[element.n2][element.n1] += -1/element.val
            A[element.n2][element.n2] += 1/element.val 

        #For inductor in dc, we treat it as a voltage source of 0 V
        elif element.name[0] == 'L' and freq == 0.0 :
            #Current leaving n1 and reaching n2
            A[n+p-s][element.n1] = 1
            A[n+p-s][element.n2] = -1

            #Vn1 - Vn2 = 0 , filled from the bottom of the G matrix to separate it from voltage sources
            A[element.n1][n+p-s] = 1
            A[element.n2][n+p-s] = -1
            
            #Since the voltage difference is zero 
            B[n+p-s] = 0
            s +=1
        
        #Voltage Source
        elif element.name[0] == 'V' :
            #Vn1 - Vn2 = element.val
            A[n+q][element.n1] = 1
            A[n+q][element.n2] = -1

            A[element.n1][n+q] = 1
            A[element.n2][n+q] = -1
            B[n+q] = element.val
            q +=1
        
        #Current Source
        elif element.name[0] == 'I' :
            B[element.n1] += element.val
            B[element.n2] += -element.val

    A[0,0] = 1      #Vgnd = 0
    A[0,1:] = 0     #Column corresponding to GND is initialed to 0
    A[1:,0] = 0     #Row corresponding to GND is initialed to 0
    B[0] = 0        
        
    #print(A)
    #print(B)

    #Solution to A x = B 
    x = numpy.dot(numpy.linalg.inv(A), B) 
    
    print("Node Voltages")
    #printing Voltage of nodes
    for i in range(n):
        print("Voltage of Node",i," is ",x[i])
    print()
    #printing Current through voltage sources
    print("Current direction follows passive sign convention")
    q = 0
    for displayvoltage in totalcircuit:
        if displayvoltage.name[0] == 'V' :
            print("Current through ",displayvoltage.name," is ",x[n+q])
            q += 1

except Exception:
    print('Invalid file')
    exit()




