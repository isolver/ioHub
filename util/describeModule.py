## {{{ http://code.activestate.com/recipes/553262/ (r5)

# Describe classes, methods and functions in a module.
# Works with user-defined modules, all Python library
# modules, including built-in modules.

import inspect
import os, sys

INDENT=0

def wi(*args):
    """ Function to print lines indented according to level """

    if INDENT: print ' '*INDENT,
    for arg in args: print arg,
    print

def indent():
    """ Increase indentation """

    global INDENT
    INDENT += 4

def dedent():
    """ Decrease indentation """

    global INDENT
    INDENT -= 4

def describe_builtin(obj,isInherited=False):
    """ Describe a builtin function """
    if isInherited is True:
        isInherited='~'
    else:
        isInherited=''

    wi('%s+Built-in Function: %s' %(isInherited, obj.__name__))
    # Built-in functions cannot be inspected by
    # inspect.getargspec. We have to try and parse
    # the __doc__ attribute of the function.
    docstr = obj.__doc__
    args = ''

    if docstr:
        items = docstr.split('\n')
        if items:
            func_descr = items[0]
            s = func_descr.replace(obj.__name__,'')
            idx1 = s.find('(')
            idx2 = s.find(')',idx1)
            if idx1 != -1 and idx2 != -1 and (idx2>idx1+1):
                args = s[idx1+1:idx2]
                wi('\t-Method Arguments:', args)

    if args=='':
        wi('\t-Method Arguments: None')

    print

def describe_func(obj, method=False,isInherited=False):
    """ Describe the function object passed as argument.
If this is a method object, the second argument will
be passed as True """
    if isInherited is True:
        isInherited='~'
    else:
        isInherited=''

    if method:
        wi('%s+Method: %s' %(isInherited, obj.__name__))
    else:
        wi('%s+Function: %s' %(isInherited, obj.__name__))

    try:
        arginfo = inspect.getargspec(obj)
    except TypeError:
        print
        return

    args = arginfo[0]
    argsvar = arginfo[1]

    if args:
        if args[0] == 'self':
            wi('\t%s is an instance method' % obj.__name__)
            args.pop(0)

        wi('\t-Method Arguments:', args)

        if arginfo[3]:
            dl = len(arginfo[3])
            al = len(args)
            defargs = args[al-dl:al]
            wi('\t--Default arguments:',zip(defargs, arginfo[3]))

    if arginfo[1]:
        wi('\t-Positional Args Param: %s' % arginfo[1])
    if arginfo[2]:
        wi('\t-Keyword Args Param: %s' % arginfo[2])

    print

def describe_klass(obj,isInherited=False):
    """ Describe the class object passed as argument,
 including its methods """

    wi('+Class: %s' % obj.__name__)

    indent()

    count = 0

    for name in obj.__dict__:
        item = getattr(obj, name)
        if inspect.ismethod(item):
            count += 1;describe_func(item, True)
        else: print "<< ",name,": ",item," >>  skipped"

    if count==0:
        wi('(No members)')

    dedent()
    print

def describe_attribute(name,obj,isInherited=False):
    """ Describe the attribute object passed as argument,
 including its methods """
    if isInherited is True:
        isInherited='~'
    else:
        isInherited=''
    wi('{2}.Attribute: {0} : {1}'.format(name,obj,isInherited))


def describe(kclass,includeMro=False):
    """ Describe the class attribute object passed as argument
        including its classes and functions """


    klsList=[kclass,]
    if includeMro:
        klsList=inspect.getmro(kclass)

    for i,kls in enumerate(klsList):
        count = 0
        klasses={}
        methods={}
        builtins={}
        attributes={}
        nextkls=None
        if i+1 < len(klsList):
            nextkls=klsList[i+1]
        for name in dir(kls):

            if not name.startswith('__'):
                obj = getattr(kls, name)
                isInherited=False
                if hasattr(nextkls,name):
                    isInherited=True
                if inspect.isclass(obj):
                    klasses[name]=obj,isInherited
                    count+=1
                elif (inspect.ismethod(obj) or inspect.isfunction(obj)):
                    methods[name]=obj,isInherited
                    count+=1
                elif inspect.isbuiltin(obj):
                    builtins[name]=obj,isInherited
                    count+=1
                else:
                    attributes[name]=obj,isInherited
                    count+=1

        if count==0:
            wi('(No members)')
        else:
            if i==0:
                result=(attributes,methods,builtins,klasses)
            wi('[Class: %s]\n' % kls.__name__)

            indent()

            keys=attributes.keys()
            keys.sort()
            for atn in keys:
                describe_attribute(atn,attributes[atn][0],attributes[atn][1])

            print

            keys=methods.keys()
            keys.sort()
            for atn in methods.keys():
                describe_func( methods[atn][0],True,methods[atn][1])

            print

            keys=builtins.keys()
            keys.sort()
            for atn in builtins.keys():
                describe_builtin(builtins[atn][0],builtins[atn][1])

            print

            keys=klasses.keys()
            keys.sort()
            for atn in klasses.keys():
                describe_klass(klasses[atn][0],klasses[atn][1])


            dedent()
            return result
        return None

if __name__ == "__main__":
    import sys

    if len(sys.argv)<2:
        sys.exit('Usage: %s <module>' % sys.argv[0])

    module = sys.argv[1].replace('.py','')
    mod = __import__(module)
    describe(mod)
## end of http://code.activestate.com/recipes/553262/ }}}

