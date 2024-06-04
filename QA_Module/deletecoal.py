import pandas as pd
from py2neo import Graph,Node,Relationship,NodeMatcher
from collections import defaultdict
graph=Graph("http://localhost:6006",username="neo4j",password="neo4j")
matcher = NodeMatcher(graph)
# query = """
# MATCH (n)
# detach DELETE n
# """
graph.run(query)


# mk_property=['使用地点','使用场景','责任单位','设备类型']
label_list = ['采煤工作面','掘进工作面','主煤流运输','辅助运输','通风与压风','供电与给排水','安全监控','绿色与节能','其他']
mk=''
#每个煤矿导入['使用地点','使用场景','责任单位','设备类型']

for cxk in label_list:
    grandpa = matcher.match(name = '雨汪煤矿一井').first()
    grandchild = Node("设备类型", name = '雨汪煤矿一井'+cxk)
    relationship = Relationship(grandpa, '包含', grandchild)
    graph.create(relationship)