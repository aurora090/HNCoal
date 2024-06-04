import json
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
import textract
from zhipuai import ZhipuAI
import re

def find_text(t):
	# /root/lmc/test_precison_raw.json
    with open('/workspace/django_project/ner/sxp/test_precison_raw.json', 'r') as file:
        data = file.readlines()
        for i in data:
            if t in json.loads(i)['text']:
                k = json.loads(i)['spo_list']
                formatted_texts = []

                for item in k:
                    for key, value in item.items():
                        formatted_texts.append(u"{}-{}".format(key, value))
                formatted_texts=set(formatted_texts)
                formatted_output = ", ".join(formatted_texts)
                return json.dumps(formatted_output, ensure_ascii=False)

        return u"不在测试集里，无法判断准确率".encode('utf-8')
def train():
    with open('/workspace/django_project/ner/sxp/test_precison_raw.json', 'r') as file:
        text_example=""
        for i in range(200):
            data = file.readline().strip()
            t= json.loads(data)['text']
            k = json.loads(data)['spo_list']
            formatted_texts = []

            for item in k:
                for key, value in item.items():
                    formatted_texts.append(u"{}-{}".format(key, value))
            formatted_texts=set(formatted_texts)
            formatted_output = ",".join(formatted_texts)
            text_example+="示例："+t+"\n抽取结果："+formatted_output+'\n'
    print(text_example)
    return text_example

def ke(request):
    print("请求：%s" % request)
    post_content = json.loads(request.body, encoding="utf-8")["text"]
    print("post_content是："+post_content)
    text_example=train()
            
    client = ZhipuAI(
        api_key="18377c6f50375bbbea94bec39dc3a731.T4s34XVox3s73LSG"
    )  # 填写您自己的APIKey
    response = client.chat.completions.create(
        model="glm-4",  # 填写需要调用的模型名称
        messages=[
            {
                "role": "system",
                "content": "你是一个煤矿领域的专家，你的任务是从一句话中抽取出存在的实体，实体的标签必须为以下9种：配件、项目、机电设备、功能、特点、方法、矿山、设备参数、企业。回答问题尽可能简短，不需要注意等说明",
            },
            {
                "role": "assistant",
                "content": "当然，请为我提供一些示例，以便在我学习这些示例后提供更准确的结果",
            },
            {
                "role": "user",
                "content": "以下是我为你提供的示例：\n"+text_example,
            },
            {
                "role": "assistant",
                "content": "好的，我已经完成学习这些示例",
            },
            {
                "role": "user",
                "content": post_content,
            },
            {
                "role": "user",
                "content": "提取这句话中的实体，格式依照样示例中格式"
            },
        ],
    )
    returntext = response.choices[0].message.content
    print("测试结果："+ returntext)
    returntext=returntext.split(',')
    print("分割后:")
    print(returntext)
    l = []
    for line in returntext:
        if line=='':
            continue
        words = line.split("-")
        if len(words) <2:
            continue
        flag = words[1]
        ent = words[0]
        if flag == "机电设备":
            l.append('<span data-v-094c2d54 class="sb" contenteditable="true">' + ent + '</span>')
        elif flag == "矿山":
            l.append('<span data-v-094c2d54 class="ks" contenteditable="true">' + ent + '</span>')
        elif flag == "配件":
            l.append('<span data-v-094c2d54 class="pj" contenteditable="true">' + ent + '</span>')
        elif flag == "功能":
            l.append('<span data-v-094c2d54 class="gn" contenteditable="true">' + ent + '</span>')
        elif flag == "项目":
            l.append('<span data-v-094c2d54 class="xm" contenteditable="true">' + ent + '</span>')
        elif flag == "特点":
            l.append('<span data-v-094c2d54 class="td" contenteditable="true">' + ent + '</span>')
        elif flag == "参数":
            l.append('<span data-v-094c2d54 class="cs" contenteditable="true">' + ent + '</span>')
        elif flag == "矿山":
            l.append('<span data-v-094c2d54 class="ks" contenteditable="true">' + ent + '</span>')
        elif flag == "方法":
            l.append('<span data-v-094c2d54 class="ff" contenteditable="true">' + ent + '</span>')
        elif flag == "企业":
            l.append('<span data-v-094c2d54 class="qy" contenteditable="true">' + ent + '</span>')
    li = '       '.join(l)
    acc=0
    if not li:
        return HttpResponse('<div style="font-size:20px;line-height:50px">' + "未能发现实体" + '</div>')

    return HttpResponse(li+'<div style="font-size:20px;line-height:50px">' + '正确抽取结果为:'+find_text(post_content) )
