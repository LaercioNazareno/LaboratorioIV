import requests
from json import dump
from json import loads
import time
import csv
import datetime

# Variaveis globais:
qtd_dados = 1000
qtd_page = qtd_dados/10
qtd_max_buscas = 20

api_url_base = 'https://api.github.com/graphql'

headers = {
    'Content-Type': 'application/json',
    'Authorization': 'bearer 6c36687d3ce57991e214284e239a11a9a6a55eff',
}

query = """
    query{
        search(query:"stars:>100", type:REPOSITORY, first:10{AFTER}){
            pageInfo{
                hasNextPage
                endCursor
            }
            nodes{
                ... on Repository{
                    nameWithOwner 
                    url 
                    createdAt 
                    pullRequests(states:MERGED){
                        totalCount
                    } 
                    updatedAt 
                    releases { 
                        totalCount 
                    } 
                    opened_issues: issues{ 
                        totalCount 
                    } 
                    closed_issues: issues(states:CLOSED){ 
                        totalCount 
                    }
                    primaryLanguage{
                        name
                    }
                }
            }
        }
    }
"""
json = {
    "query":query, "variables":{}
}

# Funções:

# #
#  A função 'request' recebe 2 parametros, um que é a busca 
#  que ela deve execultar e o outro que é o número da consulta    
#  que está sendo execuldada no momento, o segundo paramentro é
#  uma maneira de extrair informações daquela consulta. Para que 
#  consiga trazer a quantidade necessaria de dados requisitados foi incrementado um loop com uma quantidade 
#  maxima de tentativas marcado na variaval global 'qtd_max_buscas', caso ele extoure
#  o número máximo de tentativas a função retorna o erro gerado na ultima requisição. 
#  Além disso foi adicionando um log de execução, que a cada nova tentativa ele 
#  escreve no console qual o erro, de qual requisição ele fez, e ao final da 
#  requisição ele mostra o tempo da consulta. 
# #
def request(json, n_consulta = 0):
    time_start = time.time()
    
    print("consulta numero: "+str(n_consulta)+"/"+str(qtd_page))
    response = requests.post(api_url_base, headers=headers, json=json)
    
    qtd_tentativas = 1
    while response.status_code != 200 and qtd_tentativas < qtd_max_buscas:
        print("Erro "+str(response.status_code)+" na busca "+str(qtd_tentativas)+"/"+str(qtd_max_buscas)+", iniciando proxima tentativa ")
        qtd_tentativas = qtd_tentativas+1   
        response = requests.post(api_url_base, headers=headers, json=json)

    time_finish = time.time()
    delta = time_finish-time_start
    print("tempo da consulta: ")
    print(delta)
    return response

def start():
    respo = initialaze()
    result = search(respo)
    return result

def initialaze():
    
    next_query = query.replace("{AFTER}", "")
    json["query"] = next_query
    response = request(json)
    return response

# #
#   A função seach pretente buscar a quantidade de dados
#   definida na variavel global 'qtd_dados'. Sendo que
#   a busca é feita por paginação, de forma que a query 
#   é alterada para a buscar proxima pagina, caso a 
#   quantidade de paginas for atingigida ele finaliza o 
#   processo da busca. Em casos que a função de busca retorne 
#   alguma resposta diferente de 200, a função encerra retornando 
#   o erro gerado.
# #
def search(result):
    if result.status_code == 200:
        result = result.json()
        have_next_page = result["data"]["search"]["pageInfo"]["hasNextPage"]
        nodes = result['data']['search']['nodes']
        current_page = 1
        while have_next_page and current_page < qtd_page:
            cursor = result["data"]["search"]["pageInfo"]["endCursor"]
            next_query = query.replace("{AFTER}", ", after: \"%s\"" % cursor)
            json["query"] = next_query
            result = request(json, current_page)
            if result.status_code == 200:
                result = result.json()
                nodes += result['data']['search']['nodes']
                have_next_page  = result["data"]["search"]["pageInfo"]["hasNextPage"]
            else:
                print("reiniciando a consulta!")
                return result
            current_page+=1
        result['data']['search']['nodes'] = nodes
    return result

def save_file(json):
    nodes = json['data']['search']['nodes']

    file = open("arquivo.csv", 'w')
    fieldnames = ["Nome","url","Data Criacao","Total de pullRequests","Data de Atualizacao","Total de releases","Linguagem","Total de issues abertas","Total de issues fechadas","Idade","Tempo de Atualizacao", "porcentagem de issues"]
    writer = csv.DictWriter(file, fieldnames=fieldnames)
    writer.writeheader()


    for node in nodes:
        data = node['createdAt']
        data_atual = datetime.datetime.now().date()
        parametros = (data.split('T')[0]).split('-')
        date = datetime.datetime(int(parametros[0]), int(parametros[1]), int(parametros[2])).date()
        idade = int(int(abs((data_atual - date).days))/365)

        data = node['updatedAt']
        parametros_a = (data.split('T')[0]).split('-')
        date = datetime.datetime(int(parametros_a[0]), int(parametros_a[1]), int(parametros_a[2])).date()
        tempo_atualizacao = int(int(abs((data_atual - date).days)))
        
        if int(node['opened_issues']['totalCount']) > 0 :
            issuesP = (int(node['closed_issues']['totalCount'])*100)/int(node['opened_issues']['totalCount'])

        linguagem = 'Não informado'
        if node['primaryLanguage'] is not None: 
            linguagem = str(node['primaryLanguage']['name'])
        
        writer.writerow({"Nome": node['nameWithOwner'],
                         "url":node['url'],
                         "Data Criacao":date,
                         "Total de pullRequests":node['pullRequests']['totalCount'],
                         "Data de Atualizacao":node['updatedAt'],
                         "Linguagem":linguagem,
                         "Total de releases":node['releases']['totalCount'],
                         "Total de issues abertas":""+str(node['opened_issues']['totalCount']),
                         "Total de issues fechadas":""+str(node['closed_issues']['totalCount']),
                         "Idade": idade,
                         "Tempo de Atualizacao": tempo_atualizacao,
                         "porcentagem de issues": issuesP
                        })
    file.close()

result = start()
save_file(result)

