# coding=utf-8

from ovs.utils import decorator
from subprocess import Popen, PIPE

class OVSDB():
    
    @decorator.check_cmd(['ovs-vsctl -V'])
    @decorator.check_arg
    def list(self, obj_type, obj_name):
        cmd = 'ovs-vsctl list {0} {1}'.format(obj_type, obj_name)
        result, error = Popen(cmd, stdout=PIPE, stderr=PIPE, shell=True).communicate()
        objs = []
        if not error:
            obj = {}
            for l in result.split('\n'):
                if not l.strip():
                    objs.append(obj)
                    obj = {}
                else:
                    if ':' in l:
                        key, value = l.split(':', 1)
                        obj[key.strip()] = value.strip()
        return objs
    
    @decorator.check_cmd(['ovs-vsctl -V'])
    @decorator.check_arg
    def set(self, obj_type, obj_name, obj_data):
        cmd = 'ovs-vsctl set {0} {1}'.format(obj_type, obj_name)
        for key in obj_data:
            cmd += ' {0}={1}'.format(key, obj_data.get(key))
        _, error = Popen(cmd, stdout=PIPE, stderr=PIPE, shell=True).communicate()
        return False if error else True
    
    @decorator.check_cmd(['ovs-vsctl -V'])
    @decorator.check_arg
    def get(self, obj_type, obj_name, obj_key):
        cmd = 'ovs-vsctl get {0} {1} {2}'.format(obj_type, obj_name, obj_key)
        result, error = Popen(cmd, stdout=PIPE, stderr=PIPE, shell=True).communicate()
        return result.strip() if not error else None
    
    @decorator.check_cmd(['ovs-vsctl -V'])
    @decorator.check_arg
    def clear(self, obj_type, obj_name, obj_key):
        cmd = 'ovs-vsctl clear {0} {1} {2}'.format(obj_type, obj_name, obj_key)
        _, error = Popen(cmd, stdout=PIPE, stderr=PIPE, shell=True).communicate()
        return False if error else True
        
    
    