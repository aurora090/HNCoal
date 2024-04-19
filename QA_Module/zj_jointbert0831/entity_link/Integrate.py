# 导入必要的包
import xlrd
import torch.nn.functional as F
import torch
import transformers
import torch.nn as nn
from flask import request, make_response
from flask import Flask
from io import BytesIO
import xlsxwriter
from flask_cors import CORS
from transformers import BertModel, BertTokenizer


# BERT部分
# 模型中的训练过程
# 池化
class GlobalMaxPool1d(nn.Module):
    def __init__(self):
        super(GlobalMaxPool1d, self).__init__()

    def forward(self, x):
        # x shape: (batch_size, channel, seq_len)
        return F.max_pool1d(x, kernel_size=x.shape[2])  # shape: (batch_size, channel, 1)

# Bert模型
class TextBert(nn.Module):
    def __init__(self, vocab_size, embedding_dim, kernel_sizes, num_channels):
        super(TextBert, self).__init__()
        # 文本
        self.word_embeddings = nn.Embedding(vocab_size, embedding_dim)  # embedding之后的shape: torch.Size([200, 8, 300])
        self.dropout = nn.Dropout(0.5)
        # 时序最大池化层没有权重，所以可以共用一个实例
        self.pool = GlobalMaxPool1d()
        self.convs = nn.ModuleList()  # 创建多个一维卷积层
        for c, k in zip(num_channels, kernel_sizes):
            self.convs.append(nn.Conv1d(in_channels=embedding_dim,
                                        out_channels=c,
                                        kernel_size=k))
        pretrained_weights = '/workspace/zj_coal/HNCoal/QA_Module/zj_jointbert/model_mine/bert_base_chinese'
        self.bert = transformers.BertModel.from_pretrained(pretrained_weights)
        for param in self.bert.parameters():
            param.requires_grad = True

        # 定义线性函数
        self.dense = nn.Linear(768, 2)  # bert默认的隐藏单元数是768， 输出单元是2，表示二分类

    def forward(self, input_ids, token_type_ids, attention_mask):
        # 文本
        # 得到bert_output
        bert_output = self.bert(input_ids=input_ids, token_type_ids=token_type_ids, attention_mask=attention_mask)
        # 提取[CLS]对应的隐藏状态
        # bert_cls_hidden_state = bert_output[0][:,0,:]
        bert_cls_hidden_state = bert_output[0][:, 1:-1, :]
        # print("bert_cls_hidden_state.shape:",bert_cls_hidden_state.shape)
        # 将词向量转换为句子向量
        sentence_emd = torch.sum(bert_output[0][:, 1:-1, :], dim=1)  # (b,768)
        # 对于每个一维卷积层，在时序最大池化后会得到一个形状为(批量大小, 通道大小, 1)的
        # Tensor使用flatten函数去掉最后一维，然后在通道维上连结
        predict = self.dense(sentence_emd)
        return predict

# ALBERT部分
# 模型中的训练过程
class GlobalMaxPool1d(nn.Module):
    def __init__(self):
        super(GlobalMaxPool1d, self).__init__()

    def forward(self, x):
        # x shape: (batch_size, channel, seq_len)
        return F.max_pool1d(x, kernel_size=x.shape[2])  # shape: (batch_size, channel, 1)

# alBert模型
class TextBert(nn.Module):
    def __init__(self, vocab_size, embedding_dim, kernel_sizes, num_channels):
        super(TextBert, self).__init__()
        # 文本
        self.word_embeddings = nn.Embedding(vocab_size, embedding_dim)  # embedding之后的shape: torch.Size([200, 8, 300])
        self.dropout = nn.Dropout(0.5)
        # 时序最大池化层没有权重，所以可以共用一个实例
        self.pool = GlobalMaxPool1d()
        self.convs = nn.ModuleList()  # 创建多个一维卷积层
        for c, k in zip(num_channels, kernel_sizes):
            self.convs.append(nn.Conv1d(in_channels=embedding_dim,
                                        out_channels=c,
                                        kernel_size=k))
        pretrained_weights = '/workspace/zj_coal/HNCoal/QA_Module/zj_jointbert/model_mine/albert_base_chinese_cluecorpussmall'
        self.bert = transformers.BertModel.from_pretrained(pretrained_weights)
        for param in self.bert.parameters():
            param.requires_grad = True

        # 定义线性函数
        self.dense = nn.Linear(768, 2)  # bert默认的隐藏单元数是768， 输出单元是2，表示二分类

    def forward(self, input_ids, token_type_ids, attention_mask):
        # 文本
        # 得到bert_output
        bert_output = self.bert(input_ids=input_ids, token_type_ids=token_type_ids, attention_mask=attention_mask)
        # #提取[CLS]对应的隐藏状态
        # bert_cls_hidden_state = bert_output[0][:,0,:]
        bert_cls_hidden_state = bert_output[0][:, 1:-1, :]
        #         print("bert_cls_hidden_state.shape:",bert_cls_hidden_state.shape)
        # 将词向量转换为句子向量
        sentence_emd = torch.sum(bert_output[0][:, 1:-1, :], dim=1)  # (b,768)
        # 对于每个一维卷积层，在时序最大池化后会得到一个形状为(批量大小, 通道大小, 1)的
        # Tensor。使用flatten函数去掉最后一维，然后在通道维上连结
        predict = self.dense(sentence_emd)
        return predict

# RoBERTa部分
# 模型中的训练过程

class GlobalMaxPool1d(nn.Module):
    def __init__(self):
        super(GlobalMaxPool1d, self).__init__()

    def forward(self, x):
        # x shape: (batch_size, channel, seq_len)
        return F.max_pool1d(x, kernel_size=x.shape[2])  # shape: (batch_size, channel, 1)

class TextBert(nn.Module):
    def __init__(self, vocab_size, embedding_dim, kernel_sizes, num_channels):
        super(TextBert, self).__init__()
        # 文本
        self.word_embeddings = nn.Embedding(vocab_size, embedding_dim)  # embedding之后的shape: torch.Size([200, 8, 300])
        self.dropout = nn.Dropout(0.5)
        # 时序最大池化层没有权重，所以可以共用一个实例
        self.pool = GlobalMaxPool1d()
        self.convs = nn.ModuleList()  # 创建多个一维卷积层
        for c, k in zip(num_channels, kernel_sizes):
            self.convs.append(nn.Conv1d(in_channels=embedding_dim,
                                        out_channels=c,
                                        kernel_size=k))
        pretrained_weights = '/workspace/zj_coal/HNCoal/QA_Module/zj_jointbert/model_mine/chinese-roberta-wwm-ext'
        self.bert = transformers.BertModel.from_pretrained(pretrained_weights)
        for param in self.bert.parameters():
            param.requires_grad = True

        # 定义线性函数
        self.dense = nn.Linear(768, 2)  # bert默认的隐藏单元数是768， 输出单元是2，表示二分类

    def forward(self, input_ids, token_type_ids, attention_mask):
        # 文本
        # 得到bert_output
        bert_output = self.bert(input_ids=input_ids, token_type_ids=token_type_ids, attention_mask=attention_mask)
        # #提取[CLS]对应的隐藏状态
        # bert_cls_hidden_state = bert_output[0][:,0,:]
        bert_cls_hidden_state = bert_output[0][:, 1:-1, :]
        #         print("bert_cls_hidden_state.shape:",bert_cls_hidden_state.shape)
        # 将词向量转换为句子向量
        sentence_emd = torch.sum(bert_output[0][:, 1:-1, :], dim=1)  # (b,768)
        # 对于每个一维卷积层，在时序最大池化后会得到一个形状为(批量大小, 通道大小, 1)的
        # Tensor。使用flatten函数去掉最后一维，然后在通道维上连结

        predict = self.dense(sentence_emd)
        # 使用dropout
        predict = self.dropout(predict)
        return predict

# ernie部分
# 模型中的训练过程
class GlobalMaxPool1d(nn.Module):
    def __init__(self):
        super(GlobalMaxPool1d, self).__init__()
    def forward(self, x):
         # x shape: (batch_size, channel, seq_len)
        return F.max_pool1d(x, kernel_size=x.shape[2]) # shape: (batch_size, channel, 1)


class TextBert(nn.Module):
    def __init__(self, vocab_size, embedding_dim, kernel_sizes, num_channels):
        super(TextBert, self).__init__()
        # 文本
        self.word_embeddings = nn.Embedding(vocab_size, embedding_dim)  # embedding之后的shape: torch.Size([200, 8, 300])
        self.dropout = nn.Dropout(0.7)
        # 时序最大池化层没有权重，所以可以共用一个实例
        self.pool = GlobalMaxPool1d()
        self.convs = nn.ModuleList()  # 创建多个一维卷积层
        for c, k in zip(num_channels, kernel_sizes):
            self.convs.append(nn.Conv1d(in_channels=embedding_dim,
                                        out_channels=c,
                                        kernel_size=k))
        pretrained_weights = '/workspace/zj_coal/HNCoal/QA_Module/zj_jointbert/model_mine/ernie'
        self.bert = transformers.AutoModel.from_pretrained(pretrained_weights)
        for param in self.bert.parameters():
            param.requires_grad = True

        # 定义线性函数
        self.dense = nn.Linear(768, 2)  # bert默认的隐藏单元数是768， 输出单元是2，表示二分类

    def forward(self, input_ids, token_type_ids, attention_mask):
        # 文本
        # 得到bert_output
        bert_output = self.bert(input_ids=input_ids, token_type_ids=token_type_ids, attention_mask=attention_mask)
        # #提取[CLS]对应的隐藏状态
        # bert_cls_hidden_state = bert_output[0][:,0,:]
        bert_cls_hidden_state = bert_output[0][:, 1:-1, :]
        #         print("bert_cls_hidden_state.shape:",bert_cls_hidden_state.shape)
        # 将词向量转换为句子向量
        sentence_emd = torch.sum(bert_output[0][:, 1:-1, :], dim=1)  # (b,768)
        # 对于每个一维卷积层，在时序最大池化后会得到一个形状为(批量大小, 通道大小, 1)的
        # Tensor。使用flatten函数去掉最后一维，然后在通道维上连结
        predict = self.dense(sentence_emd)
        # 使用dropout
        predict = self.dropout(predict)
        return predict

# wwm部分
# 模型中的训练过程
class GlobalMaxPool1d(nn.Module):
    def __init__(self):
        super(GlobalMaxPool1d, self).__init__()
    def forward(self, x):
         # x shape: (batch_size, channel, seq_len)
        return F.max_pool1d(x, kernel_size=x.shape[2]) # shape: (batch_size, channel, 1)


class TextBert(nn.Module):
    def __init__(self, vocab_size, embedding_dim, kernel_sizes, num_channels):
        super(TextBert, self).__init__()
        # 文本
        self.word_embeddings = nn.Embedding(vocab_size, embedding_dim)  # embedding之后的shape: torch.Size([200, 8, 300])
        self.dropout = nn.Dropout(0.5)
        # 时序最大池化层没有权重，所以可以共用一个实例
        self.pool = GlobalMaxPool1d()
        self.convs = nn.ModuleList()  # 创建多个一维卷积层
        for c, k in zip(num_channels, kernel_sizes):
            self.convs.append(nn.Conv1d(in_channels=embedding_dim,
                                        out_channels=c,
                                        kernel_size=k))
        pretrained_weights = '/workspace/zj_coal/HNCoal/QA_Module/zj_jointbert/model_mine/bert-wwm'
        self.bert = transformers.BertModel.from_pretrained(pretrained_weights)
        for param in self.bert.parameters():
            param.requires_grad = True

        # 定义线性函数
        self.dense = nn.Linear(768, 2)  # bert默认的隐藏单元数是768， 输出单元是2，表示二分类

    def forward(self, input_ids, token_type_ids, attention_mask):
        # 文本
        # 得到bert_output
        bert_output = self.bert(input_ids=input_ids, token_type_ids=token_type_ids, attention_mask=attention_mask)
        # #提取[CLS]对应的隐藏状态
        # bert_cls_hidden_state = bert_output[0][:,0,:]
        bert_cls_hidden_state = bert_output[0][:, 1:-1, :]
        #         print("bert_cls_hidden_state.shape:",bert_cls_hidden_state.shape)
        # 将词向量转换为句子向量
        sentence_emd = torch.sum(bert_output[0][:, 1:-1, :], dim=1)  # (b,768)

        # 对于每个一维卷积层，在时序最大池化后会得到一个形状为(批量大小, 通道大小, 1)的
        # Tensor。使用flatten函数去掉最后一维，然后在通道维上连结
        predict = self.dense(sentence_emd)
        # 使用dropout
        predict = self.dropout(predict)
        return predict


# Flask后台框架连接部分
# Flask跨域请求
app = Flask(__name__)
CORS(app, supports_credentials=True)


# 定义请求方法
@app.route('/get_integrate', methods=['POST'])
# 单个预测
def get_pre_fusion():
    print("开始预测。。。。。")
    json = request.get_json()  # 调用服务器时输入的json字符串
    real_data = json['params']
    text = real_data['shuju']
    #  模型内部数据处理
    pretrain_model_uri = "/workspace/zj_coal/HNCoal/QA_Module/zj_jointbert/model_mine/bert-base-chinese"
    tokenizer = BertTokenizer.from_pretrained(pretrain_model_uri)

    Albert_pretrain_uri = "/workspace/zj_coal/HNCoal/QA_Module/zj_jointbert/model_mine/albert"
    altokenizer = BertTokenizer.from_pretrained(Albert_pretrain_uri)

    Robert_pretrain_uri = "/workspace/zj_coal/HNCoal/QA_Module/zj_jointbert/model_mine/roberta"
    rotokenizer = BertTokenizer.from_pretrained(Robert_pretrain_uri)

    ERNIE_pretrain_uri = "/workspace/zj_coal/HNCoal/QA_Module/zj_jointbert/model_mine/ernie"
    ertokenizer = BertTokenizer.from_pretrained(ERNIE_pretrain_uri)

    WWM_pretrain_uri = "/workspace/zj_coal/HNCoal/QA_Module/zj_jointbert/model_mine/bert-wwm"
    wwmtokenizer = BertTokenizer.from_pretrained(WWM_pretrain_uri)

#   特征提取（文本转化为tensor）
    encoded_dict = tokenizer.encode_plus(
        text,
        add_special_tokens=True,
        max_length=64,
        pad_to_max_length=True,
        return_attention_mask=True,
        return_tensors='pt',
        truncation=True
    )
    alencoded_dict = altokenizer.encode_plus(
        text,
        add_special_tokens=True,
        max_length=64,
        pad_to_max_length=True,
        return_attention_mask=True,
        return_tensors='pt',
        truncation=True
    )
    roencoded_dict = rotokenizer.encode_plus(
        text,
        add_special_tokens=True,
        max_length=64,
        pad_to_max_length=True,
        return_attention_mask=True,
        return_tensors='pt',
        truncation=True
    )
    erencoded_dict = ertokenizer.encode_plus(
        text,
        add_special_tokens=True,
        max_length=64,
        pad_to_max_length=True,
        return_attention_mask=True,
        return_tensors='pt',
        truncation=True
    )
    wwmencoded_dict = wwmtokenizer.encode_plus(
        text,
        add_special_tokens=True,
        max_length=64,
        pad_to_max_length=True,
        return_attention_mask=True,
        return_tensors='pt',
        truncation=True
    )

    b_input_ids = encoded_dict["input_ids"]
    attention_mask = encoded_dict["attention_mask"]
    alb_input_ids = alencoded_dict["input_ids"]
    alattention_mask = alencoded_dict["attention_mask"]
    rob_input_ids = roencoded_dict["input_ids"]
    roattention_mask = roencoded_dict["attention_mask"]
    erb_input_ids = erencoded_dict["input_ids"]
    erattention_mask = erencoded_dict["attention_mask"]
    wwmb_input_ids = wwmencoded_dict["input_ids"]
    wwmattention_mask = wwmencoded_dict["attention_mask"]

    bertmodel = torch.load('./file/BERT_model.pkl')
    albertmodel = torch.load('./file/ALBERT_model.pkl')
    robertmodel = torch.load('./file/RoBERTa_model.pkl')
    erbertmodel = torch.load('./file/ERNIE_model.pkl')
    wwmbertmodel = torch.load('./file/BERT_wwm_model.pkl')

#   input_ids: 将输入到的词映射到模型当中的字典ID
#   如果不传入attention_mask，模型会自动全部用1填充。

    outputs = bertmodel(b_input_ids, token_type_ids=None,
                        attention_mask=attention_mask)
    aloutputs = albertmodel(alb_input_ids, token_type_ids=None,
                            attention_mask=alattention_mask)
    rooutputs = robertmodel(rob_input_ids, token_type_ids=None,
                            attention_mask=roattention_mask)
    eroutputs = erbertmodel(erb_input_ids, token_type_ids=None,
                            attention_mask=erattention_mask)
    wwmoutputs = wwmbertmodel(wwmb_input_ids, token_type_ids=None,
                              attention_mask=wwmattention_mask)
#   将tensor转为numpy
    logits = outputs.detach().cpu().numpy()
    allogits = aloutputs.detach().cpu().numpy()
    rologits = rooutputs.detach().cpu().numpy()
    erlogits = eroutputs.detach().cpu().numpy()
    wwmlogits = wwmoutputs.detach().cpu().numpy()

    pre_list = sum(logits.tolist(), [])
    alpre_list = sum(allogits.tolist(), [])
    ropre_list = sum(rologits.tolist(), [])
    erpre_list = sum(erlogits.tolist(), [])
    wwmpre_list = sum(wwmlogits.tolist(), [])

    predict_int = pre_list.index(max(pre_list))
    alpredict_int = alpre_list.index(max(alpre_list))
    ropredict_int = ropre_list.index(max(ropre_list))
    erpredict_int = erpre_list.index(max(erpre_list))
    wwmpredict_int = wwmpre_list.index(max(wwmpre_list))

#   汇总
    final_dict = []
    final_dict.append(predict_int)
    final_dict.append(alpredict_int)
    final_dict.append(ropredict_int)
    final_dict.append(erpredict_int)
    final_dict.append(wwmpredict_int)

# 投票逻辑代码
    yes = 0
    no = 0
    final = 0
    for i in final_dict:
        if (i == 0):
            no += 1
        else:
            yes += 1
    if (yes > no):
        final = 1
    else:
        final = 0
    #pre_dict = {'text': final }
    new_dict = {"result": final}
    print(new_dict)  # 输出参数维度
    return new_dict

# 定义请求方法
@app.route('/integrate/import/batch', methods=['POST'])
# 批量预测
def get_batch_integrate():
    print("开始批量预测。。。。。")
    file = request.files['file']
    f = file.read()  # 文件内容
    data = xlrd.open_workbook(file_contents=f)
    table = data.sheets()[0]
    s = table.col_values(0, start_rowx=0, end_rowx=None)  # 第1列数据忽略
    big_list = []  # 定义存放数据列表
    for text in s:
        pretrain_model_uri = "/workspace/zj_coal/HNCoal/QA_Module/zj_jointbert/model_mine/bert-base-chinese"
        tokenizer = BertTokenizer.from_pretrained(pretrain_model_uri)

        Albert_pretrain_uri= "/workspace/zj_coal/HNCoal/QA_Module/zj_jointbert/model_mine/albert"
        altokenizer = BertTokenizer.from_pretrained(Albert_pretrain_uri)

        Robert_pretrain_uri = "/workspace/zj_coal/HNCoal/QA_Module/zj_jointbert/model_mine/roberta"
        rotokenizer = BertTokenizer.from_pretrained(Robert_pretrain_uri)

        ERNIE_pretrain_uri = "/workspace/zj_coal/HNCoal/QA_Module/zj_jointbert/model_mine/ernie"
        ertokenizer = BertTokenizer.from_pretrained(ERNIE_pretrain_uri)

        WWM_pretrain_uri = "/workspace/zj_coal/HNCoal/QA_Module/zj_jointbert/model_mine/bert-wwm"
        wwmtokenizer = BertTokenizer.from_pretrained(WWM_pretrain_uri)

        encoded_dict = tokenizer.encode_plus(
            text,
            add_special_tokens=True,
            max_length=64,
            pad_to_max_length=True,
            return_attention_mask=True,
            return_tensors='pt',
            truncation=True
        )
        alencoded_dict = altokenizer.encode_plus(
            text,
            add_special_tokens=True,
            max_length=64,
            pad_to_max_length=True,
            return_attention_mask=True,
            return_tensors='pt',
            truncation=True
        )
        roencoded_dict = rotokenizer.encode_plus(
            text,
            add_special_tokens=True,
            max_length=64,
            pad_to_max_length=True,
            return_attention_mask=True,
            return_tensors='pt',
            truncation=True
        )
        erencoded_dict = ertokenizer.encode_plus(
            text,
            add_special_tokens=True,
            max_length=64,
            pad_to_max_length=True,
            return_attention_mask=True,
            return_tensors='pt',
            truncation=True
        )
        wwmencoded_dict = wwmtokenizer.encode_plus(
            text,
            add_special_tokens=True,
            max_length=64,
            pad_to_max_length=True,
            return_attention_mask=True,
            return_tensors='pt',
            truncation=True
        )

        b_input_ids = encoded_dict["input_ids"]
        attention_mask = encoded_dict["attention_mask"]
        alb_input_ids = alencoded_dict["input_ids"]
        alattention_mask = alencoded_dict["attention_mask"]
        rob_input_ids = roencoded_dict["input_ids"]
        roattention_mask = roencoded_dict["attention_mask"]
        erb_input_ids = erencoded_dict["input_ids"]
        erattention_mask = erencoded_dict["attention_mask"]
        wwmb_input_ids = wwmencoded_dict["input_ids"]
        wwmattention_mask = wwmencoded_dict["attention_mask"]

        bertmodel = torch.load('./file/BERT_model.pkl')  # 加载特征融合模型
        albertmodel = torch.load('./file/ALBERT_model.pkl')  # 加载特征融合模型
        robertmodel = torch.load('./file/RoBERTa_model.pkl')
        erbertmodel = torch.load('./file/ERNIE_model.pkl')
        wwmbertmodel = torch.load('./file/BERT_wwm_model.pkl')

        outputs = bertmodel(b_input_ids, token_type_ids=None,
                        attention_mask=attention_mask)
        aloutputs = albertmodel(alb_input_ids, token_type_ids=None,
                            attention_mask=alattention_mask)
        rooutputs = robertmodel(rob_input_ids, token_type_ids=None,
                                attention_mask=roattention_mask)
        eroutputs = erbertmodel(erb_input_ids, token_type_ids=None,
                                attention_mask=erattention_mask)
        wwmoutputs = wwmbertmodel(wwmb_input_ids, token_type_ids=None,
                                attention_mask=wwmattention_mask)

        logits = outputs.detach().cpu().numpy()
        allogits = aloutputs.detach().cpu().numpy()
        rologits = rooutputs.detach().cpu().numpy()
        erlogits = eroutputs.detach().cpu().numpy()
        wwmlogits = wwmoutputs.detach().cpu().numpy()

        pre_list = sum(logits.tolist(), [])
        alpre_list = sum(allogits.tolist(), [])
        ropre_list = sum(rologits.tolist(), [])
        erpre_list = sum(erlogits.tolist(), [])
        wwmpre_list = sum(wwmlogits.tolist(), [])

        predict_int = pre_list.index(max(pre_list))
        alpredict_int = alpre_list.index(max(alpre_list))
        ropredict_int = ropre_list.index(max(ropre_list))
        erpredict_int = erpre_list.index(max(erpre_list))
        wwmpredict_int = wwmpre_list.index(max(wwmpre_list))

        final_dict = []
        final_dict.append(predict_int)
        final_dict.append(alpredict_int)
        final_dict.append(ropredict_int)
        final_dict.append(erpredict_int)
        final_dict.append(wwmpredict_int)

        yes = 0
        no = 0
        final = 0
        for i in final_dict:
             if(i==0):
                 no+=1
             else:
               yes+=1 
        if(yes>no):
           final=1
        else:
           final=0
        pre_dict = {'text': text, "bert": predict_int, "albert": alpredict_int, "roberta": ropredict_int, "ernie": erpredict_int, "wwm": wwmpredict_int, "final": final}
        # Flask应用程序实例的run方法启动WEB服务器
        big_list.append(pre_dict)

    print(big_list)
    re = {"big_list": big_list}
    return re


# 下载模块
def create_workbook(dictList):
    output = BytesIO()
    # 创建Excel文件,不保存,直接输出
    workbook = xlsxwriter.Workbook(output, {'in_memory': True})
    # 设置Sheet的名字为download
    worksheet = workbook.add_worksheet('download')
    # 列首
    title = ["原始数据", "预测数据"]
    worksheet.write_row('A1', title)
    # dictList = [{"a":"a1","b":"b1","c":"c1"},{"a":"a2","b":"b2","c":"c2"},{"a":"a3","b":"b3","c":"c3"}]
    for i in range(len(dictList)):
        row = [dictList[i]["text"], dictList[i]["final"], ]
        worksheet.write_row('A' + str(i + 2), row)
    workbook.close()
    response = make_response(output.getvalue())
    output.close()
    return response

# 定义请求方法
@app.route("/down", methods=['POST', 'GET'])
# 下载函数
def download():
    dictList = request.get_json()
    del (dictList[0])
    print((dictList))
    print(type(dictList))
    response = create_workbook(dictList)
    response.headers['Content-Type'] = "utf-8"
    response.headers["Cache-Control"] = "no-cache"
    response.headers["Content-Disposition"] = "attachment; filename=download.xlsx"
    return response


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5005)  # 127.0.0.1 #指的是本地ip
