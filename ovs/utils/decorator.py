# coding=utf-8

import os
from subprocess import Popen, PIPE

def check_cmd(cmd_list):
    def decorators(func):
        def wrapper(*args, **kwargs):
            for cmd in cmd_list:
                cmd += ' >/dev/null 2>/dev/null' 
                if os.system(cmd) != 0:
                    raise IOError('Command check fail : ' + cmd)
            return func( *args , **kwargs)
        return wrapper
    return decorators

def check_arg(func):
    def wrapper(*args, **kwargs):
        symbol = ['|', '>', '<']
        for arg in args:
            if isinstance(arg, basestring):
                for s in symbol:
                    if s in arg:
                        raise ValueError('Illegal arguments')
        return func( *args , **kwargs)
    return wrapper


def check_version(version):
    def decorators(func):
        def wrapper(*args, **kwargs):
            cmd = 'ovs-vswitchd -V | head -n 1'
            result, error = Popen(cmd, stdout=PIPE, stderr=PIPE, shell=True).communicate()
            if error:
                raise IOError('Version check fail : ' + error)
            else:
                ovs_ver = result[result.rindex(' '): ].strip()
                
                v1 = ovs_ver.split('.')
                v2 = version.split('.')
                if len(v1) == len(v2):
                    for i in range(len(v1)):
                        if int(v1[i]) > int(v2[i]):
                            break
                        if int(v1[i]) < int(v2[i]):
                            raise IOError('OpenvSwitch version is {0} lower than {1}'.format(ovs_ver, version))
                        
            return func( *args , **kwargs)
        return wrapper
    return decorators
        