# coding=utf-8

from ovs.utils import execute
from ovs.utils import decorator

class Tap():
    
    @decorator.check_cmd(['command -v tunctl'])
    def __init__(self):
        pass
    
    @decorator.check_arg
    def add_tap(self, tap_name):
        if tap_name:
            _, error = execute.exec_cmd('tunctl -t {0}'.format(tap_name))
            return False if error else True
        else:
            raise ValueError('Tap interface name is None')
        
    @decorator.check_arg
    def del_tap(self, tap_name):
        if tap_name:
            _, error = execute.exec_cmd('tunctl -d {0}'.format(tap_name))
            return False if error else True
        else:
            raise ValueError('Tap interface name is None')