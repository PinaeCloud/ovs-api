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
    
    