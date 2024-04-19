import numpy as np
import pandas as pd
from py2neo import Node,Relationship,Graph,Path,Subgraph
from py2neo import NodeMatcher,RelationshipMatcher
import json
from JosnData import JsonData
import time
neo4j_url='bolt://211.82.97.250:7688'
user='neo4j'
password='neo4j'
graph=Graph(neo4j_url,auth=(user,password))
search_name = '采煤机'
coal_name = '华亭煤矿'
#sql=("MATCH (f)-[r]-(t) where f.name='%s' RETURN  f,ID(f) as idf,type(r) as r,ID(t) as idt,t")%(name)
#sql=("MATCH (f)-[r]->(t) where f.name=~'.*%s.*' RETURN f,r,type(r) as rname,t")%(name)

# sql = ("MATCH (f)-[r]->(t) where (f.name contains '%s' and ID(f) < 2581 and ID(t)<2581 ) RETURN f,r,type(r) as rname,t,labels(f),labels(t)")%(search_name)
# #sql = ("MATCH (f)-[r]-(t) where (f.name contains '%s' ) and (f.UniqueCode is Null or f.所属矿山='%s') and (ID(f) < 2581 and ID(t)<2581 ) and (t.UniqueCode is Null or t.所属矿山='%s')  RETURN f,r,type(r) as rname,t,labels(f),labels(t)")%(search_name,coal_name,coal_name)

# print(sql)


# data=graph.run(sql).data()

# f_set = set()
# t_set = set()
# node=[]
# relationship=[]
# for d in data:  
#    if d['f'] not in f_set:#首次出现
#       f_set.add(d['f'])
#       start_node = { 
#             'id' : d['f'].identity,
#             'label' : d['f']['name'],  
#             'pid' : [],
#             'subids' : [],
#             'properites' : {
#                 'UniqueCode' : d['f']['UniqueCode'],               
#                 '使用场景' : d['f']['使用场景'] ,
#                 '使用日期' : d['f']['使用日期'],
#                 '内部设备编号' : d['f']['内部设备编号'],
#                 '华能设备编码' : d['f']['华能设备编码'],
#                 '备注' : d['f']['备注'],
#                 '安装地点' :d['f']['安装地点'],
#                 '所属矿山' : d['f']['所属矿山'],
#                 '技术特征' : d['f']['技术特征'],
#                 '数量' : d['f']['数量'],
#                 '是否为大型设备' : d['f']['是否为大型设备'],
#                 '生产厂家' :  d['f']['生产厂家'],
#                 '设备状态' : d['f']['设备状态'],
#                 '责任单位/责任人' : d['f']['责任单位/责任人'],         
#                 }
#       }  
#       # 保存节点间的关系
#       _from = d['f'].identity
#       _relationshipid =d['r'].identity
#       _to = d['t'].identity
#       _title = d['rname']
      
#       dict_relationship = {
#          'id' : _relationshipid,
#          'from' : _from,
#          'to' : _to,
#          'title' : _title
#       }
#       relationship.append(dict_relationship)
#       if d['t'] not in t_set and d['t'] not in f_set:
        
#          # t节点去重复
#          t_set.add(d['t'])
#          end_node={ 
#                'id' : d['t'].identity,
#                'label' : d['t']['name'],  
#                'pid' : d['f'].identity,
#                'subids' : [],
#                'properites' : {
#                         'UniqueCode' : d['t']['UniqueCode'] ,               
#                         '使用场景' : d['t']['使用场景'],
#                         '使用日期' : d['t']['使用日期'],
#                         '内部设备编号' : d['t']['内部设备编号'],
#                         '华能设备编码' : d['t']['华能设备编码'],
#                         '备注' : d['t']['备注'],
#                         '安装地点' :d['t']['安装地点'],
#                         '所属矿山' : d['t']['所属矿山'],
#                         '技术特征' : d['t']['技术特征'],
#                         '数量' : d['t']['数量'],
#                         '是否为大型设备' : d['t']['是否为大型设备'],
#                         '生产厂家' : d['t']['生产厂家'],
#                         '设备状态' : d['t']['设备状态'],
#                         '责任单位/责任人' : d['t']['责任单位/责任人'] ,
#                      }
#             }  
#          start_node['subids'].append(d['t'].identity)
#          node.append(end_node)
#       node.append(start_node) 
      
#    else: # f节点出现过但是叶子结点未出现
#       # 保存节点间的关系
#       _from = d['f'].identity
#       _relationshipid =d['r'].identity
#       _to = d['t'].identity
#       _title = d['rname']
      
#       dict_relationship = {
#          'id' : _relationshipid,
#          'from' : _from,
#          'to' : _to,
#          'title' : _title
#       }
#       relationship.append(dict_relationship)
#       if d['t'] not in t_set and d['t'] not in f_set:
       
#          # t节点去重复
#          t_set.add(d['t'])
#          end_node={ 
#                'id' : d['t'].identity,
#                'label' : d['t']['name'],  
#                'pid' : d['f'].identity,
#                'subids' : [],
#                'properites' : {
#                         'UniqueCode' : d['t']['UniqueCode'] ,               
#                         '使用场景' : d['t']['使用场景'],
#                         '使用日期' : d['t']['使用日期'],
#                         '内部设备编号' : d['t']['内部设备编号'],
#                         '华能设备编码' : d['t']['华能设备编码'],
#                         '备注' : d['t']['备注'],
#                         '安装地点' :d['t']['安装地点'],
#                         '所属矿山' : d['t']['所属矿山'],
#                         '技术特征' : d['t']['技术特征'],
#                         '数量' : d['t']['数量'],
#                         '是否为大型设备' : d['t']['是否为大型设备'],
#                         '生产厂家' : d['t']['生产厂家'],
#                         '设备状态' : d['t']['设备状态'],
#                         '责任单位/责任人' : d['t']['责任单位/责任人'] ,
#                      }
#             }  
#          start_node['subids'].append(d['t'].identity)
#          node.append(end_node)
    
# node.sort(key=lambda k: (k.get('id', 0)))

# for d in relationship:
#    print(d)
  

# print(len(node))
# print(len(relationship))

import yaml
import os
import urllib3
from django.http import FileResponse
# with open('/workspace/HNCoal/ instructions.yml','r',encoding='utf-8') as f:
#    result = yaml.load(f.read(), Loader=yaml.FullLoader)
# print(result['BRW500/37.乳化液泵站'])

# root_directory = "/workspace/HNCoal/EquipmentManualFile/"

# download_file_name = result['BRW500/37.乳化液泵站']
# file_path = root_directory+download_file_name
# file = open(file_path, 'rb')
# response = FileResponse(file,as_attachment=True)
# response['Content-Type'] = 'application/octet-stream'
# response['Content-Disposition'] = 'attachment;filename="test.xlsx"'
import uuid
import time

# 获取当前时间戳（秒级）
timestamp = time.time()
print(timestamp)
# 生成UUID
file_prefix = str(uuid.uuid4())

# 使用UUID作为文件前缀
file_name = file_prefix 

# 打印文件名
print(file_name)


if __name__ == "__main__":
   pass