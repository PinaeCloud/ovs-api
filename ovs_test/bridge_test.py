# coding=utf-8

import unittest

from ovs import bridge
from ovs import ovsdb
from ovs.utils import json_utils
from ovs.utils import tap_utils

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
        self.d = ovsdb.OVSDB()
        self.t = tap_utils.Tap()
        
        if not self.b.add_br(self.br_name):
            self.fail('add_br: add bridge fail : ' + self.br_name)
        if not self.t.add_tap(self.port_name):
            self.fail('add_tap: add tap fail : ' + self.port_name)
        if not self.b.add_port(self.br_name, self.port_name):
            self.fail('add_port: add port fail : ' + self.port_name)
            
    def tearDown(self):
        if not self.b.del_port(self.br_name, self.port_name):
            self.fail('del_port: delete port fail : ' + self.port_name)
        if not self.t.del_tap(self.port_name):
            self.fail('del_tap: delete tap fail : ' + self.port_name)
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
        in_port, out_port = 'in-port', 'out-port'
        
        self.t.add_tap(in_port)
        self.t.add_tap(out_port)
        self.b.add_port(self.br_name, in_port)
        self.b.add_port(self.br_name, out_port)
        
        mirror_name = 'test-mirror'
        if not self.b.mirror(mirror_name, self.br_name, [in_port], [out_port]):
            self.fail('mirror: mirror port fail')
        mirror_lst = self.d.list('Mirror', mirror_name)
        self.assertEquals(mirror_lst[0].get('name'), mirror_name)
        if not self.b.no_mirror(self.br_name):
            self.fail('no_mirror: no_mirror port fail')
            
        self.b.del_port(self.br_name, in_port)
        self.b.del_port(self.br_name, out_port)
        self.t.del_tap(in_port)
        self.t.del_tap(out_port)
        
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
            
    def test_qos(self):
        if not self.b.qos(self.port_name, 1200, 900):
            self.fail('qos: enable qos fail')
            
        qos_lst = self.d.list('QoS')
        self.assertEquals(qos_lst[0].get('type'), 'linux-htb')
        self.assertEquals(json_utils.parse_dict(qos_lst[0].get('other_config')).get('max-rate'), '1200000')
        
        queue_lst = self.d.list('Queue')
        self.assertEquals(json_utils.parse_dict(queue_lst[0].get('other_config')).get('min-rate'), '900000')
        
        if not self.b.no_qos(self.port_name):
            self.fail('no_qos: disable qos fail')
        qos = self.d.get('Port', self.port_name, 'Qos')
        self.assertEquals(qos, '[]')
            
    def test_ingress_rate(self):
        if not self.b.ingress_rate(self.port_name, 1000, 100):
            self.fail('ingress_rate: enable ingress_rate fail')
            
        if_lst = self.d.list('Interface', self.port_name)
        self.assertEquals(if_lst[0].get('ingress_policing_rate'), '1000')
        self.assertEquals(if_lst[0].get('ingress_policing_burst'), '100')
        
        if not self.b.no_ingress_rate(self.port_name):
            self.fail('no_ingress_rate: disable ingress_rate fail')
        if_lst = self.d.list('Interface', self.port_name)
        self.assertEquals(if_lst[0].get('ingress_policing_rate'), '0')
        self.assertEquals(if_lst[0].get('ingress_policing_burst'), '0')
        
    def test_tag(self):
        if not self.b.tag(self.port_name, 101):
            self.fail('tag: set port tag fail')
        tag = self.d.get('Port', self.port_name, 'tag')
        self.assertEquals(tag, '101')
        if not self.b.no_tag(self.port_name):
            self.fail('not_tag: clear port tag fail')
        
    def test_trunk(self):
        if not self.b.trunk(self.port_name, [101, 102]):
            self.fail('trunk: set port trunk fail')
        trunk = self.d.get('Port', self.port_name, 'trunk')
        self.assertEquals(trunk, '[101, 102]')
        if not self.b.no_trunk(self.port_name):
            self.fail('not_tag: clear port trunk fail')
            
    def test_bond(self):
        bond_name = 'test-bond'
        port1, port2 = 'port1', 'port2'
        
        self.t.add_tap(port1)
        self.t.add_tap(port2)
        
        if not self.b.bond(self.br_name, bond_name, [port1, port2], True, 'slb'):
            self.fail('bond: bond port fail')
            
        lacp = self.d.get('Port', bond_name, 'lacp')
        self.assertEquals(lacp, 'active')
        mode = self.d.get('Port', bond_name, 'bond_mode')
        self.assertEquals(mode, 'balance-slb')
        interfaces = self.d.get('Port', bond_name, 'interfaces')
        if_list = json_utils.parse_list(interfaces)
        self.assertEquals(len(if_list), 2)
        
        if not self.b.no_bond(self.br_name, bond_name):
            self.fail('not_tag: clear port trunk fail')

        self.t.del_tap(port1)
        self.t.del_tap(port2)
        
    def test_tunnel(self):
        if not self.b.tunnel(self.port_name, 'gre', '192.168.100.3', '192.168.100.6'):
            self.fail('tunnel: create tunnel fail')
            
        local_ip = self.d.get('Interface', self.port_name, 'options', 'local_ip')
        self.assertEquals(local_ip, '192.168.100.3')
        remote_ip = self.d.get('Interface', self.port_name, 'options', 'remote_ip')
        self.assertEquals(remote_ip, '192.168.100.6')
        tunnel_type = self.d.get('Interface', self.port_name, 'type')
        self.assertEquals(tunnel_type, 'gre')
        
        if not self.b.no_tunnel(self.port_name):
            self.fail('no_tunnel: clear tunnel fail')
            