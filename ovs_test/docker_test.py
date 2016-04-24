# coding=utf-8

import unittest
from ovs import docker

class DockerTest(unittest.TestCase):
    
    def setUp(self):
        self.d = docker.Docker()
        
    def test_connect(self):
        pass
    
    def test_disconnect(self):
        pass
    
    