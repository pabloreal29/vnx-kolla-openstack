Testing scenarios 

** Self service networks:

- Create external network (ExtNet)

sudo vnx -f openstack_lab.xml -v -x create-extnet

- Load VM images:

sudo vnx -f openstack_lab.xml -v -x load-img

- Create demo scenario:

sudo vnx -f openstack_lab.xml -v -x create-demo-scenario    # create net0 + router r0 + vm1
sudo vnx -f openstack_lab.xml -v -x create-demo-vm2         # add vm2 to net0
sudo vnx -f openstack_lab.xml -v -x create-demo-vm3         # add vm3 to net0

** Provider networks

- Create two virtual networks connected to VLANs 1000 and 1001 and start virtual machines vmA1 and vmB1 connected to them: 

sudo vnx -f openstack_lab.xml -v -x create-vlan-demo-scenario

- Start external VNX scenario with two networks connected to VLANs 1000 and 1001, two virtual machines (vmA2 and vmB2) connected to them and a router that routes traffic between them:

sudo vnx -f openstack_lab-vms-vlan.xml --create

- Test connectivity among all vms. Traffic goes VLAN tagged through eth3 interfaces of compute1 and compute2


** How to see the internal network topology of network and compute nodes

- Access network or computeX nodes by SSH:

ssh root@network    # or compute1/compute2

- Enter docker kolla_toolbox as root:

docker exec -u 0 -ti kolla_toolbox bash

- Show bridges connections with:

ovs-vsctl show

** How to see routers in network node 

- Access network by SSH:

ssh root@network 

- See netnamespaces:

ip netns

- Enter into one of the qrouterXXX namespaces. For example:

ip netns exec qdhcp-063eb6a4-28f6-41ce-b060-4f76e2b4d75f bash

- See interfaces with 'ifconfig' or 'ip addr'

- To use ping to test connectivity or tcpdump to capture traffic yo need to install them:

apt install tcpdump iputils-ping

