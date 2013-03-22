import os
import random

def PersonalRank(G, alpha, root, max_step):
    rank = dict()
    rank = {x:0.0 for x in G.keys()}
    rank[root] = 1.0
    for k in range(max_step):
        tmp = {x:0.0 for x in G.keys()}
        for i,ri in G.items():
            for j,wij in ri.items():
                if j not in tmp: tmp[j] = 0.0
                tmp[j] += alpha * rank[i] / (len(ri)*1.0)
                if j == root: tmp[j] += 1.0 - alpha
        rank = tmp
        print(k, rank)
    return rank

class Graph:
    def __init__(self):
        self.G = dict()
    
    def addEdge(self, p, q):
        if p not in self.G: self.G[p] = dict()
        if q not in self.G: self.G[q] = dict()
        self.G[p][q] = 1
        self.G[q][p] = 1

    def getGraphMatrix(self):
        return self.G

    
def main():
    graph = Graph()
    graph.addEdge('A', 'a')
    graph.addEdge('A', 'c')
    graph.addEdge('B', 'a')
    graph.addEdge('B', 'b')
    graph.addEdge('B', 'c')
    graph.addEdge('B', 'd')
    graph.addEdge('C', 'c')
    graph.addEdge('C', 'd')
    G = graph.getGraphMatrix()
    print(G.keys())
    print(PersonalRank(G, 0.8, 'A', 20))
#    print(PersonalRank(G, 0.8, 'B', 20))
#    print(PersonalRank(G, 0.8, 'C', 20))



if __name__ == '__main__':
    main()
