# coding=utf-8

from ovs.utils import decorator
from subprocess import Popen, PIPE

class OVSDB():
    
    @decorator.check_cmd(['ovs-vsctl -V'])
    def __init__(self, db = None, timeout = None, dry_run = False):
        self.cmd = 'ovs-vsctl'
        if db:
            self.cmd += ' --db=' + db
        if timeout:
            self.cmd += ' --timeout=' + timeout
        if dry_run:
            self.cmd += ' --dry_run' 
    
    @decorator.check_arg
    def list(self, table, record = None):
        cmd = '{0} list {1} {2}'.format(self.cmd, table, record if record else '')
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
    
    @decorator.check_arg
    def find(self, table, condition):
        cmd = '{0} find {1} {2}'.format(self.cmd, table, condition)
        result, error = Popen(cmd, stdout=PIPE, stderr=PIPE, shell=True).communicate()
        return result.strip() if not error else None
    
    @decorator.check_arg
    def set(self, table, record, data):
        cmd = '{0} set {1} {2} {3}'.format(self.cmd, table, record, self.__data(data))
        _, error = Popen(cmd, stdout=PIPE, stderr=PIPE, shell=True).communicate()
        return False if error else True
    
    @decorator.check_arg
    def get(self, table, record, column, key = None):
        cmd = '{0} get {1} {2} {3}{4}'.format(self.cmd, table, record, column, ':' + key if key else '')
        result, error = Popen(cmd, stdout=PIPE, stderr=PIPE, shell=True).communicate()
        if not error:
            result = result.strip()
            if result.startswith('"') and result.endswith('"'):
                result = result[1:len(result) - 1]
            return result
        else:
            return None
    
    @decorator.check_arg
    def clear(self, table, record, column):
        cmd = '{0} clear {1} {2} {3}'.format(self.cmd, table, record, column)
        _, error = Popen(cmd, stdout=PIPE, stderr=PIPE, shell=True).communicate()
        return False if error else True

    @decorator.check_arg
    def add(self, table, record, column, data):
        cmd = '{0} add {1} {2} {3} {4}'.format(self.cmd, table, record, column, self.__data(data))
        _, error = Popen(cmd, stdout=PIPE, stderr=PIPE, shell=True).communicate()
        return False if error else True
    
    @decorator.check_arg
    def remove(self, table, record, column, data):
        cmd = '{0} remove {1} {2} {3} {4}'.format(self.cmd, table, record, column, self.__data(data))
        _, error = Popen(cmd, stdout=PIPE, stderr=PIPE, shell=True).communicate()
        return False if error else True
        
    @decorator.check_arg
    def create(self, table, data):
        cmd = '{0} create {1} {2}'.format(self.cmd, table, self.__data(data))
        _, error = Popen(cmd, stdout=PIPE, stderr=PIPE, shell=True).communicate()
        return False if error else True
    
    @decorator.check_arg
    def destroy(self, table, record):
        cmd = '{0} destroy {1} {2}'.format(self.cmd, table, record)
        _, error = Popen(cmd, stdout=PIPE, stderr=PIPE, shell=True).communicate()
        return False if error else True
    
    def __data(self, data):
        if data:
            if isinstance(data, dict):
                kv = ''
                for key in data:
                    value = data.get(key)
                    if value:
                        if isinstance(value, dict):
                            for sub_k in value:
                                sub_v = value.get(sub_k)
                                kv += ' {0}:{1}={2}'.format(key, sub_k, self.__convert(sub_v))
                        else:
                            kv += ' {0}={1}'.format(key, self.__convert(value))
                return kv.strip()
            else:
                return self.__convert(data)
        return ''
    
    def __convert(self, value):
        if not isinstance(value, basestring):
            value = str(value)
        return '"{0}"'.format(value) if ' ' in value else value