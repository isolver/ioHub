# -*- coding: utf-8 -*-
"""
Created on Sun Apr 07 05:54:44 2013

@author: Sol
"""

from HTMLParser import HTMLParser

utf8_dict=dict()

class Utf8Char(object):
    __slots__=['utf8','code_byte_size','cpt','char','name']
    def __init__(self):
        self.utf8=None
        self.code_byte_size=None
        self.cpt=None
        self.char=None
        self.name=None
    
    def finalize(self):
        b=self.utf8.split()
        self.code_byte_size=len(b)
        self.utf8=["{0:x}".format(int(i)) for i in b]
        self.utf8='0x'+''.join(self.utf8)
        
        self.name=self.name.strip()
    def __str__(self):
        return "Utf8Char(code = {0}, bytes = {1}, html = {2}, char = {3}, name= {4})".format(self.utf8,self.code_byte_size,self.cpt,self.char,self.name)

class MyHTMLParser(HTMLParser):
    current_utf8_entry=None   
    current_utf8char_attribute=None

    def handle_starttag(self, tag, attrs):
        for attr in attrs:
            if isinstance(attr,tuple):
                atype,value=attr
                if atype == 'class':
                    if value in ['cod','cev']: # start of new entry
                        if MyHTMLParser.current_utf8_entry:
                            MyHTMLParser.current_utf8_entry.finalize()                            
                            utf8_dict[MyHTMLParser.current_utf8_entry.utf8]=MyHTMLParser.current_utf8_entry                            
                            print 'Created UTF8Entry: {0}'.format(MyHTMLParser.current_utf8_entry) 
                        MyHTMLParser.current_utf8_entry=Utf8Char()
                    elif value == 'cpt':
                        MyHTMLParser.current_utf8char_attribute='cpt'
                    elif value == 'char':
                        MyHTMLParser.current_utf8char_attribute='char'
                    elif value == 'utf8':
                        MyHTMLParser.current_utf8char_attribute='utf8'
                    elif value == 'name':
                        MyHTMLParser.current_utf8char_attribute='name'
                        
    def handle_data(self, data):
        if MyHTMLParser.current_utf8char_attribute:
            setattr(MyHTMLParser.current_utf8_entry,MyHTMLParser.current_utf8char_attribute,data)
        MyHTMLParser.current_utf8char_attribute=None

parser = MyHTMLParser()

f = open(".\\Unicode UTF-8-character table P1.html",'r')

for line in f:
    parser.feed(line)
    