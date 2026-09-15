import requests
import logging
import json
def get(url):
    response = requests.get(url)
    return response
if __name__ == '__main__':
    res = get('https://google.com')
    # data=res.text
    print(res.__dict__)
    print(res.status_code)