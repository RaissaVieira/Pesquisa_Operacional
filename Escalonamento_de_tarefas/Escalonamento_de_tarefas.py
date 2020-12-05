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

    for dado in range(n): # Identificando a capacidade e os índices de cada arco
        l = f.readline() # Lendo a linha do arco
        i, dmi, d, de, m = int(l.split()[0]), int(l.split()[1]), int(l.split()[2]), int(l.split()[3]), int(l.split()[4]) # Separando suas informações de interesse
        # Adicionando as informacoes nos respectivos array
        indice.append(i)
        data_min_ini.append(dmi)
        duracao.append(d)
        data_entrega.append(de)
        multa.append(m)

    # Criando o no 0
    n += 1
    indice.append(0)
    data_min_ini.append(0)
    duracao.append(0)
    data_entrega.append(0)
    multa.append(0)
    
    f.close() # Fecha arquivo

    return n, indice, data_min_ini, duracao, data_entrega, multa # Retorna as variáveis extraídas