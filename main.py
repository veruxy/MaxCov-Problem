from numpy import genfromtxt
import numpy as np
import matplotlib.pyplot as plt

import csv
import random
import copy

from transportation import *
from maxcov import *
def read_params():
    global time_multiple, freq, nb_steps, l_min, l_max, nr_dist, nb_steps, w_min, w_max
    csv_file = open("parameters.csv")
    csv_reader = csv.DictReader(csv_file)
    params = list(csv_reader)[0]

    nb_paths = int(params["number paths"])
    l_max = int(params["max length"])
    l_min = int(params["min length"])
    w_max = int(params["max weight"])
    w_min = int(params["min weight"])
    freq = int(params["frequence"])
    time_multiple = int(params["time multiple"])
    nb_steps = int(params["nb steps"])
    return nb_paths,l_min,l_max,nb_steps
def generate_rand_path_length(l_min,l_max, nb_paths=1):
    l = random.randint(l_min, l_max)
    if nb_paths==1:
        p= list(nx.generate_random_paths(gr_big, sample_size=nb_paths, path_length=l))[0]
        return p
    else:
        return list(nx.generate_random_paths(gr_big, sample_size=nb_paths, path_length=l))
def add_to_dict(i,vertices,start):
    global dict_platoon_edges
    t = start
    dict_platoon_edges[i] = [(vertices[0], t)]
    x = vertices[0]

    for y in vertices[1:]:
        dict_edges_platoon.setdefault((x, y), []).append(i)
        t += w[x][y]
        dict_platoon_edges[i].append((y, t))
        x = y

def first_scenario(s,d,time_multiple,plotting=True):
    global dict_platoon_edges
    """
    1. sursa, dest fixate
Tmax=2*dist(sursa,dest)
pt nr= 1, nr max plutoane fixate
    gen plutoane aleat de 100 ori; la fiecare experiment- min cov, maxcov, media (plot sau tabel)
concluzie - se stabilizeaza nr mic de plutoane eficient

    :return:
    """

    source = s
    dest = d
    result=[]
    T_dist = nx.path_weight(gr, nx.dijkstra_path(gr, source, dest), weight='weight')
    Tmax = int(T_dist * time_multiple)


    results= {}
    nb_tests=50

    for j in range(nb_tests): #number of teste
        rand_paths = [[]]
        s = [[]]
        dict_edges_platoon = {}
        dict_platoon_edges = {}

        for i in range(1,nb_paths+1):
            vertices=generate_rand_path_length(l_min,l_max)
            ts = random.randint(0,max(Tmax-nx.path_weight(gr,vertices,weight='weight')-1,0)) #start time
            rand_paths.append(vertices)
            s.append(ts)
            add_to_dict(len(rand_paths) - 1, vertices, ts)

            DP, L  = Solve(gr,n,source,dest,Tmax,dict_platoon_edges,w)



            results.setdefault(i,[]).append(DP[dest][Tmax]) #memorate all covering values for i paths

    results_min_max_med={i:[min(results[i]),sum(results[i])/len(results[i]),max(results[i])] for i in results }

    f = open(f"scenario1_s{source}_d{dest}_mult{time_multiple}.out", "w")
    x = []
    y1 = []
    y2 = []
    y3 = []
    for i, [a, y, z] in results_min_max_med.items():
        #print(f"{i} {a} {y} {z}", file=f)
        x.append(i)
        y1.append(a)
        y2.append(y)
        y3.append(z)
    f.close()
    yproc=[round(c / L[dest][Tmax] * 100, 2) for c in y2]
    if plotting:
        fig, (ax1, ax2) = plt.subplots(1, 2)
        ax1.plot(x, y1, label='minimum cov')
        ax1.plot(x, y2, label='medium cov')
        ax1.plot(x, y3, label='maximum cov')
        # ax[1].set(xlabel='X Values', ylabel='Y Values',       title='Derivative Function of f')
        ax1.set(xlabel='number of platoon paths', ylabel='covering value')
        # plt.xlabel('number of platoon paths')
        # plt.ylabel('covering value')
        #plt.legend()
        ax2.plot(x, yproc)  # procentage pf path covered
        ax2.set(xlabel='number of platoon paths', ylabel='percentage of covered length')
        # plt.ylabel('percentage of covered length')
        plt.savefig("experiment1.png")
        plt.show()


    return yproc

def second_scenario(source,dest,tip=1):

    proc_results = [[]]
    max_times=6
    #ls_times = [1, 1.25, 1.5, 1.75, 2, 2.25, 2.5, 2.75, 3, 3.5]
    if tip==1:
        ls_times = [1,2,3,4]
    else:
        ls_times = [1, 1.25, 1.5, 1.75, 2, 2.25, 2.5, 2.75,3,3.5]
    #ls_times=[1,1.25]
    proc_results={}
    #for times in range(1, max_times):
    for times in ls_times:

        proc_results.update({times:first_scenario(source, dest, times, False)})


    x=list(range(1,nb_paths+1))

    #for times in range(1, max_times):
    for times in ls_times:
        plt.plot(x, proc_results[times], label=f"times {times}")  # procentage pf path covered

    plt.xlabel('number of platoon paths')
    plt.ylabel('avg percentage of covered length')

    plt.legend()

    plt.show()
def third_scenario(nb_paths,nb_pairs,max_length,time_multiple=3):
    global dict_platoon_edges
    nb_tests=50
    to_plot=[]
    to_plot1 = []
    x=[]
    y={}
    min_max_cov={}

    #ls_length = list(range(1,max_length+1,2))
    ls_length=list(range(1,max_length+1))
    for i in range(nb_pairs):
        ls=list(gr_big.nodes())
        source=random.choice(ls)
        ls.remove(source)
        dest=random.choice(ls)
        T_dist = nx.path_weight(gr, nx.dijkstra_path(gr, source, dest), weight='weight')
        Tmax = int(T_dist) * time_multiple


        y[(source,dest)]= {lp:[] for lp in ls_length}
        min_max_cov[(source, dest)]=[-1,-1]


        for lp in ls_length:
            res = 0
            for i in range(nb_tests):
                #generate nb_paths of length 1, find medium of cov/P
                rand_paths = [[]]
                s = [[]]
                dict_edges_platoon = {}
                dict_platoon_edges = {}


                ls_vertices = generate_rand_path_length(lp, lp, nb_paths//lp)

                for vertices in ls_vertices:

                    ts = random.randint(0, max(Tmax - nx.path_weight(gr, vertices, weight='weight') - 1, 0))  # start time
                    rand_paths.append(vertices)
                    s.append(ts)
                    add_to_dict(len(rand_paths) - 1, vertices, ts)


                DP, L  = Solve(gr, n, source, dest, Tmax, dict_platoon_edges, w)

                res+=DP[dest][Tmax]*100/L[dest][Tmax]
                #print(DP[dest][Tmax],L[dest][Tmax],D[source][dest],Tmax)

            res/=nb_tests
            y[(source,dest)][lp].append(res) #average cov for lp

            if min_max_cov[(source, dest)][0]==-1 or min_max_cov[(source, dest)][0]>res:
                min_max_cov[(source, dest)][0]=res
            if min_max_cov[(source, dest)][1]==-1 or min_max_cov[(source, dest)][1]<res:
                min_max_cov[(source, dest)][1]=res
        x.append((source,dest))

    min_lp={i:0 for i in ls_length}
    max_lp={i:0 for i in ls_length}
    for pairsd in y:
        dic_sd=y[pairsd]
        for lp in ls_length:
            if min_max_cov[pairsd][0] in dic_sd[lp]:
                min_lp[lp]+=1
            if min_max_cov[pairsd][1] in dic_sd[lp]:
                max_lp[lp]+=1





    plt.bar([x - 0.2 for x in ls_length], list(min_lp.values()), 0.4, label='min')
    plt.bar([x + 0.2 for x in ls_length], list(max_lp.values()), 0.4, label='max')


    plt.xlabel("Length of path")
    plt.ylabel("Cases when gives min or max")
    plt.legend()

    plt.show()

if __name__ == '__main__':
    gr, w, n, gr_big = read_graph("graph_r.in")
    nb_paths, l_min, l_max, nb_steps = read_params()
    dict_edges_platoon = {}
    dict_platoon_edges = {}
    D = FolydWarshall(n, w)
    source = 55  # bucharest
    dest = 242  # satu mare
    first_scenario(source, dest, 3)
    first_scenario(source,dest,2)
    second_scenario(source,dest,1)
    second_scenario(source, dest,0)
    third_scenario(30,100,6)







