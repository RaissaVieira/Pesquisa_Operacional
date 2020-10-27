import sys
import cplex
from cplex.exceptions import CplexError

# Leitura dos dados presente em dados.txt
def readInstance(filePath):
    f = open(filePath, "r")
    
    n = int(f.readline()) # numero de vertices
    m = int(f.readline()) # numero de arcos
    s = int(f.readline()) # indice da origem
    t = int(f.readline()) # indice do escoadouro

    begin = [] # indices i
    end = [] # indices j
    capacity = [] # capacidade dos arcos (c_m)

    for dado in range(m):
        l = f.readline()
        i, j, c = int(l.split()[0]), int(l.split()[1]), int(l.split()[2])
        begin.append(i)
        end.append(j)
        capacity.append(c)

readInstance(sys.argv[1]) # chamada de funcao