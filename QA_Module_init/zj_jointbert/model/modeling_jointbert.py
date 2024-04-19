import torch
import torch.nn as nn
from transformers import BertPreTrainedModel, BertModel, BertConfig, BertTokenizer
from torchcrf import CRF
from .module import IntentClassifier, SlotClassifier

with open('/root/intentRecognition/zj_jointbert/tzrh/Zm_W2v_dict.jsonl', 'r')as reader:
    Zm_W2v_list_dict = reader.readlines()
with open('/root/intentRecognition/zj_jointbert/tzrh/Wb_W2v_dict.jsonl', 'r')as reader:
    Wb_W2v_list_dict = reader.readlines()
Zm_W2v_list_dict = eval(Zm_W2v_list_dict[0])
# print(list(Zm_W2v_list_dict.keys()))
Wb_W2v_list_dict = eval(Wb_W2v_list_dict[0])


class JointBERT(BertPreTrainedModel):
    def __init__(self, config, args, intent_label_lst, slot_label_lst):
        super(JointBERT, self).__init__(config)
        self.args = args
        self.num_intent_labels = len(intent_label_lst)
        self.num_slot_labels = len(slot_label_lst)
        self.bert = BertModel(config=config)  # Load pretrained bert
        self.tokenizer = BertTokenizer.from_pretrained('/root/intentRecognition/zj_jointbert/model_mine/bert_base_chinese')
        self.intent_classifier = IntentClassifier(config.hidden_size, self.num_intent_labels, args.dropout_rate)
        self.slot_classifier = SlotClassifier(config.hidden_size, self.num_slot_labels, args.dropout_rate)
        # self.att = nn.MultiheadAttention(embed_dim=768, num_heads=12)
        if args.use_crf:
            self.crf = CRF(num_tags=self.num_slot_labels, batch_first=True)
            self.device = "cuda" if torch.cuda.is_available() else "cpu"
        
    def forward(self, input_ids, attention_mask, token_type_ids, intent_label_ids, slot_labels_ids):
        outputs = self.bert(input_ids, attention_mask=attention_mask,
                            token_type_ids=token_type_ids)  # sequence_output, pooled_output, (hidden_states), (attentions)
        sequence_output = outputs[0]
        pooled_output = outputs[1]  # [CLS]
        f_all = []
        # print('....................',self.tokenizer.convert_ids_to_tokens(101))
        for index, so in enumerate(sequence_output):
            tmp = []
            for i,o in enumerate(so):
                
                # print(o)
                token = self.tokenizer.convert_ids_to_tokens(int(input_ids[index][i]))
                zm_vec = torch.zeros_like(o)
                wb_vec = torch.zeros_like(o)
                if token in Zm_W2v_list_dict:
                    # print('true')
                    zm_vec = Zm_W2v_list_dict[token]

                if token in Wb_W2v_list_dict:
                    # print('true')
                    wb_vec = Wb_W2v_list_dict[token]
                    
                zm_vec = torch.tensor(zm_vec).to(self.device)
                wb_vec = torch.tensor(wb_vec).to(self.device)
                # tmp.append(o)
                # tmp.append(zm_vec)
                # tmp.append(wb_vec)
                # tmp = torch.stack(tmp, dim = 0)
                # print(tmp.shape)
                # print(tmp)
                # tmp = torch.mean(tmp, dim=0)
                f = o + zm_vec + wb_vec
                tmp.append(f)
            f_all.append(torch.stack(tmp, dim = 0))
            # f_all.append(tmp)
        f_all = torch.stack(f_all, dim=0)
        # print('po',sequence_output.shape)
        # print('f',f_all.shape)
        intent_logits = self.intent_classifier(pooled_output)
        slot_logits = self.slot_classifier(f_all)

        total_loss = 0
        # 1. Intent Softmax
        if intent_label_ids is not None:
            if self.num_intent_labels == 1:
                intent_loss_fct = nn.MSELoss()
                intent_loss = intent_loss_fct(intent_logits.view(-1), intent_label_ids.view(-1))
            else:
                intent_loss_fct = nn.CrossEntropyLoss()
                intent_loss = intent_loss_fct(intent_logits.view(-1, self.num_intent_labels), intent_label_ids.view(-1))
            total_loss += intent_loss

        # 2. Slot Softmax
        if slot_labels_ids is not None:
            if self.args.use_crf:
                slot_loss = self.crf(slot_logits, slot_labels_ids, mask=attention_mask.byte(), reduction='mean')
                slot_loss = -1 * slot_loss  # negative log-likelihood
            else:
                slot_loss_fct = nn.CrossEntropyLoss(ignore_index=self.args.ignore_index)
                # Only keep active parts of the loss
                if attention_mask is not None:
                    active_loss = attention_mask.view(-1) == 1
                    active_logits = slot_logits.view(-1, self.num_slot_labels)[active_loss]
                    active_labels = slot_labels_ids.view(-1)[active_loss]
                    slot_loss = slot_loss_fct(active_logits, active_labels)
                else:
                    slot_loss = slot_loss_fct(slot_logits.view(-1, self.num_slot_labels), slot_labels_ids.view(-1))
            total_loss += self.args.slot_loss_coef * slot_loss

        outputs = ((intent_logits, slot_logits),) + outputs[2:]  # add hidden states and attention if they are here

        outputs = (total_loss,) + outputs

        return outputs  # (loss), logits, (hidden_states), (attentions) # Logits is a tuple of intent and slot logits
