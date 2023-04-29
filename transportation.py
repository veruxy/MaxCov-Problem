import networkx as nx
import math
import csv
def read_graph(file_name):

    f = open(file_name)
    n=int(f.readline())
    gr = nx.Graph()
    gr.add_nodes_from(range(1,n+1))
    w = [[float("inf") for i in range(n + 1)] for j in range(n + 1)]
    for i in range(n+1):
        w[i][i]=0
    nb_dec=1
    for linie in f:
        ls = linie.split()
        x, y, c = int(ls[0]), int(ls[1]), float(ls[2])
        c=int(c*math.pow(10,nb_dec)) #rotunjit la nb_dec zecimale, trecut la int,deocamdata 0
        w[x+1][y+1] = w[y+1][x+1] = c
        gr.add_edge(x+1, y+1, weight=c)


    f.close()
    gr_big = get_subgraph(gr)
    return gr,w,n, gr_big
def get_medium_population():
    csv_file = open("data.csv")
    csv_reader = list(csv.DictReader(csv_file))
    medie = 0
    for linie in csv_reader[1:]:
        medie += int(linie["Population"])
    medie /= len(csv_reader[1:])
    csv_file.close()
    return medie

def get_subgraph(gr):

    med = get_medium_population()
    big_city = []
    csv_file = open("data.csv")
    csv_reader = list(csv.DictReader(csv_file))
    for linie in csv_reader[1:]:
        if int(linie["Population"]) >= med:
            # big_city.append((linie['Unnamed: 0'],linie["City"]))
            big_city.append(int(linie['Unnamed: 0'])+1) #vertex nb from 1
    csv_file.close()

    return gr.subgraph(big_city)