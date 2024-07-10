resource "openstack_networking_network_v2" "net1" {
  name = "Net1"
}

resource "openstack_networking_subnet_v2" "subnet1" {
  name            = "subnet1"
  network_id      = openstack_networking_network_v2.net1.id
  cidr            = "10.1.1.0/24"
  ip_version      = 4
  gateway_ip      = "10.1.1.1"
  dns_nameservers = ["8.8.8.8"]
  allocation_pool {
    start = "10.1.1.2"
    end   = "10.1.1.100"
  }
}

resource "openstack_networking_router_v2" "r0" {
  name                = "r0"
  external_network_id = data.openstack_networking_network_v2.extnet.id
}

resource "openstack_networking_router_interface_v2" "r0_interface" {
  router_id = openstack_networking_router_v2.r0.id
  subnet_id = openstack_networking_subnet_v2.subnet1.id
}

resource "openstack_networking_secgroup_v2" "open" {
  name = "open"
}

resource "openstack_networking_secgroup_rule_v2" "permit_all_ingress" {
  direction         = "ingress"
  ethertype         = "IPv4"
  security_group_id = openstack_networking_secgroup_v2.open.id
  remote_ip_prefix  = "0.0.0.0/0"
}

resource "openstack_compute_flavor_v2" "m1_large" {
  name  = "m1.large"
  vcpus = 1
  ram   = 512
  disk  = 5
}
