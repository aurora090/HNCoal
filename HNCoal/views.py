from django.http import HttpResponse,FileResponse
import json
import uuid
import numpy as np
import pandas as pd
from py2neo import Node,Relationship,Graph,Path,Subgraph
from py2neo import NodeMatcher,RelationshipMatcher
import time
from datetime import datetime,timedelta
from time import sleep
import os
from django.shortcuts import render
# from .upload import process,init,process_code
from .importCoal import process
import re
import random
import requests
# 操作excel文件
from openpyxl import Workbook
from openpyxl.styles import Alignment
from openpyxl.utils import get_column_letter
from io import BytesIO  
import yaml
import os
from django.http import HttpResponse, Http404, FileResponse
from django.http import JsonResponse
# from task_two import re_spo
neo4j_url='bolt://localhost:8888'
user='neo4j'
password='neo4j'
graph=Graph(neo4j_url,auth=(user,password))

company_dic = {'华亭煤业公司':'01','庆阳煤电公司':'05','滇东矿业分公司':'06','陕西矿业分公司':'03','扎赉诺尔煤业公司':'02','北方公司':'04'}
work_scenarios = {
             '采煤工作面':'01',
             '掘进工作面':'02',
             '主煤流运输':'03',
             '辅助运输':'04',
             '通风与压风':'05',
             '供电与给排水':'06',
             '安全监控':'07',
             '绿色与节能':'08',
             '其他':'09'}
# 判断文件
tooken={
    "status":int,
}

#下载说明书
# def downloadInstructions(request):
#     if request.method=='POST':
#         postbody = request.body
#         param = json.loads(postbody.decode(),encoding='utf-8')
#         fileName = param['node_name']

#         # 得到文件名，去yml文件中读取文件路径
#         with open('/workspace/HNCoal/instructions.yml','r',encoding='utf-8') as f:
#                result = yaml.load(f.read(), Loader=yaml.FullLoader)            

#         try:
#             orinal_name = result[fileName]
#             file_path = '/workspace/HNCoal/EquipmentManualFile/' + orinal_name 
#             response = FileResponse(open(file_path, 'rb'))
#             response['content_type'] = "application/octet-stream"
#             response['Content-Disposition'] = 'attachment; filename=' + os.path.basename(file_path)
#             return response
#         except Exception:
#             tooken['status']=11000
#             return HttpResponse(json.dumps(tooken,ensure_ascii=False))

# 说明书下载
def downloadInstructions(request):
    if request.method == 'POST':
        postbody = request.body
        param = json.loads(postbody.decode(), encoding='utf-8')
        print('parm:',param)
        # node_Name = param['node_name'] # 设备名称
        # coal_Name = param['kuangshan'] # 所属矿山
        # # print("node_name: "+ node_Name,"coal_name: " + coal_Name)
        # # 读取yaml文件中的文件路径
        # with open('data/说明书/数据文件/'+coal_Name+'.yaml', 'r', encoding='utf-8') as f:
        #     result = yaml.load(f.read(), Loader=yaml.FullLoader)
        try:
            node_Name = param['node_name'] # 设备名称
            coal_Name = param['kuangshan'] # 所属矿山
            # print("node_name: "+ node_Name,"coal_name: " + coal_Name)
            # 读取yaml文件中的文件路径
            with open('data/说明书/数据文件/'+coal_Name+'.yaml', 'r', encoding='utf-8') as f:
                result = yaml.load(f.read(), Loader=yaml.FullLoader)
            original_name = result.get(node_Name, "default_file_name.ext")  # 提供默认文件名,节点名对应的文件名
            file_path = 'data/说明书/说明书备份/'+coal_Name+'/' + original_name  # 拼接文件路径
            file_name, file_extension = os.path.splitext(file_path)
            # print(file_name)
            # print(file_extension)
            # print(file_name,file_extension)
            if os.path.exists(file_path):
                response = FileResponse(open(file_path, 'rb'),as_attachment=True)
                response['Content-Type'] = 'application/octet-stream'
                response['Content-Disposition'] = 'attachment; filename="temp{}"'.format(file_extension)
                # print(response['Content-Disposition'])
                print(response)
                response['Access-Control-Expose-Headers'] = 'Content-Disposition'
                return response
            else:
                print(JsonResponse({"status": "该节点无说明书"}, json_dumps_params={'ensure_ascii':False}, charset='utf-8')
)
                return JsonResponse({"status": "该节点无说明书"}, json_dumps_params={'ensure_ascii':False}, charset='utf-8')

        except:
            print(JsonResponse({"status": "该节点无说明书"}, json_dumps_params={'ensure_ascii':False}, charset='utf-8')
) 
            print("出现异常")
            return JsonResponse({"status": "该节点无说明书"}, json_dumps_params={'ensure_ascii':False}, charset='utf-8')


def downloadInstructions_back(request):
    if request.method == 'POST':
        postbody = request.body
        param = json.loads(postbody.decode(), encoding='utf-8')
        fileName = param['node_name']
        
        # 读取yml文件中的文件路径
        with open('/workspace/HNCoal/instructions.yml', 'r', encoding='utf-8') as f:
            result = yaml.load(f.read(), Loader=yaml.FullLoader)

        try:
            original_name = result.get(fileName, "default_file_name.ext")  # 提供默认文件名
            file_path = '/workspace/HNCoal/EquipmentManualFile/' + original_name

            if os.path.exists(file_path):
                response = FileResponse(open(file_path, 'rb'))
                response['Content-Type'] = 'application/octet-stream'
                response['Content-Disposition'] = f'attachment; filename="{os.path.basename(file_path)}"'
                return response
            else:
                return JsonResponse({"error": "File not found."}, status=404)

        except KeyError:
            return JsonResponse({"error": "File name not found in YAML."}, status=400)



#定时检查进行设备预警

def DeviceAlerts(request):  
  if request.method=='POST':
     sql="match (n) where  n.`开始使用日期` is not null return n"    
     data=graph.run(sql).data()
     cur_time=time.strftime('%Y', time.localtime())
     
     ans=[]
     for d in data:
        _time=d['n']['开始使用日期']
        t=_time.split(".")
        if len(t)>1 and int(cur_time)-int(t[0])>10:#使用时长大于十年的预警推送
            ans.append(d)
     return HttpResponse(json.dumps(ans,ensure_ascii=False))

        
#节点按照公司下的矿山分类
def classifyNode(request):
    if request.method == 'POST':
        postbody = request.body
        param = json.loads(postbody.decode(),encoding='utf-8')
        #接收前端发送的数据进行分类(统一按照)
        scene_name=param['scene_name']
        if '绿色' in scene_name:
            scene_name='绿色与节能'
        elif '其他' in scene_name:
            scene_name='其他'

        coal_name = param['coal_name']
        
        if coal_name == '华能集团' or coal_name == '华能煤业公司': #总公司   
            sql = ("MATCH (f)-[r]->(t) where f.name contains '%s' and (labels(f) = %s) RETURN f,r,type(r) as rname,t,labels(f),labels(t)")%(scene_name,['设备类型'])    
        elif coal_name in company_dic.keys():#其他公司   只能展示出有设备的 设备类型，没有的不展示
            sql = ("MATCH (f)-[r]->(t) where   f.name contains '%s' and (labels(f) = %s) and t.UniqueCode=~ '%s..%s.*'  RETURN f,r,type(r) as rname,t,labels(f),labels(t)")%(scene_name,['设备类型'],company_dic[coal_name],work_scenarios[scene_name])
        else :#矿山
            # sql = ("MATCH (f)-[r]->(t) where  f.name contains '%s'  and (t.UniqueCode is Null or t.所属矿山='%s')  RETURN f,r,type(r) as rname,t,labels(f),labels(t)")%(scene_name,coal_name)
            # 10/21修改，避免出现华亭的采煤工作面结果
            sql = ("MATCH (f)-[r]->(t) where  f.name contains '%s'  and (t.所属矿山='%s')  RETURN f,r,type(r) as rname,t,labels(f),labels(t)")%(scene_name,coal_name)
   


        print(sql)  

        data=graph.run(sql).data() 

        f_set = set()
        t_set = set()
        rootId = random.randint(10000,11000)
        node=[]
        relationship=[]
        for d in data:  
            
            if d['f'] not in f_set:#首次出现
                f_set.add(d['f'])
                start_node = { 
                        'id' : d['f'].identity,
                        'label' : d['f']['name'],  
                        'pid' : rootId,
                        'subids' : [],
                        'properites' : {
                            'UniqueCode' : d['f']['UniqueCode'],               
                            '使用场景' : d['f']['使用场景'] ,
                            '使用日期' : d['f']['使用日期'],
                            '内部设备编号' : d['f']['内部设备编号'],
                            '华能设备编码' : d['f']['华能设备编码'],
                            '备注' : d['f']['备注'],
                            '安装地点' :d['f']['安装地点'],
                            '所属矿山' : d['f']['所属矿山'],
                            '技术特征' : d['f']['技术特征'],
                            '数量' : d['f']['数量'],
                            '是否为大型设备' : d['f']['是否为大型设备'],
                            '生产厂家' :  d['f']['生产厂家'],
                            '设备状态' : d['f']['设备状态'],
                            '责任单位/责任人' : d['f']['责任单位/责任人'],         
                            }
                }  
                # 保存节点间的关系
                _from = d['f'].identity
                _relationshipid =d['r'].identity
                _to = d['t'].identity
                _title = d['rname']
                
                dict_relationship = {
                    'id' : _relationshipid,
                    'from' : _from,
                    'to' : _to,
                    'label' : _title,
                    'title' : _title
                }
                relationship.append(dict_relationship)
                if d['t'] not in t_set and d['t'] not in f_set:
                
                    # t节点去重复
                    t_set.add(d['t'])
                    end_node={ 
                        'id' : d['t'].identity,
                        'label' : d['t']['name'],  
                        'pid' : d['f'].identity,
                        'subids' : [],
                        'properites' : {
                                    'UniqueCode' : d['t']['UniqueCode'] ,               
                                    '使用场景' : d['t']['使用场景'],
                                    '使用日期' : d['t']['使用日期'],
                                    '内部设备编号' : d['t']['内部设备编号'],
                                    '华能设备编码' : d['t']['华能设备编码'],
                                    '备注' : d['t']['备注'],
                                    '安装地点' :d['t']['安装地点'],
                                    '所属矿山' : d['t']['所属矿山'],
                                    '技术特征' : d['t']['技术特征'],
                                    '数量' : d['t']['数量'],
                                    '是否为大型设备' : d['t']['是否为大型设备'],
                                    '生产厂家' : d['t']['生产厂家'],
                                    '设备状态' : d['t']['设备状态'],
                                    '责任单位/责任人' : d['t']['责任单位/责任人'] ,
                                }
                        }  
                    start_node['subids'].append(d['t'].identity)
                    node.append(end_node)
                node.append(start_node) 
                
            else: # f节点出现过但是叶子结点未出现
                    # 保存节点间的关系
                _from = d['f'].identity
                _relationshipid =d['r'].identity
                _to = d['t'].identity
                _title = d['rname']
                
                dict_relationship = {
                    'id' : _relationshipid,
                    'from' : _from,
                    'to' : _to,
                    'label' : _title,
                    'title' : _title
                }
                relationship.append(dict_relationship)
                if d['t'] not in t_set and d['t'] not in f_set:
               
                    # t节点去重复
                    t_set.add(d['t'])
                    end_node={ 
                        'id' : d['t'].identity,
                        'label' : d['t']['name'],  
                        'pid' : d['f'].identity,
                        'subids' : [],
                        'properites' : {
                                    'UniqueCode' : d['t']['UniqueCode'] ,               
                                    '使用场景' : d['t']['使用场景'],
                                    '使用日期' : d['t']['使用日期'],
                                    '内部设备编号' : d['t']['内部设备编号'],
                                    '华能设备编码' : d['t']['华能设备编码'],
                                    '备注' : d['t']['备注'],
                                    '安装地点' :d['t']['安装地点'],
                                    '所属矿山' : d['t']['所属矿山'],
                                    '技术特征' : d['t']['技术特征'],
                                    '数量' : d['t']['数量'],
                                    '是否为大型设备' : d['t']['是否为大型设备'],
                                    '生产厂家' : d['t']['生产厂家'],
                                    '设备状态' : d['t']['设备状态'],
                                    '责任单位/责任人' : d['t']['责任单位/责任人'] ,
                                }
                        }  
                    start_node['subids'].append(d['t'].identity)
                    node.append(end_node)
      
        #生成根节点
        root_node={
            'id' :  rootId,
            'label' : scene_name,  
            'pid' : [],
            'subids' : [],
            'properites' : {
                'UniqueCode' : '',               
                '使用场景' : '',
                '使用日期' : '',
                '内部设备编号' : '',
                '华能设备编码' : '',
                '备注' : '',
                '安装地点' :'',
                '所属矿山' : '',
                '技术特征' : '',
                '数量' :  '',
                '是否为大型设备' : '',
                '生产厂家' : '',
                '设备状态' :  '',
                '责任单位/责任人' : '' ,         
            } 
        }
        
        
        for f in f_set:   
            #保存节点间的关系       
            root_node['subids'].append(f.identity)
            rela = {
                'id' : random.randint(11000,12000),
                'from' : rootId,
                'to' : f.identity,
                'title' : '属于'
            }
            relationship.append(rela)
        node.append(root_node)
       

        res={
            'node' : node,
            'rel' : relationship
        } 
   
        return HttpResponse(json.dumps(res,ensure_ascii=False))

#查找大型设备
def queryAllLargeEquipment(request):
    if request.method == 'POST':
        postbody = request.body
        param = json.loads(postbody.decode())       
        search_name = param['name']  
        coal_name = param['coal_name']
        if coal_name == '华能集团' or coal_name == '华能煤业公司': #总公司   
            sql = ("MATCH (f) where f.name contains '%s'  RETURN f,labels(f)")%(search_name)    
        elif coal_name in company_dic.keys():   
            sql = ("MATCH (f) where (f.name contains '%s' )  and (f.UniqueCode is Null or f.UniqueCode=~ '^%s.*')  and (ID(f) < 2581  )  RETURN f,labels(f)")%(search_name,company_dic[coal_name])
        else :#其他公司
            sql = ("MATCH (f) where (f.name contains '%s' ) and (f.UniqueCode is Null or f.所属矿山='%s') and (ID(f) < 2581 )   RETURN f,labels(f)")%(search_name,coal_name)
        data=graph.run(sql).data()  
        node=[]
        relationship=[]
        
        rootId = random.randint(5000,7000)
        #生成根节点
        root_node={
            'id' :  rootId,
            'label' :search_name,  
            'pid' : [],
            'subids' : [],
            'properites' : {
                'UniqueCode' : '',               
                '使用场景' : '',
                '使用日期' : '',
                '内部设备编号' : '',
                '华能设备编码' : '',
                '备注' : '',
                '安装地点' :'',
                '所属矿山' : '',
                '技术特征' : '',
                '数量' :  '',
                '是否为大型设备' : '',
                '生产厂家' : '',
                '设备状态' :  '',
                '责任单位/责任人' : '' ,         
            } 
        }

        for d in data: 
            start_node = { 
                'id' : d['f'].identity,
                'label' : d['f']['name'],  
                'pid' : rootId,
                'subids' : [],
                'properites' : {
                    'UniqueCode' : d['f']['UniqueCode'],               
                    '使用场景' : d['f']['使用场景'] ,
                    '使用日期' : d['f']['使用日期'],
                    '内部设备编号' : d['f']['内部设备编号'],
                    '华能设备编码' : d['f']['华能设备编码'],
                    '备注' : d['f']['备注'],
                    '安装地点' :d['f']['安装地点'],
                    '所属矿山' : d['f']['所属矿山'],
                    '技术特征' : d['f']['技术特征'],
                    '数量' : d['f']['数量'],
                    '是否为大型设备' : d['f']['是否为大型设备'],
                    '生产厂家' :  d['f']['生产厂家'],
                    '设备状态' : d['f']['设备状态'],
                    '责任单位/责任人' : d['f']['责任单位/责任人'],         
                }
            }  
            #保存节点间的关系       
            
            rela = {
                'id' : random.randint(7000,10000),
                'from' : rootId,
                'to' : d['f'].identity,
                'title' : '属于'
            }
            relationship.append(rela)
            root_node['subids'].append(d['f'].identity)
            node.append(start_node)
        if(len(data) > 0):
            node.append(root_node)
        res={
            'node' : node,
            'rel' : relationship
        } 
        
        return HttpResponse(json.dumps(res,ensure_ascii=False))

   
        

# #上传csv数据保存到neo4j数据库中
def uploadExcelData(request):
    if request.method == 'POST':
     
        if not request.FILES.get('file').name.endswith('.xls') and not request.FILES.get('file').name.endswith('.xlsx'):
            tooken['status']=10086
            return HttpResponse(json.dumps(tooken,ensure_ascii=False))
        file = request.FILES.get('file')  # 获取上传的文件
       
        coal_name=request.POST.get('coal_name')

        file_name = file.name  # 获取文件名
        file_path = file_name  # 拼接文件路径
       
        with open(file_path, 'wb+') as destination:
            for chunk in file.chunks():
                destination.write(chunk)  # 写入文件
        #处理文件
        try:
            # init(graph)
            print(coal_name)
            # 开始进行数据入库
            process(file_path,coal_name) #前端传一个excel的路径
            # process_code()
            tooken['status']=10087#处理成功
        except Exception as e:      
            print(e)
            tooken['status']=10088#文件解析失败
        finally:
            if os.path.exists(file_path):
                os.remove(file_path)
                # print("remove file successful")
        return HttpResponse(json.dumps(tooken,ensure_ascii=False))

#模糊查询
def FuzzyQueryName(request):
     if request.method=='POST':
        postbody=request.body
        param=json.loads(postbody.decode())
        name=param['node_name']
        print("===========")
        print(len(name))
        if len(name)>0:
            sql=("MATCH (f) where f.name starts with '%s' return f.name as fname")%(name)
            
            data=graph.run(sql).data()
            l=[x['fname'] for x in data]
        else:
            l=[]
        print(l)
        return HttpResponse(json.dumps(l,ensure_ascii=False))

#重复代码提取
def commonCode(sql):
    """
    封装查询的数据返回给前端
    :param sql:
    :return:
    """
    data = graph.run(sql).data()
    # 保存所有关系(线：长度为1的线)
    relationship = []
    f_list = [] # 起始结点列表
    dic_f_t = {}

    for d in data:  # 遍历每一条关系,保存数据
        f_list.append(d['f'])  # 保存起始节点
        _relationshipId = d['r'].identity
        _fromId = d['f'].identity  # 起始结点ID
        _toId = d['t'].identity  # 指向节点ID
        _title = d['rname']

        dict_relationship = {
            'id': _relationshipId,
            'from': _fromId,
            'to': _toId,
            'title': _title
        }
        relationship.append(dict_relationship)

        if _fromId in dic_f_t:  # dic的作用就是保存 所有 一个父-》[多个子]
            dic_f_t.get(_fromId).append(d['t'])
        else:
            dic_f_t.setdefault(_fromId, [d['t']])

    # print("关系数：",len(relationship))
    # 返回数据结点的结构
    dict_node = {
        'id': int,
        'label': str,
        'pid': [],
        'subids': [],
        'properites': {
            'UniqueCode': str,
            '使用场景': str,
            '使用日期': str,
            '内部设备编号': str,
            '华能设备编码': str,
            '备注': str,
            '安装地点': str,
            '所属矿山': str,
            '技术特征': str,
            '数量': str,
            '是否为大型设备': str,
            '生产厂家': str,
            '设备状态': str,
            '责任单位/责任人': str,
        }
    }
    # 保存所有(不重复)节点
    node = []
    start = set()
    end = set()
    # 遍历起始节点列表
    for f in f_list:  # f_list是起始节点列表，可能会有所不同吧：既一次查出多个树
        dict_node1 = dict_node.copy()
        if f.identity not in start: # 这个起始节点是否已经保存过， 相同ID只保存一次,已经操作过的就可以忽略了
                                    # 一棵树也就执行一次
                                    # start和end就是为了保证最终返回的node列表中不含重复id节点
            start.add(f.identity)
            dict_node1['id'] = f.identity
            dict_node1['label'] = f['name']
            if f.identity in dic_f_t:
                for t in dic_f_t.get(f.identity): # 遍历这个起始节点所有的子节点
                    if t.identity not in end:  # 这个子节点是否保存过了
                        end.add(t.identity)
                        dict_node1['subids'].append(t.identity)

                        # 封装子节点信息
                        dict_node2 = {
                            'id': t.identity,
                            'label': t['name'],
                            'pid': f.identity,
                            'subids': [],
                            'properites': {
                                'UniqueCode': t['UniqueCode'],
                                '使用场景': t['使用场景'],
                                '使用日期': t['使用日期'],
                                '内部设备编号': t['内部设备编号'],
                                '华能设备编码': t['华能设备编码'],
                                '备注': t['备注'],
                                '安装地点': t['安装地点'],
                                '所属矿山': t['所属矿山'],
                                '技术特征': t['技术特征'],
                                '数量': t['数量'],
                                '是否为大型设备': t['是否为大型设备'],
                                '生产厂家': t['生产厂家'],
                                '设备状态': t['设备状态'],
                                '责任单位/责任人': t['责任单位/责任人'],

                            }
                        }
                        node.append(dict_node2)

                    else:
                        dict_node1['subids'].append(t.identity)
            dict_node1['properites']['UniqueCode'] = f['UniqueCode']
            dict_node1['properites']['使用场景'] = f['使用场景']
            dict_node1['properites']['使用日期'] = f['使用日期']
            dict_node1['properites']['内部设备编号'] = f['内部设备编号']
            dict_node1['properites']['华能设备编码'] = f['华能设备编码']
            dict_node1['properites']['备注'] = f['备注']
            dict_node1['properites']['安装地点'] = f['安装地点']
            dict_node1['properites']['所属矿山'] = f['所属矿山']
            dict_node1['properites']['技术特征'] = f['技术特征']
            dict_node1['properites']['数量'] = f['数量']
            dict_node1['properites']['是否为大型设备'] = f['是否为大型设备']
            dict_node1['properites']['生产厂家'] = f['生产厂家']
            dict_node1['properites']['设备状态'] = f['设备状态']
            dict_node1['properites']['责任单位/责任人'] = f['责任单位/责任人']
            node.append(dict_node1)

    # 返回数据结果：
    #   node：[]包含所有结点(id不能重复)
              # 每个节点包含pid 和 subid
    #   relationship：[{},{}..] 所有关系组成的列表{}：r_id,from,to,title

    # print('结点数：',len(node))
    res = {
        'node': node,
        'rel': relationship
    }
    # print(res)
    return res

# findById不会出现多起点问题
# findByName是有可能的
def queryNeo4jInfoByname(request):
     if request.method == 'POST':
        postbody = request.body
        param = json.loads(postbody.decode())
        print("param:-----------------------------------------------")
        print(param)
        search_name = param['name'] # 查询节点名
        #user_type = param['type']
       
        coal_name = param['coal_name'] # 角色
        
        if coal_name == '华能集团' or coal_name == '华能煤业公司': #总公司

            sql = ("MATCH (f)-[r]->(t) where f.name='%s'  RETURN f,r,type(r) as rname,t,labels(f),labels(t)") % (
            search_name)  # 起始结点，关系，关系名，指向节点，起始label、指向label
                           # （比findId多了后面两个，是因为，要根据label进行假节点构造，这里改一下，不要构造假节点，太容易出错了（双起点的时候））
            # print(sql)  
        elif coal_name in company_dic.keys():   # 指定公司的所有  长度为1的关系
            sql = (
                  "MATCH (f)-[r]->(t) where (f.name = '%s' )  and (f.UniqueCode is Null or f.UniqueCode=~ '^%s.*') "
                  "and (t.UniqueCode is Null or t.UniqueCode=~ '^%s.*')  RETURN f,r,type(r) as rname,t,labels(f),"
                  "labels(t)") % (
                  search_name, company_dic[coal_name], company_dic[coal_name])
            
        else:#其他公司:具体矿山
            if search_name == coal_name:  # 查询矿山时屏蔽掉 非设备类型结点（矿山下面有一堆地点之类的傻缺东西，实际应用根本没用，也没有必要构造假节点，会造成一系列的连锁错误）
                sql = (
                      "MATCH (f:矿山)-[r]->(t) where (f.name='%s' ) and (labels(t) = %s)  RETURN "
                      "f,r,type(r) as rname,t,labels(f),labels(t)") % (
                      search_name, ['设备类型'])
                        # (f.UniqueCode is Null or f.所属矿山='%s')这个查询条件是为了在搜索框中查询  不是设备的中间节点
            else:  # 查询矿山的其他结点
                sql = (
                      "MATCH (f)-[r]->(t) where (f.name='%s' ) and (f.UniqueCode is Null or f.所属矿山='%s') and ("
                      "t.UniqueCode is Null or t.所属矿山='%s')  RETURN f,r,type(r) as rname,t,labels(f),labels(t)") % (
                      search_name, coal_name, coal_name)
        print('按名称查询：',sql)
        
        res = commonCode(sql)


        # 果然是因为重名造成的不可显示（暂时解决之后还要考虑改）
        # if search_name=='灵东煤矿':
        #     for node in res['node']:
        #         if node['id']==3610:
        #             print(node['label'])
        #             node['label']="灵东煤矿责任单位"
        #             print(node)
        # if search_name=='灵泉煤矿':
        #     for node in res['node']:
        #         if node['id']==2847:
        #             print(node['label'])
        #             node['label']="灵泉煤矿责任单位"
        #             print(node)
        return HttpResponse(json.dumps(res,ensure_ascii=False))

def queryNeo4jInfoByID(request):
    if request.method=='POST':
        postbody=request.body
        param=json.loads(postbody.decode())
        id=param['Id']
        #type = param['type']
        coal_name=param['coal_name']


        _sql=("MATCH (f) where ID(f)=%d RETURN labels(f) as label")%(id)
        _d=graph.run(_sql).data()
     
        a = ['矿山']
        b = ['设备类型']
        if _d[0]['label'] == a:
            print("**********")
            if coal_name == '华能集团' or coal_name == '华能煤业公司': #总公司        
                sql=("MATCH (f)-[r]->(t) where ID(f)=%d and labels(t) = %s RETURN f,r,type(r) as rname,t ")%(id,b) 
            elif coal_name in company_dic.keys():   #公
                sql = ("MATCH (f)-[r]->(t) where (ID(f) = %d )  and (f.UniqueCode is Null or f.UniqueCode=~ '^%s.*') and (t.UniqueCode is Null or t.UniqueCode=~ '^%s.*')  and labels(t) = %s RETURN f,r,type(r) as rname,t,labels(f),labels(t)")%(id,company_dic[coal_name],company_dic[coal_name],b)
            else:#矿山
                sql=("MATCH (f)-[r]->(t) where ID(f)=%d and (f.UniqueCode is Null or f.所属矿山='%s') and (t.UniqueCode is Null or t.所属矿山='%s') and labels(t) = %s RETURN f,r,type(r) as rname,t ")%(id,coal_name,coal_name,b)
                
        else:
            if coal_name == '华能集团' or coal_name == '华能煤业公司': #总公司        
                sql=("MATCH (f)-[r]->(t) where ID(f)=%d RETURN f,r,type(r) as rname,t ")%(id) 
            elif coal_name in company_dic.keys():   #公司
                sql = ("MATCH (f)-[r]->(t) where (ID(f) = %d )  and (f.UniqueCode is Null or f.UniqueCode=~ '^%s.*') and (t.UniqueCode is Null or t.UniqueCode=~ '^%s.*')  RETURN f,r,type(r) as rname,t,labels(f),labels(t)")%(id,company_dic[coal_name],company_dic[coal_name])
            else:#矿山
                sql=("MATCH (f)-[r]->(t) where ID(f)=%d and (f.UniqueCode is Null or f.所属矿山='%s') and (t.UniqueCode is Null or t.所属矿山='%s') RETURN f,r,type(r) as rname,t ")%(id,coal_name,coal_name)
        
        print(sql)
    
        #sql=("MATCH (f)-[r]->(t) where ID(f)=%d RETURN f,r,type(r) as rname,t ")%(id)
        data=graph.run(sql).data()
        
        dict_node={ 
        'id' : int,
        'label' : str,  
        'pid' : [],
        'subids' : [],
        'properites' : {
                'UniqueCode' : str,               
                '使用场景' : str,
                '使用日期' : str,
                '内部设备编号' : str,
                '华能设备编码' : str,
                '备注' : str,
                '安装地点' :str,
                '所属矿山' : str,
                '技术特征' : str,
                '数量' : str,
                '是否为大型设备' : str,
                '生产厂家' : str,
                '设备状态' : str,
                '责任单位/责任人' : str ,         
            }
        }
        node=[]
        relationship=[]
        f_list=[]
        t_list=[]
        
        dic={int:[]}
        start=set()
        end=set()
        for d in data:  
            f_list.append(d['f'])
            _relationshipid =d['r'].identity
            _from = d['f'].identity
            
            _to = d['t'].identity
            _title = d['rname']
            
            dict_relationship = {
                'id' : _relationshipid,
                'from' : _from,
                'to' : _to,
                'title' : _title
            } 
            relationship.append(dict_relationship)
            id=d['f'].identity
            if id in dic:    
                dic.get(id).append(d['t'])
            else:
                dic.setdefault(id,[d['t']])
            t_list.append(dic.copy())
        for f in f_list:
          dict_node1=dict_node.copy()
          if f.identity not in start:
          
            dict_node1['id']=f.identity
            dict_node1['label']=f['name']
           
            if f.identity in dic:  
               
                for t in dic.get(f.identity):
                    if t.identity not in end:   
                        dict_node1['subids'].append(t.identity)             
                      
                        dict_node2={
                            'id' : t.identity,
                            'label' : t['name'],  
                            'pid' : f.identity,
                            'subids' : [],
                            'properites' : {
                                'UniqueCode' : t['UniqueCode'] ,               
                                '使用场景' : t['使用场景'],
                                '使用日期' : t['使用日期'],
                                '内部设备编号' : t['内部设备编号'],
                                '华能设备编码' : t['华能设备编码'],
                                '备注' : t['备注'],
                                '安装地点' :t['安装地点'],
                                '所属矿山' : t['所属矿山'],
                                '技术特征' : t['技术特征'],
                                '数量' : t['数量'],
                                '是否为大型设备' : t['是否为大型设备'],
                                '生产厂家' : t['生产厂家'],
                                '设备状态' : t['设备状态'],
                                '责任单位/责任人' : t['责任单位/责任人'] ,
                                
                                }                   
                        }   
                        end.add(t.identity) 
                        node.append(dict_node2)
                    else:
                          dict_node1['subids'].append(t.identity)


        
            dict_node1['properites']['UniqueCode']= f['UniqueCode']
            dict_node1['properites']['使用场景']=f['使用场景']
            dict_node1['properites']['使用日期']=f['使用日期']
            dict_node1['properites']['内部设备编号']=f['内部设备编号']
            dict_node1['properites']['华能设备编码']=f['华能设备编码']
            dict_node1['properites']['备注']=f['备注']
            dict_node1['properites']['安装地点']=f['安装地点']
            dict_node1['properites']['所属矿山']=f['所属矿山']
            dict_node1['properites']['技术特征'] = f['技术特征']
            dict_node1['properites'] ['数量'] = f['数量']
            dict_node1['properites']['是否为大型设备'] = f['是否为大型设备']
            dict_node1['properites']['生产厂家'] = f['生产厂家']
            dict_node1['properites']['设备状态'] = f['设备状态']
            dict_node1['properites']['责任单位/责任人'] = f['责任单位/责任人'] 
           
            start.add(f.identity)
            node.append(dict_node1)
       
     
        print("节点信息:  ",node)
        res={
            'node' : node,
            'rel' : relationship
        }
        return HttpResponse(json.dumps(res,ensure_ascii=False))
# from django.views.decorators.csrf import csrf_exempt
# import textract
# from django.http import JsonResponse
# from django.views.decorators.csrf import csrf_exempt
# import io
# import docx
# import PyPDF2

# @csrf_exempt
# def convert_file(request):
#     if request.method == 'POST':
#         uploaded_file = request.FILES['file']
#         file_type = uploaded_file.content_type
#         if file_type == 'text/plain':
#             return JsonResponse({'text': uploaded_file.read().decode('utf-8')})
#         elif file_type == 'application/pdf':
#             pdf_reader = PyPDF2.PdfFileReader(io.BytesIO(uploaded_file.read()))
#             text = '\n'.join([pdf_reader.getPage(page_num).extractText() for page_num in range(pdf_reader.getNumPages())])
#             return JsonResponse({'text': text})
#         elif file_type == 'application/msword':
#             doc = docx.Document(io.BytesIO(uploaded_file.read()))
#             text = '\n'.join([paragraph.text for paragraph in doc.paragraphs])
#             return JsonResponse({'text': text})
#         else:
#             return JsonResponse({'error': 'Unsupported file type'})

import re
#实体入库
def entityImport(request):
    tooken={
            "status":int,
        }
    matcher = NodeMatcher(graph)
    char2label = {'sb':'机电设备','pj':'配件','ff':'方法','td':'特点','cs':'设备参数','ks':'矿山',
                  'qy':'企业','xm':'项目'}
    if request.method == 'POST':
        postBody=request.body
        param=json.loads(postBody.decode())
        kuangshan=param["kuangshan"]
        gzm=param["gongzuomian"]
        shit=param["shiti"]
        
        

        pattern1 = 'class="(.*?)"'
        pattern2 = '>(.*?)</span>'
        # print(type(postBody))
        xiaojiji = re.findall(pattern1,str(shit))
        
        
        label = []
        for l in xiaojiji:
            
            label.append(char2label[l])
        print("label",label)

        ent = re.findall(pattern2,str(shit))
        
        xxx=matcher.match("设备类型",name=kuangshan+gzm).first()
        
        
        for l, e in zip(label, ent):
            if len(e)>2:
                node_tail=Node('模型抽取',name=e,label=l)
                graph.create(node_tail)      
                node_tail['导入时间'] = time.strftime('%Y-%m-%d')
                node_tail['导入IP'] = '10.3.102.118'
                node_tail['导入人'] = '华能集团管理员'
                node_tail['数据来源'] = '模型抽取'
                graph.push(node_tail)
                relationship=Relationship(xxx,'包含',node_tail)
            
                graph.create(relationship)
        
        tooken['status']=10087#处理成功
        
        # return HttpResponse(json.dumps(tooken,ensure_ascii=False))
        return HttpResponse(json.dumps(tooken,ensure_ascii=False))
    
#三元组入库
def tripleImport(request):
    tooken={
            "status":int,
        }
    pattern1 = 'true">(.*?)</span>'
    pattern2 = 'id="gx">(.*?)</span> '
    matcher = NodeMatcher(graph)
    rmatcher = RelationshipMatcher(graph)
    if request.method == 'POST':
        postBody = request.body
        param=json.loads(postBody.decode())
        kuangshan=param["kuangshan"]
        gzm=param["gongzuomian"]
        shit=param["shiti"]
        
        triple = re.findall(pattern1,str(shit))
        print("triple",triple)
        sub = [i.strip() for i in triple[::2]]
        obj = [i.strip()for i in triple[1::2]]
        rel =  re.findall(pattern2,str(shit))
        print("sub",sub)
        print("obj",obj)
        print("rel",rel)

    shuju = matcher.match("设备类型",name=kuangshan+gzm).first()
    for s, r, o in zip(sub, rel, obj):
        flag = True
        if r=='设备参数' or r=='特点' or r=='具有'  or r=='采取'or r=='应用':
            node_head = matcher.match('模型抽取', name = s).first()
            if not node_head:
                node_head = Node('模型抽取', name = s)
                graph.create(node_head)
                node_head['导入时间'] = time.strftime('%Y-%m-%d')
                node_head['导入IP'] = '10.3.102.118'
                node_head['导入人'] = '华能集团管理员'
                node_head['设备属性'] = o
                node_head['数据来源'] = '模型抽取'
                graph.push(node_head)
                baohan1=Relationship(shuju,'包含',node_head)
                graph.create(baohan1)
        elif r=='研制' or r=='生产' :
            node_head = matcher.match('模型抽取', name = o).first()
            if not node_head:
                node_head = Node('模型抽取', name = s)
                graph.create(node_head)
                node_head['导入时间'] = time.strftime('%Y-%m-%d')
                node_head['导入IP'] = '10.3.102.118'
                node_head['导入人'] = '华能集团管理员'
                node_head['生产厂家'] = s
                node_head['数据来源'] = '模型抽取'
                graph.push(node_head)
                baohan1=Relationship(shuju,'包含',node_head)
                graph.create(baohan1)
        else:
            node_head = matcher.match('模型抽取', name = s).first()
            if not node_head:
                node_head = Node('模型抽取', name = s)
                graph.create(node_head)
                node_head['导入时间'] = time.strftime('%Y-%m-%d')
                node_head['导入IP'] = '10.3.102.118'
                node_head['导入人'] = '华能集团管理员'
                node_head['数据来源'] = '模型抽取'
                graph.push(node_head)
                baohan1=Relationship(shuju,'包含',node_head)
                graph.create(baohan1)
            node_tail = matcher.match('模型抽取', name = o).first()
            if not node_tail:
                node_tail = Node('模型抽取', name = o)
                graph.create(node_tail)
                node_tail['导入时间'] = time.strftime('%Y-%m-%d')
                node_tail['导入IP'] = '10.3.102.118'
                node_tail['导入人'] = '华能集团管理员'
                node_tail['数据来源'] = '模型抽取'
                graph.push(node_tail)
                baohan2 = Relationship(node_head,r,node_tail)
                graph.create(baohan2)

    tooken['status']=10087#处理成功
    return HttpResponse(json.dumps(tooken,ensure_ascii=False))
  

import textract
def uploadTXT_WORD_PDF(request):
    if request.method == 'POST':
    
        # 判断是否是Excel文件
        tooken={
            "status":int,
        }
        print('萨达萨达是')
        if not request.FILES.get('file').name.endswith('.docx') and not request.FILES.get('file').name.endswith('.txt') \
            and not request.FILES.get('file').name.endswith('.pdf'):
            tooken['status']=10086
            return HttpResponse(json.dumps(tooken,ensure_ascii=False))
        file = request.FILES.get('file')
        file_name = file.name
        file_path = file_name
        with open(file_path, 'wb+') as destination:
            for chunk in file.chunks():
                destination.write(chunk)  # 写入文件
        try:
            text = textract.process(file_path,'utf-8')
        except Exception as e:      
            print(e)
        finally:
            if os.path.exists(file_path):
                os.remove(file_path)
    return HttpResponse(text.decode())
# def uploadExcelData(request):
#     if request.method == 'POST':
      
#         # 判断是否是Excel文件
#         tooken={
#             "status":int,
#         }
#         print()

#         if not request.FILES.get('file').name.endswith('.xls') and not request.FILES.get('file').name.endswith('.xlsx'):
#             tooken['status']=10086
#             return HttpResponse(json.dumps(tooken,ensure_ascii=False))
#         file = request.FILES.get('file')  # 获取上传的文件
       
#         coal_name=request.POST.get('coal_name')

#         file_name = file.name
#         file_path = file_name  # 拼接文件路径
       
#         with open(file_path, 'wb+') as destination:
#             for chunk in file.chunks():
#                 destination.write(chunk)  # 写入文件
#         #处理文件
#         try:
#             init(graph)
#             print(coal_name)
#             process(file_path,coal_name) #前端传一个excel的路径
#             process_code()
#             tooken['status']=10087#处理成功
#         except Exception as e:      
#             print(e)
#             tooken['status']=10088#文件解析失败
#         finally:
#             if os.path.exists(file_path):
#                 os.remove(file_path)
#         return HttpResponse(json.dumps(tooken,ensure_ascii=False))