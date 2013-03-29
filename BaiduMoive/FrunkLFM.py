import os
import basic
from   operator import itemgetter
import math
import random
import time
import traceback

#############################################

class LatentFactorModel:
    def __init__(self):
        self.p = dict()
        self.q = dict()
        self.F = 0
        return

    def InitLFM(self, records, F):
        self.F = F
        for r in records:
            if r.test != 0: continue
            if r.user not in self.p:
                self.p[r.user] = [random.random()/math.sqrt(self.F)
                             for x in range(0,self.F)]
            if r.item not in self.q:
                self.q[r.item] = [random.random()/math.sqrt(self.F)
                             for x in range(0,self.F)]
        return

    def Predict(self, user, item):
        if user not in self.p: return 3.78
        if item not in self.q: return 3.78
        predict = sum(self.p[user][f]*self.q[item][f] for f in range(0,self.F))
        #print("=====", user, item, predict)
        #print("=========", self.p[user], self.q[item])
        return predict

    def PredictAll(self, records):
        for r in records:
            if r.test == 0: continue
            r.predict = self.Predict(r.user, r.item)
        return
        
    def LearningLFM(self, records, n, F, alpha, Lambda):
        self.InitLFM(records, F)
        print("self.F=", self.F)
        print(len(self.p), len(self.q))
        print(self.p[7245481])
        #print(self.q[687076])
        for step in range(0, n):
            print("Step = ", time.strftime('%Y-%m-%d_%H:%M:%S',time.localtime(time.time())), step)
            for r in records:
                if r.test != 0: continue
                pui = self.Predict(r.user, r.item)
             #   if r.user == 7245481 and r.item==929118: print("before", self.p[7245481], self.q[929118],pui, r.vote)
                eui = r.vote - pui
                for k in range(0,F):
                    self.p[r.user][k] += alpha * (self.q[r.item][k]*eui - Lambda*self.p[r.user][k])
                    self.q[r.item][k] += alpha * (self.p[r.user][k]*eui - Lambda*self.q[r.item][k])
              #  if r.user == 7245481 and r.item==929118: print("after", self.p[7245481], self.q[929118],pui, r.vote)
            #print("step after", self.p[7245481], self.q[929118])
            alpha *= 0.9
            
        print(self.p[7245481])

class BiasLatentFactorModel:
    def __init__(self):
        self.p = dict()
        self.q = dict()
        self.bu = dict()    #用户偏置项
        self.bi = dict()    #物品偏置项
        self.mu = 0         #训练集中所有评分的平均值
        self.F = 0
        return

    def InitLFM(self, records, F):
        self.F = F
        for r in records:
            if r.test != 0: continue
            self.bu[r.user] = 0
            self.bi[r.item] = 0
            if r.user not in self.p:
                self.p[r.user] = [random.random()/math.sqrt(self.F)
                             for x in range(0,self.F)]
            if r.item not in self.q:
                self.q[r.item] = [random.random()/math.sqrt(self.F)
                             for x in range(0,self.F)]
        return

    def Predict(self, u, i):
        ret = self.mu + self.bu[u] + self.bi[i]
        ret += sum(self.p[u][f]*self.q[i][f] for f in range(0,self.F))
        return ret
    
    def PredictAll(self, records):
        for r in records:
            if r.test == 0: continue
            r.predict = self.Predict(r.user, r.item)
    
    def LearningLFM(self, records, n, F, alpha, Lambda):
        self.InitLFM(records, F)
        for step in range(0, n):
            print("Step = ", step)
            for r in records:
                if r.test != 0: continue
                pui = self.Predict(r.user, r.item)
                eui = r.vote - pui
                self.bu[r.user] += alpha * (eui - Lambda*self.bu[r.user])
                self.bi[r.item] += alpha * (eui - Lambda*self.bi[r.item])
                for k in range(0,F):
                    self.p[r.user][k] += alpha * (self.q[r.item][k]*eui - Lambda*self.p[r.user][k])
                    self.q[r.item][k] += alpha * (self.p[r.user][k]*eui - Lambda*self.q[r.item][k])
            alpha *= 0.9
        return 

#############################################

def RMSE(records):
    train = 0.0
    test  = 0.0
    train_count = 0
    test_count = 0
    for r in records:
        if r.test == 0:
            train += (r.predict - r.vote) * (r.predict - r.vote)
            train_count += 1
        elif r.test == 1:
            test += (r.predict - r.vote) * (r.predict - r.vote)
            test_count += 1

    train_score = 11111111111111.0
    if train_count != 0:
        train_score = math.sqrt(train / (1.0 * train_count))
    test_score = 11111111111111.0
    if test_count != 0:
        test_score  = math.sqrt(test / (1.0 * test_count))
    return train_count, train_score, test_count, test_score

class Record:
    def __init__(self, uid, item, vote=0.0, test=0, predict=0.0):
        self.user = uid
        self.item = item
        self.vote = vote
        self.test = test
        self.predict = predict
    def Print(self):
        print (self.user, self.item, self.vote, self.test, self.predict)


def LoadData(f_name):
    random.seed(int(time.time()))
    records = []
    count = 0
    f = open(f_name, 'r')
    lines = f.readlines()
    for line in lines:
        if line == "\r\n": continue
        if len(line) == 0: continue
        fields = line.split()
        if len(fields) == 3:
            if random.randint(0, 2) == 1:
                records.append( Record(int(fields[0]), int(fields[1]), float(fields[2])) )
        elif len(fields) == 2:
            records.append( Record(int(fields[0]), int(fields[1]), test=1) )
        count += 1
        #if count == 50000: break
    f.close()
    return records

'''
将列表records中的记录，按照模M进行划分，结果为k的作为测试集合.
seed为随机函数的种子
'''
def SplitData(records, M, k, seed):
    random.seed(seed)
    for r in records:
        if random.randint(0, M) == k:
            r.test = 1

def DumpPredictData(records, f_name):
    f = open(f_name, 'w')
    for r in records:
        f.write(str(r.user)+"\t"+str(r.item)+"\t"+str(round(r.predict,4))+"\n")
    f.close()
    return records


def main():
    # 第一个参数是评分文件，按1/10随机挑选测试集.
#    records = LoadData(sys.argv[0])

    records = LoadData("./data-v/training_set.txt")
    print( len(records) )

    SplitData(records, 10, 3, int(time.time()))

    LFM = LatentFactorModel()
    # n F alpha Lambda
    LFM.LearningLFM(records, 30, 40, 0.02, 0.1)
    
    print('================================ Predict ================================')
    LFM.PredictAll(records)
    print(RMSE(records) )
    
    test_data = LoadData("./data-v/predict.txt")
    LFM.PredictAll(test_data)
    print("Predict Done")
    DumpPredictData(test_data, "./data-v/predict_data.txt")


if __name__ == '__main__':
    main()

