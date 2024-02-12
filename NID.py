import requests
import math
from PIL import Image
from io import BytesIO
import matplotlib.pyplot as plt
import numpy as np
import pickle
import copy
import sys
import re

def response(collection_name):
    '''récupère toutes les données des listings de la collection sur magiceden et les stock dans un fichier'''
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

def dic_attrib(collection_name):
    '''construit un dictionnaire de dictionnaire où chaque type d'attribut (exemple chapeau) se voit attribuer un dictionnaire où chaque variante de l'attribut (exemple chapeau bleu) se voit attribuer sa probabilité'''
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

def proba(nft,dic_attributes,combine=False):
    '''calcule la probabilité d'existence d'un NFT'''
    proba = 1
    attribute_types = list(dic_attributes.keys())
    if combine:
        attribute_types*=2
    attributes = nft['token']['attributes']
    for attribute in attributes:
        if attribute['value'] == 'same':
            attribute_types.remove(attribute['trait_type'])
            continue
        try:
            proba *= dic_attributes[str(attribute['trait_type'])][str(attribute['value'])]
        except:
            #print(dic_attributes[attribute['trait_type']])
            print(attribute['trait_type'],attribute['value'])
        attribute_types.remove(attribute['trait_type'])
    attribute_types = set(attribute_types)
    for attribute_type in attribute_types:
        proba *= dic_attributes[attribute_type]['None']
    return proba

def combine(nft_1,nft_2):
    '''combine les attributs de 2 NFT pour en former un troisième'''
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
    '''calcule la distance NID entre 2 NFTs'''
    if not proba_1:
        proba_1 = proba(nft_1,dic_attributes)
    if not proba_2:
        proba_2 = proba(nft_2,dic_attributes)
    proba_12 = proba(combine(nft_1,nft_2),dic_attributes,combine=True)

    NID = -(max(math.log2(proba_1),math.log2(proba_2)) - math.log2(proba_12))/(min(math.log2(proba_1),math.log2(proba_2)))

    return NID

def Matrice(collection_name,dic_attributes):
    '''construit la matrice des proximités (1-distance) entre chaques NFTs de la collection et le vecteur des prix de chaque NFT puis les stock dans des fichiers'''
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


def file(collection_name,dic_attributes):
    '''permet de construire les fichiers pour stocker les données d'une collection et économiser du temps de calcul'''
    response(collection_name)
    print("response OK")
    Matrice(collection_name,dic_attributes)
    print("Matrice OK")

def f(d,a,b):
    '''fonction qui adapte le poids de chaque NFT de la collection dans le calcul du prix dans NFT en fonction de leurs distances'''
    return (d**a)*(np.exp(b*d))/(np.exp(b))


def forecast_price(collection_name,id,a,b):
    '''prédit le prix d'un NFT dans la collection à partir de l'id de ce dernier et de la fonction'''
    with open(collection_name,'rb') as file:
        response = pickle.load(file)
    with open(f"{collection_name}_dist",'rb') as file:
        D = pickle.load(file)
    with open(f"{collection_name}_price",'rb') as file:
        P = pickle.load(file)
    chaine =response[0]['token']['name']
    mot = re.match(r'([^#]+)', chaine).group(1)
    pos = list(filter(lambda x: 'token' in x and 'name' in x['token'] and x['token']['name'] == f'{mot}#{id}', response))[0]
    nft_1=pos
    indice=response.index(pos)
    return np.dot(f(D[indice],a,b),P)/sum(f(D[indice],a,b)),nft_1


def show_image(nft):
    '''affiche l'image d'un NFT'''
    r_img1 = requests.get(nft['token']['image'], stream = True)
    image1 = Image.open(BytesIO(r_img1.content))
    image1.show(title="")

def closers(collection_name,id,x=1,show=False):
    '''trouve les x NFT les plus proches du NFT numéro id et peut les afficher'''
    with open(collection_name,'rb') as file:
            response = pickle.load(file)
    with open(f"{collection_name}_dist",'rb') as file:
            D = pickle.load(file)
    with open(f"{collection_name}_price",'rb') as file:
            P = pickle.load(file)
    chaine =response[0]['token']['name']
    mot = re.match(r'([^#]+)', chaine).group(1)
    nft = list(filter(lambda x: 'token' in x and 'name' in x['token'] and x['token']['name'] == f'{mot}#{id}', response))[0]

    indice=response.index(nft)
    D=list(D[indice])
    if x==1: #on regarde uniquement le NFT le plus proche
        nft_min=response[D.index(max(D))]
        ind_min=response.index(nft_min)
        if show :
            show_image(nft)
            show_image(nft_min)
        return nft,(nft_min,P[ind_min])
    else: #on regarde les x NFT les plus proches
        ind_mins=np.argsort(D)[::-1][:x]
        nft_mins=[]
        prices=[]
        for ind_min in ind_mins:
            nft_mins+=[response[int(ind_min)]]
            prices+=[P[int(ind_min)]]
        if show:
            show_image(nft)
            for nft_min in nft_mins:
                show_image(nft_min)
        return nft,(nft_mins,prices)
    
def closer_price(collection_name,id,x):
    '''récupère uniquement les prix des x plus proches NFT du NFT numéro id'''
    _,couple_min=closers(collection_name,id,x)
    return couple_min[1]


def graph(x,y):
    '''fonction pour plot des graphs pour visualiser nos données'''
    plt.scatter(x, y)
    Y=[f(d) for d in np.linspace(0,1,100)]
    plt.plot(np.linspace(0,1,100),Y,'red')
    plt.title("Erreur absolue en fonction de la distance")
    plt.xlabel("Distance")
    plt.ylabel("Delta prix")
    plt.ylim(0, 30)
    plt.xlim(0, 0.65)

    #plt.xscale('log')
    #plt.yscale('log')

    plt.show()


if __name__ =='__main__':

    with open(sys.argv[1],'rb') as file:
            L = pickle.load(file)
    dic=dic_attrib(sys.argv[1])
    Deltas=[]
    Deltas2=[]
    a,b = 1,5
    x=5
    max_price = 11 #on filtre arbitrairement les prix pour éliminer les NFT décorrélés du marché
    prices = []
    for nft in L:
        if nft['price']<max_price:
            prices.append(nft['price'])
            if x==1:
                prix=closer_price(sys.argv[1],nft['token']['name'].split("#")[-1].strip(),x)
            else:
                prix=min(closer_price(sys.argv[1],nft['token']['name'].split("#")[-1].strip(),x))
            Delta=abs(prix-nft['price'])
            Deltas+=[Delta]

            prix2,nft_1=forecast_price(sys.argv[1],nft['token']['name'].split("#")[-1].strip(),a,b)
            Delta2=abs(prix2-nft_1['price'])
            Deltas2+=[Delta2]
    print(f"Delta moyen stratégie prix minimum des {x} plus proches voisins : {np.mean(Deltas)}, erreur relative : {np.mean(Deltas)/np.mean(np.array(prices))}")
    print(f"Delta moyen stratégie prix poids adaptés par la fonction f : {np.mean(Deltas2)}, erreur relative : {np.mean(Deltas2)/np.mean(np.array(prices))}")
    


    