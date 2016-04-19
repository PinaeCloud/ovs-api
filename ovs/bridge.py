# coding=utf-8

from itertools import chain

from ovs import execute, db
from ovs.utils import decorator

class Bridge():
    
    @decorator.check_cmd(['ovs-vsctl -V'])
    def __init__(self):
        pass
    
    def list_br(self):
        cmd = 'ovs-vsctl list-br'
        result, error = execute.exec_cmd(cmd)
        return [l.strip() for l in result.split('\n') if l.strip()] if not error else []
                
    def exists_br(self, br_name):
        if br_name:
            brs = self.list_br()
            return True if br_name in brs else False
        else:
            raise IOError('Bridge name is NONE')
    
    def show_br(self):
        brs, br = {}, ''
        cmd = 'ovs-vsctl show'
        result, error = execute.exec_cmd(cmd)
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
    
    @decorator.check_arg
    def add_br(self, br_name, parent = None, vlan = None):
        if br_name:
            cmd = 'ovs-vsctl --may-exist add-br {0}'.format(br_name)
            if parent != None and vlan != None:
                cmd = '{0} {1} {2}'.format(cmd, parent, vlan)
            _, error = execute.exec_cmd(cmd)
            return False if error else True
        else:
            raise IOError('Bridge name is NONE')
    
    @decorator.check_arg
    def del_br(self, br_name):
        if br_name:
            cmd = 'ovs-vsctl --if-exists del-br {0}'.format(br_name)
            _, error = execute.exec_cmd(cmd)
            return False if error else True
        else:
            raise IOError('Bridge name is NONE')
        
    @decorator.check_arg
    def list_port(self, br_name):
        cmd = 'ovs-vsctl list-ports {0}'.format(br_name)
        result, error = execute.exec_cmd(cmd)
        return [l.strip() for l in result.split('\n') if l.strip()] if not error else []
    
    @decorator.check_arg
    def list_port_to_br(self, port_name):
        cmd = 'ovs-vsctl port-to-br {0}'.format(port_name)
        result, error = execute.exec_cmd(cmd)
        return [l.strip() for l in result.split('\n') if l.strip()] if not error else []
    
    @decorator.check_arg
    def add_port(self, br_name, port_name, iface = None):
        if br_name and port_name:
            cmd = 'ovs-vsctl add-port {0} {1}'.format(br_name, port_name)
            if iface != None:
                cmd = '{0} {1}'.format(cmd, iface)
            _, error = execute.exec_cmd(cmd)
            return False if error else True
        else:
            raise IOError('Bridge name or Port name is NONE')
    
    @decorator.check_arg
    def del_port(self, br_name, port_name):
        if br_name and port_name:
            cmd = 'ovs-vsctl del-port {0} {1}'.format(br_name, port_name)
            _, error = execute.exec_cmd(cmd)
            return False if error else True
        else:
            raise IOError('Bridge name or Port name is NONE')

    def mirror(self, name, br_name, input_port, output_port, direction = None):
        if name and br_name and input_port and output_port:
            br_cmd = '-- set bridge {0} mirror=@m'.format(br_name)
      
            ports = chain(input_port, output_port)
            ports_cmds = []
            for port in ports:
                ports_cmds.append('-- --id=@{0} get Port {0}'.format(port))
                
            mirror_cmd = '-- --id=@m create Mirror name={0}'.format(name)
            if not direction or direction == 'in' or direction == 'all':
                mirror_cmd += ' select-src-port=@' + ',@'.join(input_port)
            if not direction or direction == 'out' or direction == 'all':
                mirror_cmd += ' select-dst-port=@' + ',@'.join(input_port)
            mirror_cmd += ' output-port=@' + ',@'.join(output_port)
            
            cmd = 'ovs-vsctl {0} {1} {2}'.format(br_cmd, ' '.join(ports_cmds), mirror_cmd)
            _, error = execute.exec_cmd(cmd)
            return False if error else True
        else:
            raise IOError('Mirror name or Bridge name or Ports is NONE')
        
    def no_mirror(self, br_name):
        return self.__clear_br_attr(br_name, 'mirrors')
        
    def netflow(self, br_name, target_ip = '127.0.0.1', target_port = '5566', params = None):
        return self.__flow_rec(br_name, 'netflow', target_ip, target_port, params)
        
    def no_netflow(self, br_name):
        return self.__clear_br_attr(br_name, 'netflow')
    
    def sflow(self, br_name, agent, target_ip = '127.0.0.1', target_port = '6343', params = None):
        if agent:
            params = {} if not params else params
            params['agent'] = agent
        return self.__flow_rec(br_name, 'sflow', target_ip, target_port, params)
        
    def no_sflow(self, br_name):
        return self.__clear_br_attr(br_name, 'sflow')
    
    def ipfix(self, br_name, target_ip = '127.0.0.1', target_port = '4739', params = None):
        return self.__flow_rec(br_name, 'ipfix', target_ip, target_port, params)
        
    def no_ipfix(self, br_name): 
        return self.__clear_br_attr(br_name, 'ipfix')
    
    def qos(self, port_name, max_rate, min_rate):
        if port_name:
            max_rate = (100 if not str(max_rate).isalnum() or max_rate < 0 else max_rate) * 1000
            min_rate = (10 if not str(min_rate).isalnum() or min_rate < 0 else min_rate) * 1000
            
            port_cmd = '-- set port {0} qos=@q'.format(port_name)
            qos_cmd = '-- --id=@q create qos type=linux-htb other-config:max-rate={0} queues=0=@q0'.format(max_rate)
            queue_cmd = '-- --id=@q0 create queue other-config:min-rate={0} other-config:max-rate={1}'.format(min_rate, max_rate)
            
            cmd = 'ovs-vsctl {0} {1} {2}'.format(port_cmd, qos_cmd, queue_cmd)
            _, error = execute.exec_cmd(cmd)
            return False if error else True
        else:
            raise IOError('Port name is NONE')
    
    def no_qos(self, port_name, clean_policy = True):
        d = db.OVSDB()
        qos_id = d.get('Port', port_name, 'Qos')
        queue_id = d.get('QoS', qos_id, 'queues:0')
        if qos_id != '[]':
            if d.clear('Port', port_name, 'qos'):
                if clean_policy:
                    if d.destroy('QoS', qos_id) and d.destroy('Queue', queue_id):
                        return True
                else:
                    return True
        return False
                
    
    def ingress_rate(self, port_name, rate = 1000, burst = 100):
        if port_name:
            rate = 100 if not str(rate).isalnum() or rate < 0 else rate
            burst = 10 if not str(burst).isalnum() or burst < 0 else burst
            cmd = 'ovs-vsctl set Interface {0} ingress_policing_rate={1}'.format(port_name, rate)
            _, error = execute.exec_cmd(cmd)
            if not error:
                cmd = 'ovs-vsctl set Interface {0} ingress_policing_burst={1}'.format(port_name, burst)
                _, error = execute.exec_cmd(cmd)
            return False if error else True
                
        else:
            raise IOError('Port name is NONE')
    
    def no_ingress_rate(self, port_name):
        if port_name:
            cmd = 'ovs-vsctl set Interface {0} ingress_policing_rate=0'.format(port_name)
            _, error = execute.exec_cmd(cmd)
            if not error:
                cmd = 'ovs-vsctl set Interface {0} ingress_policing_burst=0'.format(port_name)
                _, error = execute.exec_cmd(cmd)
            return False if error else True
        else:
            raise IOError('Port name is NONE')
    
    def __flow_rec(self, br_name ,flow_type, target_ip, target_port, params):
        if br_name:
            cmd = 'ovs-vsctl -- set Bridge {0} {1}=@f '.format(br_name, flow_type) 
            cmd += '-- --id=@f create {0} targets=\\"{1}:{2}\\" '.format(flow_type, target_ip, target_port)
            cmd += self.__build_params(params)
            _, error = execute.exec_cmd(cmd)
            return False if error else True
        else:
            raise IOError('Bridge name is NONE')
    
    def __clear_br_attr(self, br_name, col_name):
        if br_name:
            return db.OVSDB().clear('Bridge', br_name, col_name)
        else:
            raise IOError('Bridge name is NONE')
        
    def __clear_port_attr(self, port_name, col_name):
        if port_name:
            return db.OVSDB().clear('Port', port_name, col_name)
        else:
            raise IOError('Port name is NONE')
        
    def __build_params(self, params):
        param_list = []
        if params and isinstance(params, dict):
            for key in params:
                value = params.get(key)
                param_list.append('{0}={1}'.format(key, value))
        return ' '.join(param_list)
    