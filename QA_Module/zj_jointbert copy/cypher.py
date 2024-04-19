# -*- codeing = utf-8 -*-
# @Time : 2023/5/18 4:10
# @Author : 剑
# @File : cypher.py
# @Software : PyCharm
import json

from py2neo import Graph,Node,Relationship,NodeMatcher,RelationshipMatcher
from collections import defaultdict
import pandas as pd

graph=Graph("http://211.82.97.250:7606/browser/",auth=("neo4j", "root"))

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
                    "query_entity_by_label_double":"",
                    "query_entity_by_label_single":"",
                    "query_entity_property_all_double":"",
                    "query_entity_property_all_single":"",
                    "query_entity_property_one":"",
                    "query_entity_property_two":"",
                    "query_related_entity_one":"",
                    "query_statistic_entity_all":""
                    }

entityLabel_dict = {"ent.mine_name":"所属矿山",
                   "ent.major_calss":"大类",
                   "ent.middle_class":"中类",
                   "ent.sub_class":"小类",
                   "ent.equip_name":"物料名",
                   "ent.department":"责任单位",
                   "ent.place":"使用地点",
                   "ent.factory":"生产厂家",
                   "ent.reference":"参考标准"
                   }
property_dict = {"ent.pro.number":"number",
                 "ent.pro.status":"status",
                 "ent.pro.specsi":"specsification",
                 "ent.pro.count":"count",
                 "ent.pro.equip_code":"equip_code",
                 "ent.pro.person_res":"person_res",
                 "ent.pro.factory_code":"factory_code",
                 "ent.pro.date_pro":"date_production",
                 "ent.pro.date_use":"date_use",
                 "ent.pro.tech_param":"tech_param",
                 "ent.pro.equip_desc":"equip_description",
                 "pro.name":"name",
                 "pro.number":"number",
                 "pro.status":"status",
                 "pro.specs":"specsification",
                 "pro.count":"count",
                 "pro.equip_code":"equip_code",
                 "pro.respon_name":"person_res",
                 "pro.factory_code":"factory_code",
                 "pro.product_date":"date_production",
                 "pro.use_date":"date_use",
                 "pro.tech_param":"tech_param",
                 "pro.equip_descri":"equip_description"
                 }
labelType_dict = {"label.equip_name":"物料名",
                  "label.reference":"参考标准",
                  "label.major_calss":"大类",
                  "label.middle_class":"中类",
                  "label.sub_class":"小类",
                  "label.mine_name":"所属矿山",
                  "label.department":"责任单位",
                  "label.place":"使用地点",
                  "label.factory":"生产厂家"
                  }
relType_dict = {"rel.place":"使用地点",
                "rel.reference":"参考标准",
                "rel.factory":"生产厂家",
                "rel.department":"责任单位",
                "rel.belong":"属于",
                "label.mine_name":"属于",
                "label.department":"责任单位",
                "label.place":"使用地点",
                "label.factory":"生产厂家",
                "label.reference":"参考标准"}

# 查询接口
def queryKG(intent_pred,slot_key,slot_value):
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
    elif "query_entity_by_label_double" == intent_pred:
        tips = "--Tips:按多个label查询所有实体"
        labelType_ls = []
        for key,value in zip(slot_key,slot_value):
            if 'label.' in key:
                if key in labelType_dict:
                    # print("key ##################### = ",key)
                    labelType_ls.append(labelType_dict[key])
                else:
                    key_error = 'slot_key error: slot_key not in labelType_dict'
                    return tips + "\n" + key_error
        answer = queryEntityByLabel_multi(labelType_ls,limitType=True,limit=25)
        answer = json.dumps(answer,indent=2,ensure_ascii=False) + "\n" + tips
        return answer
    elif "query_entity_by_label_single" == intent_pred:
        tips = "--Tips:按单个label查询所有实体"
        labelType = ''
        for key,value in zip(slot_key,slot_value):
            if 'label.' in key:
                if key in labelType_dict:
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
    elif "query_entity_property_all_double" == intent_pred:
        tips = "--Tips:查询多实体全部属性值"
        ent_label_ls = []
        ent_name_ls = []
        for key,value in zip(slot_key,slot_value):
            if 'ent.' in key:
                if key in entityLabel_dict:
                    label = entityLabel_dict[key]
                    ent_label_ls.append(label)
                    ent_name_ls.append(value)
                else:
                    key_error = 'slot_key error: slot_key not in entityLabel_dict'
                    return tips + "\n" + key_error
        answer = queryEntityAllPro_multi(ent_label_ls,ent_name_ls)
        answer = json.dumps(answer,indent=2,ensure_ascii=False) + "\n" + tips
        return answer
    elif "query_entity_property_all_single" == intent_pred:
        tips = "--Tips:查询单实体全部属性值"
        ent_label = ''
        ent_name = ''
        for key,value in zip(slot_key,slot_value):
            if 'ent.' in key:
                if key in entityLabel_dict:
                    ent_label = entityLabel_dict[key]
                    ent_name = value
                else:
                    key_error = 'slot_key error: slot_key not in entityLabel_dict'
                    return tips + "\n" + key_error
            break    # 只查询第1个实体的属性

        answer = queryEntityAllPro_single(ent_label,ent_name)
        answer = json.dumps(answer,indent=2,ensure_ascii=False) + "\n" + tips
        return answer
    elif "query_entity_property_one" == intent_pred:
        tips = "--Tips:查询单实体单个属性值"
        ent_label = ""
        ent_name = ""
        ent_pro_key = ""
        for key,value in zip(slot_key,slot_value):
            if "ent.pro." in key:
                if key in property_dict:
                    ent_pro_key = property_dict[key]
                else:
                    key_error = 'slot_key error: slot_key not in property_dict'
                    return tips + "\n" + key_error
            elif "pro." in key:
                if key in property_dict:
                    ent_pro_key = property_dict[key]
                else:
                    key_error = 'slot_key error: slot_key not in property_dict'
                    return tips + "\n" + key_error
            elif "ent." in key:
                if key in entityLabel_dict:
                    ent_label = entityLabel_dict[key]
                    ent_name = value
                else:
                    key_error = 'slot_key error: slot_key not in entityLabel_dict'
                    return tips + "\n" + key_error
        print("ent_label = ",ent_label)
        print("ent_name == ",ent_name)
        print("ent_pro === ",ent_pro_key)
        if ent_label and ent_name and ent_pro_key:
            answer = queryEntityPro_single(ent_label,ent_name,ent_pro_key)
            answer = json.dumps(answer, indent=2, ensure_ascii=False) + "\n" + tips
            return answer
        else:
            queryParam_error = 'queryParam_error: missing ent_label or ent_name or ent_pro_key'
            return queryParam_error + "\n" + tips
    elif "query_entity_property_two" == intent_pred:
        tips = "--Tips:查询单实体多个属性值"
        ent_label = ""
        ent_name = ""
        ent_pro_ls = []
        for key,value in zip(slot_key,slot_value):
            if "ent." in key:
                if key in entityLabel_dict:
                    ent_label = entityLabel_dict[key]
                    ent_name = value
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
    elif "query_related_entity_one" == intent_pred:
        tips = "--Tips:查询 实体-关系->实体(单个关系)"
        for key,value in zip(slot_key,slot_value):
            if 'ent.' in key:
                if key in entityLabel_dict:
                    ent_label = entityLabel_dict[key]
                    ent_name = value
                else:
                    key_error = 'slot_key error: slot_key not in entityLabel_dict'
                    return tips + "\n" + key_error
            elif 'rel.' in key:
                if key in relType_dict:
                    rel = relType_dict[key]
                else:
                    key_error = 'slot_key error: slot_key not in relType_dict'
                    return tips + "\n" + key_error
        if ent_label and ent_name and rel:
            answer = queryRelEntity(ent_label,ent_name,rel)
            answer = json.dumps(answer,indent=2,ensure_ascii=False) + "\n" + tips
            return answer
        else:
            queryParam_error = 'queryParam_error: missing ent_label or ent_name or relationship '
            return tips + '\n' + queryParam_error
    elif "query_statistic_entity_all" == intent_pred:
        tips = "--Tips:实体<-关系-实体(统计所有关系实体)"

        ent_label = ''
        ent_name = ''
        rel = ''
        for key,value in zip(slot_key,slot_value):
            if 'ent.' in key:
                if key in entityLabel_dict:
                    ent_label = entityLabel_dict[key]
                    ent_name = value
                else:
                    key_error = 'slot_key error: slot_key not in entityLabel_dict'
                    return tips + "\n" + key_error
            elif 'rel.' or 'label.' in key:
                print("------------------------slot_key = ",key)
                if key in relType_dict:
                    rel = relType_dict[key]
                else:
                    key_error = 'slot_key error: slot_key not in relType_dict'
                    return tips + "\n" + key_error
        if not rel:
            rel = relType_dict["rel.belong"] # 默认查询 属于 关系
        if ent_label and ent_name and rel:
            answer = queryRelEntity_multi(ent_label,ent_name,rel)
            answer = json.dumps(answer,indent=2,ensure_ascii=False) + "\n" + tips
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
            res_dict[pro] = value
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
        return result_dict

# 2.2 查询多实体属性（全部属性值）
def queryEntityAllPro_multi(label_ls,name_ls):
    '''
    label:实体label
    name_ls:实体名称列表
    '''
    res_dict = {}
    if not name_ls:
        return '物料名非法'
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
            result_dict_2 = dict(result_2[0])
            return result_dict_2
    else:
        cypher_1 = "MATCH (n:`%s`) RETURN n"%(labelType)
        result_1 = pd.DataFrame(graph.run(cypher_1))
        if result_1.empty:
            res = "查询'%s'所有实体失败"%(labelType)
            return res
        else:
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

    cypher = "MATCH (n:`%s`{name:'%s'})-[r:`%s`]->(m) RETURN m" % (label, name, rel)
    result = pd.DataFrame(graph.run(cypher))
    if result.empty:
        error = "查询'%s'的关系'%s'失败" % (name, rel)
        return error
    else:
        result_dict = dict(result[0][0])
        #         print(result_dict)
        return result_dict["name"]

# 4.2 查询 实体<-关系-实体(多关系实体统计)
def queryRelEntity_multi(label,name,rel):
    """
    label: 实体label
    name: 实体名
    rel: 关系
    """
    name_dict = {}
    cypher = "MATCH (n:`%s`{name:'%s'})<-[r:`%s`]-(m) RETURN m"%(label,name,rel)
    result = pd.DataFrame(graph.run(cypher))
    if result.empty:
        error = "查询'%s'的关系'%s'失败"%(name,rel)
        return error
    else:
        result_dict = dict(result[0])

        for i in result_dict:
            node_name = result_dict[i]["name"]
            name_dict[i+1] = node_name

        return name_dict


if __name__ == "__main__":

    res = queryEntityPro_single('物料名','成型盘根','factory_code')
    print("1.1 res ===== ",res)