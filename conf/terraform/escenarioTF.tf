
# Redes y Subredes
resource "openstack_networking_network_v2" "net1" {
  name = "Net1"
}

resource "openstack_networking_network_v2" "net2" {
  name = "Net2"
}

resource "openstack_networking_subnet_v2" "subnet1" {
  name            = "subnet1"
  network_id      = openstack_networking_network_v2.net1.id
  cidr            = "10.1.1.0/24"
  ip_version      = 4
  dns_nameservers = ["8.8.8.8"]
  gateway_ip      = "10.1.1.1"
  allocation_pool {
    start = "10.1.1.2"
    end   = "10.1.1.100"
  }
}

resource "openstack_networking_subnet_v2" "subnet2" {
  name            = "subnet2"
  network_id      = openstack_networking_network_v2.net2.id
  cidr            = "10.1.2.0/24"
  ip_version      = 4
  allocation_pool {
    start = "10.1.2.2"
    end   = "10.1.2.100"
  }
}

# Router Firewall
resource "openstack_networking_router_v2" "firewall_router" {
  name = "firewall_router"
  external_network_id = data.openstack_networking_network_v2.extnet.id
}

resource "openstack_networking_router_interface_v2" "fw_router_inface" {
  router_id = openstack_networking_router_v2.firewall_router.id
  subnet_id = openstack_networking_subnet_v2.subnet1.id
}

# Grupo de Seguridad
resource "openstack_networking_secgroup_v2" "my_security_group" {
  name        = "open"
  description = "Grupo de Seguridad para permitir todo el trafico"
  delete_default_rules = true
}

resource "openstack_networking_secgroup_rule_v2" "security_group_rule_ingress" {
  direction         = "ingress"
  ethertype         = "IPv4"
  protocol          = "tcp"
  remote_ip_prefix  = "0.0.0.0/0"
  security_group_id = openstack_networking_secgroup_v2.my_security_group.id
}

resource "openstack_networking_secgroup_rule_v2" "security_group_rule_engress" {
  direction         = "egress"
  ethertype         = "IPv4"
  protocol          = "tcp"
  remote_ip_prefix  = "0.0.0.0/0"
  security_group_id = openstack_networking_secgroup_v2.my_security_group.id
}

# Puertos Net1
resource "openstack_networking_port_v2" "port1_net1" {
  network_id       = openstack_networking_network_v2.net1.id
  name             = "port1_net1"
  security_group_ids = [openstack_networking_secgroup_v2.my_security_group.id]
  fixed_ip {
    subnet_id = openstack_networking_subnet_v2.subnet1.id
  }
}

resource "openstack_networking_port_v2" "port2_net1" {
  network_id       = openstack_networking_network_v2.net1.id
  name             = "port2_net1"
  security_group_ids = [openstack_networking_secgroup_v2.my_security_group.id]
  fixed_ip {
    subnet_id = openstack_networking_subnet_v2.subnet1.id
  }
}

resource "openstack_networking_port_v2" "port3_net1" {
  network_id       = openstack_networking_network_v2.net1.id
  name             = "port3_net1"
  security_group_ids = [openstack_networking_secgroup_v2.my_security_group.id]
  fixed_ip {
    subnet_id = openstack_networking_subnet_v2.subnet1.id
  }
}

# Puertos Net2
resource "openstack_networking_port_v2" "port1_net2" {
  network_id       = openstack_networking_network_v2.net2.id
  name             = "port1_net2"
  security_group_ids = [openstack_networking_secgroup_v2.my_security_group.id]
  fixed_ip {
    subnet_id = openstack_networking_subnet_v2.subnet2.id
  }
}

resource "openstack_networking_port_v2" "port2_net2" {
  network_id       = openstack_networking_network_v2.net2.id
  name             = "port2_net2"
  security_group_ids = [openstack_networking_secgroup_v2.my_security_group.id]
  fixed_ip {
    subnet_id = openstack_networking_subnet_v2.subnet2.id
  }
}

resource "openstack_networking_port_v2" "port3_net2" {
  network_id       = openstack_networking_network_v2.net2.id
  name             = "port3_net2"
  security_group_ids = [openstack_networking_secgroup_v2.my_security_group.id]
  fixed_ip {
    subnet_id = openstack_networking_subnet_v2.subnet2.id
  }
}

resource "openstack_networking_port_v2" "portBBDD_net2" {
  network_id       = openstack_networking_network_v2.net2.id
  name             = "portBBDD_net2"
  security_group_ids = [openstack_networking_secgroup_v2.my_security_group.id]
  fixed_ip {
    subnet_id = openstack_networking_subnet_v2.subnet2.id
    ip_address = "10.1.2.83"
  }
}

# Puerto Acceso Admin
resource "openstack_networking_port_v2" "port_admin1" {
  network_id       = openstack_networking_network_v2.net1.id
  name             = "port_admin1"
  security_group_ids = [openstack_networking_secgroup_v2.my_security_group.id]
  fixed_ip {
    subnet_id = openstack_networking_subnet_v2.subnet1.id
  }
}

resource "openstack_networking_port_v2" "port_admin2" {
  network_id       = openstack_networking_network_v2.net2.id
  name             = "port_admin2"
  security_group_ids = [openstack_networking_secgroup_v2.my_security_group.id]
  fixed_ip {
    subnet_id = openstack_networking_subnet_v2.subnet2.id
  }
}

# IPs Flotantes
resource "openstack_networking_floatingip_v2" "floating_ipLB" {
  pool = data.openstack_networking_network_v2.extnet.name
  port_id = openstack_lb_loadbalancer_v2.load_balancer.vip_port_id
}

resource "openstack_networking_floatingip_v2" "floating_ipAdmin" {
  pool = data.openstack_networking_network_v2.extnet.name
  port_id = openstack_networking_port_v2.port_admin1.id
}

# Load Balancer
resource "openstack_lb_loadbalancer_v2" "load_balancer" {
  vip_subnet_id = openstack_networking_subnet_v2.subnet1.id
  name = "load_balancer"
}

resource "openstack_lb_listener_v2" "lb_listener" {
  name           = "lb_listener"
  protocol       = "HTTP"
  protocol_port  = 80
  loadbalancer_id = openstack_lb_loadbalancer_v2.load_balancer.id
}

resource "openstack_lb_pool_v2" "lb_pool" {
  name          = "lb_pool"
  lb_method     = "ROUND_ROBIN"
  protocol      = "HTTP"
  listener_id   = openstack_lb_listener_v2.lb_listener.id
}

resource "openstack_lb_members_v2" "lb_members" {
  pool_id = openstack_lb_pool_v2.lb_pool.id

  member {
    address       = openstack_compute_instance_v2.s1.network[0].fixed_ip_v4
    protocol_port = 80
  }
  member {
    address       = openstack_compute_instance_v2.s2.network[0].fixed_ip_v4
    protocol_port = 80
  }
  member {
    address       = openstack_compute_instance_v2.s3.network[0].fixed_ip_v4
    protocol_port = 80
  }
}

# Servidores
resource "openstack_compute_instance_v2" "s1" {
  name       = "s1"
  image_name = data.openstack_images_image_v2.focal-servers-vnx.name
  flavor_name = data.openstack_compute_flavor_v2.m1-large.name
  network {
    port = openstack_networking_port_v2.port1_net1.id
  }
  network {
    port = openstack_networking_port_v2.port1_net2.id
  }
  key_pair = data.openstack_compute_keypair_v2.s1.name
  user_data = <<-EOT
    #!/bin/bash
    systemctl start apache2
    echo "<h1>Bienvenidos al Servidor 1</h1>" > /var/www/html/index.html
  EOT
}

resource "openstack_compute_instance_v2" "s2" {
  name       = "s2"
  image_name = data.openstack_images_image_v2.focal-servers-vnx.name
  flavor_name = data.openstack_compute_flavor_v2.m1-large.name
  network {
    port = openstack_networking_port_v2.port2_net1.id
  }
  network {
    port = openstack_networking_port_v2.port2_net2.id
  }
  key_pair = data.openstack_compute_keypair_v2.s2.name
  user_data = <<-EOT
    #!/bin/bash
    systemctl start apache2
    echo "<h1>Bienvenidos al Servidor 2</h1>" > /var/www/html/index.html
  EOT
}

resource "openstack_compute_instance_v2" "s3" {
  name       = "s3"
  image_name = data.openstack_images_image_v2.focal-servers-vnx.name
  flavor_name = data.openstack_compute_flavor_v2.m1-large.name
  network {
    port = openstack_networking_port_v2.port3_net1.id
  }
  network {
    port = openstack_networking_port_v2.port3_net2.id
  }
  key_pair = data.openstack_compute_keypair_v2.s3.name
  user_data = <<-EOT
    #!/bin/bash
    systemctl start apache2
    echo "<h1>Bienvenidos al Servidor 3</h1>" > /var/www/html/index.html
  EOT
}

# Administrador
resource "openstack_compute_instance_v2" "administrador" {
  name       = "administrador"
  image_name = data.openstack_images_image_v2.focal-administrador-vnx.name
  flavor_name = data.openstack_compute_flavor_v2.m1-smaller.name
  network {
    port = openstack_networking_port_v2.port_admin1.id
  }
  network {
    port = openstack_networking_port_v2.port_admin2.id
  }
  key_pair = data.openstack_compute_keypair_v2.administrador.name
  user_data = <<-EOT
    #!/bin/bash
    systemctl start apache2
    echo "<h1>Bienvenidos al Administrador</h1>" > /var/www/html/index.html
  EOT
}

# BBDD
resource "openstack_compute_instance_v2" "bbdd" {
  name       = "bbdd"
  image_name = data.openstack_images_image_v2.focal-bbdd-vnx.name
  flavor_name = data.openstack_compute_flavor_v2.m1-large.name
  network {
    port = openstack_networking_port_v2.portBBDD_net2.id
  }
  key_pair = data.openstack_compute_keypair_v2.bbdd.name
  user_data = <<-EOT
    #!/bin/bash
    systemctl start mongod
  EOT
}

# Firewall
resource "openstack_fw_rule_v2" "ssh_admin_rule" {
  name                   = "ssh_admin"
  protocol               = "tcp"
  ip_version             = 4
  destination_ip_address = openstack_compute_instance_v2.administrador.network[0].fixed_ip_v4
  destination_port       = "2022"
  action                 = "allow"
  enabled                = "true"
}

resource "openstack_fw_rule_v2" "www_lb_rule" {
  name                   = "www_lb"
  protocol               = "tcp"
  ip_version             = 4
  destination_ip_address = openstack_lb_loadbalancer_v2.load_balancer.vip_address
  destination_port       = "80"
  action                 = "allow"
  enabled                = "true"
}

resource "openstack_fw_rule_v2" "server_connection_rule" {
  name                 = "server_connection"
  protocol             = "any"
  ip_version           = 4
  source_ip_address    = openstack_networking_subnet_v2.subnet1.cidr
  action               = "allow"
  enabled              = "true"
}

resource "openstack_fw_policy_v2" "policy_ingress" {
  name = "firewall_ingress_policy"

  rules = [
    openstack_fw_rule_v2.ssh_admin_rule.id,
    openstack_fw_rule_v2.www_lb_rule.id
  ]
}

resource "openstack_fw_policy_v2" "policy_engress" {
  name = "firewall_egress_policy"

  rules = [
    openstack_fw_rule_v2.server_connection_rule.id,
  ]
}

resource "openstack_fw_group_v2" "group_1" {
  name      = "firewall_group"
  ingress_firewall_policy_id = openstack_fw_policy_v2.policy_ingress.id
  egress_firewall_policy_id = openstack_fw_policy_v2.policy_engress.id
}

