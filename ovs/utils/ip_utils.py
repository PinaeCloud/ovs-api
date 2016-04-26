# coding=utf-8

from ovs.utils import execute
from ovs.utils import decorator

class IFace():
    
    @decorator.check_cmd(['ip -V'])
    def __init__(self, netns = None):
        self.netns = netns if netns else ''
    
    @decorator.check_arg
    def add_if(self, if_name, if_type = None, mtu = 1500, args = None):
        if if_name:
            if_type = ' type ' + if_type if if_type else ''
            _, error = execute.exec_cmd('{0} ip link add name {1} mtu {2} {3} {4}'.format(self.netns, if_name, mtu, if_type, args if args else ''))
            return False if error else True
        else:
            raise ValueError('Interface name is None')
    
    @decorator.check_arg
    def add_veth_peer_if(self, local_if, guest_if, mtu = 1500):
        return self.add_if(local_if, 'veth', mtu, 'peer name {0} mtu {1}'.format(guest_if, mtu))
    
    @decorator.check_arg
    def del_if(self, if_name):
        if if_name:
            _, error = execute.exec_cmd('{0} ip link delete {1}'.format(self.netns, if_name))
            return False if error else True
        else:
            raise ValueError('Interface name is None')
    
    @decorator.check_arg
    def exist_if(self, if_name):
        if if_name:
            _, error = execute.exec_cmd('{0} ip link show {1}'.format(self.netns, if_name))
            return False if error else True
        else:
            raise ValueError('Interface name is None')
    
    @decorator.check_arg
    def set_if(self, if_name, key, value):
        if if_name:
            if not key or not value:
                raise ValueError('Key or Value is None')
            _, error = execute.exec_cmd('{0} ip link set {1} {2} {3}'.format(self.netns, if_name, key, value))
            return False if error else True
        else:
            raise ValueError('Interface name is None')
    
    @decorator.check_arg
    def startup(self, if_name):
        if if_name:
            _, error = execute.exec_cmd('{0} ip link set {1} up'.format(self.netns, if_name))
            return False if error else True
        else:
            raise ValueError('Interface name is None')
    
    @decorator.check_arg
    def shutdown(self, if_name):
        if if_name:
            _, error = execute.exec_cmd('{0} ip link set {1} down'.format(self.netns, if_name))
            return False if error else True
        else:
            raise ValueError('Interface name is None')

class Address():
    
    @decorator.check_cmd(['ip -V'])
    def __init__(self, netns = None):
        self.netns = netns if netns else ''
        
    @decorator.check_arg
    def add_addr(self, if_name, ip_addr):
        if if_name:
            if not ip_addr:
                raise ValueError('Ip Address is None')
            _, error = execute.exec_cmd('{0} ip addr add {1} dev {2}'.format(self.netns, ip_addr, if_name))
            return False if error else True
        else:
            raise ValueError('Interface name is None')
    
    @decorator.check_arg
    def del_addr(self, if_name, ip_addr):
        if if_name:
            if not ip_addr:
                raise ValueError('Ip Address is None')
            _, error = execute.exec_cmd('{0} ip addr del {1} dev {2}'.format(self.netns, ip_addr, if_name))
            return False if error else True
        else:
            raise ValueError('Interface name is None')
    
    @decorator.check_arg
    def flush(self, if_name):
        if if_name:
            _, error = execute.exec_cmd('{0} ip addr flush dev {1}'.format(self.netns, if_name))
            return False if error else True
        else:
            raise ValueError('Interface name is None')
    
class Route():
    
    @decorator.check_cmd(['ip -V'])
    def __init__(self, netns = None):
        self.netns = netns if netns else ''
    
    @decorator.check_arg
    def add_route(self, gw, dst_ip = None, if_name = None):
        if gw:
            dst_ip = 'default' if not dst_ip else dst_ip
            if_name = 'dev ' + if_name if if_name else ''
            _, error = execute.exec_cmd('{0} ip route replace {1} via {2} {3}'.format(self.netns, dst_ip, gw, if_name))
            return False if error else True
        else:
            raise ValueError('Gateway is None')
    
    @decorator.check_arg
    def del_route(self, gw, dst_ip = None, if_name = None):
        if gw:
            dst_ip = 'default' if not dst_ip else dst_ip
            if_name = 'dev ' + if_name if if_name else ''
            if gw:
                _, error = execute.exec_cmd('{0} ip route del {1} via {2} {3}'.format(self.netns, dst_ip, gw, if_name))
            else:
                _, error = execute.exec_cmd('{0} ip route del {1}'.format(self.netns, dst_ip))
            return False if error else True
        else:
            raise ValueError('Gateway is None')
    
    @decorator.check_arg
    def flush(self):
        _, error = execute.exec_cmd('{0} ip route flush cache')
        return False if error else True
    
class Netns():
    
    def __init__(self):
        pass
    
    def add_ns(self, ns_name):
        if ns_name:
            _, error = execute.exec_cmd('ip netns add {0}'.format(ns_name))
            return False if error else True
        else:
            raise ValueError('Naamespace name is None')
    
    def del_ns(self, ns_name):
        if ns_name:
            _, error = execute.exec_cmd('ip netns del {0}'.format(ns_name))
            return False if error else True
        else:
            raise ValueError('Naamespace name is None')
    
    def get_exec(self, pid):
        return 'ip netns exec {0}'.format(pid) if pid else None
    
    def exec_ns(self, pid, cmd):
        return execute.exec_cmd('ip netns exec {0} {1}'.format(pid, cmd)) if pid and cmd else None
    