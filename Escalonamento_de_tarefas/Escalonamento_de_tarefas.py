''' 
PROJETO 2 DA DISCIPLINA DE PESQUISA OPERACIONAL
COMPONENTES: RAISSA VIEIRA, LUCIANO JUNIOR E YASMIN MEDEIROS
OBJETIVO: MODELAGEM DO PROBLEMA DE ESCALONAMENTO DE TAREFAS COM JANELAS DE TEMPO
'''

#Importação das biliotecas
import sys #Usada para a leitura de arquivos
import cplex # Resolvedor utilizado
from cplex.exceptions import CplexError 

# Função que tem como objetivo ler o arquivo e retornar as informações que serão utilizadas pelo resolvedor
def readInstance(filePath):
    f = open(filePath, "r") # Abrindo o arquivo 
    
    n = int(f.readline()) # Lendo o numero de tarefas

    indice = [] # indice da atividade
    data_min_ini = [] # Datas minimas de inicio
    duracao = [] # Duracao 
    data_entrega = [] # Data de entrega
    multa = [] #multa por dia de atraso

    # Criacao do no 0
    n += 1
    indice.append(0)

    for dado in range(n-1): # Identificando a capacidade e os índices de cada arco
        l = f.readline() # Lendo a linha do arco
        i, dmi, d, de, m = int(l.split()[0]), int(l.split()[1]), int(l.split()[2]), int(l.split()[3]), int(l.split()[4]) # Separando suas informações de interesse
        # Adicionando as informacoes nos respectivos array
        indice.append(i)
        data_min_ini.append(dmi)
        duracao.append(d)
        data_entrega.append(de)
        multa.append(m)
    
    f.close() # Fecha arquivo

    return n, indice, data_min_ini, duracao, data_entrega, multa # Retorna as variáveis extraídas

def createProblem(n, indice, data_min_ini, duracao, data_entrega, multa):
    prob = cplex.Cplex() # inicializando o resolvedor do CPLEX

    prob.set_problem_type(cplex.Cplex.problem_type.LP) # Definindo como um problema de programação linear

    prob.objective.set_sense(prob.objective.sense.minimize) # Definindo que a função objetivo irá buscar a minimização, como pede o problema do custo mínimo

    V = [] # Definindo um array com todos os vértices a partir dos indices
    for i in indice: 
        V.append(i) 
    
    J = []
    for j in indice[1:]:
        J.append(j)

    for i, m in zip(J,multa): # Iteração sequencial das variáveis dos vértices de origem, escoagem e capacidade de cada arco
        prob.variables.add(obj=[m], lb=[0], ub=[], types="I", names=["L_" + str(i)])

    for j, date_min in zip(J, data_min_ini):
        prob.variables.add(obj=[0], lb=[date_min], ub=[], types="I", names=["R_" + str(j)])

    for j in J:
        prob.variables.add(obj=[0], lb=[], ub=[], types="I", names=["F_" + str(j)])

    for i in V:
        coef, arc = [], []
        for j in V:
            if (i != j):
                prob.variables.add(obj=[0], lb=[0], ub=[1], types="I", names=["x_" + str(i) + "_" + str(j)])
    
    constraints, rhs = [], []
    for i in V:
        coef, arc = [], []
        for j in V:
            if (i != j):
                coef.append(1)
                arc.append("x_" + str(i) + "_" + str(j))
        constraints.append([arc,coef])
        rhs.append(1)

    for j in V:
        coef, arc = [], []
        for i in V:
            if (i != j):
                coef.append(1)
                arc.append("x_" + str(i) + "_" + str(j))
        constraints.append([arc,coef])
        rhs.append(1)

    constraint_senses = ["E"] * len(constraints)

    for j, pj in zip(J, data_entrega):
        coef, arc = [], []
        coef.append(1)
        coef.append(-1)
        arc.append("F_" + str(j))
        arc.append("L_" + str(j))
        constraint_senses.append("L")
        constraints.append([arc,coef])
        rhs.append(pj) 

    M = 0
    for rj in data_min_ini:
        if rj > M:
            M = rj
    
    for dj in duracao:
        M += dj

    for i, di in zip(J, data_entrega):
        for j in J:
            coef, arc = [], []
            if (i != j):
                coef.append(1)
                arc.append("R_" + str(i))
                coef.append(M)
                arc.append("x_" + str(i) + "_" + str(j))
                coef.append(-1)
                arc.append("R_" + str(j))
                constraint_senses.append("L")
                constraints.append([arc,coef])
                rhs.append(-di + M)  

    constraint_names = ["c" + str(i) for i, _ in enumerate(constraints)]
    prob.linear_constraints.add(names=constraint_names,
                                lin_expr=constraints,
                                senses=constraint_senses,
                                rhs=rhs) 

    return prob
    
def main():

    try: # Tentando resolver o problema
        n,indice,data_min_ini,duracao,data_entrega,multa = readInstance(sys.argv[1]) # Lendo o arquivo
        prob = createProblem(n,indice,data_min_ini,duracao,data_entrega,multa) # Chamada da funcao para a criacao do problema
        prob.write("model.lp") 
        prob.solve() # Resolvendo o problema
    except CplexError as exc:
        print(exc)
        return

    print ("Solution status = ", prob.solution.get_status(), ":") # Retorna o status da resolução
    print (prob.solution.status[prob.solution.get_status()]) #Retorna a solução do status
    print ("Solution value  = ", prob.solution.get_objective_value()) # Retorna o valor da solução

    for i in V:
        for j in V:
            if (i != j):
                value = prob.solution.get_values("x_" + str(i) + "_" + str(j))
                print(value)

main()