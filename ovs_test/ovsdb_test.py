# coding=utf-8

import unittest

from ovs import bridge
from ovs import ovsdb
from ovs.utils import tap_utils

class OVSDBTest(unittest.TestCase):
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
            
    def test_list_br(self):
        brs = self.d.list('br', self.br_name)
        self.assertEquals(brs[0].get('name'), self.br_name)
        
    def test_list_port(self):
        ports = self.d.list('port', self.port_name)
        self.assertEquals(ports[0].get('name'), self.port_name)
        
    def test_set(self):
        if self.d.set('port', self.port_name, {'tag' : 2}):
            tag = self.d.get('port', self.port_name, 'tag')
            self.assertEquals(tag, '2')
        else:
            self.fail('set: set port tag fail')
            
        if self.d.set('port', self.port_name, {'other_config': {'comment' : 'Test Port'}}):
            comment = self.d.get('port', self.port_name, 'other_config', 'comment')
            self.assertEqual(comment, 'Test Port')
        else:
            self.fail('set: set port tag fail')
            
    def test_get(self):
        result = self.d.get('port', self.port_name, 'name')
        if result:
            self.assertEquals(result, self.port_name)
        else:
            self.fail('get: get port name fail')
            
    def test_clear(self):
        if self.d.set('port', self.port_name, {'tag' : 2}):
            tag = self.d.get('port', self.port_name, 'tag')
            self.assertEquals(tag, '2')
            if self.d.clear('port', self.port_name, 'tag'):
                tag = self.d.get('port', self.port_name, 'tag')
                self.assertEquals(tag, '[]')
            else:
                self.fail('clear: clear port tag fail')
        else:
            self.fail('set: set port tag fail')
            
    def test_add(self):
        if self.d.add('port', self.port_name, 'trunks', '300'):
            result = self.d.get('port', self.port_name, 'trunks')
            if result:
                self.assertEquals(result, '[300]')
            else:
                self.fail('get: get port comment fail')
        else:
            self.fail('add: add port comment')
            
    def test_remove(self):
        if self.d.add('port', self.port_name, 'trunks', '300'):
            result = self.d.get('port', self.port_name, 'trunks')
            if result and result == '[300]':
                if self.d.remove('port', self.port_name, 'trunks', '300'):
                    result = self.d.get('port', self.port_name, 'trunks')
                    self.assertEquals(result, '[]')
                else:
                    self.fail('remove: remove port comment fail')
            else:
                self.fail('get: get port comment fail')
        else:
            self.fail('add: add port comment fail')
            
                    
    def test_history(self):
        history_list = self.d.history()
        self.assertGreater(len(history_list), 0)
        