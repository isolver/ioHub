
class Events:
    def __getattr__(self, name):
        if hasattr(self.__class__, '__events__'):
            assert name in self.__class__.__events__, \
                     "Event '%s' is not declared" % name
        self.__dict__[name] = ev = _EventSlot(name)
        return ev
  
    def __repr__(self):
        return 'Events' + str(list(self))
    
    __str__ = __repr__
    
    def __len__(self): 
        return NotImplemented
    
    def __iter__(self):
        def gen(dictitems=self.__dict__.items()):
            for val in dictitems.itervalues():
                if isinstance(val, _EventSlot):
                    yield val
        return gen()


class _EventSlot:
    def __init__(self, name):
        self.targets = []
        self.__name__ = name

    def __repr__(self):
        return 'event ' + self.__name__

    def __call__(self, *a, **kw):
        for f in self.targets: f(*a, **kw)

    def __iadd__(self, f):
        self.targets.append(f)
        return self

    def __isub__(self, f):
        while f in self.targets: 
            self.targets.remove(f)
        return self

