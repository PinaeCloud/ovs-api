# coding=utf-8

from ovs.utils import execute
from ovs.utils import decorator

class Flow():
    
    def __init__(self):
        self.ethertype = {'ip' : 0x0800, 'arp' : 0x0808, 'ipv6' : 0x86DD, 'ppp' : 0x880B}
        self.ip_proto = {'icmp' : 1, 'igmp' : 2, 'tcp' : 6, 'udp' : 17, 'sctp' : 132}
    
    def ipv4_flow(self, in_port, priority, table, idle_timeout,
                   dl_type, dl_vlan, dl_src, dl_dst, 
                   nw_proto, nw_src, nw_dst, nw_tos, 
                   port_src, port_dst, tcp_flag, icmp_type, action, params = {}):
        
        if isinstance(dl_type, basestring):
            dl_type = dl_type.lower()
        dl_type = self.ethertype.get(dl_type) if self.ethertype.has_key(dl_type) else dl_type
            
        if isinstance(nw_proto, basestring):
            nw_proto = nw_proto.lower()
        nw_proto = self.ip_proto.get(nw_proto) if self.ip_proto.has_key(nw_proto) else nw_proto
        
        match_fields = {'in_port' : in_port, 'priority' : priority, 'table' : table, 'idle_timeout' : idle_timeout,
                'dl_type' : dl_type, 'dl_vlan' : dl_vlan, 'dl_src' :  dl_src, 'dl_dst' : dl_dst,
                'nw_proto' : nw_proto, 'nw_src' : nw_src, 'nw_dst' : nw_dst, 'nw_tos' : nw_tos,
                'tcp_flag' : tcp_flag, 'icmp_type' : icmp_type
                    }
            
        if nw_proto == 6: # TCP
            match_fields['tcp_src'], match_fields['tcp_dst'] = port_src, port_dst
        elif nw_proto == 17: # UDP
            match_fields['udp_src'], match_fields['udp_dst'] = port_src, port_dst
        elif nw_proto == 132: # SCTP
            match_fields['sctp_src'], match_fields['sctp_dst'] = port_src, port_dst
            
        return self.__build_flow(match_fields, action, params)
    
    def __build_flow(self, match_fields, action, params):
        
        fields = []
        
        if match_fields != None:
            for field_name in match_fields:
                field_value = match_fields.get(field_name)
                if field_value != None:
                    fields.append('{0}={1}'.format(field_name, field_value))
                
        if params != None: 
            for param_name in params:
                param_value = params.get(params.get(param_name))
                if param_value != None:
                    fields.append('{0}={1}'.format(field_name, field_value))
               
        flow = ', '.join(fields)
        
        if action != None:
            actions = []
            for action_name in action:
                action_value = action.get(action_name)
                if action_value != None:
                    actions.append('{0}:{1}'.format(action_name, action_value))
                else:
                    actions.append(action_name)
            flow = '{0}, actions={1}'.format(flow, ','.join(actions))
                    
        return flow

class MeterTable():
    def __init__(self):
        pass
    
    def dump_meters(self):
        pass
    
    def add_meter(self):
        pass
    
    def mod_meter(self):
        pass
    
    def del_meter(self):
        pass

class FlowTable():
    
    @decorator.check_cmd(['ovs-ofctl -V'])
    def __init__(self):
        pass
    
    def dump_flow(self, br_name, flow_cond = None):
        if not br_name:
            raise ValueError('Bridge name is None')
        cmd = 'ovs-ofctl dump-flows {0} \"{1}\"'.format(br_name, flow_cond if flow_cond else '')
        result, error = execute.exec_cmd(cmd)
        flows = []
        if not error:
            lines = result.split('\n')
            for l in lines:
                l = l.strip()
                if l != None and not l.startswith('NXST_FLOW'):
                    if 'actions' in l:
                        flow = {}
                        i = l.index('actions')
                        conition, action = l[:i], l[i:]
                        if conition:
                            for item in conition.split(','):
                                item = item.strip()
                                if '=' in item:
                                    k, v = item.split('=')
                                    flow[k] = v
                                else:
                                    flow['protocol'] = item
                        if action:
                            k, v = action.split('=')
                            flow[k] = v
                        flows.append(flow)
            return flows
        else:
            return []
    
    def add_flow(self, br_name, flow):
        if not br_name:
            raise ValueError('Bridge name is None')
        if not flow:
            raise ValueError('Flow is None')
        cmd = 'ovs-ofctl add-flow {0} \"{1}\"'.format(br_name, flow)
        _, error = execute.exec_cmd(cmd)
        return False if error else True
    
    def del_flow(self, br_name, flow = None):
        if not br_name:
            raise ValueError('Bridge name is None')
        cmd = 'ovs-ofctl del-flows {0} \"{1}\"'.format(br_name, flow)
        _, error = execute.exec_cmd(cmd)
        return False if error else True
    
class GroupTable():
    
    def __init__(self):
        pass
    
    def dump_group(self):
        pass
    
    def add_group(self):
        pass
    
    def mod_group(self):
        pass
    
    def del_group(self):
        pass
    
    def insert_buckets(self):
        pass
    
    def remove_buckets(self):
        pass
