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
    
    J = [] # Definindo um array com todos os vértices a partir dos indices
    for j in indice[1:]:
        J.append(j)

    for i, m in zip(J,multa): # Definindo a variável que representa os dias de atraso na entrega, 
                            # cujo valor é multiplicado pelo valor da multa por dia, e apresenta como valor mínimo 0
        prob.variables.add(obj=[m], lb=[0], ub=[], types="I", names=["L_" + str(i)])

    for j, date_min in zip(J, data_min_ini): # Definindo a variável que representa a data de início da produção do pedido, 
                                             # cujo o valor multiplicado é 0 e o valor mínimo é data mínima do pedido
        prob.variables.add(obj=[0], lb=[date_min], ub=[], types="I", names=["R_" + str(j)])

    for j in J: # Definindo a variável que representa a data em que o pedido será entregue, cujo o valor multiplicado é 0
        prob.variables.add(obj=[0], lb=[], ub=[], types="I", names=["F_" + str(j)])

    for i in V:
        coef, arc = [], []
        for j in V:
            if (i != j):
                # Criando as variáveis de arco, relacionando os pedidos, cada arco representado por Xij
                prob.variables.add(obj=[0], lb=[0], ub=[1], types="I", names=["x_" + str(i) + "_" + str(j)])
    
    #Após a criação das variáveis, será definido as restrições: 
    
    constraints, rhs = [], []
    for i in V:
        coef, arc = [], []
        for j in V:
            if (i != j):
                coef.append(1) # Multiplicando cada Xij, de um mesmo i, por 1
                arc.append("x_" + str(i) + "_" + str(j)) # Realizando a somatória de todos Xij de um mesmo i
        constraints.append([arc,coef])
        rhs.append(1) # Definindo que a somatória deve ter alguma relação com 1

    for j in V:
        coef, arc = [], []
        for i in V:
            if (i != j):
                coef.append(1) # Multiplicando cada Xij, de um mesmo j, por 1
                arc.append("x_" + str(i) + "_" + str(j)) # Realizando a somatória de todos Xij de um mesmo j
        constraints.append([arc,coef])
        rhs.append(1) # Definindo que a somatória deve ter alguma relação com 1

    constraint_senses = ["E"] * len(constraints) # Definindo que todas as restrições definidas até agora tratam-se de relações de igualdade entre as somatórias e o rhs

    for j, pj in zip(J, data_entrega): # Fj - Lj <= pj
        coef, arc = [], []
        coef.append(1) # Índice multiplicativo da variável Fj, que representa a data de entrega do pedido
        coef.append(-1) # Índice multiplicativo da variável Lj, que representa os dias de atraso na entrega do pedido
        arc.append("F_" + str(j)) # Definindo Fj, que seria a data de entrega real do pedido
        arc.append("L_" + str(j)) # Definindo Lj, que seria os dias de atraso na entrega do pedido
        constraint_senses.append("L") # Definindo a relação como menor igual 
        constraints.append([arc,coef])
        rhs.append(pj) # Valor relacionado a operação de soma das variáveis contidas no constraints, no caso seria o valor da data de entrega prevista
    
    # Calculando o M, um valor suficiente grande para servir de gatilho em uma restrição.
    M = 0
    for rj in data_min_ini:
        if rj > M:
            M = rj # M será o valor máximo da data mínima de início, acrescentando todas as durações de todas as tarefas
    
    for dj in duracao:
        M += dj # Acrescentando a duração de todas as tarefas

    for i, di in zip(J, data_entrega): # Ri + M*Xij - Rj <= -di + M ou Rj - Ri - M*Xij >= di - M
                                       # Xij = 0 -> Não tendo relação entre esses arcos não precisará existir uma relação entre a duração das tarefas,
                                       #            tal feito se faz possível pelo número suficientemente grande definido por M, o qual guarda todas as 
                                       #            durações de todos os pedidos e a data mínima máxima
                                       # Xij = 1 -> Existindo relação entre i e j, a diferença entre as datas de ínicio da tarefa posterior e sua anterior 
                                       #            tem que ser maior ou igual a duração da tarefa anterior
        for j in J:
            coef, arc = [], []
            if (i != j):
                coef.append(1) # Definindo o índice multiplicativo de Ri, que seria a data de início da produção do pedido i
                arc.append("R_" + str(i))# Definindo Ri, que seria a data de início da produção do pedido i
                coef.append(M) # Definindo o índice multiplicativo de Xij, como o M suficientemente grande
                arc.append("x_" + str(i) + "_" + str(j))  # Definindo Xij, que seriam as variáveis de arco
                coef.append(-1) # Definindo o índice multiplicativo de Rj, que seria a data de início da produção do pedido j
                arc.append("R_" + str(j)) # Definindo Rj, que seria a data de início da produção do pedido j
                constraint_senses.append("L") # Definindo a relação como menor igual
                constraints.append([arc,coef])
                rhs.append(-di + M) # Definindo a relação de soma das variáveis acima, no caso a relação de menor ou igual, 
                                    # como a diferença entre o M suficientemente grande o di, que seria a duração da tarefa i    

    constraint_names = ["c" + str(i) for i, _ in enumerate(constraints)] # Definindo o nome de cada restrição conforme o número existente destas
    prob.linear_constraints.add(names=constraint_names, # Adicionando os nomes das restrições
                                lin_expr=constraints, # Adicionando as relações entre variáveis e coeficientes em cada restrição
                                senses=constraint_senses, # Definindo os tipos de relação de cada restrição
                                rhs=rhs) # Definindo o que estas devem resultar.

    return prob # Retorna problema
    
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