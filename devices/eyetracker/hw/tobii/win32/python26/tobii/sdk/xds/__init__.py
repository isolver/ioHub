
from tobii.sdk._native import tobiisdkpy
from tobii.sdk.types import Node

XDS_ROW_TYPE_ID = 3000
XDS_COL_TYPE_ID = 3001

class _ConverterRegistry(object):
    def __init__(self):
        self._converters = {}

    def register(self, typeid, converter):
        self._converters[typeid] = converter
    
    def convert(self, node):
        if not isinstance(node, Node):
            raise TypeError("The node argument must be a Node")
        
        if not node.type in self._converters:
            return None
        
        return self._converters[node.type](node)
    
    def to_tree(self, param_stack, obj):
        if isinstance(obj, tobiisdkpy.ParamStack):
            param_stack.append(obj)
            return
        
        cls = obj.__class__
        if hasattr(cls, "_tree_converter"):
            cls._tree_converter(obj, param_stack)
            return
        
        raise TypeError("type does not support TreeConverter")


Converter = _ConverterRegistry()


class Row(object):
    def __init__(self, node):
        if not isinstance(node, Node):
            raise TypeError("The node argument must be a Node")
        
        if node.type != XDS_ROW_TYPE_ID:
            raise ValueError("Expected type id: %d got %d" % (XDS_ROW_TYPE_ID, node.type))
        
        self._node = node
        self._columns = {}
        
        for child in node.children:
            if not isinstance(child, Node):
                continue
            if child.type != XDS_COL_TYPE_ID:
                continue
            
            column = Column(child)
            self._columns[column.id] = column
    
    def __len__(self):
        return len(self._columns)
    
    def __getitem__(self, column_id):
        return self._columns[column_id]
    
    @property
    def node(self):
        return self._node
    
        

class Column(object):
    Converter = Converter
    
    def __init__(self, node):
        if not isinstance(node, Node):
            raise TypeError("The node argument must be a Node")
        
        if node.type != XDS_COL_TYPE_ID:
            raise ValueError("Expected type id: %d got %d" % (XDS_COL_TYPE_ID, node.type))
        
        self._node = node
        
        if isinstance(node[1], Node):
            self._data = Column.Converter.convert(node[1])
        else:
            self._data = node[1]
    
    @property
    def id(self):
        return self._node[0]
    
    @property
    def node(self):
        return self._node[1]
    
    @property
    def data(self):
        return self._data
    
    @property
    def column_node(self):
        return self._node
