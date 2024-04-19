class JsonData:
    id=int
    label=str
    pid=int
    subids=list
    
    def __init__(self) -> None:
        pass
    def setAttr(self,id,label,pid,subid):
        self.id=id
        self.label=label
        self.pid=pid
        self.subids=subid
    def keys(self):
        '''当对实例化对象使用dict(obj)的时候, 会调用这个方法,这里定义了字典的键, 其对应的值将以obj['name']的形式取,
        但是对象是不可以以这种方式取值的, 为了支持这种取值, 可以为类增加一个方法'''
        return ('id', 'label', 'pid','subids')

    def __getitem__(self, item):
        '''内置方法, 当使用obj['name']的形式的时候, 将调用这个方法, 这里返回的结果就是值'''
        return getattr(self, item)

        