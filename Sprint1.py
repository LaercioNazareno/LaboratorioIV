import json
import requests

api_url_base = 'https://api.github.com/graphql'
headers = {
    'Content-Type': 'application/json',
    'Authorization': 'bearer 42f40018bbb6242ca2b2163e8866936e3ef6e65e',
}
 
query = '{"query": "{ search(query:\\"stars:>100\\", type:REPOSITORY, first:100){ nodes { ... on Repository {nameWithOwner url createdAt pullRequests(states:MERGED){totalCount} updatedAt releases { totalCount } opened_issues: issues{ totalCount } closed_issues: issues(states:CLOSED){ totalCount } } } } }"}'

response = requests.post(api_url_base, headers=headers, data=query)

if response.status_code != 200:
    print(response)
json = json.loads(response.text)
#resposta das 6 perguntas 
print(json)





