# coding=utf-8

import unittest
from ovs import bridge

class BridgeTest(unittest.TestCase):
    def setUp(self):
        self.br_name = 'obr-test'
        self.b = bridge.Bridge()
        if not self.b.add_br(self.br_name):
            self.fail('add_br: add bridge fail : ' + self.br_name)
        
    def tearDown(self):
        if not self.b.del_br(self.br_name):
            self.fail('del_br: delete bridge fail : ' + self.br_name)
            
    def test_list_br(self):
        brs = self.b.list_br()
        self.assertGreaterEqual(len(brs), 1)
        self.assertIn(self.br_name, brs)
        
    def test_exists_br(self):
        self.assertTrue(self.b.exists_br(self.br_name))
        self.assertFalse(self.b.exists_br('other-br'))
        
    def test_show_br(self):
        brs = self.b.show_br()
        self.assertIn(self.br_name, brs)
        
class PortsTest(unittest.TestCase):
    def setUp(self):
        self.br_name = 'obr-test'
        self.port_name = 'vport-test'
        self.b = bridge.Bridge()
        if not self.b.add_br(self.br_name):
            self.fail('add_br: add bridge fail : ' + self.br_name)
        if not self.b.add_port(self.br_name, self.port_name):
            self.fail('add_port: add port fail : ' + self.port_name)
            
    def tearDown(self):
        if not self.b.del_port(self.br_name, self.port_name):
            self.fail('del_port: delete port fail : ' + self.port_name)
        if not self.b.del_br(self.br_name):
            self.fail('del_br: delete bridge fail : ' + self.br_name)
            
    def test_list(self):
        ports = self.b.list_port(self.br_name)
        self.assertEquals(len(ports), 1)
        self.assertIn(self.port_name, ports)
        