import pandas as pd
from py2neo import Graph,Node,Relationship,NodeMatcher
from collections import defaultdict
import re

def init(g):
    global graph
    global matcher
    graph=g
    matcher=NodeMatcher(g)
    
# def date(para):
#     if type(para) == int:
#         delta = pd.Timedelta(str(int(para))+'days')
#         time = pd.to_datetime('1899-12-30') + delta
#         return time
#     else:
#         return para
#数据处理一下
def process(file_path,meikuangming):
    global zrdw_list, sycj_list, sbm_list, jstz_list, sl_list, azdd_list, sccj_list, syrq_list, bz_list, label_list, new_sbm_list, dxsb_list, sbzt_list
    df=pd.read_excel(file_path,header=2)
    df.dropna(subset=['设备型号'],
                axis=0, # axis=0表示删除行；
                inplace=True # inplace=True表示在原df上进行修改；
                )
    df = df.reset_index(drop=True)
    # df['使用日期'] = df['使用日期'].apply(date)
    # df['使用日期'] = pd.to_datetime(df['使用日期'].astype(str),dayfirst=True, errors='coerce')
    df = df.where(df.notnull(), '')
    df = df.replace('\n','', regex=True)
    df.rename(columns={"设备状态\n（在用/备用/待报废）": "设备状态", "安装/存放地点（含备件）": "存放地点"}, inplace=True)
    for i in range(len(df)):
        sbmc=df.loc[i]['设备的全称']
        zjxh=df.loc[i]['设备型号']
        df.loc[i,'设备名']=str(zjxh)+str(sbmc)
    sccj_list=df['生产厂家'].tolist()
    sbm_list=df['设备名'].tolist()
    jstz_list=df['技术参数'].tolist()
    sl_list=df['数量'].tolist()
    azdd_list=df['存放地点'].tolist()
    zrdw_list=df['责任单位/责任人'].tolist()
    syrq_list=df['开始使用日期'].tolist()
    sycj_list=df['使用场景'].tolist()
    dxsb_list=df['是否为大型设备'].tolist()
    bz_list=df['备注'].tolist()
    sbzt_list=df['设备状态'].tolist()
    label_list = df ['名称'].tolist()
    
    #处理公司名称中同一单位却是空值的情况
    for i in range(len(label_list)-1):
        temp = label_list[i]
        if label_list[i+1] == '':
            label_list[i+1] = temp
            
    #处理煤矿名称中同一单位却是空值的情况
    # for i in range(len(mkmc_list)-1):
    #     temp = mkmc_list[i]
    #     if mkmc_list[i+1] == '':
    #         mkmc_list[i+1] = temp
            
    # #处理煤矿名称中去除非中文部分
    # for i,item in enumerate(mkmc_list):
    #     item = re.sub('[^\u4e00-\u9fa5]+', '', item)
    #     mkmc_list[i] = item
        
    #处理相同型号姓名设备的情况，添加-1，-2，-3......等
    new_sbm_list=[]
    sbm_count={}
    for sb in sbm_list:
        if sb not in sbm_count:
            sbm_count[sb] = 1
            new_sbm_list.append(sb)
        else:
            if sbm_count[sb]==1:
                i=new_sbm_list.index(sb)
                new_sbm_list[i]+='-1'
                sbm_count[sb]+=1
            else:
                sbm_count[sb]+=1
            new_sbm_list.append(sb+'-'+str(sbm_count[sb]))
    print(len(new_sbm_list),len(sccj_list),len(azdd_list))
    print(new_sbm_list[0],sccj_list[0],azdd_list[0])
    print("数据处理完毕")
    for sbm,jstz,sl,azdd,sccj,zrdw,syrq,sycj,bz,label,dxsb,sbzz in zip(new_sbm_list,jstz_list,sl_list,azdd_list,sccj_list,
                                               zrdw_list,syrq_list,sycj_list,bz_list,label_list,dxsb_list,sbzt_list):

        node_head=matcher.match(name=label).first()
        if not node_head:
            node_head=Node(label,name=label)
            graph.create(node_head)
        node_tail=matcher.match(label,name=sbm,所属矿山=meikuangming)
        if not node_tail:
            node_tail=Node(label,name=sbm)
            graph.create(node_tail)

        relationship=Relationship(node_head,'包含',node_tail)
        graph.create(relationship)

        node_tail['使用场景']=str(sycj)
        node_tail['所属矿山']=meikuangming
        node_tail['技术特征']=str(jstz)
        node_tail['数量']=str(sl)
        node_tail['安装地点']=str(azdd)
        node_tail['生产厂家']=str(sccj)
        node_tail['使用日期']=str(syrq)
        node_tail['备注']=str(bz)
        node_tail['责任单位/责任人']=str(zrdw)
        node_tail['设备状态']=str(sbzz)
        node_tail['是否为大型设备']=str(dxsb)
        graph.push(node_tail)
    print(meikuangming+"节点入库完毕")

    h_node=matcher.match('矿山',name='矿山').first()
    t_node=matcher.match('矿山',name=meikuangming).first()
    if not t_node:
        t_node=Node('矿山',name=meikuangming)
        relationship=Relationship(h_node,'包含',t_node)
        graph.create(relationship)
    for sbm in new_sbm_list:
        sbm_node=matcher.match(name=sbm,所属矿山=meikuangming).first()
        mkmc_node=matcher.match(name=meikuangming).first()
        relationship=Relationship(mkmc_node,'所属设备',sbm_node)
        graph.create(relationship)
        relationship=Relationship(sbm_node,'所属矿山',mkmc_node)
        graph.create(relationship)
    print(meikuangming+"所属矿山关系入库完毕")


    h_node=matcher.match('地名',name='地名').first()
    azdd_set=set(azdd_list)
    for item in azdd_set:
        t_node=matcher.match('地名',name=item).first()
        if not t_node:
            t_node=Node('地名',name=item)
            relationship=Relationship(h_node,'包含',t_node)
            graph.create(relationship)
    for sbm,azdd in zip(new_sbm_list,azdd_list):
        if azdd != '':
            sbm_node=matcher.match(name=sbm,所属矿山=meikuangming).first()
            azdd_node=matcher.match(name=azdd).first()
            relationship=Relationship(azdd_node,'所含设备',sbm_node)
            graph.create(relationship)
            relationship=Relationship(sbm_node,'安装地点',azdd_node)
            graph.create(relationship)
    print(meikuangming+"安装地点关系入库完毕")

    h_node=matcher.match('企业',name='企业').first()
    sccj_set=set(sccj_list)
    for item in sccj_set:
        t_node=matcher.match('企业',name=item).first()
        if not t_node:
            t_node=Node('企业',name=item)
            relationship=Relationship(h_node,'包含',t_node)
            graph.create(relationship)
    for sbm,sccj in zip(new_sbm_list,sccj_list):
        if sccj != '':
            sbm_node=matcher.match(name=sbm,所属矿山=meikuangming).first()
            if not sbm_node:
                continue
            sccj_node=matcher.match(name=sccj).first()
            relationship=Relationship(sccj_node,'制造',sbm_node)
            graph.create(relationship)
            relationship=Relationship(sbm_node,'生产厂家',sccj_node)
            graph.create(relationship)
    print(meikuangming+"生产厂家关系入库完毕")


#删除撤销
# def delete():
#     for item in new_sbm_list:
#         node = matcher.match(name=item).first()
#         graph.delete(node)





# 看看撤销怎么根据前端接起来，前端那边要撤销就执行删除。
# if delete_tag:
#     delete()
def get_key(d, value):
    for k, v in d.items():
        if value in v:
            return k
def process_code():
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