#!/bin/bash

source conf/admin-openrc.sh
openstack network create Net1
openstack subnet create --network Net1 --gateway 10.1.1.1 --dns-nameserver 8.8.8.8 --subnet-range 10.1.1.0/24 --allocation-pool start=10.1.1.2,end=10.1.1.100 subnet1
openstack router create r0
openstack router set r0 --external-gateway ExtNet
openstack router add subnet r0 subnet1
openstack security group create open
openstack security group rule create --proto any --dst-port 1:65535 --ingress open
openstack flavor create --vcpus 1 --ram 512 --disk 3 m1.prueba
