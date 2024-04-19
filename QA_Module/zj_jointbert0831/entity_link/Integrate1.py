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
class GlobalMaxPool1d(nn.Module):
    def __init__(self):
        super(GlobalMaxPool1d, self).__init__()

    def forward(self, x):
        # x shape: (batch_size, channel, seq_len)
        return F.max_pool1d(x, kernel_size=x.shape[2])  # shape: (batch_size, channel, 1)

# Bert特征融合模型
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
        # #提取[CLS]对应的隐藏状态
        # bert_cls_hidden_state = bert_output[0][:,0,:]
        bert_cls_hidden_state = bert_output[0][:, 1:-1, :]
        #         print("bert_cls_hidden_state.shape:",bert_cls_hidden_state.shape)
        # 将词向量转换为句子向量
        sentence_emd = torch.sum(bert_output[0][:, 1:-1, :], dim=1)  # (b,768)
        print("sentence_emd.shape:", sentence_emd.shape)

        # 对于每个一维卷积层，在时序最大池化后会得到一个形状为(批量大小, 通道大小, 1)的
        # Tensor。使用flatten函数去掉最后一维，然后在通道维上连结
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

# Bert特征融合模型
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
        print("sentence_emd.shape:", sentence_emd.shape)

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
        print("sentence_emd.shape:", sentence_emd.shape)

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
        print("sentence_emd.shape:", sentence_emd.shape)

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
        pretrained_weights = '/workspace/zj_coal/HNCoal/QA_Module/zj_jointbert/model_mine//bert-wwm'
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
        print("sentence_emd.shape:", sentence_emd.shape)

        # 对于每个一维卷积层，在时序最大池化后会得到一个形状为(批量大小, 通道大小, 1)的
        # Tensor。使用flatten函数去掉最后一维，然后在通道维上连结
        predict = self.dense(sentence_emd)
        # 使用dropout
        predict = self.dropout(predict)
        return predict

def softmax(X):
    X_exp = torch.exp(X)#指数运算
    partition = X_exp.sum(1, keepdim=True)#对每一行进行运算
    #第i个元素除以 partition中的第i个元素
    return X_exp / partition

# Flask后台框架连接部分
# Flask跨域请求
app = Flask(__name__)
CORS(app, supports_credentials=True)


# 定义请求方法
@app.route('/get_integrate1', methods=['POST'])
# 单个评论预测
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

    outputs = softmax(outputs)
    aloutputs = softmax(aloutputs)
    rooutputs = softmax(rooutputs)
    eroutputs = softmax(eroutputs)
    wwmoutputs = softmax(wwmoutputs)

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

    pre_fake = pre_list[0]
    alpre_fake = alpre_list[0]
    ropre_fake = ropre_list[0]
    erpre_fake = erpre_list[0]
    wwmpre_fake = wwmpre_list[0]

    pre_real = pre_list[1]
    alpre_real = alpre_list[1]
    ropre_real = ropre_list[1]
    erpre_real = erpre_list[1]
    wwmpre_real = wwmpre_list[1]

    final_fake = (pre_fake+alpre_fake+ropre_fake+erpre_fake+wwmpre_fake)/5
    final_real = (pre_real+alpre_real+ropre_real+erpre_real+wwmpre_real)/5

    if (final_fake > final_real):
        final = {"label": 0}
    else:
        final =  {"label": 1}
    #pre_dict = {'text': final }
    new_dict = {"result": final}
    print(new_dict)  # 输出参数维度
    return new_dict



# 定义请求方法
@app.route('/integrate1/import/batch', methods=['POST'])
# 批量评论预测
def get_batch_integrate1():
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

        bertmodel = torch.load('./file/BERT_model.pkl')
        albertmodel = torch.load('./file/ALBERT_model.pkl')
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

        outputs = softmax(outputs)
        aloutputs = softmax(aloutputs)
        rooutputs = softmax(rooutputs)
        eroutputs = softmax(eroutputs)
        wwmoutputs = softmax(wwmoutputs)

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

#       概率平均法逻辑部分
        pre_fake = pre_list[0]
        alpre_fake = alpre_list[0]
        ropre_fake = ropre_list[0]
        erpre_fake = erpre_list[0]
        wwmpre_fake = wwmpre_list[0]

        pre_real = pre_list[1]
        alpre_real = alpre_list[1]
        ropre_real = ropre_list[1]
        erpre_real = erpre_list[1]
        wwmpre_real = wwmpre_list[1]

        final_fake = (pre_fake + alpre_fake + ropre_fake + erpre_fake + wwmpre_fake) / 5
        final_real = (pre_real + alpre_real + ropre_real + erpre_real + wwmpre_real) / 5


        if (final_fake > final_real):
            final_pro = final_fake
            final = 0
        else:
            final_pro = final_real
            final = 1

        pre_dict = {'text': text, "bert0": pre_fake, "bert1": pre_real,
                    "albert0": alpre_fake, "albert1": alpre_real,
                    "roberta0": ropre_fake, "roberta1":ropre_real,
                    "ernie0": erpre_fake,"ernie1": erpre_real,
                    "wwm0": wwmpre_fake, "wwm1": wwmpre_real,
                    "final": final, "finalpro":final_pro}
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
    app.run(host='127.0.0.1', port=5008)  # 127.0.0.1 #指的是本地ip
