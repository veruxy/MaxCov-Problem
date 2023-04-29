import copy
D=[]
P=[]
inf=float("inf")

def FolydWarshall(n,w):
    global D,P
    D=copy.deepcopy(w)
    P=[[i if w[i][j]<inf and i!=j else 0 for j in range(n+1)] for i in range(n+1)]
    for k in range(1,n+1):
        for i in range(1, n + 1):
            for j in range(1, n + 1):
                if D[i][k]<inf and D[k][j]<inf and D[i][k]+D[k][j]<D[i][j]:
                    D[i][j]=D[i][k]+D[k][j]
                    P[i][j]=P[k][j]

    return D





def Solve(gr,n,source,dest,Tmax,dict_platoon_edges,w):
    #get N teh set of pairs (v,t) from all platoons

    N=set()
    for pl in dict_platoon_edges:
        vertices=dict_platoon_edges[pl]
        N.update(vertices)

    N.add((source,0))

    N.add((dest, Tmax))
    nb_pairs=len(N)
    DP=[[-float("inf") for t in range(0,Tmax+1)]for i in range(n+1) ]
    L=[[-float("inf") for t in range(0,Tmax+1)]for i in range(n+1) ]
   # Fathers = [[(source,0,t-D[source][i],1,0) if t-D[source][i]>=0 else (None,None,None,-1,0)for t in range(0, Tmax + 1)] for i in range(n + 1)]
    N=sorted(N,key=lambda x:x[1])

    DP[source][0]=0
    L[source][0]=0
    for v,t in N:

        if t>Tmax:
            break

        for u,tp in N:

            if tp>t:
                break
            #R1
            if tp+w[u][v]<=t:
                #search if (u,v) is a member of a platoon with arrival time in u equal tot tp
                for a in dict_platoon_edges:
                    try:
                        poz=dict_platoon_edges[a].index((u,tp)) #arrive in u and next edge is uv
                        if poz+1<= len(dict_platoon_edges[a])-1 and dict_platoon_edges[a][poz+1][0]==v:
                            if DP[u][tp]>=0 and DP[v][t]<DP[u][tp]+w[u][v]:
                                DP[v][t]=DP[u][tp]+w[u][v]
                                L[v][t]=L[u][tp]+w[u][v]
                               # Fathers[v][t]=(u,tp,t-tp-w[u][v],0,a)
                    except ValueError:
                        pass
           #R2:

            if tp+D[u][v]<= t:

                if DP[u][tp]>DP[v][t]:
                    DP[v][t] =  DP[u][tp]
                    L[v][t] = L[u][tp] + D[u][v]
                    #Fathers[v][t] = (u, tp, t - tp - D[u][v],1,0)
    return DP,L#,Fathers



def printShortestPath(u,v):
    global ls_path
    if u==v:
        return
    if   u!=P[u][v]:
        printShortestPath(u,P[u][v])
    ls_path.append((v,"wait",0,"type",0))

def printPath(v,t,w):
    print(v,t,Fathers[v][t])
    global ls_path
    a=0
    if (v,t)!=(source,0):
        u,tp,wu,tip,a=Fathers[v][t]
        if u!=v:
            printPath(u, tp,wu)
        if tip==1  and u!=v and u!=P[u][v]:
            printShortestPath(u,P[u][v])

    ls_path.append((v,"wait",w,"type",a))

