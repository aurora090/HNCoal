import sys
import torch
import torch.nn as nn
import math
import torch.nn.functional as F
from transformers import BertModel
from gensim.models.word2vec import Word2Vec
from tzrh.myDataset import train_dataset as dataloader
from torch.nn.utils.rnn import pad_sequence
import math

data_path = '/xiaowang/ner_dataset/shiyan1/uncle/dev.char.bmes'
wubi_path = '/root/intentRecognition/zj_test/tzrh/wubi.txt'
zhengma_path = '/root/intentRecognition/zj_test/tzrh/zhengma.txt'
pinyin_path = '/root/intentRecognition/zj_test/tzrh/pinyin.txt'
bihua_path = '/xiaowang/ner_dataset/shiyan1/bihua.txt'

# from gensim.models import Word2Vec
# wordvec = Word2Vec.load(r'/xiaowang/ner_dataset/shiyan1/textcnn-bihua/word2vec_model/word2vec.model1')

# 输入五笔、郑码等数据地址，得到一个字典，键为汉字，值为对应的五笔值、郑码值等. 笔画值为数列，每个数分别代表横竖撇捺中的一个
def get_dic(data_path) -> dict:
    dic = {}
    with open(data_path, mode='r', encoding='utf-8') as f:
        ff = f.readlines()
        for line in ff:
            if len(line) > 0:
                line = line.strip()
                word, label = line.split(' ')
                if '|' in label:
                    label = label.split('|')[0]
                dic[word] = label
    return dic

wubi_dic = get_dic(wubi_path)
zhengma_dic = get_dic(zhengma_path)
pinyin_dic = get_dic(pinyin_path)

# with open(data_path, mode='r', encoding='utf-8') as f:
#     ff = f.readlines()
#     raw_word, raw_label, wubi = [], [], []
#     for line in ff:
#         if line != '\n':
#             line = line.strip()
#             word, label = line.split(' ')

word_record = []
for idx, data in enumerate(dataloader):
    for sentence in data['raw_word']:
        word_record.append(sentence)

# 得到相应五笔、郑码等序列结果，开头结尾特殊标记被标为zzzz
def get_map_sequence(word_record, dic):
    word_record = [[dic[word] if word in dic else 'zzzz' for word in record] for record in word_record]
    return word_record

wubi_record = get_map_sequence(word_record=word_record, dic=wubi_dic)
zhengma_record = get_map_sequence(word_record=word_record, dic=zhengma_dic)
wubi_model = Word2Vec(wubi_record, window=8, min_count=1, epochs=5, vector_size=50)
zhengma_model = Word2Vec(zhengma_record, window=8, min_count=1, epochs=5, vector_size=50)
wubi_model.save('/root/intentRecognition/zj_test/tzrh/wubi1')
zhengma_model.save('/root/intentRecognition/zj_test/tzrh/zhengma1')
wubi_model = Word2Vec.load('/root/intentRecognition/zj_test/tzrh/wubi1')
zhengma_model = Word2Vec.load('/root/intentRecognition/zj_test/tzrh/zhengma1')

class Attention(nn.Module):
    def __init__(self, hidden_size=868, num_head=12, head_dim=64):
        super(Attention, self).__init__()
        self.hidden_size = hidden_size
        self.num_head = num_head
        self.head_dim = head_dim
        self.pro = nn.Linear(self.hidden_size, self.num_head*self.head_dim)

        self.q_metric = nn.Linear(self.num_head * self.head_dim, self.num_head * self.head_dim)
        self.k_metric = nn.Linear(self.num_head * self.head_dim, self.num_head * self.head_dim)
        self.v_metric = nn.Linear(self.num_head * self.head_dim, self.num_head * self.head_dim)

        self.ffn = nn.Sequential(nn.Linear(self.num_head*self.head_dim, 2048),
                                 nn.ReLU(inplace=True),
                                 nn.Linear(2048, self.num_head*self.head_dim))
        self.dropout1 = nn.Dropout(0.1)
        self.dropout2 = nn.Dropout(0.2)

    def forward(self, input, bert_output=None):
        sentences = input['raw_word']

        wubi = [[wubi_dic[word] if word in wubi_dic else 'zzzz' for word in sentence] for sentence in sentences]
        zhengma = [[zhengma_dic[word] if word in zhengma_dic else 'zzzz' for word in sentence] for sentence in sentences]

        wubi_vector = [[torch.tensor(wubi_model.wv[word]) for word in seq_list] for seq_list in wubi]
        wubi_vector = [torch.stack(vector, dim=0) for vector in wubi_vector]
        wubi_vector = pad_sequence(wubi_vector, batch_first=True, padding_value=0)

        zhengma_vector = [[torch.tensor(zhengma_model.wv[word]) for word in seq_list] for seq_list in zhengma]
        zhengma_vector = [torch.stack(vector, dim=0) for vector in zhengma_vector]
        zhengma_vector = pad_sequence(zhengma_vector, batch_first=True, padding_value=0)

        final_result = torch.cat([wubi_vector, zhengma_vector], dim=-1)
        # batch, seq_len, hidden_size=768
        final_result = self.pro(torch.cat([bert_output, final_result], dim=-1))

        ## start attention
        attention_mask = input['attention_mask']
        batch_size, seq_len, hidden_dim = final_result.size()
        # batch, num_head, seq_len, head_dim
        Q = self.q_metric(final_result).view(batch_size, seq_len, self.num_head, self.head_dim).transpose(1, 2)
        K = self.k_metric(final_result).view(batch_size, seq_len, self.num_head, self.head_dim).transpose(1, 2)
        V = self.v_metric(final_result).view(batch_size, seq_len, self.num_head, self.head_dim).transpose(1, 2)

        K = K.transpose(-1, -2)
        # batch num_head, seq_len, seq_len
        attention_score = torch.matmul(Q, K)
        attention_score += attention_mask
        attention_score /= math.sqrt(self.head_dim)
        attention_score = F.softmax(attention_score, dim=-1)
        attention_score = self.dropout1(attention_score)
        # batch, num_head, hidden_size=768
        score_result = torch.matmul(attention_score, V).transpose(1, 2).view(batch_size, seq_len, -1)
        score_result = nn.LayerNorm(self.num_head*self.head_dim)(score_result+final_result)

        new_result = self.ffn(score_result)
        new_result = self.dropout2(new_result)
        new_result2 = nn.LayerNorm(self.num_head*self.head_dim)(new_result+score_result)

        return new_result2



