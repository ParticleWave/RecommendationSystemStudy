import os

def AddToDict(d, key, cnt):
    if key not in d: d[key] = 0
    d[key] += cnt

def AddToMat(d, key1, key2, cnt):
    if key1 not in d: d[key1] = dict()
    if key2 not in d[key1]: d[key1][key2] = 0
    d[key1][key2] += cnt
    
def NotInMat(d, key1, key2):
    if key1 not in d: return True
    if key2 not in d[key1]: return True
    return False


def main():
    d = dict()
    AddToMat(d, 'a', 1, 10.0)
    AddToMat(d, 'b', 3, 100)
    AddToMat(d, 'b', 3, 200.0)
    AddToMat(d, 'a', 1, 1000)

    print(d['a'][1])
    print(d)
    

if __name__ == '__main__':
    main()
