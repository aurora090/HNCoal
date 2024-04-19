import torch  
from transformers import BertModel, BertTokenizer  
import numpy as np  
from sklearn.metrics.pairwise import cosine_similarity  
import torch.nn.functional as F
from scipy.spatial.distance import cosine 
  
def calculate_similarity(candidate_file,vector_file):  
    predict_vector = None  
    
    # 使用BERT模型将预测文本转换为向量表示  
    tokenizer = BertTokenizer.from_pretrained('/workspace/HNCoal/QA_Module/zj_jointbert/model_mine/bert-base-chinese')  
    model = BertModel.from_pretrained('/workspace/HNCoal/QA_Module/zj_jointbert/model_mine/bert-base-chinese')  
    
    with open('/workspace/HNCoal/QA_Module/zj_jointbert/entity_link/input_ent.txt', "r", encoding="utf-8") as file:   
        lines = file.readlines()
    # for line in lines:
    #     encoded_text = tokenizer.encode(line, return_tensors="pt")
    #     with torch.no_grad(): 
    #         output = model(encoded_text)
    #     predict_vector = output.last_hidden_state.detach().numpy()
    encoded_text = tokenizer.encode(lines[0], return_tensors="pt")
    with torch.no_grad():
        output = model(encoded_text)
    predict_vector = torch.mean(output.last_hidden_state,dim=1)
    # print(predict_vector)
    # print(predict_vector.shape)
    # predict_vector = output.last_hidden_state.detach().numpy()[0]
    
    scores = []  # 存储相似度得分
    with open(vector_file, "rb") as f:
        vectors = torch.load(f)
    
    # print(len(vectors))
    # predict_vector = np.mean(predict_vector, axis=0)
    
    for i,sentence in enumerate(vectors):
        # print(sentence)
        # sentence = torch.mean(sentence[0],dim=0)
        # sentence = np.mean(sentence, axis=0)
        cos_sim = torch.nn.CosineSimilarity(dim=1) 
        score = cos_sim(predict_vector,sentence)
        scores.append(score)
    final_scores = [tensor.item() for tensor in scores]
    
    # print("vectors:",vectors)
    # print("scores:",scores)
    # print(len(scores))
    # print(final_scores)
    
    original_indices = np.arange(len(final_scores))
    top_indices = np.argsort(final_scores)[::-1][:5]  # 获取得分最高的前五个向量
    print("前五个得分最高的下标：",top_indices)
    with open(candidate_file, "r", encoding="utf-8") as file:   
         lines=file.readlines()
         top_ent = lines[top_indices[0]]
         top_score = final_scores[top_indices[0]]
    return top_ent,top_score
    



candidate_files = ['/workspace/HNCoal/QA_Module/zj_jointbert/entity_link/candidate_files/1huaneng.txt','/workspace/HNCoal/QA_Module/zj_jointbert/entity_link/candidate_files/2fengongsi.txt','/workspace/HNCoal/QA_Module/zj_jointbert/entity_link/candidate_files/3qiye.txt','/workspace/HNCoal/QA_Module/zj_jointbert/entity_link/candidate_files/4yuangong.txt','/workspace/HNCoal/QA_Module/zj_jointbert/entity_link/candidate_files/5didian.txt','/workspace/HNCoal/QA_Module/zj_jointbert/entity_link/candidate_files/6kuangshan.txt','/workspace/HNCoal/QA_Module/zj_jointbert/entity_link/candidate_files/7shebei.txt','/workspace/HNCoal/QA_Module/zj_jointbert/entity_link/candidate_files/8shebeileixing.txt','/workspace/HNCoal/QA_Module/zj_jointbert/entity_link/candidate_files/9zerendanwei.txt']
embedding_files = ['/workspace/HNCoal/QA_Module/zj_jointbert/entity_link/embedding_files/1huaneng.pt','/workspace/HNCoal/QA_Module/zj_jointbert/entity_link/embedding_files/2fengongsi.pt','/workspace/HNCoal/QA_Module/zj_jointbert/entity_link/embedding_files/3qiye.pt','/workspace/HNCoal/QA_Module/zj_jointbert/entity_link/embedding_files/4yuangong.pt','/workspace/HNCoal/QA_Module/zj_jointbert/entity_link/embedding_files/5didian.pt','/workspace/HNCoal/QA_Module/zj_jointbert/entity_link/embedding_files/6kuangshan.pt','/workspace/HNCoal/QA_Module/zj_jointbert/entity_link/embedding_files/7shebei.pt','/workspace/HNCoal/QA_Module/zj_jointbert/entity_link/embedding_files/8shebeileixing.pt','/workspace/HNCoal/QA_Module/zj_jointbert/entity_link/embedding_files/9zerendanwei.pt']
candidate_file = candidate_files[1]
vector_file = embedding_files[1]  # 根据实际的文件名进行修改  
# vector_files_to_classes = {file: class_name for file, class_name in zip(vector_files, ["class1", "class2", "class3", "class4", "class5", "class6", "class7", "class8", "class9"])}  # 根据实际的类别进行修改  
  
predict_ent = "华亭煤业公司"  # 替换为您预测的实体  

with open('/workspace/HNCoal/QA_Module/zj_jointbert/entity_link/input_ent.txt', "r", encoding="utf-8") as file:   
        line = file.readline() 
        print('预测实体名为：',line) 
ent,score = calculate_similarity(candidate_file,vector_file)  
# # index = int(indices[0][0])  # 取出索引数组中的数字
# # score = scores[0][0][0][0][0][0][0]  # 取出得分数组中的数字
# with open('/workspace/HNCoal/QA_Module/zj_jointbert/entity_link/candidate_files/5didian.txt', "r", encoding="utf-8") as file:   
#         lines = file.readlines() 
print("相似的库中实体为:",ent)  
print("对应的得分:", score)