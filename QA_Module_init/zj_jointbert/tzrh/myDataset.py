# -*- codeing = utf-8 -*-
# @Time : 2023/3/1 21:36
# @Author : 剑
# @File : myDataset.py
# @Software : PyCharm
import os
import sys

import torch
from torch.utils.data import Dataset, DataLoader
from transformers import BertTokenizer, BertModel
from tqdm import tqdm
import os

labels = ['X','PAD','UNK','O',
 'B-ent.department',
 'I-ent.department',
 'B-ent.equip_name',
 'I-ent.equip_name',
 'B-ent.factory',
 'I-ent.factory',
 'B-ent.mine_name',
 'I-ent.mine_name',
 'B-ent.place',
 'I-ent.place',
 'B-ent.pro.count',
 'I-ent.pro.count',
 'B-ent.pro.date_pro',
 'I-ent.pro.date_pro',
 'B-ent.pro.date_use',
 'I-ent.pro.date_use',
 'B-ent.pro.equip_code',
 'I-ent.pro.equip_code',
 'B-ent.pro.equip_desc',
 'I-ent.pro.equip_desc',
 'B-ent.pro.factory_code',
 'I-ent.pro.factory_code',
 'B-ent.pro.number',
 'I-ent.pro.number',
 'B-ent.pro.person_res',
 'I-ent.pro.person_res',
 'B-ent.pro.specsi',
 'I-ent.pro.specsi',
 'B-ent.pro.status',
 'I-ent.pro.status',
 'B-ent.pro.tech_param',
 'I-ent.pro.tech_param',
 'B-ent.reference',
 'I-ent.reference',
 'B-label.department',
 'I-label.department',
 'B-label.equip_name',
 'I-label.equip_name',
 'B-label.factory',
 'I-label.factory',
 'B-label.major_calss',
 'I-label.major_calss',
 'B-label.middle_class',
 'I-label.middle_class',
 'B-label.mine_name',
 'I-label.mine_name',
 'B-label.place',
 'I-label.place',
 'B-label.reference',
 'I-label.reference',
 'B-label.sub_class',
 'I-label.sub_class',
 'B-mk.domain_vocab',
 'I-mk.domain_vocab',
 'B-mk.worker_type',
 'I-mk.worker_type',
 'B-pro.count',
 'I-pro.count',
 'B-pro.equip_code',
 'I-pro.equip_code',
 'B-pro.equip_descri',
 'I-pro.equip_descri',
 'B-pro.factory_code',
 'I-pro.factory_code',
 'B-pro.name',
 'I-pro.name',
 'B-pro.number',
 'I-pro.number',
 'B-pro.product_date',
 'I-pro.product_date',
 'B-pro.respon_name',
 'I-pro.respon_name',
 'B-pro.specs',
 'I-pro.specs',
 'B-pro.status',
 'I-pro.status',
 'B-pro.tech_param',
 'I-pro.tech_param',
 'B-pro.use_date',
 'I-pro.use_date',
 'B-rel.department',
 'I-rel.department',
 'B-rel.factory',
 'I-rel.factory',
 'B-rel.place',
 'I-rel.place',
 'B-rel.reference',
 'I-rel.reference',"[END]", '[CLS]', '[SEP]']

label2id = {}
for label in labels:
    label2id[label] = len(label2id)
id2label = {value: key for key, value in label2id.items()}

intent_label2id = {}
intent_path = '/root/intentRecognition/zj_test/data/atis/intent_label.txt'
with open(intent_path, mode='r', encoding='utf-8') as f:
    ff = f.readlines()
    for line in ff:
        line = line.strip()
        intent_label2id[line] = len(intent_label2id)
id2intent_label = {value: key for key, value in intent_label2id.items()}


class MNER_process(Dataset):
    def __init__(self, data_path, bert_name, label2id, intent_label2id, max_length = 510):
        super(MNER_process, self).__init__()
        self.data_path = data_path
        self.tokenizer = BertTokenizer.from_pretrained(bert_name)
        self.label2id = label2id
        self.intent_label2id = intent_label2id
        self.data = []
        self.seq_path = os.path.join(self.data_path, 'seq.in')
        self.ner_label_path = os.path.join(self.data_path, 'seq.out')
        self.yitu_label_path = os.path.join(self.data_path, 'label')
        self.seq, self.ner_label, self.yitu = [], [], []
        self.max_length = max_length

        with open(self.seq_path, mode='r', encoding='utf-8') as f:
            ff = f.readlines()
            for line in ff:
                line = line.strip()
                line = line.split(' ')
                self.seq.append(line)
        with open(self.ner_label_path, mode='r', encoding='utf-8') as f:
            ff = f.readlines()
            for line in ff:
                line = line.strip()
                line = line.split(' ')
                self.ner_label.append(line)
        with open(self.yitu_label_path, mode='r', encoding='utf-8') as f:
            ff = f.readlines()
            for line in ff:
                line = line.strip()
                self.yitu.append(line)
        index = 0
        for seq, ner_label, yitu in zip(self.seq, self.ner_label, self.yitu):
            raw_word = seq
            raw_label = ner_label
            # print(index)
            assert len(raw_word) == len(raw_label)
            index += 1

            pad_length = self.max_length - len(raw_word)

            old_word = raw_word
            old_label = raw_label

            raw_word = [self.tokenizer.cls_token] + raw_word[:max_length] + [self.tokenizer.sep_token]
            raw_label = [self.tokenizer.cls_token] + raw_label[:max_length] + [self.tokenizer.sep_token]
            REAL_LEN = len(raw_word)
            for _ in range(pad_length):
                raw_word.append('PAD')
                raw_label.append('PAD')

            raw_word_id = [self.tokenizer.convert_tokens_to_ids(word) for word in raw_word]
            raw_label_id = [self.label2id[label] for label in raw_label]

            real_len = len(raw_word)
            attention_mask = torch.ones(real_len)
            old_yitu = yitu
            yitu = self.intent_label2id[yitu]

            assert len(raw_word) == len(
                raw_label), f'The length of raw word, raw label is {len(raw_word)} and {len(raw_label)} respectively.'
            self.data.append({
                'raw_word': old_word, 'raw_label': old_label,
                'raw_word_id': raw_word_id, 'raw_label_id': raw_label_id,
                'attention_mask': attention_mask, 'real_len': REAL_LEN,
                'yitu': old_yitu, 'yitu_label': yitu
            })



        # with open(self.data_path, mode='r', encoding='utf-8') as f:
        #     ff = f.readlines()
        #     raw_word, raw_label = [], []
        #     for line in ff:
        #         if line != '\n':
        #             line = line.strip()
        #             word, label = line.split(' ')
        #             if len(word) == 0:
        #                 continue
        #             raw_word.append(word)
        #             raw_label.append(label)
        #             assert len(raw_word) == len(raw_label), \
        #                 f'The length of raw word, raw label is {len(raw_word), len(raw_label), line}'
        #
        #         else:
        #             raw_word = [self.tokenizer.cls_token] + raw_word[:max_length] + [self.tokenizer.sep_token]
        #             raw_label = [self.tokenizer.cls_token] + raw_label[:max_length] + [self.tokenizer.sep_token]
        #
        #             raw_word_id = [self.tokenizer.convert_tokens_to_ids(word) for word in raw_word]
        #             raw_label_id = [self.label2id[label] for label in raw_label]
        #
        #             real_len = len(raw_word)
        #             attention_mask = torch.ones(real_len)
        #
        #             assert len(raw_word) == len(
        #                 raw_label), f'The length of raw word, raw label is {len(raw_word)} and {len(raw_label)} respectively.'
        #             self.data.append({
        #                 'raw_word': raw_word, 'raw_label': raw_label,
        #                 'raw_word_id': raw_word_id, 'raw_label_id': raw_label_id,
        #                 'attention_mask': attention_mask, 'real_len': real_len,
        #             })
        #
        #             raw_word, raw_label = [], []


    def __len__(self):
        return len(self.data)
    def __getitem__(self, item):
        return self.data[item]

from torch.nn.utils.rnn import pad_sequence
def collate_in(batch):
    raw_word_list, raw_label_list, raw_word_id_list, raw_label_id_list, attention_mask_list, real_len_list = [], [], [], [], [], []
    yitu_list, yitu_label_list = [], []

    for idx, data in enumerate(batch):
        raw_word, raw_label = data['raw_word'], data['raw_label']
        raw_word_id, raw_label_id = data['raw_word_id'], data['raw_label_id']
        attention_mask, real_len = data['attention_mask'], data['real_len']
        yitu, yitu_label = data['yitu'], data['yitu_label']

        raw_word_list.append(raw_word)
        raw_label_list.append(raw_label)
        raw_word_id_list.append(torch.tensor(raw_word_id))
        raw_label_id_list.append(torch.tensor(raw_label_id))
        attention_mask_list.append(torch.tensor(attention_mask))
        real_len_list.append(real_len)
        yitu_list.append(yitu)
        yitu_label_list.append(yitu_label)

    return {
        'raw_word': raw_word_list, 'raw_label': raw_label_list,
        'raw_word_id': pad_sequence(raw_word_id_list, batch_first=True, padding_value=0),
        'raw_label_id': pad_sequence(raw_label_id_list, batch_first=True, padding_value=0),
        'attention_mask': pad_sequence(attention_mask_list, batch_first=True, padding_value=0),
        'real_len': real_len_list,
        'yitu': yitu_list,
        'yitu_label': yitu_label_list
    }
train_data_path = '/root/intentRecognition/zj_test/data/atis/train'
train_data = MNER_process(data_path=train_data_path, bert_name='bert-base-chinese', label2id=label2id,
                                              intent_label2id=intent_label2id)
train_dataset = DataLoader(train_data, batch_size=64, shuffle=True, collate_fn=collate_in)