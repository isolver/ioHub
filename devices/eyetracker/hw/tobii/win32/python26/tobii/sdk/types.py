
class GazeDataConstants:
    TimeStamp = 1
    
    LeftEyePosition3D = 2
    LeftEyePosition3DRelative = 3
    LeftGazePoint3D = 4
    LeftGazePoint2D = 5
    LeftPupil = 6
    LeftValidity = 7
    
    RightEyePosition3D = 8
    RightEyePosition3DRelative = 9
    RightGazePoint3D = 10
    RightGazePoint2D = 11
    RightPupil = 12
    RightValidity = 13

class Point2D(object):
    NODE_ID = 8000
    
    def __init__(self, x = 0, y = 0):
        self.x = x
        self.y = y
    
    def __str__(self):
        return '(%s, %s)' % (self.x, self.y)

    @staticmethod
    def _node_converter(node):
        if not isinstance(node, Node):
            raise TypeError("node must be Node")
        
        if node.type != Point2D.NODE_ID:
            raise ValueError("Expected node type: %d got %d" % (Point2D.NODE_ID, node.type))
        
        if len(node) != 2:
            raise TypeError("invalid node length")
        
        x, y, = node[0], node[1]
        for c in x, y:
            if not isinstance(c, (int, float, long)):
                raise TypeError("invalid node contents")
        return Point2D(x, y)

    @staticmethod
    def _tree_converter(obj, param_stack):
        if not isinstance(obj, Point2D):
            raise TypeError("obj must be a Point2D")
        
        node_prolog = (2 & 0x00000fff) << 16 # length
        node_prolog |= (Point2D.NODE_ID & 0x0000ffff) # type
        
        param_stack.push_node_prolog(node_prolog)
        param_stack.push_float64_as_fixed_22x41(obj.x)
        param_stack.push_float64_as_fixed_22x41(obj.y)


class Point3D(object):
    NODE_ID = 8001    

    def __init__(self, x = 0, y = 0, z = 0):
        self.x, self.y, self.z = x, y, z
    
    def __str__(self):
        return '(%s, %s, %s)' % (self.x, self.y, self.z)

    @staticmethod
    def _node_converter(node):
        if not isinstance(node, Node):
            raise TypeError("node must be Node")
        
        if node.type != Point3D.NODE_ID:
            raise ValueError("Expected node type: %d got %d" % (Point3D.NODE_ID, node.type))
        
        if len(node) != 3:
            raise TypeError("invalid node length")
        
        x, y, z = node[0], node[1], node[2]
        for c in x, y, z:
            if not isinstance(c, (int, float, long)):
                raise TypeError("invalid node contents")
        return Point3D(x, y, z)
    
    @staticmethod
    def _tree_converter(obj, param_stack):
        if not isinstance(obj, Point3D):
            raise TypeError("obj must be a Point3D")
        
        node_prolog = (3 & 0x00000fff) << 16 # length
        node_prolog |= (Point3D.NODE_ID & 0x0000ffff) # type
        
        param_stack.push_node_prolog(node_prolog)
        param_stack.push_float64_as_fixed_22x41(obj.x)
        param_stack.push_float64_as_fixed_22x41(obj.y)
        param_stack.push_float64_as_fixed_22x41(obj.z)
    

Blob = str


class Node(object):
    def __init__(self, type=None, children=None):
        if type is None:
            return
        
        if children is None:
            self.children = list()
        else:
            self.children = children
            
        self.node_type = type

    def __iter__(self):
        return self.children.__iter__()
    
    def __len__(self):
        return len(self.children)
    
    @property
    def type(self):
        return self.node_type
    
    def __getitem__(self, index):
        return self.children[index]
    
    def append(self, child):
        self.children.append(child)
    
    def __str__(self):
        return self._to_str()
    
    def _to_str(self, level=0):
        indent  = "  " * level
        s = indent + "Node<%d> [%d]:\n" % (self.node_type, len(self))
        for child in self.children:
            if isinstance(child, Node):
                s += child._to_str(level+1)
            else:
                s += indent + "  "
                s += str(child)
                s += "\n"
        return s
        
        

class GazeDataItem(object):
    
    def __init__(self):
        self.Timestamp = long()
        
        self.LeftEyePosition3D           = Point3D()
        self.LeftEyePosition3DRelative   = Point3D()
        self.LeftGazePoint3D             = Point3D()
        self.LeftGazePoint2D             = Point2D()
        self.LeftPupil                   = float()
        self.LeftValidity                = long()
                                         
        self.RightEyePosition3D          = Point3D()
        self.RightEyePosition3DRelative  = Point3D()
        self.RightGazePoint3D            = Point3D()
        self.RightGazePoint2D            = Point2D()
        self.RightPupil                  = float()
        self.RightValidity               = long()
                

    
    
    
    
    
    
    
    
    
    
