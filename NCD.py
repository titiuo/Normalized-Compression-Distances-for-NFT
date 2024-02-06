import lzma
import sys

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

if __name__ == "__main__":
    collection={}
    dp=[]
    for hash in collection:
        if hash != sys.argv[1]:
            dp.append((1-ncd(collection[hash][0],collection[sys.argv[1]][0]),collection[hash][1]))
    price=sum([d * p for d, p in dp])/sum([d for d,_  in dp])
