# coding=utf-8

from ovs.utils import json_utils
import unittest

class TextUtilsTest(unittest.TestCase):

    def test_parse_list(self):
        json_txt = '["foo", "bar"]'
        lst = json_utils.parse_list(json_txt)
        self.assertEquals(len(lst), 2)
        
        json_txt = '[foo, bar]'
        lst = json_utils.parse_list(json_txt)
        self.assertEquals(len(lst), 2)

    def test_parse_dict(self):
        json_txt = '{"key":"value", "foo":"bar"}'
        dct = json_utils.parse_dict(json_txt)
        self.assertEquals(len(dct), 2)
        self.assertEquals(dct.get('key'), 'value')
        
        json_txt = '{key="value", foo="bar"}'
        dct = json_utils.parse_dict(json_txt)
        self.assertEquals(len(dct), 2)
        self.assertEquals(dct.get('foo'), 'bar')
        
if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()