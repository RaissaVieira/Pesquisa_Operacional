import sys
import cplex
from cplex.exceptions import CplexError

# Leitura dos dados presente em dados.txt
def readInstance(filePath):
    f = open(filePath, "r")
    
    n = int(f.readline()) # numero de vertices
    m = int(f.readline()) # numero de arcos
    s = int(f.readline()) # indice da origem
    t = int(f.readline()) # indice do escoadouro0

    begin = [] # indices i
    end = [] # indices j
    capacity = [] # capacidade dos arcos (c_m)

    for dado in range(m):
        l = f.readline()
        i, j, c = int(l.split()[0]), int(l.split()[1]), int(l.split()[2])
        begin.append(i)
        end.append(j)
        capacity.append(c)

    return n,m,s,t,begin,end,capacity

# Criação do modelo (ainda não está completo)
def createProblem(n,m,s,t,begin,end,capacity):
    prob = cplex.Cplex()

    custo = 0 # custo em todos os arcos é 0
    b = 0 # fluxo liquido em cada arco

    prob.objective.set_sense(prob.objective.sense.minimize)

    for i, j, c in zip(begin,end,capacity):
        prob.variables.add(obj=[custo], lb=[0], ub=[c], types="I", names=["x_" + str(i) + "_" + str(j)])

    prob.variables.add(obj=[custo], lb=[0], ub=[float("inf")], types="I", names=["x_" + str(s) + "_" + str(t)])

    return prob

def main():

    try:
        n,m,s,t,begin,end,capacity = readInstance(sys.argv[1])
        prob = createProblem(n,m,s,t,begin,end,capacity)
        prob.write("model.lp")
        #prob.solve()
    except CplexError as exc:
        print(exc)
        return

main()