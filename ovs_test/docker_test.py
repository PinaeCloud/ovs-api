# coding=utf-8

import unittest
from ovs import bridge, docker
from ovs import execute
from ovs.utils import ip_utils

class DockerTest(unittest.TestCase):
    
    def setUp(self):
        self.d = docker.Docker()
        self.b = bridge.Bridge()
        
    def test_docker_network(self):
        container_name = 'c1'
        br_name = 'test-br'
        br_ip = '192.168.150.1/24'
        c_ip = '192.168.150.3'
        c_mask = '24'
        
        execute.exec_cmd('docker run -d --name {0} --net=none interhui/alpine-ssh /usr/sbin/sshd -D'.format(container_name))
        
        if not self.b.exists_br(br_name):
            self.b.add_br(br_name)
            
        ip_utils.IFace().startup(br_name)
        ip_utils.Address().add_addr(br_name, br_ip)
        
        self.d.connect(container_name, br_name, '{0}/{1}'.format(c_ip, c_mask))
        result, _ = execute.exec_cmd('ping {0} -c 1 -q | grep packets'.format(c_ip))
        self.assertTrue('0% packet loss' in result.strip())
            
        self.d.disconnect(container_name, br_name)
        self.b.del_br(br_name)
        
        execute.exec_cmd('docker stop ' + container_name)
        execute.exec_cmd('docker rm ' + container_name)
        