import torch  
from transformers import BertModel, BertTokenizer
import pandas as pd
import numpy as np  
# 加载已经训练好的BERT模型和tokenizer：
model_path = "/workspace/HNCoal/QA_Module/zj_jointbert/model_mine/bert-base-chinese"  # 根据您的模型名称进行修改  
tokenizer = BertTokenizer.from_pretrained(model_path)  
model = BertModel.from_pretrained(model_path)

input_texts = []  
candidate_files = ['/workspace/HNCoal/QA_Module/zj_jointbert/entity_link/candidate_files/1huaneng.txt','/workspace/HNCoal/QA_Module/zj_jointbert/entity_link/candidate_files/2fengongsi.txt','/workspace/HNCoal/QA_Module/zj_jointbert/entity_link/candidate_files/3qiye.txt','/workspace/HNCoal/QA_Module/zj_jointbert/entity_link/candidate_files/4yuangong.txt','/workspace/HNCoal/QA_Module/zj_jointbert/entity_link/candidate_files/5didian.txt','/workspace/HNCoal/QA_Module/zj_jointbert/entity_link/candidate_files/6kuangshan.txt','/workspace/HNCoal/QA_Module/zj_jointbert/entity_link/candidate_files/7shebei.txt','/workspace/HNCoal/QA_Module/zj_jointbert/entity_link/candidate_files/8shebeileixing.txt','/workspace/HNCoal/QA_Module/zj_jointbert/entity_link/candidate_files/9zerendanwei.txt']
embedding_files = ['/workspace/HNCoal/QA_Module/zj_jointbert/entity_link/embedding_files/1huaneng.pt','/workspace/HNCoal/QA_Module/zj_jointbert/entity_link/embedding_files/2fengongsi.pt','/workspace/HNCoal/QA_Module/zj_jointbert/entity_link/embedding_files/3qiye.pt','/workspace/HNCoal/QA_Module/zj_jointbert/entity_link/embedding_files/4yuangong.pt','/workspace/HNCoal/QA_Module/zj_jointbert/entity_link/embedding_files/5didian.pt','/workspace/HNCoal/QA_Module/zj_jointbert/entity_link/embedding_files/6kuangshan.pt','/workspace/HNCoal/QA_Module/zj_jointbert/entity_link/embedding_files/7shebei.pt','/workspace/HNCoal/QA_Module/zj_jointbert/entity_link/embedding_files/8shebeileixing.pt','/workspace/HNCoal/QA_Module/zj_jointbert/entity_link/embedding_files/9zerendanwei.pt']
for i in range(1):  # 根据您的文件名进行修改  
    all_embeddings = []
    file_name = candidate_files[i]  # 根据您的文件名进行修改  
    with open(file_name, "r", encoding="utf-8") as file:  
        lines = file.readlines()  

        for line in lines:
            text = line
            encoded_text = tokenizer.encode(text, return_tensors="pt")  
         # 关闭梯度计算，以提高效率  
            with torch.no_grad(): 
                output = model(encoded_text)  # 输出为模型的隐藏状态，即文本的向量表示  
            
            vector = torch.mean(output.last_hidden_state,dim=1)
            # last_hidden_states = output.last_hidden_state
            # vector = last_hidden_states.detach().numpy()
            all_embeddings.append(vector)
            print(vector.shape)
        #     print(vector)
        #     print(len(vector))
        #     print(len(vector[0]))   
        # print(all_embeddings)
        # print(all_embeddings[0])
        torch.save(all_embeddings,embedding_files[i])
            # with open(embedding_files[i], "wb") as vector_file:  
            #     torch.save(vector, vector_file)
# -------------------------------------------------------------------------------------
