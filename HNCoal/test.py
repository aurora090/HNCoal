import pandas as pd
from py2neo import Graph,Node,Relationship,NodeMatcher
from collections import defaultdict
user="neo4j"
key="root"
graph=Graph("http://211.82.97.250:7606",auth=(user,key))
matcher = NodeMatcher(graph)



# mk_property=['使用地点','使用场景','责任单位','设备类型']
label_list = ['采煤工作面','掘进工作面','主煤流运输','辅助运输','通风与压风','供电与给排水','安全监控','绿色与节能','其他']
mk='雨汪煤矿一井'
#每个煤矿导入['使用地点','使用场景','责任单位','设备类型']

for cxk in label_list:
    爷爷 = matcher.match(name = mk).first()
    孙子 = Node("设备类型", name = mk+cxk)
    relationship = Relationship(爷爷, '包含', 孙子)
    graph.create(relationship)