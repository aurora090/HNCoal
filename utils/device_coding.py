import yaml


def coal_coding():
    """
    以字典形式返回，各煤矿的编码信息
    """
    with open('data/coals.yaml', 'r',encoding='utf-8') as f:
        data = yaml.load(f, Loader=yaml.FullLoader)
        return data

def company_coding():
    """
    以字典形式返回，各公司的编码信息
    """
    with open('data/company.yaml', 'r',encoding='utf-8') as f:
        data = yaml.load(f, Loader=yaml.FullLoader)
        return data

def type_coding():
    """
    以字典形式返回，各设备类型的编码信息
    """
    with open('data/types.yaml', 'r',encoding='utf-8') as f:
        data = yaml.load(f, Loader=yaml.FullLoader)
        return data