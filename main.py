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
    source = int(params["source"])
    dest = int(params["dest"])
    return nb_paths,l_min,l_max,nb_steps,source,dest
def generate_rand_path_length(l_min,l_max, nb_paths=1):
    l = random.randint(l_min, l_max)
    if nb_paths==1:
        p= list(nx.generate_random_paths(gr_big, sample_size=nb_paths, path_length=l))[0]
        return p
    else:
        return list(nx.generate_random_paths(gr_big, sample_size=nb_paths, path_length=l))


def first_scenario(s,d,time_multiple,plotting=True,nb_tests=100):
    """

    :param s: - source
    :param d: -destination
    :param time_multiple: T_max=time_multiple*distance(source,destination)
    :param plotting: the result is plotted or not
    :param nb_tests: how many tests are generated;
    :return: run nb_tests tests for MaxCov algorithm for the pair (s,d)
    with nb_path platoon paths randomly generated between big cities, having lengths between l_min and l_max,
    with nb_path, l_min, l_max from parameters.csv; starting time for each platoon is also randomly generated
    """
    global dict_platoon_edges


    source = s
    dest = d

    result=[]
    T_dist = nx.path_weight(gr, nx.dijkstra_path(gr, source, dest), weight='weight')
    Tmax = int(T_dist * time_multiple)


    results= {}


    for j in range(nb_tests):
        rand_paths = [[]]
        s = [[]]
        dict_edges_platoon = {}
        dict_platoon_edges = {}

        for i in range(1,nb_paths+1):
            vertices=generate_rand_path_length(l_min,l_max)
            ts = random.randint(0,max(Tmax-nx.path_weight(gr,vertices,weight='weight')-1,0)) #start time
            rand_paths.append(vertices)
            s.append(ts)

            add_to_dict(w, len(rand_paths) - 1, vertices, ts, dict_platoon_edges)

            DP, L  = Solve(gr,n,source,dest,Tmax,w,D,dict_platoon_edges=dict_platoon_edges)



            results.setdefault(i,[]).append(DP[dest][Tmax]) #memorate all covering values for i paths

    results_min_max_med={i:[min(results[i]),sum(results[i])/len(results[i]),max(results[i])] for i in results }

    f = open(f"scenario1_s{source}_d{dest}_mult{time_multiple}.out", "w")
    x = []
    y1 = []
    y2 = []
    y3 = []
    for i, [a, y, z] in results_min_max_med.items():

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

        ax1.set(xlabel='number of platoon paths', ylabel='covering value')

        ax2.plot(x, yproc)
        ax2.set(xlabel='number of platoon paths', ylabel='avg percentage of covered length')


        plt.show()


    return yproc

def second_scenario(source,dest,type=1, nb_tests=50):
    """
    :param source: source
    :param dest: destination
    :param type: in the scenario, Tmax=times* D[source,dest] where  times in [1, 2, 3, 4] if type=1,
    or times in [1, 1.25, 1.5, 1.75, 2, 2.25, 2.5, 2.75, 3, 3.5] otherwise
    :param nb_test: number of tests for the first scenario
    :return: how average covering evolves when Tmax have various values, according to type;
    average covering is estimated using first_scenario
    """

    proc_results = [[]]
    #max_times=6
    ls_times = [1, 1.25, 1.5, 1.75, 2, 2.25, 2.5, 2.75, 3, 3.5]
    if type==1:
        ls_times = [1, 2, 3, 4]
    else:
        ls_times = [1, 1.25, 1.5, 1.75, 2, 2.25, 2.5, 2.75, 3, 3.5]

    proc_results={}

    for times in ls_times:

        proc_results.update({times:first_scenario(source, dest, times, False,nb_tests)})


    x=list(range(1,nb_paths+1))


    for times in ls_times:
        plt.plot(x, proc_results[times], label=f"times {times}")

    plt.xlabel('number of platoon paths')
    plt.ylabel('avg percentage of covered length')

    plt.legend()

    plt.show()
def third_scenario(nb_paths,nb_pairs,max_length,time_multiple=3):
    """

    :param nb_paths: the total length of the platoon paths generated, equals number of paths if platoons paths have length 1
    :param nb_pairs: number of pairs (source,destination) from the experiment
    :param max_length: experiments are made for each length from 1 to max_length
    :param time_multiple: Tmax=time_multiple*distance(source,dest)
    :return: for each length of paths in how many scenarious average covering is min or max for this length of the platoon paths
    """
    global dict_platoon_edges
    nb_tests=50
    to_plot=[]
    to_plot1 = []
    x=[]
    y={}
    min_max_cov={}

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

                rand_paths = [[]]
                s = [[]]
                dict_edges_platoon = {}
                dict_platoon_edges = {}


                ls_vertices = generate_rand_path_length(lp, lp, nb_paths//lp)

                for vertices in ls_vertices:

                    ts = random.randint(0, max(Tmax - nx.path_weight(gr, vertices, weight='weight') - 1, 0))  # start time
                    rand_paths.append(vertices)
                    s.append(ts)
                    add_to_dict(w, len(rand_paths) - 1, vertices, ts, dict_platoon_edges)



                DP, L  = Solve(gr, n, source, dest, Tmax,w=w,D=D,dict_platoon_edges=dict_platoon_edges)

                res+=DP[dest][Tmax]*100/L[dest][Tmax]


            res/=nb_tests
            y[(source,dest)][lp].append(res)

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
    gr, w, n = read_graph("graph_r.in")
    gr_big = get_subgraph(gr)
    nb_paths, l_min, l_max, nb_steps, source, dest = read_params()
    dict_edges_platoon = {}
    dict_platoon_edges = {}
    D = FloydWarshall(n, w)

    first_scenario(source, dest, 3,nb_tests=100 )
    first_scenario(source, dest, 2, nb_tests=100)
    second_scenario(source,dest,0,nb_tests=50)
    second_scenario(source, dest, 1, nb_tests=50)

    third_scenario(30,1 ,6)







