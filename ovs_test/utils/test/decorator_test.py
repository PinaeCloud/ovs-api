#coding=utf-8

import unittest
from ovs.utils import decorator

class DecoratorTest(unittest.TestCase):
    
    def test_check_cmd(self):
        @decorator.check_cmd(['no-such-cmd'])
        def cmd_1():
            pass
        
        @decorator.check_cmd(['echo hello']) 
        def cmd_2():
            pass
        
        try:
            cmd_1()
        except:
            self.assertRaises(IOError)
        
        cmd_2()
        
    def test_check_arg(self):
        @decorator.check_arg
        def cmd(arg1, arg2):
            pass
        try:
            cmd('| more', '> file')
        except:
            self.assertRaises(ValueError)
        cmd('hello', 'world')
