# coding=utf-8

import os
import logging 
from subprocess import Popen, PIPE

enable_log_command = True
enable_log_result = False
enable_log_error = True
enable_raise = False

fmt = '%(asctime)s - %(name)s [%(process)d] : %(message)s' 
handler = logging.StreamHandler()
handler.setFormatter(logging.Formatter(fmt))
    
logger = logging.getLogger('execute')
logger.addHandler(handler)
logger.setLevel(logging.DEBUG)

def exec_cmd(cmd):
    if not cmd.strip():
        raise ValueError('Command is Empty')
    if cmd and isinstance(cmd, basestring):
        cmd = cmd.strip()
        if enable_log_command :
            logger.debug(cmd) 
        result, error = Popen(cmd, stdout=PIPE, stderr=PIPE, shell=True).communicate()
        if not error and enable_log_result:
            logger.debug(result)
        if error and enable_log_error:
            logger.error(error)
        if enable_raise:
            raise IOError(error) 
        return result, error
    raise IOError('Command is None or Command is not string')

def check_cmd(cmd):
    cmd += ' >/dev/null 2>/dev/null' 
    return os.system(cmd) == 0
