import pandas as pd
from py2neo import Graph,Node,Relationship,NodeMatcher
from collections import defaultdict
def get_key(d, value):
    for k, v in d.items():
        if value in v:
            return k
graph=Graph("http://211.82.97.250:7606",username="neo4j",password="neo4j")
matcher = NodeMatcher(graph)

bm = pd.read_excel('编码方案.xlsx',engine='openpyxl')
bm = bm.where(bm.notnull(), '')
gs2ks = {}
first = bm['公司名称'].to_list()
first_num = bm['Unnamed: 1'].to_list()
second = bm['矿山'].to_list()
second_num = bm['Unnamed: 3'].to_list()
third = bm['大类'].to_list()
third_num = bm['Unnamed: 5'].to_list()
gs2ks['华亭煤业公司'] = second[:10]
gs2ks['扎贵诺尔煤业公司'] = second[10:14]
gs2ks['陕西矿业分公司'] = second[14:17]
gs2ks['北方公司'] = second[17:18]
gs2ks['庆阳煤电公司'] = second[18:21]
gs2ks['滇东矿业分公司'] = second[21:]
gs2id = {}
ks2id = {}
lb2id = {}
third.append('`绿色、节能设备`')
lb2id['`绿色、节能设备`'] = '08'
for i,j in zip(first, first_num):
    if i:
        gs2id[i] = '0'+str(int(j))
for i,j in zip(second, second_num):
    if i:
        if len(str(int(j))) == 1:
            ks2id[i] = '0'+str(int(j))
        else:
            ks2id[i] = str(int(j))
for i,j in zip(third, third_num):
    if i:
        if len(str(int(j))) == 1:
            lb2id[i] = '0'+str(int(j))
        else:
            lb2id[i] = str(int(j))
first = [x for x in first if x]
second = [x for x in second if x]
third = [x for x in third if x]


for lmcsg in third:
    count = 1
    results = matcher.match(lmcsg).all()
    
    print(len(results))
    for node in results:
        if len(node.keys()) > 2:
            name = node["name"]
            label = node.labels

            if str(label)[1:] in third:
                ks = node['所属矿山']
                if ks in second:
                    gs = get_key(gs2ks, ks)
                    bm1_2 = gs2id[gs]
                    bm3_4 = ks2id[ks]
                    bm5_6 = lb2id[str(label)[1:]]
                    bm7_10="%04d" % count
                    count+=1
                    终极编码=bm1_2+bm3_4+bm5_6+bm7_10
                    node['UniqueCode']=终极编码
                    graph.push(node)
                    print(终极编码)
                else:
                    print(ks)