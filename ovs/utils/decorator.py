# coding=utf-8

import os

def check_cmd(cmd_list):
    def decorators(func):
        def wrapper(*args, **kwargs):
            for cmd in cmd_list:
                if os.system(cmd) != 0:
                    raise IOError('Command check fail : ' + cmd)
            return func( *args , **kwargs)
        return wrapper
    return decorators
