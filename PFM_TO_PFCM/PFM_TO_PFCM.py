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

    f.close()

    return n,m,s,t,begin,end,capacity

# Criação do modelo 
def createProblem(n,m,s,t,begin,end,capacity):
    prob = cplex.Cplex()

    custo = 0 # custo em todos os arcos é 0
    b = 0 # fluxo liquido em cada arco

    vertices = []
    for i in begin:
        if (i not in vertices):
            vertices.append(i)
    for i in end:
        if (i not in vertices):
            vertices.append(i)

    prob.objective.set_sense(prob.objective.sense.minimize)

    for i, j, c in zip(begin,end,capacity):
        prob.variables.add(obj=[custo], lb=[0], ub=[c], types="I", names=["x_" + str(i) + "_" + str(j)])

    prob.variables.add(obj=[10000], lb=[0], ub=[float("inf")], types="I", names=["x_" + str(s) + "_" + str(t)])

    names = []
    for i,j in zip (begin,end):
        names.append("x_" + str(i) + "_" + str(j))
    
    limite_superior = 0
    rhs = []
    for x in vertices:
        if x == s:
            for i,j,c in zip (begin, end,capacity):
                if (i == x):
                    limite_superior += c

    constraints = []

    for x in vertices:
        coef, arc = [], []
        for i,j,num in zip (begin, end, range(len(begin))):
            if (i == x):
                coef.append(1)
                arc.append(names[num])
            if (j == x):
                coef.append(-1)
                arc.append(names[num])
        
        constraints.append([arc,coef])
        
        if x != s and x!= t:
            rhs.append(0)
        if x == s:
            rhs.append(limite_superior)
        elif x == t:
            rhs.append(limite_superior)


    constraint_names = ["c" + str(i) for i, _ in enumerate(constraints)]

    constraint_senses = ["E"] * len(constraints)

    prob.linear_constraints.add(names=constraint_names,
                                lin_expr=constraints,
                                senses=constraint_senses,
                                rhs=rhs)
              
    return prob

def main():

    try:
        n,m,s,t,begin,end,capacity = readInstance(sys.argv[1])
        prob = createProblem(n,m,s,t,begin,end,capacity)
        prob.write("model.lp")
        prob.solve()
    except CplexError as exc:
        print(exc)
        return

    # solution.get_status() returns an integer code
    print ("Solution status = ", prob.solution.get_status(), ":")
    # the following line prints the corresponding string
    print (prob.solution.status[prob.solution.get_status()])
    print ("Solution value  = ", prob.solution.get_objective_value())

main()