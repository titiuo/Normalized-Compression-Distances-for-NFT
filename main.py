import requests
import lzma
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
                id = int(match.group(1))
                image = Image.open(BytesIO(r_img.content))
                prix = nft['price']
                dict[id] = (image,prix)

    return dict


def ncd(x,y):
    x_y = x + y  # the concatenation of files

    x_comp = lzma.compress(x)  # compress file 1
    y_comp = lzma.compress(y)  # compress file 2
    x_y_comp = lzma.compress(x_y)  # compress file concatenated

    # print len() of each file
    print(len(x_comp), len(y_comp), len(x_y_comp), sep=' ', end='\n')

    # magic happens here
    ncd = (len(x_y_comp) - min(len(x_comp), len(y_comp))) / max(len(x_comp), len(y_comp))

    return ncd

if __name__ == '__main__':
    collection_name = sys.argv[1]
    nft_id = int(sys.argv[2])
    collection_dict = getCollection(collection_name)
    print(co)
    dp=[]
    for id in collection_dict:
        if id != nft_id:
            dp.append((1-ncd(collection_dict[id][0],collection_dict[nft_id][0]),collection_dict[id][1]))

    price=sum([d * p for d, p in dp])/sum([d for d,_  in dp])
    print(price)
