import os
import sys
import math

'''
item_tags = dict()
item_tags[item_id] = dict()
item_tags[item_id][tag_id] = count   <item_id, tag_id> count times
'''
def CosineSim(item_tags, i, j):
    ret = 0
    for b,wib in item_tags[i].items():
        if b in item_tags[j]:
            ret += wib * item_tags[j][b]
    ni = 0
    nj = 0
    for b,w in item_tags[i].items():
        ni += w * w
    for b,w in item_tags[j].items():
        nj += w * w

    if ret == 0: return 0.0
    return ret / math.sqrt(ni * nj)


def Diversity(item_tags, recommend_items):
    ret = 0
    n = 0
    for i in recommend_items.keys():
        for j in recommend_items.keys():
            if i == j: continue
            ret += CosineSim(item_tags, i, j)
            n += 1
    return ret / (n * 1.0)






'''
一些数据结构的定义:
records[i] = [user, item, tag] 存储标签数据的三元组
user_tags[u][b] = nub    用户u打过标签b的次数
tag_items[b][i] = nbi    物品i被打过标签b的次数
user_items[u][i] = nui   用户u对物品i的打标签个数
'''
class SimpleTagBased:
    def __init__(self):
        self.user_tags = dict()
        self.tag_items = dict()
        self.user_items = dict()
        return
    def addValueToMat(self, data, a, b, cnt):
        if a not in data: data[a] = dict()
        if b not in data[a]: data[a][b] = 0
        data[a][b] += cnt
        
    def InitStat(self, records):
        for user,item,tag in records:
            self.addValueToMat(self.user_tags, user, tag, 1)
            self.addValueToMat(self.tag_items, tag, item, 1)
            self.addValueToMat(self.user_items, user, item, 1)

    def Recommend(self, user):
        recommend_items = dict()
        tagged_items = self.user_items[user]
        for tag, wut in self.user_tags[user].items():
            for item, wti in self.tag_items[tag].items():
                #if items have been tagged, do not recommend them
                if item in tagged_items: continue
                if item not in recommend_items:
                    recommend_items[item] = 0
                recommend_items[item] += wut * wti
        return recommend_items
    
    def PrintStat(self):
        print("user_tags", self.user_tags)
        print("tag_items", self.tag_items)
        print("user_items", self.user_items)
    
def main():
    model = SimpleTagBased()
    records = []
    records.append( ['u1', 'i1', 't1'] )
    records.append( ['u1', 'i1', 't2'] )
    records.append( ['u2', 'i2', 't1'] )
    records.append( ['u2', 'i1', 't3'] )
    model.InitStat(records)
    model.PrintStat() 
    return

if __name__ == '__main__':
    main()
