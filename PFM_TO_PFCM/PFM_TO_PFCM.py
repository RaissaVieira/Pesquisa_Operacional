''' 
PROJETO 1 DA DISCIPLINA DE PESQUISA 
COMPONENTES: RAISSA VIEIRA, LUCIANO JUNIOR E YASMIN MEDEIROS
OBJETIVO: MODELAGEM DO PROBLEMA DO FLUXO MÁXIMO A PARTIR DO PROBLEMA DO FLUXO MÍNIMO
'''

#Importação das biliotecas
import sys #Usada para a leitura de arquivos
import cplex # Resolvedor utilizado
from cplex.exceptions import CplexError 


# Função que tem como objetivo ler o arquivo e retornar as informações que serão utilizadas pelo resolvedor
def readInstance(filePath):
    f = open(filePath, "r") # Abrindo o arquivo 
    
    n = int(f.readline()) # Lendo o numero de vértices
    m = int(f.readline()) # Lendo o numero de arcos
    s = int(f.readline()) # Lendo o indice da origem
    t = int(f.readline()) # Lendo o indice do escoadouro

    begin = [] # Indices i
    end = [] # Indices j
    capacity = [] # Capacidade dos arcos (c_m)

    for dado in range(m): # Identificando a capacidade e os índices de cada arco
        l = f.readline() # Lendo a linha do arco
        i, j, c = int(l.split()[0]), int(l.split()[1]), int(l.split()[2]) # Separando suas informações de interesse
        begin.append(i)} # Pondo a informação no seu respectivo array
        end.append(j) # Pondo a informação no seu respectivo array
        capacity.append(c) # Pondo a informação no seu respectivo array

    begin.append(s) # Adiciona o índice de origem extraído do arquivo até o array begin
    end.append(t) # Adiciona o índice do escoadouro extraído do arquivo até o array end

    f.close() # Fecha arquivo

    return n,m,s,t,begin,end,capacity # Retorna as variáveis extraídas

# Esta função tem como objetivo a criação do modelo
# Possui como parâmetros, aqueles que foram lidos do arquivo
# n-> número de vértices
# m-> numero de arcos
# s-> indice da origem
# t-> indice do escoadouro
# begin -> array que contém os vértices de origem de cada arco
# end -> array que contém os vértices de escoagem de cada arco
def createProblem(n,m,s,t,begin,end,capacity):
    prob = cplex.Cplex() # inicializando o resolvedor do CPLEX

    custo = 0 # Como pede o modelo, o custo em todos os arcos é 0, com execeção do arco que vai da origem até o escoadouro
    custo_s_t = 3 # Custo acima de 0, definido para o arco que sai da origem e vai até o escoadouro
    b = 0 # Fluxo em cada arco, com exceção do que saí da origem e vai até o escoadouro

    vertices = [] # Definindo um array com todos os vértices a partir da verificação nos array begin e end
    for i in begin:
        if (i not in vertices): # Verificando a presença do nó no array vértices para não ocorrer repetições 
            vertices.append(i)
    for i in end:
        if (i not in vertices): # Verificando a presença do nó no array vértices para não ocorrer repetições
            vertices.append(i)

    limite_superior = 0 #Cálculo do limite superior, que seria o fluxo máximo que poderia passar da origem pro escoadouro
    for x in vertices:
        if x == t: # Identificando o vértice que representa o escoadouro
            for i,j,c in zip (begin, end,capacity): # Uso das variáveis i,j,c sequencialmente em um for
                if (j == x): # Identificando quando o vértice de escoamento do arco é o escoadouro
                    limite_superior += c # Somando as capacidades dos vértices filtrados na linha anterior

    prob.set_problem_type(cplex.Cplex.problem_type.LP) # Definindo como um problema de programação linear

    prob.objective.set_sense(prob.objective.sense.minimize) # Definindo que a função objetivo irá buscar a minimização, como pede o problema do custo mínimo

    for i, j, c in zip(begin,end,capacity): # Iteração sequencial das variáveis dos vértices de origem, escoagem e capacidade de cada arco
        '''Definindo os elementos da função objetivo, sendo o índice multiplicativo o custo, os valores 
        podendo variar de 0 até a capacidade, seu tipo sendo definido como float, e o nome sendo montado 
        como x + o número da origem do arco + o número de escoagem do arco
        '''
        prob.variables.add(obj=[custo], lb=[0], ub=[c], types="C", names=["x_" + str(i) + "_" + str(j)])

    # Adicionando o arco que sai da origem e vai até o escoadouro, como um custo diferente, e o seu máximo sendo o infinito
    prob.variables.add(obj=[custo_s_t], lb=[0], ub=[float("inf")], types="I", names=["x_" + str(s) + "_" + str(t)])

    # Definidno os nomes de todos os arcos
    names = [] 
    for i,j in zip (begin,end):
        names.append("x_" + str(i) + "_" + str(j))

    rhs = [] # Aqui seŕa guardado todos os índices que serão multiplicados pelos arcos por vértice 
    constraints = [] # Aqui será guardado o nome de cada arco e seu respectivo coeficiente multiplicativo (rhs) 

    for x in vertices: # Analisando cada nó
        coef, arc = [], []
        for i,j,num in zip (begin, end, range(len(begin))): #Iterando sequencialmente cada índice de origem e escoagem dos arcos e o número do arco
            if (i == x): # Se o nó analisado for de origem
                coef.append(1) # Coeficiente multiplicativo igual a 1
                arc.append(names[num]) # Adicionando o nome do arco ao array arc
            if (j == x): # Se o nó analisado for o do escoadouro
                coef.append(-1) # Coeficiente multiplicativo igual a 1
                arc.append(names[num]) # Adicionando o nome do arco ao array arc
        
        constraints.append([arc,coef]) # Adicionando um array com o par de arcos e coeficientes desse respectivo nó 
    
        if x != s and x!= t: # Se o arco for transbordo, rhs = 0
            rhs.append(0)
        if x == s: # Se o arco for o de origem, o rhs é o positivo do limite superior
            rhs.append(limite_superior)
        elif x == t: # Se o arco for o do escoadouro, o rhs é o negativo do limite superior
            rhs.append(-limite_superior)

    constraint_names = ["c" + str(i) for i, _ in enumerate(constraints)] # Definindo os nomes dos constraits a partir do número do nó

    constraint_senses = ["E"] * len(constraints) # Definindo todas as relações como igual, no caso E = Equality

    #Criação das restrições
    prob.linear_constraints.add(names=constraint_names,
                                lin_expr=constraints,
                                senses=constraint_senses,
                                rhs=rhs)
              
    return prob #Retorna o modelo

def main():

    try: # Tentando resolver o problema
        n,m,s,t,begin,end,capacity = readInstance(sys.argv[1]) # Lendo o arquivo
        prob = createProblem(n,m,s,t,begin,end,capacity) # Aplicando o resolvedor
        prob.write("model.lp") 
        prob.solve() # Resolvendo o problema
    except CplexError as exc:
        print(exc)
        return

    print ("Solution status = ", prob.solution.get_status(), ":") # Retorna o status da resolução
    print (prob.solution.status[prob.solution.get_status()]) #Retorna a solução do status
    print ("Solution value  = ", prob.solution.get_objective_value()) # Retorna o valor da solução

    #Expões os arcos e calcula o valor do fluxo máximo
    print ("Solution:")
    fluxo_maximo = 0
    for i, j in zip(begin,end):
        value = prob.solution.get_values("x_" + str(i) + "_" + str(j))

        if i == s and j != t:
            fluxo_maximo += value

    print("Fluxo Maximo: ", fluxo_maximo) # Expõe o o fluxo máximo dos dados inseridos

main()