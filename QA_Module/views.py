from django.shortcuts import render
import json
# Create your views here.
from flask import Flask, request, jsonify
#import pytorch_model  # 将 "your_model" 替换为你的模型名称
from django.http import HttpResponse
import torch
import string

import os
import re
import logging
import argparse
from tqdm import tqdm, trange
from QA_Module.zj_jointbert.predict import predict
from QA_Module.zj_jointbert.cypher import queryKG
from .inputPretreat import replace_text
# from predict import predict

from py2neo import Graph,Node,Relationship,NodeMatcher,RelationshipMatcher
from collections import defaultdict
import pandas as pd
import sys
import os

user = 'neo4j'
key = 'root'
graph=Graph("http://211.82.97.250:7606/browser/",auth=(user, key))
import numpy as np
import torch
from torch.utils.data import TensorDataset, DataLoader, SequentialSampler
# from QA_Module import predict
# from utils import init_logger, load_tokenizer, get_intent_labels, get_slot_labels, MODEL_CLASSES
logger = logging.getLogger(__name__)

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
def QaFuzzyName(name):
    sql = ("MATCH (f) WHERE f.name CONTAINS '%s' RETURN f.name AS fname") % (name)
    data = graph.run(sql).data()
    result = [x['fname'] for x in data]
    return result

def qa(request):
    # 获取前端发送的问题
    print("请求：%s"%request)
    if request.method=='POST':
        postbody=request.body
        param=json.loads(postbody.decode())
        question1=param['input']
        slot_pred_html='意图分类：'
        link_html =''

        # 输入预处理
        # question2=re.sub(r'[.,"\'-?:!;]', '', question1)
        punc='_+=|";:,?><…!@#￥%&+=“：’；、。，？》《{}'
        question2=re.sub(r"[%s]+"%punc,"",question1)
        # question2=question1.translate(str.maketrans('','',string.punctuation))
        print(question2)
        question3=question2.replace(' ','')
        question=" ".join(question3)
        print("问题：%s"%question)
        
        with open("/workspace/HNCoal/QA_Module/zj_jointbert/sample_pred_in.txt", 'r+') as file:
            file.truncate(0)
            file.close()
        with open("/workspace/HNCoal/QA_Module/zj_jointbert/sample_pred_out.txt", 'r+') as file:
            file.truncate(0)
            file.close()
        # 将问题传入模型

        # file = open('/workspace/zj_coal/HNCoal/QA_Module/zj_jointbert/sample_pred_in.txt','w')
        # file.write(question)
        # file.close()

        # 不带空格数据保存为字典形式并保存到json文件，目的是适配原有predict数据处理
        input_dict = {}
        # input_text = "708型烧结焊剂的全部属性和属性值"
        question3 = replace_text(question3)
        print("replace_text = ",question3)
        input_dict['text'] = question3
        with open("/workspace/HNCoal/QA_Module/zj_jointbert/input_data.json", 'w') as f:
            json.dump(input_dict, f, ensure_ascii=False)

        # 调用模型得到答案
        # init_logger()
        # if __name__=="__main__":
        
        parser = argparse.ArgumentParser()
        print("@@@@@@@@@@@")


        parser.add_argument("--input_file", default="/workspace/HNCoal/QA_Module/zj_jointbert/input_data.json", type=str, help="Input file for prediction")
        parser.add_argument("--output_file", default="/workspace/HNCoal/QA_Module/zj_jointbert/sample_pred_out.txt", type=str, help="Output file for prediction")
        parser.add_argument("--model_dir", default="/workspace/HNCoal/QA_Module/zj_jointbert/model_mine/bert_0518", type=str, help="Path to save, load model")

        parser.add_argument("--batch_size", default=32, type=int, help="Batch size for prediction")
        parser.add_argument("--no_cuda", action="store_true", help="Avoid using CUDA when available")

        pred_config = parser.parse_args(args=[])
        #     print("1111111")
        #     predict(pred_config)
        predict(pred_config)

        # 读取模型输出
        # with open('/workspace/zj_coal/HNCoal/QA_Module/zj_jointbert/sample_pred_out.txt','r',encoding='utf-8') as f:
        #     content = f.read()
        #     print("待处理输出：%s"%content)
        #     f.close()

        # 处理模型预测结果
        with open('/workspace/HNCoal/QA_Module/zj_jointbert/sample_pred_out.txt','r',encoding='utf-8') as f:
            line_pred = f.readline()
            try:
                tmp = line_pred.split('\t')
            except:
                print(line_pred)
            print("line_pred = ",line_pred)
            intent_pred = re.findall('<(.*?)>', tmp[1])[0]
            pattern = r"\[(.*?)\]"  # 正则提取方括号中的所有内容
            slot_pred = re.findall(pattern, tmp[0])
            print('slot_pred ====', slot_pred[0])
            print('intent_pred===', intent_pred)

            # yyt
            slot_pred_html+=intent_pred
            # slot_pred_html+='<br><br>槽位抽取结果：'+ slot_pred[0]
            slot_pred_html+='<br><br>槽位抽取：'

            slot_list = slot_pred[0].split(',')
            print("slot_list=====", slot_list)
            slot_dict = {}
            slot_key = []
            slot_val = []
            if [''] == slot_list:
                content = "Tips: 非煤矿领域问答，无法提供答案"
            else:
                for i in range(len(slot_list)):
                    slot = eval(slot_list[i])
                    print(slot)
                    slot_dict[i] = slot
                    key = list(slot.keys())
                    key = key[0]
                    slot_key.append(key)
                    slot_val.append(slot[key])
                    cla = {'ent': 'pj'
                        ,'pro' :'xm'
                        ,'rel' :'sb'
                        ,'lab':'gn'}
                    # yyt
                    slot_pred_html+='<span data-v-094c2d54 class="'+cla[key[:3]]+'" contenteditable="true">'+slot[key]+'</span>  <br>&emsp;&emsp;&emsp;&emsp;&emsp;'
              
                print("slot_key======", slot_key)
                print("slot_val======", slot_val)
                # print("slot_dict====",slot_dict)
                content,link_html = queryKG(intent_pred, slot_key, slot_val)
                print("没有后处理的查库文本",content)
# 如果拿到的content是错误，查询失败等，做处理。如果抽出来有实体或者关系，拿这个进行模糊查询，在这里引用QaFuzzyName函数
                # 如果查询到了，根据查询结果设置模板返回答案，如果查询不到，返回抱歉等语句。
        fuzzy_answer=[]
        if('失败' in content):
            # 只有一个实体，说明问的是单个实体，比如设备、矿山等的信息。1、设备返回技术参数2、矿山返回包含的东西
            if (len(slot_val) == 1):
                # 下面这种情况是针对单独输入一个设备时，匹配到与该设备最相似的设备，
                # 然后返回该设备的技术参数，假装意图是查单个设备的属性，属性自定义为技术参数
                if ("ent.equipName" in slot_key):
                    if (slot_val[0] == '设备'):
                        fuzzy_answer.append(QaFuzzyName(slot_val[0]))
                        print("在查库失败的情况下，返回给前端加上有用的模糊搜索后的相关信息：\n")
                        content="失败"+"--Tips:查询 实体-关系->实体(单个关系)"+str(fuzzy_answer)
                    else:
                        final_equipName = QaFuzzyName(slot_val[0])
                        print('模糊搜索后返回的相关信息：',final_equipName)
                        slot_key = ['ent.equipName','pro.techChara']
                        slot_val = [final_equipName[0],'技术特征']
                        content,link_html = queryKG("query_entity_property_one",slot_key,slot_val)
                # 如果不是问设备的，那么一个实体是查不出来的，直接模糊查询返回该实体的相关信息就行
                else:   
                    fuzzy_answer.append(QaFuzzyName(slot_val[0]))
                    print("在查库失败的情况下，返回给前端加上有用的模糊搜索后的相关信息：\n")
                    content="失败"+"--Tips:查询 实体-关系->实体(单个关系)"+str(fuzzy_answer)
            # 有多个实体，说明包含关系，但查询失败了，此时返回第一个实体包含的东西
            else:
                cypher = "MATCH (parent:`%s` {name: '%s'})-[:包含]->(child) RETURN child.name"%(entityLabel_dict[slot_key[0]],slot_val[0])
                result = pd.DataFrame(graph.run(cypher))
                print("只查第一个实体包含的东西：",result)
                result = result.values.tolist()
                flat_result = [item[0] for item in result]  
                content = "失败"+"--Tips:查询 实体-关系->实体(单个关系)" + str([flat_result])
                # 如果失败，加个判断，如果slot_key里面有两个及以上实体，用cypher语句返回第一个实体包含的所有东西，作为结果，不需要模糊搜索
                
                
                
                # print(fuzzy_answer)

            # else:
            #     print("content应该为抱歉，请提供更多有效信息。")
        if('error' in content):
            content = "未能理解您的意思，请您描述的更清晰一点。"


        # slot_pred_html='<span data-v-094c2d54 class="pj" contenteditable="true">DSJ80/40/2×1104210</span>'
        res = ''
        with open('/workspace/HNCoal/QA_Module/zj_jointbert/entity_link/cand_score.txt', "r", encoding="utf-8") as file:   
            lines=file.readlines()
            print('lines',lines)
            for i in range(len(lines)):
                res+=lines[i]
        link_html=res+'链接结果：&emsp;<span data-v-094c2d54 class="pj" contenteditable="true">'+link_html+'</span>'
        answer={
            'answer': content
            # ,'slot_pred' :slot_pred[0]
            ,'slot_pred_html' :slot_pred_html
            # ,'intent_pred':intent_pred
            ,'link_html':link_html
            }
        #print(answer.answer)
        # 将答案作为JSON数据返回给前端

    return HttpResponse(json.dumps(answer,ensure_ascii=False))


