# coding=utf-8

import os.path
import time
import json

from ovs import execute
from ovs.utils import decorator

class OVSDB():
    
    @decorator.check_cmd(['ovs-vsctl -V'])
    def __init__(self, db = None, timeout = None, dry_run = False):
        self.db = db
        self.cmd = 'ovs-vsctl'
        if db:
            self.cmd += ' --db=' + db
        if timeout != None:
            self.cmd += ' --timeout=' + timeout
        if dry_run:
            self.cmd += ' --dry_run' 
    
    @decorator.check_arg
    def list(self, table, record = None):
        cmd = '{0} list {1} {2}'.format(self.cmd, table, record if record else '')
        result, error = execute.exec_cmd(cmd)
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
        result, error = execute.exec_cmd(cmd)
        return result.strip() if not error else None
    
    @decorator.check_arg
    def set(self, table, record, data):
        cmd = '{0} set {1} {2} {3}'.format(self.cmd, table, record, self.__build_params(data))
        _, error = execute.exec_cmd(cmd)
        return False if error else True
    
    @decorator.check_arg
    def get_uuid(self, table, record):
        return self.get(table, record, '_uuid') 
    
    @decorator.check_arg
    def get(self, table, record, column, key = None):
        cmd = '{0} get {1} {2} {3}{4}'.format(self.cmd, table, record, column, ':' + key if key else '')
        result, error = execute.exec_cmd(cmd)
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
        _, error = execute.exec_cmd(cmd)
        return False if error else True

    @decorator.check_arg
    def add(self, table, record, column, data):
        cmd = '{0} add {1} {2} {3} {4}'.format(self.cmd, table, record, column, self.__build_params(data))
        _, error = execute.exec_cmd(cmd)
        return False if error else True
    
    @decorator.check_arg
    def remove(self, table, record, column, data):
        cmd = '{0} remove {1} {2} {3} {4}'.format(self.cmd, table, record, column, self.__build_params(data))
        _, error = execute.exec_cmd(cmd)
        return False if error else True
        
    @decorator.check_arg
    def create(self, table, data):
        cmd = '{0} create {1} {2}'.format(self.cmd, table, self.__build_params(data))
        _, error = execute.exec_cmd(cmd)
        return False if error else True
    
    @decorator.check_arg
    def destroy(self, table, record):
        cmd = '{0} destroy {1} {2}'.format(self.cmd, table, record)
        _, error = execute.exec_cmd(cmd)
        return False if error else True
    
    def history(self):
        _, records = self.__read(self.db)
        history_list = []
        if records:
            for r in records:
                date = r.get('_date') if '_date' in r else None
                comment = r.get('_comment') if '_comment' in r else None
                if date and comment:
                    date = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(date / 1000))
                    history_list.append((date, comment))
        return history_list 
                    
    def __read(self, db_path = None):
        
        db_path = '/etc/openvswitch/conf.db' if not db_path else db_path
        if not os.path.exists(db_path):
            return None, None
        
        summary, records = [], []
        with open(db_path) as f:
            for line in f:
                line = line.strip()
                if line:
                    if line.startswith('OVSDB'):
                        _, _, t, h = line.split(' ')
                        summary.append({'type': t, 'hash': h})
                    else:
                        records.append(json.loads(line))
        return summary, records
        
    def __build_params(self, data):
        if data != None:
            if isinstance(data, dict):
                kv = ''
                for key in data:
                    value = data.get(key)
                    if value != None:
                        if isinstance(value, dict):
                            for sub_k in value:
                                sub_v = value.get(sub_k)
                                if sub_v != None:
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
    