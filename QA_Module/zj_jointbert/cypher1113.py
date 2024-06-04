








# -*- codeing = utf-8 -*-
# @Time : 2023/5/18 4:10
# @Author : 剑
# @File : cypher.py
# @Software : PyCharm
import json
import re

from py2neo import Graph,Node,Relationship,NodeMatcher,RelationshipMatcher
from collections import defaultdict
import pandas as pd
import sys
import os
script_dir = os.path.dirname(os.path.abspath(r'/workspace/HNCoal/QA_Module/zj_jointbert/entity_link'))
sys.path.append(script_dir)
from entity_link.similar_caculate import calculate_similarity
user = 'neo4j'
key = 'root'
graph=Graph("http://localhost:6006/browser/",auth=(user, key))

intent_to_cypher = {"UNK":"",
                    "mine_knowledge_Infrastruct":"",
                    "mine_knowledge_driving_mining":"",
                    "mine_knowledge_electric":"",
                    "mine_knowledge_geology":"",
                    "mine_knowledge_open-pit_mining":"",
                    "mine_knowledge_rocksupport":"",
                    "mine_knowledge_transport":"",
                    "mine_knowledge_ventilation":"",
                    "mine_knowledge_washing":"",
                    "query_entity_by_label_mul":"",
                    "query_entity_by_label_single":"",
                    "query_entity_property_all_mul":"",
                    "query_entity_property_all_single":"",
                    "query_entity_property_one":"",
                    "query_entity_property_mul":"",
                    "query_related_entity_one":"",
                    "query_related_entity_two":"",
                    "query_related_entity_three":""
                    }

entityLabel_dict = {"ent.mineName":"矿山",
                   "ent.equipCalss":"设备类型",
                   "ent.equipName":"设备",
                   "ent.subComp":"分公司",
                   "ent.Huaneng":"华能集团",
                   "ent.department":"责任单位",
                   "ent.place":"地点",
                   "ent.firm":"企业",
                   "ent.employee":"员工"
                   }
candidate_files_dict = {"ent.mineName":"/workspace/HNCoal/QA_Module/zj_jointbert/entity_link/candidate_files/6kuangshan.txt",
                   "ent.equipCalss":"/workspace/HNCoal/QA_Module/zj_jointbert/entity_link/candidate_files/8shebeileixing.txt",
                   "ent.equipName":"/workspace/HNCoal/QA_Module/zj_jointbert/entity_link/candidate_files/7shebei.txt",
                   "ent.subComp":"/workspace/HNCoal/QA_Module/zj_jointbert/entity_link/candidate_files/2fengongsi.txt",
                   "ent.Huaneng":"/workspace/HNCoal/QA_Module/zj_jointbert/entity_link/candidate_files/1huaneng.txt",
                   "ent.department":"/workspace/HNCoal/QA_Module/zj_jointbert/entity_link/candidate_files/9zerendanwei.txt",
                   "ent.place":"/workspace/HNCoal/QA_Module/zj_jointbert/entity_link/candidate_files/5didian.txt",
                   "ent.firm":"/workspace/HNCoal/QA_Module/zj_jointbert/entity_link/candidate_files/3qiye.txt",
                   "ent.employee":"/workspace/HNCoal/QA_Module/zj_jointbert/entity_link/candidate_files/4yuangong.txt"
                   }
embedding_files_dict = {"ent.mineName":"/workspace/HNCoal/QA_Module/zj_jointbert/entity_link/embedding_files/6kuangshan.pt",
                   "ent.equipCalss":"/workspace/HNCoal/QA_Module/zj_jointbert/entity_link/embedding_files/8shebeileixing.pt",
                   "ent.equipName":"/workspace/HNCoal/QA_Module/zj_jointbert/entity_link/embedding_files/7shebei.pt",
                   "ent.subComp":"/workspace/HNCoal/QA_Module/zj_jointbert/entity_link/embedding_files/2fengongsi.pt",
                   "ent.Huaneng":"/workspace/HNCoal/QA_Module/zj_jointbert/entity_link/embedding_files/1huaneng.pt",
                   "ent.department":"/workspace/HNCoal/QA_Module/zj_jointbert/entity_link/embedding_files/9zerendanwei.pt",
                   "ent.place":"/workspace/HNCoal/QA_Module/zj_jointbert/entity_link/embedding_files/5didian.pt",
                   "ent.firm":"/workspace/HNCoal/QA_Module/zj_jointbert/entity_link/embedding_files/3qiye.pt",
                   "ent.employee":"/workspace/HNCoal/QA_Module/zj_jointbert/entity_link/embedding_files/4yuangong.pt"
                   }
property_dict = {"pro.UniqueCode":"UniqueCode",
                 "pro.name":"name",
                 "pro.useDate":"使用日期",
                 "pro.intEquipNum":"内部设备编号",
                 "pro.smName":"别名",
                 "pro.HNCode":"华能设备编码",
                 "pro.spNum":"备件数量",
                 "pro.remark":"备注",
                 "pro.instSite":"安装地点",
                 "pro.importIP":"导入IP",
                 "pro.importPerson":"导入人",
                 "pro.importTime":"导入时间",
                 "pro.owningMine":"所属矿山",
                 "pro.techChara":"技术特征",
                 "pro.dataSource":"数据来源",
                 "pro.quantity":"数量",
                 "pro.WhethLarge":"是否为大型设备",
                 "pro.manufacturer":"生产厂家",
                 "pro.equipType":"设备型号",
                 "pro.equipStatus":"设备状态",
                 "pro.specification":"说明书",
                 "pro.respUnitPerson":"责任单位与责任人"
                 }
labelType_dict = {"label.mineName":"矿山",
                  "label.equipCalss":"设备类型",
                  "label.equipName":"设备",
                  "label.subComp":"分公司",
                  "label.huaneng":"华能集团",
                  "label.department":"责任单位",
                  "label.place":"地点",
                  "label.firm":"企业",
                  "label.employee":"员工"
                  }
relType_dict = {"rel.manufacture":"制造",
                "rel.contain":"包含",
                "rel.instSite":"安装地点",
                "rel.belong":"属于",
                "rel.factory":"生产厂家",
                "rel.charge":"负责",
                "rel.chargePerson":"责任人"
                }

# 查询接口
def queryKG(intent_pred,slot_key,slot_value):
    #举例  slot_key====== ['ent.place', 'rel.contain', 'ent.equipName', 'rel.instSite']
    #     slot_val====== ['洗煤厂-电煤仓上', '包含', '技术设备', '安装区域']
    if "UNK" == intent_pred:
        tips = "Tips:非煤矿领域问答"
        return tips
    elif "mine_knowledge_Infrastruct" == intent_pred:
        tips = "Tips:矿井基建知识问答"
        return tips
    elif "mine_knowledge_driving_mining" == intent_pred:
        tips = "Tips:掘进采煤知识问答"
        return tips
    elif "mine_knowledge_electric" == intent_pred:
        tips = "Tips:机械电气知识问答"
        return tips
    elif "mine_knowledge_geology" == intent_pred:
        tips = "Tips:地测防水知识问答"
        return tips
    elif "mine_knowledge_open-pit_mining" == intent_pred:
        tips = "Tips:露天开采知识问答"
        return tips
    elif "mine_knowledge_rocksupport" == intent_pred:
        tips = "Tips:压力支护知识问答"
        return tips
    elif "mine_knowledge_transport" == intent_pred:
        tips = "Tips:运输提升知识问答"
        return tips
    elif "mine_knowledge_ventilation" == intent_pred:
        tips = "Tips:一通三防知识问答"
        return tips
    elif "mine_knowledge_washing" == intent_pred:
        tips = "Tips:洗选化工知识问答"
        return tips
    elif "query_entity_by_label_single" == intent_pred:  #完成，但输出是unicode形式，还没找到解决办法
        tips = "--Tips:按单个label查询所有实体"
        labelType = ''
        for key,value in zip(slot_key,slot_value):
            if 'label.' in key:
                if key in labelType_dict:
                    if value in labelType_dict.values():
                        labelType = value
                    else:
                        labelType = labelType_dict[key]   # 获取 实体label 标签
                else:
                    key_error = 'slot_key error: slot_key not in labelType_dict'
                    return tips + "\n" + key_error
            break # 只查询第一个实体类型
        if labelType:
            answer = queryEntityByLabel_single(labelType,limitType=True,limit=25)
            answer = json.dumps(answer,indent=2,ensure_ascii=False) + "\n" + tips
            return answer
        else:
            labelType_error = 'Type_error: 意图识别error，无可用labelType'
            return tips + "\n" + labelType_error
    elif "query_entity_by_label_mul" == intent_pred:    #输出了该label的实体的所有属性，我觉得留个name属性就够了，待解决。
        tips = "--Tips:按多个label查询所有实体"
        labelType_ls = []
        for key,value in zip(slot_key,slot_value):
            if 'label.' in key:
                if key in labelType_dict:
                    print("key ##################### = ",key)
                    labelType_ls.append(labelType_dict[key])
                else:
                    key_error = 'slot_key error: slot_key not in labelType_dict'
                    return tips + "\n" + key_error
        answer = queryEntityByLabel_multi(labelType_ls,limitType=True,limit=25)
        answer = json.dumps(answer,indent=2,ensure_ascii=False)+ "\n" + tips
        return answer
    
    elif "query_entity_property_one" == intent_pred:  #完成
        tips = "--Tips:查询单实体单个属性值"
        ent_label = ""
        ent_name = ""
        ent_pro_key = []
        for key,value in zip(slot_key,slot_value):
            if "pro." in key:
                if key in property_dict:
                    ent_pro_key .append( property_dict[key])
                else:
                    key_error = 'slot_key error: slot_key not in property_dict'
                    return tips + "\n" + key_error
            elif "ent." in key:
                if key in entityLabel_dict:
                    ent_label = entityLabel_dict[key]
                    # ent_name = value
                    print('对应文件：',candidate_files_dict[key])
                    print('对应向量文件：',embedding_files_dict[key])
                    prdict_ent,score = calculate_similarity(value,candidate_files_dict[key],embedding_files_dict[key])  
                    print("相似实体：%s 最高得分：%f"%(prdict_ent,score))
                    ent_name = prdict_ent.strip()
                else:
                    key_error = 'slot_key error: slot_key not in entityLabel_dict'
                    return tips + "\n" + key_error
        print("ent_label = ",ent_label)
        print("ent_name == ",ent_name)
        print("ent_pro === ",ent_pro_key)
        if ent_label and ent_name and ent_pro_key:
            if len(ent_pro_key)<2:
                answer = queryEntityPro_single(ent_label,ent_name,ent_pro_key[0])   #都是用的库里的名字（中文）
                answer = json.dumps(answer, indent=2, ensure_ascii=False) + "\n" + tips
            else:
                answer = queryEntityPro_multi(ent_label,ent_name,ent_pro_key)
                answer = json.dumps(answer, indent=2, ensure_ascii=False) + "\n" + "--Tips:查询单实体多个属性值"
            
            return answer
        else:
            queryParam_error = 'queryParam_error: missing ent_label or ent_name or ent_pro_key'
            return queryParam_error + "\n" + tips
    elif "query_entity_property_mul" == intent_pred:  #完成
        tips = "--Tips:查询单实体多个属性值"
        ent_label = ""
        ent_name = ""
        ent_pro_ls = []
        for key,value in zip(slot_key,slot_value):
            if "ent." in key:
                if key in entityLabel_dict:
                    ent_label = entityLabel_dict[key]
                    prdict_ent,score = calculate_similarity(value,candidate_files_dict[key],embedding_files_dict[key])  
                    print('对应文件：',candidate_files_dict[key])
                    print('对应向量文件：',embedding_files_dict[key])
                    print("相似实体：%s 最高得分：%f"%(prdict_ent,score))
                    ent_name = prdict_ent.strip()
                else:
                    key_error = 'slot_key error: slot_key not in entityLabel_dict'
                    return tips + "\n" + key_error
            if "pro." in key:
                if key in property_dict:
                    ent_pro_ls.append(property_dict[key])
                else:
                    key_error = 'slot_key error: slot_key not in property_dict'
                    return tips + "\n" + key_error
        if ent_label and ent_name and ent_pro_ls:
            answer = queryEntityPro_multi(ent_label,ent_name,ent_pro_ls)
            answer = json.dumps(answer,indent=2,ensure_ascii=False) + "\n" + tips
            return answer
        else:
            queryParam_error = 'queryParam_error: missing ent_label or ent_name or ent_pro_ls'
            return queryParam_error + "\n" + tips
    elif "query_entity_property_all_single" == intent_pred:  #完成
        tips = "--Tips:查询单实体全部属性值"
        ent_label = ''
        ent_name = ''
        for key,value in zip(slot_key,slot_value):
            if 'ent.' in key:
                if key in entityLabel_dict:
                    ent_label = entityLabel_dict[key]
                    prdict_ent,score = calculate_similarity(value,candidate_files_dict[key],embedding_files_dict[key])  
                    print('对应文件：',candidate_files_dict[key])
                    print('对应向量文件：',embedding_files_dict[key])
                    print("相似实体：%s 最高得分：%f"%(prdict_ent,score))
                    ent_name = prdict_ent.strip()
                else:
                    key_error = 'slot_key error: slot_key not in entityLabel_dict'
                    return tips + "\n" + key_error
            break    # 只查询第1个实体的属性

        answer = queryEntityAllPro_single(ent_label,ent_name)
        answer = json.dumps(answer,indent=2,ensure_ascii=False) + "\n" + tips
        return answer
    elif "query_entity_property_all_mul" == intent_pred:    #完成
        tips = "--Tips:查询多实体全部属性值"
        ent_label_ls = []
        ent_name_ls = []
        for key,value in zip(slot_key,slot_value):
            if 'ent.' in key:
                if key in entityLabel_dict:
                    label = entityLabel_dict[key]
                    ent_label_ls.append(label)
                    prdict_ent,score = calculate_similarity(value,candidate_files_dict[key],embedding_files_dict[key])  
                    print('对应文件：',candidate_files_dict[key])
                    print('对应向量文件：',embedding_files_dict[key])
                    print("相似实体：%s 最高得分：%f"%(prdict_ent,score))
                    ent_name = prdict_ent.strip()
                    ent_name_ls.append(ent_name)
                else:
                    key_error = 'slot_key error: slot_key not in entityLabel_dict'
                    return tips + "\n" + key_error
        answer = queryEntityAllPro_multi(ent_label_ls,ent_name_ls)
        answer = json.dumps(answer,indent=2,ensure_ascii=False) + "\n" + tips
        print('answer:',answer)
        return answer
    
    
    elif "query_related_entity_one" == intent_pred or "query_related_entity_two" == intent_pred:
        tips = "--Tips:查询 实体-关系->实体(单个关系)"
        rel = ''
        label = []
        for key,value in zip(slot_key,slot_value):
            if 'ent.' in key:
                if key in entityLabel_dict:
                    ent_label = entityLabel_dict[key]
                    label.append(ent_label)
                    # print("ent_label",ent_label)
                    if len(label) <2: 
                        prdict_ent,score = calculate_similarity(value,candidate_files_dict[key],embedding_files_dict[key])  
                        print('对应文件：',candidate_files_dict[key])
                        print('对应向量文件：',embedding_files_dict[key])
                        print("相似实体：%s 最高得分：%f"%(prdict_ent,score))
                        ent_name = prdict_ent.strip()

                else:
                    key_error = 'slot_key error: slot_key not in entityLabel_dict'
                    return tips + "\n" + key_error
            elif 'rel.' in key:
                if key in relType_dict:
                    rel = relType_dict[key]
                else:
                    key_error = 'slot_key error: slot_key not in relType_dict'
                    return tips + "\n" + key_error
            elif not rel:  #如果只有实体，没有关系，可以默认为包含关系
                rel = '包含'
        if ent_label and ent_name and rel:
            if rel == '责任人':
                answer_shebei_jishucanshu = queryEntityPro_single(ent_label,ent_name,"技术特征")["技术特征"]   #都是用的库里的名字（中文）
                print("技术特征：",answer_shebei_jishucanshu)
                answer = queryRelEntity(label,ent_name,rel) 
                answer.append(answer_shebei_jishucanshu)
                print(answer)
                answer = json.dumps(answer,indent=2,ensure_ascii=False) + "\n" + tips
            else:
                answer = queryRelEntity(label,ent_name,rel)
                answer = json.dumps(answer, indent=2, ensure_ascii=False) + "\n" + tips
            return answer
        else:
            queryParam_error = 'queryParam_error: missing ent_label or ent_name or relationship '
            return tips + '\n' + queryParam_error
    elif "query_related_entity_three" == intent_pred:
        tips = "--Tips:实体<-关系-实体(统计所有关系实体)"

        ent_label = ''
        ent_name = ''
        ent_lab=[]
        ent=[] #存放这句话中的所有实体
        rel_ls = [] #存放这句话中的所有关系
        for key,value in zip(slot_key,slot_value):
            if 'ent.' in key:
                if key in entityLabel_dict:
                    ent_label = entityLabel_dict[key]  #实体在库里的标签
                    ent_lab.append(ent_label)
                    prdict_ent,score = calculate_similarity(value,candidate_files_dict[key],embedding_files_dict[key])  
                    if score >0.75:
                        ent_name = prdict_ent.strip()       #实体实际的名字
                        ent.append(ent_name) 
                    else:
                        ent.append(value)
                    print('对应文件：',candidate_files_dict[key])
                    print('对应向量文件：',embedding_files_dict[key])
                    print("相似实体：%s 最高得分：%f"%(prdict_ent,score))
                    
                else:
                    key_error = 'slot_key error: slot_key not in entityLabel_dict'
                    return tips + "\n" + key_error
            elif 'rel.' or 'label.' in key:
                print("------------------------slot_key = ",key)
                if key in relType_dict:
                    rel = relType_dict[key]   #关系在库里的名称
                    rel_ls.append(rel)
                else:
                    key_error = 'slot_key error: slot_key not in relType_dict'
                    return tips + "\n" + key_error
        if not rel_ls:
            rel = relType_dict["rel.belong"] # 默认查询 属于 关系
            rel_ls.append(rel)
        if ent_label and ent_name and rel:
            answer = query_related_entity_two(ent_lab,ent,rel_ls)
            answer = json.dumps(answer,indent=2,ensure_ascii=False)+ "\n" + tips
            return answer
        else:
            queryParam_error = 'queryParam_error: missing ent_label or ent_name or relationship'
            return queryParam_error + "\n" + tips





# 1.1 查询单实体属性（单个属性值）
def queryEntityPro_single(label, name, pro):
    """
    label: 实体label
    name: 实体名
    pro: 属性名
    """
    print("label ====== ",label)
    print("name ======= ",name)
    print("pro ======== ",pro)
    res_dict = {}
    cypher = "MATCH (n:`%s`) WHERE n.name='%s' RETURN n" % (label, name)
    result = pd.DataFrame(graph.run(cypher))
    print("result ==========",result)
    if result.empty:
        res = "查询'%s'的属性值'%s'失败"%(name,pro)
        return  res
    result_dict = dict(result[0][0])
    # print('result_dict',result_dict)
    if pro in result_dict.keys():
        res_dict[pro] = result_dict[pro]
        return res_dict
    else:
        return '属性不存在'

# 1.2 查询单实体属性（多个属性值）
def queryEntityPro_multi(label,name,pro_ls):
    '''
    label:实体label
    name:实体名称
    pro_ls:属性列表
    '''
    res_dict = {}
    if not pro_ls:
        return '属性关键字非法'
    else:
        for pro in pro_ls:
            value = queryEntityPro_single(label,name,pro)
            res_dict[pro] = value[pro]
    return res_dict

# 2.1 查询单实体属性（全部属性值）
def queryEntityAllPro_single(label, name):
    """
    label: 实体label
    name: 实体名
    """

    cypher = "MATCH (n:`%s`) WHERE n.name='%s' RETURN n" % (label, name)
    result = pd.DataFrame(graph.run(cypher))
    if result.empty:
        res = "查询'%s'全部属性失败" % (name)
        return res
    else:
        result_dict = dict(result[0][0])
        print('result_dict:',result_dict)
        return result_dict

# 2.2 查询多实体属性（全部属性值）
def queryEntityAllPro_multi(label_ls,name_ls):
    '''
    label:实体label
    name_ls:实体名称列表
    '''
    res_dict = {}
    if not name_ls:
        return '设备名非法'
    else:
        for label,name in zip(label_ls,name_ls):
            value = queryEntityAllPro_single(label,name)
            res_dict[name] = value
    return res_dict

# 3.1 按label查询所有实体（单label）
def queryEntityByLabel_single(labelType,limitType=True,limit=25):
    '''
    label:待查询实体类型
    limitType:是否取消限制 -- False:不限制；True:限制
    limit:限制查询结果的最大数量
    '''
    if limitType:
        cypher_2 = "MATCH (n:`%s`) RETURN n limit %d"%(labelType,limit)
        result_2 = pd.DataFrame(graph.run(cypher_2))
        if result_2.empty:
            res = "查询'%s'所有实体失败"%(labelType)
            return res
        else:
            print('result_2',result_2)
            result_dict_2 = dict(result_2[0])
            return result_dict_2
    else:
        cypher_1 = "MATCH (n:`%s`) RETURN n"%(labelType)
        result_1 = pd.DataFrame(graph.run(cypher_1))
        if result_1.empty:
            res = "查询'%s'所有实体失败"%(labelType)
            return res
        else:
            print('result_1',result_1)
            result_dict_1 = dict(result_1[0])
            return result_dict_1

# 3.2 按label查询所有实体(多label)
def queryEntityByLabel_multi(label_ls,limitType=True,limit=25):
    res_dict = {}
    if not label_ls:
        return '实体类别(label)非法'
    else:
        for label in label_ls:
            value = queryEntityByLabel_single(label,limitType,limit)
            res_dict[label] = value
    return res_dict

# 4.1 查询 实体-关系->实体(单个关系)
def queryRelEntity(label, name, rel):
    """
    label: 实体label
    name: 实体名
    rel: 关系
    """
    if rel == '负责' or rel == '包含' or rel == '制造' or rel == '属于':
        cypher = "MATCH (n:%s)-[:%s]->(m:%s) WHERE n.name = '%s' RETURN m"%(label[0],rel,label[1],name)
    # cypher = "MATCH (n:`%s`{name:'%s'})-[r:`%s`]->(m) RETURN m" % (label, name, rel)
    # result = pd.DataFrame(graph.run(cypher))
    # if result.empty:
    #     error = "查询'%s'的关系'%s'失败" % (name, rel)
    #     return error
    # else:
    #     result_dict = dict(result[0][0])
    #     #         print(result_dict)
    #     return result_dict["name"]
    else:
        cypher = "MATCH (n:`%s`{name:'%s'})-[r:`%s`]->(m) RETURN m"%(label[0],name,rel)
    print("cypher:",cypher)
    result = pd.DataFrame(graph.run(cypher))
    if result.empty:
        error = "查询'%s'的关系'%s'失败"%(name,rel)
        return error
    else:
        result_dict = dict(result[0])
#         print(result_dict)
        return [item["name"] for item in result_dict.values()]
# 4.3 查询 实体-关系-实体-关系->实体(两跳关系)
def query_related_entity_two(label,name,rel_ls):
    """
    label: 实体label
    name: 实体名
    rel: 关系
    """
    import re
    
    # res= []
    
    if not rel_ls:
        return '关系类别(rel)非法'
    else:
            # for i in range(len(rel_ls)):
            #     lab = label[i]
            #     nam = name[i] 
            #     rel = rel_ls[i]
            # 把 洗煤厂-电煤仓 上 包含 的 技术设备 的 安装区域 全都检索出来。
            # value = query_related_entity_one(label,name,rel)
            if len(label)>2:
                if label[2] == '责任单位':
                    label[2] = '属于'
                cypher = "MATCH (n:%s)-[:%s]->(m:%s)-[:%s]->(k) WHERE n.name = '%s' RETURN [m.name,k.name]"%(label[0],rel_ls[0],label[1],label[2],name[0])
            else:
                cypher = "MATCH (n:%s)-[:%s]->(m:%s)-[:%s]->(k) WHERE n.name = '%s' RETURN [m.name,k.name]"%(label[0],rel_ls[0],label[1],rel_ls[1],name[0])
            # cypher = "MATCH (n:`%s`)-[:`%s`]->(m:`%s`)-[:`%s`]->(k) WHERE n.name = '%s' RETURN [m.name,k.name]"%(label[0],rel_ls[0],label[1],rel_ls[1] or label[2],name[0])
            print("cypher语句是:",cypher)
            result = pd.DataFrame(graph.run(cypher))
            print('result:',result)
            # print(lab,nam,rel)
            if result.empty:
                error = "查询'%s'的关系'%s'失败"%(name,rel_ls)
                return error
            else:
                result_dict = dict(result[0])
                print('result_dict',result_dict)
            
                
            
    return result_dict
# 4.2 查询 实体<-关系-实体(多关系实体统计)
def queryRelEntity_multi(label,name,rel_ls):
    """
    label: 实体label
    name: 实体名
    rel: 关系
    """
    import re
    res= []
    
    if not rel_ls:
        return '关系类别(rel)非法'
    else:
        
        rel = rel_ls[0]
#             value = query_related_entity_one(label,name,rel)
        cypher = "MATCH (n:`%s`{name:'%s'})-[r:`%s`]->(m) RETURN m"%(label,name,rel)
        result = pd.DataFrame(graph.run(cypher))
        print(label,name,rel)
        if result.empty:
            error = "查询'%s'的关系'%s'失败"%(name,rel)
            return error
        else:
            result_dict = dict(result[0])
            stri = str(result_dict)
            label_2 = re.findall(r"Node\(\'(.+?)\',",stri)[0]

            for item in result_dict.values():
                res_dict = {}
                
                if  item["name"]:name_2= item["name"]
                rel_2 = rel_ls[1]

                res_dict[rel] = name_2
                
                res.append(res_dict)
    
                cypher = "MATCH (n:`%s`{name:'%s'})-[r:`%s`]->(m) RETURN m"%(label_2,name_2,rel_2)
                result_2 = pd.DataFrame(graph.run(cypher))
#                     print(label_2,name_2,rel_2)
                if result_2.empty:
                    error = "查询'%s'的关系'%s'失败"%(name,rel)
                    return error
                else:
                    result_dict_2 = dict(result_2[0])
                    stri = str(result_dict_2)
                    label_3= re.findall(r"Node\(\'(.+?)\',",stri)[0]
                
#                     res_dict[rel_2] = query_related_entity_one(label,name,rel_2)
                for item2 in result_dict_2.values():
                    res_dict_3 = {}

                    if  item2["name"]:name_3= item2["name"]

                    res_dict[rel_2] = name_3
                    rel_3 = rel_ls[2]
#                         print(label_3,name_3,rel_3)
                    res_dict[rel_3]= queryRelEntity(label_3,name_3,rel_3)
                res.append(res_dict) 
    return res


if __name__ == "__main__":
    # 目前问题推测：
    # slot_key =['ent.equipName','pro.manufacturer']
    # slot_value =['EBZ160型掘机','生产厂家']
    # # 1、实体识别太差：数据集除了具体实体名称外，应该增加标签本身，比如华能集团、分公司这些的标注。有部分实体标签没用到，应该逐个在数据集里查查是否存在。
    # intent_pred="query_entity_property_one"
    # queryKG(intent_pred,slot_key,slot_value)
    # 2、模型推测出实体和关系后，需要进行实体链接，不然大多数实体和关系查库是查不到的。
    res = queryEntityPro_single('设备','EBZ160D型掘进机','生产厂家')
    # print("1.1 res ===== ",res)
    # res2 = queryEntityPro_multi('设备','EBZ160D型掘进机',['生产厂家','数量','使用场景'])
    # print("1.2 res ===== ",res2)
    # res3 = queryEntityAllPro_single('设备','EBZ160D型掘进机' )
    # print("1.3 res ===== ",res2)
    # res4 = queryEntityByLabel_single('设备',limitType=True,limit=25)
    # print("2.3 res ===== ",res4)
    # res5 = queryEntityByLabel_multi(['企业','设备'],limitType=True,limit=25)
    # print("2.5 res ===== ",res5)
    # res6 = queryEntityAllPro_multi(['设备','设备'],['ZFT18000/22/32D端头液压支架','EBZ160D型掘进机'])
    # print("2.6 res ===== ",res6)