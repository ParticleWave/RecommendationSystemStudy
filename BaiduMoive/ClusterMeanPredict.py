import os
import basic
from   operator import itemgetter
import math
import random
import time
import traceback

'''
对用户/电影, 用naive的办法进行分类，用对应分类的均值，作为预测结果.
最优秀的是<UserVote, ItemVote>组合，RMSE到0.68
'''

#基类, 也即全局平均值.
class Cluster:
    def __init__(self, records):
        self.group = dict()

    def GetGroup(self, i):
        return 0

#按ID, 也就是用户或电影的平均值
class IdCluster(Cluster):
    def __init__(self, records):
        Cluster.__init__(self, records)

    def GetGroup(self, i):
        return i

#对用户按打分的电影数量，从小到大进行平均分成N类
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

#对电影按被打分的数量，从小到大进行平均分成N类
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

#按用户打分的平均分，分成N类
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

#按电影得分的平均分，分成N类
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


def Train(records, user_cluster, item_cluster):
    total = dict()
    count = dict()
    model = dict()
    for r in records:
        if r.test != 0: continue  #测试数据
        gu = user_cluster.GetGroup(r.user)
        gi = item_cluster.GetGroup(r.item)
        basic.AddToMat(total, gu, gi, r.vote)
        basic.AddToMat(count, gu, gi, 1)
    for gu in total.keys():
        for gi in total[gu].keys():
            basic.AddToMat(model, gu, gi, total[gu][gi] / (1.0 * count[gu][gi] + 1.0))
    return model

def Predict(test_data, model, user_cluster, item_cluster):
    for r in test_data:
        gu = user_cluster.GetGroup(r.user)
        gi = item_cluster.GetGroup(r.item)
        if basic.NotInMat(model, gu, gi):
            r.predict = 2.5
        else:
            r.predict = model[gu][gi]
    return

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

    SplitData(records, 10, 3, int(time.time()))
    model = Train(records, UserVoteCluster(records), ItemVoteCluster(records))
    print('================================ Predict ================================')
    Predict(records, model, UserVoteCluster(records), ItemVoteCluster(records))
    print(RMSE(records) )
    

    test_data = LoadData("./data-v/predict.txt")
    print( len(test_data) )
    Predict(test_data, model, UserVoteCluster(records), ItemVoteCluster(records))
    print("Predict Done")
    DumpData(test_data, "./data-v/predict_data.txt")


if __name__ == '__main__':
    main()
