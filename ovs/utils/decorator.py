# coding=utf-8

import os

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