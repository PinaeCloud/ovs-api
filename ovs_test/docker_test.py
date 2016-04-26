# coding=utf-8

import unittest
from ovs import bridge, docker
from ovs.utils import execute

class DockerTest(unittest.TestCase):
    
    def setUp(self):
        self.d = docker.Docker()
        self.b = bridge.Bridge()
        
    def test_docker_network(self):
        container_name = 'c1'
        br_name, br_ip = 'test-br', '192.168.150.1/24'
        c_ip, c_mask = '192.168.150.3', '24'
        
        c_pid, error = execute.exec_cmd('docker inspect --format={{.State.Pid}} ' + container_name)
        if c_pid.strip() and not error:
            self.__delete_container(container_name)
            
        execute.exec_cmd('docker run -d --name {0} --net=none interhui/alpine-ssh /usr/sbin/sshd -D'.format(container_name))
        
        self.d.add_network(br_name, br_ip)
        
        self.d.connect(container_name, br_name, '{0}/{1}'.format(c_ip, c_mask))
        result, _ = execute.exec_cmd('ping {0} -c 1 -q | grep packets'.format(c_ip))
        self.assertTrue('0% packet loss' in result.strip())
            
        self.d.disconnect(container_name, br_name)
        self.d.del_network(br_name)
        
        self.__delete_container(container_name)
        
    def __delete_container(self, container_name):
        execute.exec_cmd('docker stop ' + container_name)
        execute.exec_cmd('docker rm ' + container_name)
        