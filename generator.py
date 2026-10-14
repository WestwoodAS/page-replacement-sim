import random

def gen_random_ref(n=300000, page_range=1500): #產生隨機的page存取序列
    return [random.randint(1, page_range) for _ in range(n)]

def gen_locality_ref(n=300000, page_range=1500, win=40): #集中存取40個連續的page
    seq = []
    while len(seq) < n:
        start = random.randint(1, page_range - win) #先決定一個start
        for _ in range(win * 100):  # 100只是亂選
            if len(seq) >= n:
                break
            seq.append(random.randint(start, start + win)) #區間隨機取page
    return seq

def gen_custom_ref(n=300000, page_range=1500): #週期性存取
    seq = []
    for i in range(n):
        if i % 5000 < 2500: #每5000筆存取分兩階段
            seq.append(random.randint(1, 100))     
        else:
            seq.append(random.randint(1000, 1200)) 
    return seq
