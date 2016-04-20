# coding=utf-8

from ovs import execute
from ovs.utils import decorator

class SwitchLog():
    
    @decorator.check_cmd(['ovs-appctl -V'])
    def __init__(self):
        pass
    
    def list_log(self):
        log_lst = {}
        cmd = 'ovs-appctl vlog/list'
        result, error = execute.exec_cmd(cmd)
        if not error:
            for l in result.split('\n'):
                items = [item for item in l.strip().split(' ') if item.strip()]
                if len(items) == 4:
                    log_lst[items[0]] = {'console':items[1], 'syslog':items[2], 'file':items[3]}
                    
        return log_lst
    
    @decorator.check_arg
    def set_log(self, module, destination, level):
        cmd = 'ovs-appctl vlog/set {0}:{1}:{2}'.format(module, destination, level)
        _, error = execute.exec_cmd(cmd)
        return False if error else True
    
    @decorator.check_arg
    def set_log_pattern(self, destination, pattern):
        cmd = 'ovs-appctl vlog/set PATTERN:{0}:{1}'.format(destination, pattern)
        _, error = execute.exec_cmd(cmd)
        return False if error else True
    
    @decorator.check_arg
    def set_log_facility(self, facility):
        cmd = 'ovs-appctl vlog/set FACILITY:{0}'.format(facility)
        _, error = execute.exec_cmd(cmd)
        return False if error else True
        