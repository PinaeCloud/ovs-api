# coding=utf-8

import unittest

from ovs import bridge
from ovs import flow

class FlowTableTest(unittest.TestCase):
    
    def setUp(self):
        self.br_name = 'obr-test'
        self.b = bridge.Bridge()
        if not self.b.add_br(self.br_name):
            self.fail('add_br: add bridge fail : ' + self.br_name)
        
        self.f = flow.Flow()
        self.ft = flow.FlowTable()
        
    def tearDown(self):
        if not self.b.del_br(self.br_name):
            self.fail('del_br: delete bridge fail : ' + self.br_name)
            
    def test_flow_table(self):
        flow_info = self.f.ipv4_flow(None, None, 100, None, 
                                    'ip', None, None, None, 
                                    'tcp', None, '192.168.24.0/24', None, 
                                    None, '80', None, None, {'output' : 1}, None)
        if not self.ft.add_flow(self.br_name, flow_info):
            self.fail('add_flow: add flow fail : {0}'.format(flow_info))
            
        flow_info = self.f.ipv4_flow(None, None, 100, None, 
                                    'ip', None, '00:05:2E:12:06:12', None, 
                                    'icmp', None, None, None, 
                                    None, None, None, None, {'output' : 2}, None)
        if not self.ft.add_flow(self.br_name, flow_info):
            self.fail('add_flow: add flow fail : {0}'.format(flow_info))
            
        result = self.ft.dump_flow(self.br_name)
        self.assertEquals(len(result), 3)
        
        if not self.ft.del_flow(self.br_name, 'tcp'):
            self.fail('del_flow: del flow fail')
            
        result = self.ft.dump_flow(self.br_name)
        self.assertEquals(len(result), 2)
        