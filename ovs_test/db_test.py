# coding=utf-8

import unittest
from ovs import bridge, db

class OVSDBTest(unittest.TestCase):
    def setUp(self):
    
        self.br_name = 'obr-test'
        self.port_name = 'vport-test'
        
        self.b = bridge.Bridge()
        if not self.b.add_br(self.br_name):
            self.fail('add_br: add bridge fail : ' + self.br_name)
        if not self.b.add_port(self.br_name, self.port_name):
            self.fail('add_port: add port fail : ' + self.port_name)
            
        self.d = db.OVSDB()
            
    def tearDown(self):
        if not self.b.del_port(self.br_name, self.port_name):
            self.fail('del_port: delete port fail : ' + self.port_name)
        if not self.b.del_br(self.br_name):
            self.fail('del_br: delete bridge fail : ' + self.br_name)
            
    def test_list_br(self):
        brs = self.d.list('br', self.br_name)
        self.assertEquals(brs[0].get('name'), self.br_name)
        
    def test_list_port(self):
        ports = self.d.list('port', self.port_name)
        self.assertEquals(ports[0].get('name'), self.port_name)
        