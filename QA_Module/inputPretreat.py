# -*- codeing = utf-8 -*-
# @Time : 2023/5/25 8:36
# @Author : 剑
# @File : inputPretreat.py
# @Software : PyCharm

input_Pretreat = {"系统中有哪些矿山?":"系统中有哪些矿山",
                  "系统中有哪些矿山.":"系统中有哪些矿山",
                  "系统中有那些矿山":"系统中有哪些矿山",
                  "所有矿山":"系统中有哪些矿山",
                  }


def replace_text(text):

    # if '矿山' in text:
    #     if '所属矿山' in text:
    #         text = text
    #     else:
    #         text = text.replace('矿山','所属矿山')

    # if '单位' in text:
    #     if '责任单位' in text :
    #         text = text.replace('责任单位','属于')
    #     elif '负责单位' in text:
    #         text = text.replace('负责单位','属于')
        # else:
            # text = text.replace('单位','属于')

    # if '标准' in text:
    #     if '参考标准' in text:
    #         text = text
    #     else:
    #         text = text.replace('标准','参考标准')

    # if '地点' in text:
    #     if '使用地点' in text:
    #         text = text
    #     else:
    #         text = text.replace('地点','使用地点')

    if '物料' in text:
        if '物料名' in text:
            text = text
        else:
            text = text.replace('物料','物料名')

    # if '设备' in text:
    #     if '设备名' in text:
    #         text = text
    #     else:
    #         text = text.replace('设备','设备名')
    return text


if __name__ == '__main__':
     text = replace_text('系统有哪些单位')
     print('text = ',text)