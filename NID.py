import requests
import math
from PIL import Image
from io import BytesIO
import matplotlib.pyplot as plt
import numpy as np
import pickle
import copy

def proba(nft,dic_attributes,combine=False):
    proba = 1
    attribute_types = list(dic_attributes.keys())
    if combine:
        attribute_types*=2
    attributes = nft['token']['attributes']
    for attribute in attributes:
        if attribute['value'] == 'same':
            attribute_types.remove(attribute['trait_type'])
            continue
        proba *= dic_attributes[attribute['trait_type']][attribute['value']]
        attribute_types.remove(attribute['trait_type'])
    attribute_types = set(attribute_types)
    for attribute_type in attribute_types:
        proba *= dic_attributes[attribute_type]['None']
    return proba

def combine(nft_1,nft_2):
    attributes_1 = nft_1['token']['attributes']
    attributes_2 = nft_2['token']['attributes']
    nft_3 = copy.deepcopy(nft_2)
    for attribute_1 in attributes_1:
        if attribute_1 not in attributes_2:
            nft_3['token']['attributes'].append(attribute_1)
        else:
            nft_3['token']['attributes'].append({'trait_type': attribute_1['trait_type'],'value':'same'})
    return nft_3

def NID(nft_1,nft_2,dic_attributes,proba_1 = None,proba_2 = None):
    if not proba_1:
        proba_1 = proba(nft_1,dic_attributes)
    if not proba_2:
        proba_2 = proba(nft_2,dic_attributes)
    proba_12 = proba(combine(nft_1,nft_2),dic_attributes,combine=True)

    NID = -(max(math.log2(proba_1),math.log2(proba_2)) - math.log2(proba_12))/(min(math.log2(proba_1),math.log2(proba_2)))

    return NID

def response(collection_name):
    url_listings = f"https://api-mainnet.magiceden.dev/v2/collections/{collection_name}/listings"
    url_stats = f"https://api-mainnet.magiceden.dev/v2/collections/{collection_name}/stats"

    headers = {"accept": "application/json"}

    response_stats = requests.get(url_stats, headers=headers)
    listed_count = int(response_stats.json()['listedCount'])

    response=[]
    for i in range(listed_count//20): #filtrer les prix trop hauts / prendre en compte les ventes
        params = {"offset":20*i,"listingAggMode":True}
        response += requests.get(url_listings, headers=headers,params=params).json()
    print("OK")
    with open(collection_name,'wb') as f:
            pickle.dump(response,f)

def Matrice(collection_name,dic_attributes):
    with open(collection_name,'rb') as file:
            response = pickle.load(file)
    n=len(response)
    D=np.zeros((n, n))
    P=np.zeros(n)
    i=0
    for nft1 in response:
        j=0
        for nft2 in response :
            if nft2 !=nft1 :
                d = 1 - NID(nft1,nft2,dic_attributes)
                d = max(0,d)
                D[i][j]=d
            j+=1
        P[i]=nft1['price']
        i+=1
    with open(f"{collection_name}_dist",'wb') as file:
        pickle.dump(D,file)
    with open(f"{collection_name}_price",'wb') as file:
        pickle.dump(P,file)

def dic_attrib(collection_name):
    url_attributes = f"https://api-mainnet.magiceden.dev/v2/collections/{collection_name}/attributes"
    url_holders = f"https://api-mainnet.magiceden.dev/v2/collections/{collection_name}/holder_stats"

    headers = {"accept": "application/json"}

    response_holders = requests.get(url_holders, headers=headers)
    totalSupply = response_holders.json()['totalSupply']


    response_attributes = requests.get(url_attributes, headers=headers)
    dic_attributes = {}

    for attribute in response_attributes.json()['results']['availableAttributes']:
        if attribute['attribute']['trait_type'] == 'Attributes Count':
            continue
        elif attribute['attribute']['trait_type'] not in dic_attributes:
            dic_attributes[attribute['attribute']['trait_type']] = {}
        dic_attributes[attribute['attribute']['trait_type']][attribute['attribute']['value']] = (attribute['countByListingType']['1'] + attribute['countByListingType']['2'])/totalSupply

    for attribute_type_dic in dic_attributes.values():
        complementary = 1
        for attribute_proba in attribute_type_dic.values():
            complementary -= attribute_proba
        attribute_type_dic['None'] = complementary
    return dic_attributes

def file(collection_name,dic_attributes):
    response(collection_name)
    print("response OK")
    Matrice(collection_name,dic_attributes)
    print("Matrice OK")


def main(collection_name,id,a,b):
    with open(collection_name,'rb') as file:
            response = pickle.load(file)
    with open(f"{collection_name}_dist",'rb') as file:
            D = pickle.load(file)
    with open(f"{collection_name}_price",'rb') as file:
            P = pickle.load(file)
    pos = list(filter(lambda x: 'token' in x and 'name' in x['token'] and x['token']['name'] == f'sandbar #{id}', response))[0]
    nft_1=pos
    indice=response.index(pos)
    return np.dot(f(D[indice],a,b),P)/sum(f(D[indice],a,b)),nft_1

def closer(collection_name,id):
    with open(collection_name,'rb') as file:
            response = pickle.load(file)
    with open(f"{collection_name}_dist",'rb') as file:
            D = pickle.load(file)
    nft = list(filter(lambda x: 'token' in x and 'name' in x['token'] and x['token']['name'] == f'sandbar #{id}', response))[0]

    indice=response.index(nft)
    D=list(D[indice])
    nft_min=response[D.index(max(D))]
    D[indice]=0.5
    nft_max=response[D.index(min(D))]
    r_img1 = requests.get(nft['token']['image'], stream = True)
    image1 = Image.open(BytesIO(r_img1.content))
    image1.show(title="")
    r_img2 = requests.get(nft_min['token']['image'], stream = True)
    image2 = Image.open(BytesIO(r_img2.content))
    image2.show(title="")
    r_img3 = requests.get(nft_max['token']['image'], stream = True)
    image3 = Image.open(BytesIO(r_img3.content))
    image3.show(title="")
     

def graph(x,y):
    plt.scatter(x, y)
    plt.title("Prix en fonction de la proba")
    plt.xlabel("distance")
    plt.ylabel("delta")

    plt.xscale('log')
    plt.yscale('log')

    plt.show()

def f(d,a,b):
    #return d
    #return d**(a)*(np.exp(b*d)-1)/(np.exp(b)-1)
    return d

if __name__ =='__main__':
    '''
    with open("sandbar",'rb') as file:
            L = pickle.load(file)
    dic=dic_attrib("sandbar")
    Deltas_moy=[]
    Deltas=[]
    p=[]
    a=1/100
    b=5
    for nft in L:
        prix,nft_1=main("sandbar",nft['token']['name'].split("#")[-1].strip(),a,b)
        Delta=abs(prix-nft_1['price'])
        #print(f"Prix estimé :{prix}\nPrix réelle :{nft_1['price']}\nDelta = {Delta}")
        Deltas+=[Delta]
        p+=[proba(nft,dic)]
    graph(p,Deltas)
    print(f"Delta moyen = {np.mean(Deltas)}")
    Deltas_moy+=[np.mean(Deltas)]
    '''
    closer("sandbar",2344)


    