import pandas as pd
from py2neo import Graph,Node,Relationship,NodeMatcher
from collections import defaultdict
import re
import time
import socket

user = 'neo4j'
key = 'root'
graph=Graph("http://localhost:6006/browser/",auth=(user, key))
matcher=NodeMatcher(graph)


def UniqueCode(ks,label):
    def get_key(d, value):
        for k, v in d.items():
            if value in v:
                return k
    bm = pd.read_excel('/workspace/HNCoal/HNCoal/编码方案.xlsx',dtype=str,engine='openpyxl')
    bm = bm.where(bm.notnull(), '')
    gs2ks = {}
    first = bm['公司名称'].to_list()
    first_num = bm['Unnamed: 1'].to_list()
    second = bm['矿山'].to_list()
    second_num = bm['Unnamed: 3'].to_list()
    third = bm['大类'].to_list()
    third_num = bm['Unnamed: 5'].to_list()
    gs2ks['华亭煤业公司'] = second[:10]
    gs2ks['扎赉诺尔煤业公司'] = second[10:14]
    gs2ks['陕西矿业分公司'] = second[14:17]
    gs2ks['北方公司'] = second[17:18]
    gs2ks['庆阳煤电公司'] = second[18:21]
    gs2ks['滇东矿业分公司'] = second[21:]
    gs2id = {}
    ks2id = {}
    lb2id = {}
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
    first_num = [x for x in first_num if x]
    second_num = [x for x in second_num if x]
    third_num = [x for x in third_num if x]
    lb2id['洗选煤']="10"
    gs = get_key(gs2ks, ks)
    bm1_2 = gs2id[gs]
    bm3_4 = ks2id[ks]
    bm5_6 = lb2id[label]
    query = r'MATCH (parent:`矿山` {{name: "{}"}})-[:包含]->(:`设备类型`{{name: "{}"}})-[:包含]->(device:`设备`)RETURN count(device)'.format(ks,ks+label)
    count_result = graph.run(query).data()
    count=int(count_result[0]['count(device)'])+1
    bm7_10="%04d" % count
    
    终极编码=bm1_2+bm3_4+bm5_6+bm7_10
    return 终极编码

def process(file_path,meikuangming):
    # global zrdw_list, sycj_list, sbm_list, jstz_list, sl_list, azdd_list, sccj_list, syrq_list, bz_list, label_list, new_sbm_list, dxsb_list, sbzt_list
    try:
        df=pd.read_excel(file_path,dtype=str,header=2,engine='openpyxl')
    except:
        df=pd.read_excel(file_path,dtype=str,header=2)
        
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
    alias_list=df['设备的全称'].tolist()
    sbxh_list=df['设备型号'].tolist()
    jstz_list=df['技术参数'].tolist()
    sbbm_list = df ['华能设备编码'].astype(str).tolist()
    sbbh_list = df ['内部设备编号'].tolist()
    sl_list=df['数量'].tolist()
    bjsl_list=df['备件数量'].tolist()

    sycj_list=df['使用场景'].tolist()
    dxsb_list=df['是否为大型设备'].tolist()
    sbzt_list=df['设备状态'].tolist()
    sccj_list=df['生产厂家'].tolist()
    syrq_list=df['开始使用日期'].tolist()
    azdd_list=df['存放地点'].tolist()
    
    bz_list=df['备注'].tolist()
    label_list = df ['名称'].tolist()
    #分割 责任单位 责任人
    zr_list=df['责任单位/责任人'].tolist()
    zrdw_list=[i.split('/')[0]  if '/' in i else i for i in zr_list]
    zrdw_list=['未知' if i=='' else i for i in zrdw_list ]
    zrr_list=[i.split('/')[1] if '/' in i else '未知' for i in zr_list ]
    #9大类空值的情况

    for i in range(len(label_list)-1):
        temp = label_list[i]
        if label_list[i+1] == '':
            label_list[i+1] = temp
    label_list=[i[:-2] for i in label_list]
    label_list = ['绿色与节能' if i == '绿色、节能' else i for i in label_list]
    label_list = ['其他' if i == '其他系统机电' else i for i in label_list]
    

    id_list=[]
    for i,label in enumerate(label_list):
        if label:
            query = r'MATCH (parent:矿山 {{name: "{}"}})-[:包含]->(child {{name: "{}"}}) RETURN ID(child)'.format(meikuangming,meikuangming+label)
            id_result = graph.run(query).data()
            if id_result :
        
                id_list.append(id_result[0]['ID(child)'])
            elif label=='白龙山煤矿一井洗选煤':
                query = r'MATCH (node) WHERE node.name = "白龙山煤矿一井洗选煤" RETURN ID(node)'
                id_result = graph.run(query).data()
                id_list.append(id_result[0]['ID(node)'])
                
                

    #说明书值为 名称+型号
    sms_list=[]
    for i in range(len(df)):
        sbmc=df.loc[i]['设备的全称']
        zjxh=df.loc[i]['设备型号']
        sms_list.append(str(zjxh).rstrip(' ')+str(sbmc).lstrip(' ')+"说明书")
    sbm_list=[i[:-3] for i in sms_list]
    sbm_list = [device.replace(" ", "") for device in sbm_list]

    print("数据处理完毕")
    
    for _id,bieming,sbm,sbxh,bjsl,sms,jstz,sl,azdd,sccj,zr,syrq,sycj,bz,label,dxsb,sbzz,sbbm,sbbh in zip(id_list,alias_list,sbm_list,sbxh_list,bjsl_list,sms_list,jstz_list,sl_list,azdd_list,sccj_list,
                                               zr_list,syrq_list,sycj_list,bz_list,label_list,dxsb_list,sbzt_list,sbbm_list,sbbh_list):
        

        node_head=graph.nodes.get(_id)
        node_tail=matcher.match("设备",name=sbm,华能设备编码=sbbm,内部设备编号=sbbh,责任单位与责任人=zr,生产厂家=sccj,所属矿山=meikuangming,使用场景=sycj,安装地点=azdd,技术特征=jstz,).first()
        if node_tail :
            if node_tail['数量'] and node_tail['数量']!="excel里为空":
                try:
                    match = re.match(r'(\d+)(\D+)', str(node_tail['数量']))
                    numbers=str(int(match.group(1))+1)
                    unit=match.group(2)
                    node_tail['数量']=numbers+unit
                except:
                    numbers = re.findall(r'\d+', str(node_tail['数量']))[0]
                    node_tail['数量']=int(numbers)+1
            else:
                node_tail['数量']="excel里为空"
        else:
            终极编码=UniqueCode(meikuangming,label)
            node_tail=Node('设备',name=sbm,UniqueCode=终极编码)
            graph.create(node_tail)
            node_tail=matcher.match("设备",name=sbm,UniqueCode=终极编码).first()
        relationship=Relationship(node_head,'包含',node_tail)
        graph.create(relationship)
        
        node_tail['别名']=bieming
        node_tail['设备型号']=sbxh
        node_tail['说明书']=sms
        node_tail['备件数量']=bjsl
        node_tail['使用场景']=sycj
        node_tail['所属矿山']=meikuangming
        node_tail['技术特征']=jstz
        node_tail['数量']=sl
        node_tail['设备状态']=sbzz
        node_tail['是否为大型设备']=dxsb
        node_tail['华能设备编码']=sbbm
        node_tail['内部设备编号']=sbbh
        node_tail['使用日期']=syrq
        node_tail['备注']=bz
        
        node_tail['责任单位与责任人']=zr

        
        node_tail['安装地点']=azdd
        node_tail['生产厂家']=sccj
        node_tail['导入时间'] = time.strftime('%Y-%m-%d')
        node_tail['导入IP'] = socket.gethostbyname(socket.gethostname())
        node_tail['导入人'] = '华能集团管理员'
        node_tail['数据来源'] = 'excel导入'
        

        
        graph.push(node_tail)
        
    print(meikuangming+"节点入库完毕")


    #安装地点节点与关系 创建
    h_node=matcher.match('矿山',name=meikuangming).first()
    azdd_set=set(azdd_list)
    for azdd in azdd_set:
        azdd_node=matcher.match('地点',name=azdd,所属矿山=meikuangming).first()
        if not azdd_node:
            azdd_node=Node('地点',name=azdd,所属矿山=meikuangming) #创建安装地点节点
            graph.create(azdd_node)
            relationship=Relationship(h_node,'包含',azdd_node) #创建 矿山->安装地点 关系
            graph.create(relationship)
    for sbm,azdd in zip(sbm_list,azdd_list):
        if azdd != '':
            try:
                sbm_node=matcher.match("设备",name=sbm,所属矿山=meikuangming,安装地点=azdd).first()
                azdd_node=matcher.match('地点',name=azdd,所属矿山=meikuangming).first()
                relationship=Relationship(azdd_node,'包含',sbm_node)
                graph.create(relationship)
                relationship=Relationship(sbm_node,'安装地点',azdd_node)
                graph.create(relationship)
            except:
                print(meikuangming,' ',sbm,' ',azdd,'关系创建失败')
    print(meikuangming+"安装地点关系入库完毕")
    
    #责任单位节点与关系 创建
    zrdw_set=set(zrdw_list)
    zrr_set=set(zrr_list)
    for zrdw in zrdw_set:
        zrdw_node=matcher.match('责任单位',name=zrdw,所属矿山=meikuangming).first()
        if not zrdw_node:
            zrdw_node=Node('责任单位',name=zrdw,所属矿山=meikuangming) #创建责任单位节点
            graph.create(zrdw_node)
            relationship=Relationship(h_node,'包含',zrdw_node) #创建 矿山->责任单位 关系
            graph.create(relationship)
    for zrr in zrr_set:
        zrr_node=matcher.match('员工',name=zrr,所属矿山=meikuangming).first()
        if not zrr_node:
            zrr_node=Node('员工',name=zrr,所属矿山=meikuangming) #创建员工节点
            graph.create(zrr_node)
    
    for sbm,zrdw,zrr,zr in zip(sbm_list,zrdw_list,zrr_list,zr_list):
        if sbm!='' and zrr!='':
            try:
                sbm_node=matcher.match("设备",name=sbm,所属矿山=meikuangming,责任单位与责任人=zr).first()
                zrdw_node=matcher.match('责任单位',name=zrdw,所属矿山=meikuangming).first()
                zrr_node=matcher.match('员工',name=zrr,所属矿山=meikuangming).first()
                relationship=Relationship(zrdw_node,'包含',zrr_node) #创建 责任单位->责任人 关系
                graph.create(relationship)
                relationship=Relationship(zrr_node,'属于',zrdw_node) #创建 责任人->责任单位 关系
                graph.create(relationship)
                relationship=Relationship(zrr_node,'负责',sbm_node) #创建 责任人->设备 关系
                graph.create(relationship)
                relationship=Relationship(sbm_node,'责任人',zrr_node) #创建 设备>责任人 关系
                graph.create(relationship)
                relationship=Relationship(zrdw_node,'负责',sbm_node) #创建 责任单位->设备 关系
                graph.create(relationship)
                relationship=Relationship(sbm_node,'属于',zrdw_node) #创建 设备>责任单位 关系
                graph.create(relationship)
            except:
                print(meikuangming,' ',sbm,' ',zrdw,' ',zrr,'关系创建失败')
            
            # print(meikuangming,'-----',sbm,zrdw,'未创建关系')
    print(meikuangming+"责任单位关系入库完毕")


    #生产厂家节点与关系 创建
    sccj_set=set(sccj_list)

    for sccj in sccj_set:
        d_node=matcher.match('企业',name=sccj).first()
        if not d_node:
            d_node=Node('企业',name=sccj)
            graph.create(d_node)


    for sbm,sccj in zip(sbm_list,sccj_list):
        if sccj != '':
            try:
                sbm_node=matcher.match("设备",name=sbm,所属矿山=meikuangming,生产厂家=sccj).first()
                sccj_node=matcher.match('企业',name=sccj).first()
                relationship=Relationship(sccj_node,'制造',sbm_node)
                graph.create(relationship)
                relationship=Relationship(sbm_node,'生产厂家',sccj_node)
                graph.create(relationship)
            except:
                print(meikuangming,' ',sbm,' ',sccj,'关系创建失败')
    print(meikuangming+"生产厂家关系入库完毕")

#已入
# process("./semi-structured/附件2.华能煤炭产业井工煤矿机电设备知识库数据调查表（赤城煤矿公司）.xls",'赤城煤矿公司') 
# process("./semi-structured/青岗坪煤矿.xlsx",'青岗坪煤矿') 
# process("./semi-structured/铁北煤矿.xlsx",'铁北煤矿') 
# process("./semi-structured/西川煤矿.xlsx",'西川煤矿') 
# process("./semi-structured/灵露煤矿.xlsx",'灵露煤矿') 
# process("/workspace/煤矿/semi-structured/附件2.华能煤炭产业井工煤矿机电设备知识库数据调查表(新窑煤矿).xls",'新窑煤矿') 
# process("/workspace/煤矿/semi-structured/附件2.华能煤炭产业井工煤矿机电设备知识库数据调查表-华亭煤矿.xls",'华亭煤矿') 
# process("/workspace/煤矿/semi-structured/华能煤炭产业井工煤矿机电设备知识库数据调查表(高头窑煤矿).xls",'高头窑煤矿') 
# process("/workspace/煤矿/semi-structured/山寨煤矿-华能煤炭产业井工煤矿机电设备知识库数据调查表.xls",'山寨煤矿') 
# process("/workspace/煤矿/semi-structured/陕西矿业分公司煤矿机电设备知识库数据调查表柳巷煤矿.xls",'柳巷煤矿')
# process("/workspace/煤矿/semi-structured/华能煤炭产业井工煤矿机电设备知识库数据调查表(灵泉煤矿).xls",'灵泉煤矿') 
# process("/workspace/煤矿/semi-structured/华能煤炭产业井工煤矿机电设备知识库数据调查表(华能滇东矿业分公司雨汪煤矿一井)(1).xls",'雨汪煤矿一井') 
# process("/workspace/煤矿/semi-structured/华能煤炭产业井工煤矿机电设备知识库数据调查表(核桃峪).xls",'核桃峪煤矿') 
# process("/workspace/煤矿/semi-structured/附件2.华能煤炭产业井工煤矿机电设备知识库数据调查表(砚北煤矿）.xls",'砚北煤矿') 
# process("/workspace/煤矿/semi-structured/附件2.华能煤炭产业井工煤矿机电设备知识库数据调查表（新柏煤矿）.xls",'新柏煤矿') 
# process("/workspace/煤矿/semi-structured/附件2.华能煤炭产业井工煤矿机电设备知识库数据调查表(大柳煤矿).xls",'大柳煤矿') 
# process("/workspace/煤矿/semi-structured/附件2.华能煤炭产业井工煤矿机电设备知识库数据调查表(陈家沟煤矿).xls",'陈家沟煤矿') 
# process("/workspace/煤矿/semi-structured/（汇总版）华能煤炭产业井工煤矿机电设备知识库数据调查表--灵东煤矿.xls",'灵东煤矿') 
# process("/workspace/煤矿/semi-structured/附件2.华能煤炭产业井工煤矿机电设备知识库数据调查表（东峡煤矿）.xlsx",'东峡煤矿') 
# process("/workspace/煤矿/semi-structured/附件2.华能煤炭产业井工煤矿机电设备知识库数据调查表(马蹄沟煤矿）.xls",'马蹄沟煤矿') 
# process("/workspace/煤矿/semi-structured/华能煤炭产业井工煤矿机电设备知识库数据调查表(华能滇东矿业分公司白龙山煤矿一井2023-1-13).xls",'白龙山煤矿一井') 


#未入

