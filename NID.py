import requests
import math
from PIL import Image
from io import BytesIO
import matplotlib.pyplot as plt
import numpy as np
import pickle

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
    for attribute_1 in attributes_1:
        if attribute_1 not in attributes_2:
            nft_2['token']['attributes'].append(attribute_1)
        else:
            nft_2['token']['attributes'].append({'trait_type': attribute_1['trait_type'],'value':'same'})
    return nft_2

def NID(nft_1,nft_2,dic_attributes,proba_1 = None,proba_2 = None):
    if not proba_1:
        proba_1 = proba(nft_1,dic_attributes)
    if not proba_2:
        proba_2 = proba(nft_2,dic_attributes)
    proba_12 = proba(combine(nft_1,nft_2),dic_attributes,combine=True)

    NID = -(max(math.log2(proba_1),math.log2(proba_2)) - math.log2(proba_12))/(min(math.log2(proba_1),math.log2(proba_2)))

    return NID

def f(d):
    return d

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

def main(collection_name,id):
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

    lf = 0
    p = 0
    sd = 0
    dist=[]
    delta=[]
    with open(collection_name,'rb') as file:
            response = pickle.load(file)
    nft_1 = list(filter(lambda x: 'token' in x and 'name' in x['token'] and x['token']['name'] == f'sandbar #{id}', response))[0]
    proba_1 = proba(nft_1,dic_attributes)
    print(nft_1['token']['name'])
    for nft in response:
        #if nft['price']>300:
        #    break
        print(nft['token']['name'])
        if nft != nft_1:
            d = 1 - NID(nft_1,nft,dic_attributes,proba_1=proba_1)
            d = max(0,d)
            sd += f(d)
            p += f(d)*nft['price']
            dist+=[d]
            delta+=[abs(nft_1['price']-nft['price'])]
    return p/sd,delta,nft_1


'''response = requests.get(url, headers=headers)
print(NID(response.json()[1],response.json()[5]))
print(NID(response.json()[1],response.json()[4]))
print(NID(response.json()[1],response.json()[3]))

r_img1 = requests.get(response.json()[1]['token']['image'], stream = True)
r_img3 = requests.get(response.json()[3]['token']['image'], stream = True)
r_img4 = requests.get(response.json()[4]['token']['image'], stream = True)
r_img5 = requests.get(response.json()[5]['token']['image'], stream = True)
image1 = Image.open(BytesIO(r_img1.content))
image3 = Image.open(BytesIO(r_img3.content))
image4 = Image.open(BytesIO(r_img4.content))
image5 = Image.open(BytesIO(r_img5.content))
image1.show(title=response.json()[1]['token']['name'])
image3.show(title=response.json()[3]['token']['name'])
image4.show(title=response.json()[4]['token']['name'])
image5.show(title=response.json()[5]['token']['name'])'''


'''
prob=[]
price=[]
for i in range(listed_count//20): #filtrer les prix trop hauts / prendre en compte les ventes
    params = {"offset":20*i,"listingAggMode":True}
    response = requests.get(url_listings, headers=headers,params=params)
    # Coordonnées des points
    prob += [proba(nft) for nft in response.json() if nft['price']<1000 and proba(nft)<1e-5]
    price += [nft['price'] for nft in response.json() if nft['price']<1000 and proba(nft)<1e-5]
'''

'''
dist=1-np.array(dist)
delta_norm=np.array(delta)/max(delta)
coefficients = np.polyfit(dist, delta_norm, 2)
print(coefficients)
'''

def graph(x,y):
    plt.scatter(x, y)
    plt.title("Prix en fonction de la proba")
    plt.xlabel("distance")
    plt.ylabel("delta")

    plt.xscale('log')
    plt.yscale('log')

    plt.show()

if __name__ =='__main__':
    #response("sandbar")
    prix,delta,nft_1=main("sandbar",2936)
    print(f"Prix estimé :{prix}, Prix réelle :{nft_1['price']}")
    print(f"Moyenne des deltas price: {np.mean(delta)}")