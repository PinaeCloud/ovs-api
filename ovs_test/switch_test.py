# coding=utf-8

import unittest
from ovs import switch

class SwitchLogTest(unittest.TestCase):
    
    def setUp(self):
        self.s = switch.SwitchLog()
    
    def test_list_log(self):
        result = self.s.list_log()
        self.assertGreater(len(result), 0)
        module = result.get('bfd')
        self.assertEquals(module.get('console'), 'OFF')
        self.assertEquals(module.get('syslog'), 'ERR')
        self.assertEquals(module.get('file'), 'INFO')
        
    def test_set_log(self):
        if not self.s.set_log('bfd', 'syslog', 'INFO'):
            self.fail('set_log : set switch log fail')
            
        result = self.s.list_log()
        module = result.get('bfd')
        self.assertEquals(module.get('syslog'), 'INFO')
        
        self.s.set_log('bfd', 'syslog', 'ERR')

if __name__ =='__main__':  
    unittest.main()          