import requests
import json


def search_somenthing(type, query, num):    
    url = f"https://google.serper.dev/{type}"

    payload = json.dumps({
    "q": query,
    "gl": "br",
    "hl": "pt-br",
    "num": num
    })
    headers = {
    'X-API-KEY': '743d014e37a492abe1bd2d6a5a8ab8e4aae04050',
    'Content-Type': 'application/json'
    }

    response = requests.request("POST", url, headers=headers, data=payload)

    return response.text

if __name__ == "__main__":
    print(search_somenthing("search", "jfa eletronicos", 3))
