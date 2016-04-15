# coding=utf-8

import unittest
from ovs import bridge
from ovs import db

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
        self.d = db.OVSDB()
            
    def tearDown(self):
        if not self.b.del_port(self.br_name, self.port_name):
            self.fail('del_port: delete port fail : ' + self.port_name)
        if not self.b.del_br(self.br_name):
            self.fail('del_br: delete bridge fail : ' + self.br_name)
            
    def test_list_port(self):
        ports = self.b.list_port(self.br_name)
        self.assertEquals(len(ports), 1)
        self.assertIn(self.port_name, ports)
        
    def test_list_port_to_br(self):
        brs = self.b.list_port_to_br(self.port_name)
        self.assertEquals(len(brs), 1)
        self.assertIn(self.br_name, brs)
        
    def test_mirror(self):
        self.b.add_port(self.br_name, 'in-port')
        self.b.add_port(self.br_name, 'out-port')
        
        mirror_name = 'test-mirror'
        if not self.b.mirror(mirror_name, self.br_name, ['in-port'], ['out-port']):
            self.fail('mirror: mirror port fail')
        mirror_lst = self.d.list('Mirror', mirror_name)
        self.assertEquals(mirror_lst[0].get('name'), mirror_name)
        if not self.b.no_mirror(self.br_name):
            self.fail('no_mirror: no_mirror port fail')
            
        self.b.del_port(self.br_name, 'in-port')
        self.b.del_port(self.br_name, 'out-port')
        
    def test_netflow(self):
        if not self.b.netflow(self.br_name, '127.0.0.1', '5566', {'active-timeout':'30'}):
            self.fail('netflow: enable netflow fail')
        nf_lst = self.d.list('Netflow')
        self.assertEquals(nf_lst[0].get('targets'), '["127.0.0.1:5566"]')
        if not self.b.no_netflow(self.br_name):
            self.fail('no_netflow: disable netflow fail')

    def test_sflow(self):
        if not self.b.sflow(self.br_name, 'eth1', '127.0.0.1', '6343', {'header':'128', 'sampling':'64', 
                                                                        'polling':'10'}):
            self.fail('sflow: enable sflow fail')
        sf_lst = self.d.list('sflow')
        self.assertEquals(sf_lst[0].get('targets'), '["127.0.0.1:6343"]')
        self.assertEquals(sf_lst[0].get('agent'), '"eth1"')
        if not self.b.no_sflow(self.br_name):
            self.fail('no_sflow: disable sflow fail')  
            
    def test_ipfix(self):
        if not self.b.ipfix(self.br_name, '127.0.0.1', '4739', {'obs_domain_id':'123', 'obs_point_id':'456', 
                                                                'cache_active_timeout':'60', 'cache_max_flows':'13'}):
            self.fail('ipfix: enable ipfix fail')
        ipfix_lst = self.d.list('IPFIX')
        self.assertEquals(ipfix_lst[0].get('targets'), '["127.0.0.1:4739"]')
        if not self.b.no_ipfix(self.br_name):
            self.fail('no_ipfix: disable ipfix fail')
            