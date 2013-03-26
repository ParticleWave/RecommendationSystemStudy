import os
import basic
from   operator import itemgetter
import math
import random
import time
import traceback


#############################################
def UserSimilarity(records):
    item_users = dict()
    ave_vote = dict()
    activity = dict()
    for r in records:
        if r.test != 0: continue
        basic.AddToMat(item_users, r.item, r.user, r.vote)
        basic.AddToDict(ave_vote, r.user, r.vote)
        basic.AddToDict(activity, r.user, 1)
    ave_vote = {x:y/activity[x] for x,y in ave_vote.items()}
    nu = dict()
    W = dict()
    for i,ri in item_users.items():
        for u,rui in ri.items():
            basic.AddToDict(nu, u, (rui - ave_vote[u])*(rui - ave_vote[u]))
            for v,rvi in ri.items():
                if u == v: continue
                basic.AddToMat(W, u, v, (rui - ave_vote[u])*(rvi - ave_vote[v]))
    for u in W:
        W[u]= {x:y/math.sqrt(nu[x]*nu[u]) for x,y in W[u].items()}
    return W,ave_vote

def Predict(records, test, ave_vote, W, K):
    user_items = dict()
    for r in records:
        if r.test != 0: continue  #测试数据
        basic.AddToMat(user_items, r.user, r.item, r.vote)
    for r in records:
        if r.test == 0: continue  #训练数据
        r.predict = 0
        norm = 0
        for v,wuv in sorted(W[r.user].items(), key=itemgetter(1), reverse=Truse)[0:K]:
            if r.item in user_items[v]:
                rvi = user_items[v][r.item]
                r.predict += wuv * (rvi - ave_vote[v])
                norm += abs(wuv)
        if norm > 0: r.predict /= norm
        r.predict += ave_vote[r.user]
    for r in test:
        r.predict = 0
        norm = 0
        for v,wuv in sorted(W[r.user].items(), key=itemgetter(1), reverse=Truse)[0:K]:
            if r.item in user_items[v]:
                rvi = user_items[v][r.item]
                r.predict += wuv * (rvi - ave_vote[v])
                norm += abs(wuv)
        if norm > 0: r.predict /= norm
        r.predict += ave_vote[r.user]
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
    records = []
    count = 0
    f = open(f_name, 'r')
    lines = f.readlines()
    for line in lines:
        if line == "\r\n": continue
        if len(line) == 0: continue
        fields = line.split()
        if len(fields) == 3:
            records.append( Record(fields[0], fields[1], float(fields[2])) )
        elif len(fields) == 2:
            records.append( Record(fields[0], fields[1], test=1) )
        count += 1
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

def DumpData(records, f_name):
    f = open(f_name, 'w')
    for r in records:
        f.write(r.user+"\t"+r.item+"\t"+str(round(r.predict,4))+"\n")
    f.close()
    return records


def main():
    # 第一个参数是评分文件，按1/10随机挑选测试集.
#    records = LoadData(sys.argv[0])
    records = LoadData("./data-v/training_set.txt")
    print( len(records) )

    
    SplitData(records, 5, 3, int(time.time()))
    W,ave_vote = UserSimilarity(records)
    print('================================ Predict ================================')

    test_data = LoadData("./data-v/predict.txt")
    print( len(test_data) )

    Predict(records, test_data, ave_vote, W, 10)
    print(RMSE(records) )
    
    print("Predict Done")
    DumpData(test_data, "./data-v/predict_data.txt")


if __name__ == '__main__':
    main()

