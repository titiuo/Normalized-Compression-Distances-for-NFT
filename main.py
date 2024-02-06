import requests
import sys
from PIL import Image
from io import BytesIO
import re


def getCollection(collection_name):
    dict = {}

    url = f"https://api-mainnet.magiceden.dev/v2/collections/{collection_name}/listings"
    url_stats = f"https://api-mainnet.magiceden.dev/v2/collections/{collection_name}/stats"

    headers = {"accept": "application/json"}

    response_stat = requests.get(url_stats, headers=headers)
    listed_count = int(response_stat.json()['listedCount'])

    for i in range(listed_count//100): #modifier le pas et filtrer les prix trop hauts / prendre en compte les ventes
        params = {"limit": 100,"offset":100*i}
        response = requests.get(url, headers=headers,params=params)
        for nft in response.json():
            r_img = requests.get(nft['token']['image'], stream = True)
            match = re.search(r'#(\d+)', nft['token']['name'])
            if match and r_img.status_code == 200:
                id = match.group(1)
                image = Image.open(BytesIO(r_img.content))
                prix = nft['price']
                dict[id] = (image,prix)

    return dict

if __name__ == '__main__':
    collection_name = sys.argv[1]
    collection_dict = getCollection(collection_name)