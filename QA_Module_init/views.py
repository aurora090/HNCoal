from django.shortcuts import render
import json
# Create your views here.
from flask import Flask, request, jsonify
#import pytorch_model  # 将 "your_model" 替换为你的模型名称
from django.http import HttpResponse
import torch
import string

import os
import logging
import argparse
from tqdm import tqdm, trange
from QA_Module.zj_jointbert.predicted import predict
# from predict import predict

import numpy as np
import torch
from torch.utils.data import TensorDataset, DataLoader, SequentialSampler
# from QA_Module import predict
# from utils import init_logger, load_tokenizer, get_intent_labels, get_slot_labels, MODEL_CLASSES
logger = logging.getLogger(__name__)
def qa(request):
    # 获取前端发送的问题
    print("请求：%s"%request)
    if request.method=='POST':
        postbody=request.body
        param=json.loads(postbody.decode())
        question1=param['input']
        # 输入预处理
        # question2=re.sub(r'[.,"\'-?:!;]', '', question1)
        question2=question1.translate(str.maketrans('','',string.punctuation))
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
        file = open('/workspace/HNCoal/QA_Module/zj_jointbert/sample_pred_in.txt','w')
        file.write(question)
        file.close()
        # 调用模型得到答案
        # init_logger()
        # if __name__=="__main__":
        
        parser = argparse.ArgumentParser()
        print("1111111")
        parser.add_argument("--input_file", default="/workspace/HNCoal/QA_Module/zj_jointbert/sample_pred_in.txt", type=str, help="Input file for prediction")
        print("1111111")
        parser.add_argument("--output_file", default="/workspace/HNCoal/QA_Module/zj_jointbert/sample_pred_out.txt", type=str, help="Output file for prediction")
        parser.add_argument("--model_dir", default="/workspace/HNCoal/QA_Module/zj_jointbert/model_mine/mk_major_000", type=str, help="Path to save, load model")

        parser.add_argument("--batch_size", default=32, type=int, help="Batch size for prediction")
        parser.add_argument("--no_cuda", action="store_true", help="Avoid using CUDA when available")

        pred_config = parser.parse_args(args=[])
        #     print("1111111")
        #     predict(pred_config)
        predict(pred_config)

        # 读取模型输出
        with open('/workspace/HNCoal/QA_Module/zj_jointbert/sample_pred_out.txt','r',encoding='utf-8') as f:
            content = f.read()
            print("模型答案是：%s"%content)
            f.close()
        
        # answer={ "0": { "number": "lq_06d", "name": "库房管理部" }, "1": { "number": "lq_01d", "name": "采煤队" }, "2": { "number": "lq_05d", "name": "掘进队" }, "3": { "number": "lq_09d", "name": "运输队" }, "4": { "number": "lq_03d", "name": "机电队" }, "5": { "number": "lq_08d", "name": "通风队" }, "6": { "number": "lq_07d", "name": "提升队" }, "7": { "number": "lq_04d", "name": "技术部" }, "8": { "number": "lq_02d", "name": "测绘部" }, "9": { "number": "ehj_06d", "name": "库房管理部" }, "10": { "number": "ehj_01d", "name": "采煤队" }, "11": { "number": "ehj_05d", "name": "掘进队" }, "12": { "number": "ehj_09d", "name": "运输队" }, "13": { "number": "ehj_03d", "name": "机电队" }, "14": { "number": "ehj_08d", "name": "通风队" }, "15": { "number": "ehj_07d", "name": "提升队" }, "16": { "number": "ehj_04d", "name": "技术部" }, "17": { "number": "ehj_02d", "name": "测绘部" }, "18": { "number": "gq_06d", "name": "库房管理部" }, "19": { "number": "gq_01d", "name": "采煤队" }, "20": { "number": "gq_05d", "name": "掘进队" }, "21": { "number": "gq_09d", "name": "运输队" }, "22": { "number": "gq_03d", "name": "机电队" }, "23": { "number": "gq_08d", "name": "通风队" }, "24": { "number": "gq_07d", "name": "提升队" } } --Tips:按单个label查询所有实体
        answer={
            'answer': content
            }
        print(answer.answer)
        # 将答案作为JSON数据返回给前端

    return HttpResponse(json.dumps(answer,ensure_ascii=False))
       

