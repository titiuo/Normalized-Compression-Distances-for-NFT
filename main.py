import requests
import lzma
import sys
import re
import pickle


def getCollection(collection_name):
    dict = {}

    url = f"https://api-mainnet.magiceden.dev/v2/collections/{collection_name}/listings"
    url_stats = f"https://api-mainnet.magiceden.dev/v2/collections/{collection_name}/stats"
    url_attributs = f"https://api-mainnet.magiceden.dev/v2/collections/{collection_name}/attributes"

    headers = {"accept": "application/json"}

    response_stat = requests.get(url_stats, headers=headers)
    listed_count = int(response_stat.json()['listedCount'])

    listed_count = 100

    for i in range(listed_count//100): #modifier le pas et filtrer les prix trop hauts / prendre en compte les ventes
        params = {"limit": 100,"offset":100*i}
        response = requests.get(url, headers=headers,params=params)
        for nft in response.json():
            r_img = requests.get(nft['token']['image'], stream = True)
            match = re.search(r'#(\d+)', nft['token']['name'])
            if match and r_img.status_code == 200:
                id = int(match.group(1))
                image = r_img.content
                prix = nft['price']
                dict[id] = (image,prix)

    return dict


def ncd(x,y):
    x_y = x + y  # the concatenation of files

    x_comp = lzma.compress(x)
    y_comp = lzma.compress(y)
    x_y_comp = lzma.compress(x_y)

    ncd = (len(x_y_comp) - min(len(x_comp), len(y_comp))) / max(len(x_comp), len(y_comp))

    return ncd

def len_dict(collection_name):
    with open(collection_name,'rb') as f:
        collection_dict = pickle.load(f)
    return len(collection_dict)

def see_in_dict(collection_name,id):
    with open(collection_name,'rb') as f:
        collection_dict = pickle.load(f)
    return collection_dict[id]


if __name__ == '__main__':
    
    collection_name = sys.argv[1]
    nft_id = int(sys.argv[2])
    if sys.argv[3]=="y":
        with open(collection_name,'rb') as f:
            collection_dict = pickle.load(f)
        print("ok")
    else:
        collection_dict = getCollection(collection_name)
        #collection_dict_str={str(key): value for key,value in collection_dict.items()}
        with open(collection_name,'wb') as f:
            pickle.dump(collection_dict,f)
            print("ok")
    dp=[]
    for id in collection_dict:
        if id != nft_id:
            dp.append((1-ncd(collection_dict[id][0],collection_dict[nft_id][0]),collection_dict[id][1])) #si nft_id pas dans la liste l'ajouter
            print(id)
    price=sum([d * p for d, p in dp])/sum([d for d,_  in dp])
    print(f"Prix estimé : {price}\nPrix réelle : {see_in_dict(collection_name,nft_id)[1]}")
    
