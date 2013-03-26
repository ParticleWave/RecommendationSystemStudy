import os
import sys

class LatentFactorModel:
    def __init__(self):
        self.p = dict()
        self.q = dict()
        self.F = 0
        return

    def __InitLFM(self, train, F):
        self.F = F
        self.train = train
        for u,i,rui in train.items():
            if u not in self.p:
                self.p[u] = [random.random()/math.sqrt(self.F)
                             for x in range(0,self.F)]
            if i not in self.q:
                self.q[i] = [random.random()/math.sqrt(self.F)
                             for x in range(0,self.F)]
        return

    def Predict(self, u, i):
        return sum(self.p[u][f]*self.q[i][f]
                   for f in range(0,self.F))
    
    def LearningLFM(self, train, n, alpha, Lambda):
        __InitLFM(train, F)
        for step in range(0, n):
            for u,i,rui in train.items():
                pui = Predict(u, i)
                eui = rui - pui
                for f in range(0,F):
                    self.p[u][k] += alpha * (self.q[i][k]*eui - Lambda*self.p[u][k])
                    self.q[i][k] += alpha * (self.p[u][k]*eui - Lambda*self.q[i][k])
            alpha *= 0.9

class BiasLatentFactorModel:
    def __init__(self):
        self.p = dict()
        self.q = dict()
        self.bu = dict()    #用户偏置项
        self.bi = dict()    #物品偏置项
        self.mu = 0         #训练集中所有评分的平均值
        self.F = 0
        return

    def __InitLFM(self, train, F):
        self.F = F
        self.train = train
        for u,i,rui in train.items():
            self.bu[u] = 0
            self.bi[i] = 0
            if u not in self.p:
                self.p[u] = [random.random()/math.sqrt(self.F)
                             for x in range(0,self.F)]
            if i not in self.q:
                self.q[i] = [random.random()/math.sqrt(self.F)
                             for x in range(0,self.F)]
        return

    def Predict(self, u, i):
        ret = mu + self.bu[u] + self.bi[i]
        ret += sum(self.p[u][f]*self.q[i][f] for f in range(0,self.F))
        return ret
    
    def LearningLFM(self, train, n, alpha, Lambda):
        __InitLFM(train, F)
        for step in range(0, n):
            for u,i,rui in train.items():
                pui = Predict(u, i)
                eui = rui - pui
                self.bu[u] += alpha * (eui - Lambda*self.bu[u])
                self.bi[i] += alpha * (eui - Lambda*self.bi[i])
                for f in range(0,F):
                    self.p[u][k] += alpha * (self.q[i][k]*eui - Lambda*self.p[u][k])
                    self.q[i][k] += alpha * (self.p[u][k]*eui - Lambda*self.q[i][k])
            alpha *= 0.9
        return 

def main():
    print ("Hello World!")
    return

if __name__ == '__main__':
    main()
