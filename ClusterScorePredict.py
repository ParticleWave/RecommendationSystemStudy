import os
import basic
from   operator import itemgetter
import math
import random
import time
import traceback

class Cluster:
    def __init__(self, records):
        self.group = dict()

    def GetGroup(self, i):
        return 0

class IdCluster(Cluster):
    def __init__(self, records):
        Cluster.__init__(self, records)

    def GetGroup(self, i):
        return i
    
class UserActivityCluster(Cluster):
    def __init__(self, records):
        Cluster.__init__(self, records)
        activity = dict()
        for r in records:
            if r.test != 0: continue
            basic.AddToDict(activity, r.user, 1)
        k = 0
        for user,n in sorted(activity.items(), key=itemgetter(1), reverse=False):
            c = int((k*5) / (1.0 * len(activity)))
            self.group[user] = c
            k += 1

    def GetGroup(self, uid):
        if uid not in self.group:
            return -1
        else:
            return self.group[uid]


class ItemPopularityCluster(Cluster):
    def __init__(self, records):
        Cluster.__init__(self, records)
        popularity = dict()
        for r in records:
            if r.test != 0: continue
            basic.AddToDict(popularity, r.item, 1)
        k = 0
        for item,n in sorted(popularity.items(), key=itemgetter(1), reverse=False):
            c = int((k*5) / (1.0 * len(popularity)))
            self.group[item] = c
            k += 1

    def GetGroup(self, item):
        if item not in self.group:
            return -1
        else:
            return self.group[item]

class UserVoteCluster(Cluster):
    def __init__(self, records):
        Cluster.__init__(self, records)
        vote = dict()
        count = dict()
        for r in records:
            if r.test != 0: continue
            basic.AddToDict(vote, r.user, r.vote)
            basic.AddToDict(count, r.user, 1)
        k = 0
        for user,v in vote.items():
            ave = v / (count[user]*1.0)
            c = int(ave * 2)
            self.group[user] = c
    
    def GetGroup(self, uid):
        if uid not in self.group:
            return -1
        else:
            return self.group[uid]


class ItemVoteCluster(Cluster):
    def __init__(self, records):
        Cluster.__init__(self, records)
        vote = dict()
        count = dict()
        for r in records:
            if r.test != 0: continue
            basic.AddToDict(vote, r.item, r.vote)
            basic.AddToDict(count, r.item, 1)
        k = 0
        for item,v in vote.items():
            ave = v / (count[item]*1.0)
            c = int(ave * 2)
            self.group[item] = c
    
    def GetGroup(self, item):
        if item not in self.group:
            return -1
        else:
            return self.group[item]

def PredictAll(records, user_cluster, item_cluster):
    total = dict()
    count = dict()
    a = 0
    b = 0
    for r in records:
        if r.test != 0: continue
        gu = user_cluster.GetGroup(r.user)
        gi = item_cluster.GetGroup(r.item)
        basic.AddToMat(total, gu, gi, r.vote)
        basic.AddToMat(count, gu, gi, 1)
    for r in records:
        gu = user_cluster.GetGroup(r.user)
        gi = item_cluster.GetGroup(r.item)
        if basic.NotInMat(total, gu, gi) or basic.NotInMat(count, gu, gi):
            if gu not in total: a += 1
            if gi not in total[gu]: b += 1
            r.test = 2
            continue
        try:
            average = total[gu][gi] / (1.0 * count[gu][gi] + 1.0)
            r.predict = average
        except:
            print(gu, gi)
            traceback.print_exc()
    return a, b


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

    train_score = math.sqrt(train) / (1.0 * train_count)
    test_score  = math.sqrt(test) / (1.0 * test_count)
    return train_count, train_score, test_count, test_score
    
class Record:
    def __init__(self, uid, item, vote=0, test=0, predict=0.0):
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
    while True:
        line = f.readline().strip()
        if len(line) == 0: break
        u,m,s,t = line.split('::')
        records.append( Record(u, m, int(s)) )
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

def main():
    # 第一个参数是评分文件，按1/10随机挑选测试集.
    records = LoadData(sys.argv[0])
    print( len(records) )

    SplitData(records, 10, 3, int(time.time()))

    print('================================ Predict ================================')
    PredictAll(records, Cluster(records), Cluster(records))
    print("Clutesr,Cluster", RMSE(records) )
    PredictAll(records, IdCluster(records), Cluster(records))
    print("IdClutesr,Cluster", RMSE(records) )
    PredictAll(records, Cluster(records), IdCluster(records))
    print("Clutesr,IdCluster", RMSE(records) )
    PredictAll(records, UserVoteCluster(records), ItemVoteCluster(records))
    print("UserVoteCluster,ItemVoteCluster", RMSE(records) )



if __name__ == '__main__':
    main()

