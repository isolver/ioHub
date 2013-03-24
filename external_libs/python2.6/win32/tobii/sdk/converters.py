
import struct
from tobii.sdk.types import (Point2D, Node)

unpack_from = None
try: 
    unpack_from = struct.unpack_from
except AttributeError:
    def f(format, blob, offset):
        size = struct.calcsize(format)
        return struct.unpack(format, blob[offset:offset+size])
    unpack_from = f

class OneCalibrationSample(object):
    def __init__(self, map_point, validity, quality):
        self.map_point = map_point
        self.validity = validity
        self.quality = quality
    
    def __str__(self):
        return "%s validity: %d" % (self.map_point, self.validity)
    
    @staticmethod
    def _extract(blob, offset):
        (x, y, v, q) = unpack_from("<fflf", blob, offset)
        return OneCalibrationSample(Point2D(x, y), v, q)
    
    @staticmethod
    def _size():
        return struct.calcsize("<fflf")


class OneCalibrationData(object):
    def __init__(self, true_point, left_sample, right_sample):
        self.true_point = true_point
        self.left = left_sample
        self.right = right_sample
    
    def __str__(self):
        return "%s --> [left: %s, right: %s]" % (self.true_point, self.left, self.right)

    @staticmethod
    def _extract(blob, offset):
        (x, y) = unpack_from("<ff", blob, offset)
        left = OneCalibrationSample._extract(blob, offset + struct.calcsize("<ff"))
        right = OneCalibrationSample._extract(blob, offset + struct.calcsize("<ff") + OneCalibrationSample._size())
        return OneCalibrationData(Point2D(x, y), left, right)

    @staticmethod
    def _size():
        return struct.calcsize("<ff") + 2 * OneCalibrationSample._size()


class Calibration(object):
    def __init__(self, blob):
        self.rawData = blob
        
        self.data = []
        
        raw_data_size = unpack_from("<L", self.rawData, 0)
        offset = struct.calcsize("<L") + raw_data_size[0]
        num_data = unpack_from("<L", self.rawData, offset)
        offset = offset + struct.calcsize("<L")
        
        for i in xrange(num_data[0]):
            self.data.append(OneCalibrationData._extract(blob, offset))
            offset += OneCalibrationData._size()
            i = i # remove warning
            
    
    @property
    def plot_data(self):
        return self.data


def ToCalibration(param_stack):
    return Calibration(param_stack[0])


class ParamStackReader(object):
    def __init__(self, param_stack, index=0):
        self.param_stack = param_stack
        self.index = index

    def pop(self):
        if self.param_stack.get_type(self.index) != 10: # node_prolog
            value = self.param_stack[self.index]
            self.index += 1
            return value
        
        node_prolog = self.param_stack[self.index]
        node_length = self._length(node_prolog)
        node_type = self._type(node_prolog)
        self.index += 1
        return self._pop_node(node_length, Node(type=node_type))
    
    def skip(self):
        self.pop()
    
    def _pop_node(self, length, current_node):
        while length:
            current_node.append(self.pop())
            length -= 1
        return current_node
    
    def _length(self, node_prolog):
        return (node_prolog & 0x0fff0000) >> 16
    
    def _type(self, node_prolog):
        return (node_prolog & 0x0000ffff)

        
