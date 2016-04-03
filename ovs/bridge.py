# coding=utf-8

import json

from ovs.utils import decorator
from subprocess import Popen, PIPE

class Bridge():
    
    def __init__(self):
        pass
    
    @decorator.check_cmd(['ovs-vsctl --version > /dev/null'])
    def inspect(self, obj_type, obj_name):
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
    
    @decorator.check_cmd(['ovs-vsctl --version > /dev/null'])
    def list_br(self):
        cmd = 'ovs-vsctl list-br'
        result, error = Popen(cmd, stdout=PIPE, stderr=PIPE, shell=True).communicate() 
        return [l.strip() for l in result.split('\n') if l.strip()] if not error else []
    
    def inspect_br(self, br_name):
        return self.inspect('br', br_name)
                
    def exists_br(self, br_name):
        if br_name:
            brs = self.list_br()
            return True if br_name in brs else False
        else:
            raise IOError('Bridge name is NONE')
    
    @decorator.check_cmd(['ovs-vsctl --version > /dev/null'])
    def show_br(self):
        brs, br = {}, ''
        cmd = 'ovs-vsctl show'
        result, error = Popen(cmd, stdout=PIPE, stderr=PIPE, shell=True).communicate()
        if error:
            return {}
        for l in result.split('\n'):
            l = l.strip().replace('"', '')
            if l.startswith('Bridge '):
                br = l.lstrip('Bridge ')
                brs[br] = {}
                brs[br]['Controller'] = []
                brs[br]['Port'] = {}
                brs[br]['fail_mode'] = ''
            else:
                if l.startswith('Controller '):
                    brs[br]['Controller'].append(l.replace('Controller ', ''))
                elif l.startswith('fail_mode: '):
                    brs[br]['fail_mode'] = l.replace('fail_mode: ', '')
                elif l.startswith('Port '):
                    phy_port = l.replace('Port ', '')  # e.g., br-eth0
                    brs[br]['Port'][phy_port] = {'vlan': '', 'type': ''}
                elif l.startswith('tag: '):
                    brs[br]['Port'][phy_port]['vlan'] = l.replace('tag: ', '')
                elif l.startswith('Interface '):
                    brs[br]['Port'][phy_port]['intf'] = \
                        l.replace('Interface ', '')
                elif l.startswith('type: '):
                    brs[br]['Port'][phy_port]['type'] = l.replace('type: ', '')
        return brs
    
    @decorator.check_cmd(['ovs-vsctl --version > /dev/null'])
    def add_br(self, br_name, parent = None, vlan = None):
        if br_name:
            cmd = 'ovs-vsctl add-br {0}'.format(br_name)
            if parent != None and vlan != None:
                cmd = '{0} {1} {2}'.format(cmd, parent, vlan)
            _, error = Popen(cmd, stdout=PIPE, stderr=PIPE, shell=True).communicate()
            return False if error else True
        else:
            raise IOError('Bridge name is NONE')
    
    @decorator.check_cmd(['ovs-vsctl --version > /dev/null'])
    def del_br(self, br_name):
        if br_name:
            cmd = 'ovs-vsctl del-br {0}'.format(br_name)
            _, error = Popen(cmd, stdout=PIPE, stderr=PIPE, shell=True).communicate()
            return False if error else True
        else:
            raise IOError('Bridge name is NONE')
        
    @decorator.check_cmd(['ovs-vsctl --version > /dev/null'])
    def list_port(self, br_name):
        cmd = 'ovs-vsctl list-ports {0}'.format(br_name)
        result, error = Popen(cmd, stdout=PIPE, stderr=PIPE, shell=True).communicate() 
        return [l.strip() for l in result.split('\n') if l.strip()] if not error else []
            
    def inspect_port(self, port_name):
        return self.inspect('port', port_name)
    
    @decorator.check_cmd(['ovs-vsctl --version > /dev/null'])
    def add_port(self, br_name, port_name, iface = None):
        if br_name and port_name:
            cmd = 'ovs-vsctl add-port {0} {1}'.format(br_name, port_name)
            if iface != None:
                cmd = '{0} {1}'.format(cmd, iface)
            _, error = Popen(cmd, stdout=PIPE, stderr=PIPE, shell=True).communicate()
            return False if error else True
        else:
            raise IOError('Bridge name or Port name is NONE')
    
    @decorator.check_cmd(['ovs-vsctl --version > /dev/null'])
    def del_port(self, br_name, port_name):
        if br_name and port_name:
            cmd = 'ovs-vsctl del-port {0} {1}'.format(br_name, port_name)
            _, error = Popen(cmd, stdout=PIPE, stderr=PIPE, shell=True).communicate()
            return False if error else True
        else:
            raise IOError('Bridge name or Port name is NONE')
    
    def dump_ports(self):
        pass
    
    def vlan(self):
        pass
    
    def mirror(self):
        pass

    