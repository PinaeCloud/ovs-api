# coding=utf-8

import os.path

from ovs import execute
from ovs.utils import decorator
from ovs.utils import ip_utils
from ovs import bridge, db

class Docker():
    
    @decorator.check_cmd(['ip -V', 'ovs-vsctl -V', 'docker -v'])
    def __init__(self):
        self.b = bridge.Bridge()
        self.d = db.OVSDB
    
    def connect(self, container_name, br_name, ip, gateway, if_name = None, mtu = 1500, vlan = 0):
        
        if not container_name:
            raise ValueError('Container name is None')
        if not ip or not gateway:
            raise ValueError('IP or Gateway is None')
        
        # Get Docker container PID
        c_pid = self.__get_container_pid(container_name)
        
        self.__ln_netns(c_pid)
        
        iface = ip_utils.IFace()
        netns = ip_utils.Netns()
        guest_iface = ip_utils.IFace(netns.get_exec(c_pid))
        guest_addr = ip_utils.Address(netns.get_exec(c_pid))
        guest_route = ip_utils.Route(netns.get_exec(c_pid))
        
        # Set local interface name and guest interface name
        if_name = 'eth0' if not if_name else if_name
        local_if = 'v{0}pl{1}'.format(if_name, c_pid)
        guest_if = 'v{0}pg{1}'.format(if_name, c_pid)
        
        # Add new local interface and guest interface
        if not iface.exist_if(local_if):
            if not iface.add_veth_peer_if(local_if, guest_if, mtu):
                raise IOError('Add new interface {0}　and {1} fail'.format(local_if, guest_if))
        
        # Add local interface to openvswitch
        if not self.b.exists_br(br_name):
            self.b.add_br(br_name)
        if self.b.exists_port(br_name, local_if):
            self.b.del_port(br_name, local_if)
        if self.b.add_port(br_name, local_if):
            if vlan:
                self.d.set('Port', local_if, {'tag' : vlan})
        else:
            raise IOError('Add {0} to bridge {1} fail'.format(local_if, br_name))
        
        # Startup local interface
        if not iface.startup(local_if):
            raise IOError('Startup local interface {0}　fail'.format(local_if))
        
        # Set guest interface to PID
        if not iface.set_if(guest_if, 'netns', c_pid):
            raise IOError('Set guest interface {0} to {1} fail'.format(guest_if, c_pid))
        
        # Rename guest interface
        if guest_iface.exist_if(if_name):
            guest_iface.del_if(if_name)
        if not guest_iface.set_if(guest_if, 'name', if_name):
            raise IOError('Rename {0} to {1} fail'.format(guest_if, if_name))
        
        # Set guest interface ip
        if ip and not guest_addr.add_addr(if_name, ip):
            raise IOError('Set guest interface {0} ip:{1} fail'.format(if_name, ip))
        
        # Delete guest interface default route
        if gateway:
            guest_route.del_route(None, 'default')
        
        # Startup guest interface
        if not guest_iface.startup(if_name):
            raise IOError('Startup guest interface {0} fail'.format(if_name))
        
        # Set guest default gateway
        if gateway and not guest_route.add_route(gateway):
            raise IOError('Replace gateway {0} fail'.format(gateway))
        
        # Execute arping
        if execute.check_cmd('arping -V'):
            ip, _ = ip.split('/')
            netns.exec_ns(c_pid, 'arping -c 1 -A -I {0} {1}'.format(if_name, ip))
        
        return True
    
    def disconnect(self, container_name, br_name, if_name):
        c_pid = self.__get_container_pid(container_name)
        self.__ln_netns(c_pid)
        
        iface = ip_utils.IFace()
        netns = ip_utils.Netns()
        guest_iface = ip_utils.IFace(netns.get_exec(c_pid))
        
        # Set local interface name and guest interface name
        if_name = 'eth0' if not if_name else if_name
        local_if = 'v{0}pl{1}'.format(if_name, c_pid)
        
        # Rename guest interface
        if guest_iface.exist_if(if_name):
            guest_iface.del_if(if_name)
        
        # Delete ovs interface 
        if self.b.exists_port(br_name, local_if):
            self.b.del_port(br_name, local_if)
            
        # Delete local interface
        if iface.exist_if(local_if):
            iface.del_if(local_if)

    def __get_container_pid(self, container_name):
        c_pid, error = execute.exec_cmd('docker inspect --format={{.State.Pid}} ' + container_name)
        if not c_pid or error:
            raise IOError('Get container {0} PID fail : {1}'.format(container_name, error))
        return c_pid.strip()
    
    def __ln_netns(self, c_pid):
        # Link container's netns
        execute.exec_cmd('rm -f /var/run/netns/{0}'.format(c_pid))
        if not os.path.exists('/var/run/netns'):
            os.makedirs('/var/run/netns', 0755)
            execute.exec_cmd('ln -s /proc/{0}/ns/net /var/run/netns/{0}'.format(c_pid))
        