import torch

model = torch.load('/root/intentRecognition/zj_jointbert/model_mine/mk_major_000/pytorch_model.bin')

question='你好啊，我是前端'
with torch.no_grad():
    ans = model.predict(question)
# answer = str(output_tensor)

# 将问题传入模型并获取答案
# print("模型输出: %s",(answer))
# answer = model.predict(question)
print(ans)