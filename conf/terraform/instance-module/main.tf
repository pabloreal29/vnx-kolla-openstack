# Define required providers
terraform {
required_version = ">= 0.14.0"
  required_providers {
    openstack = {
      source  = "terraform-provider-openstack/openstack"
      version = "~> 1.53.0"
    }
  }
}

# Configure the OpenStack Provider
provider "openstack" {
  user_name   = "admin"
  tenant_name = "admin"
  password    = "xxxx"
  auth_url    = "http://10.0.0.11:5000/v3"
  region      = "RegionOne"
}

# Variable que refleja el numero de servidores actuales en el escenario
variable "server_number" {
  description = "The number to use in the server name"
  type        = string
}

# Data sources to get the existing images information
data "openstack_images_image_v2" "focal-servers-vnx" {
  name = "focal-servers-vnx"
}

data "openstack_compute_flavor_v2" "m1-large" {
  name = "m1.large"
}

# Data sources to get the existing keypairs information
data "openstack_compute_keypair_v2" "server_keypair" {
  name = "s${var.server_number}"
}

# Data sources to get the existing security group information
data "openstack_networking_secgroup_v2" "my_security_group" {
  name = "open"
}

# Data sources to get the existing network information
data "openstack_networking_network_v2" "net1" {
  name = "Net1"
}

data "openstack_networking_network_v2" "net2" {
  name = "Net2"
}

# Data sources to get the existing subnets information
data "openstack_networking_subnet_v2" "subnet1" {
  name = "subnet1"
}

data "openstack_networking_subnet_v2" "subnet2" {
  name = "subnet2"
}

# Servidores
resource "openstack_compute_instance_v2" "server_instance" {
  name        = "s${var.server_number}"
  image_name = data.openstack_images_image_v2.focal-servers-vnx.name
  flavor_name = data.openstack_compute_flavor_v2.m1-large.name
  network {
    port = openstack_networking_port_v2.port_net1.id
  }
  network {
    port = openstack_networking_port_v2.port_net2.id
  }
  key_pair = data.openstack_compute_keypair_v2.server_keypair.name
  user_data = <<-EOT
    #!/bin/bash
    systemctl start apache2
    echo "<h1>Bienvenidos al Servidor s${var.server_number}</h1>" > /var/www/html/index.html
    echo "<h2>Este servidor ha sido desplegado mediante autoescalado</h2>" >> /var/www/html/index.html
  EOT
}

# Puertos
resource "openstack_networking_port_v2" "port_net1" {
  network_id       = data.openstack_networking_network_v2.net1.id
  name             = "port${var.server_number}_net1"
  security_group_ids = [data.openstack_networking_secgroup_v2.my_security_group.id]
  fixed_ip {
    subnet_id = data.openstack_networking_subnet_v2.subnet1.id
  }
}

resource "openstack_networking_port_v2" "port_net2" {
  network_id       = data.openstack_networking_network_v2.net2.id
  name             = "port${var.server_number}_net2"
  security_group_ids = [data.openstack_networking_secgroup_v2.my_security_group.id]
  fixed_ip {
    subnet_id = data.openstack_networking_subnet_v2.subnet2.id
  }
}

# Load Balancer
resource "openstack_lb_member_v2" "lb_member" {
  pool_id        = data.terraform_remote_state.main.outputs.lb_pool_id
  address        = openstack_compute_instance_v2.server_instance.network[0].fixed_ip_v4
  protocol_port  = 80
}

data "terraform_remote_state" "main" {
  backend = "local"
  config = {
    path = "../terraform.tfstate"
  }
}


