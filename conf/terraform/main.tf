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

# Data source to get the existing external network information
data "openstack_networking_network_v2" "extnet" {
  name = "ExtNet"
}

# Data sources to get the existing images information
data "openstack_images_image_v2" "focal-servers-vnx" {
  name = "focal-servers-vnx"
}

data "openstack_images_image_v2" "focal-administrador-vnx" {
  name = "focal-administrador-vnx"
}

data "openstack_images_image_v2" "focal-bbdd-vnx" {
  name = "focal-bbdd-vnx"
}

# Data sources to get the existing flavours information
data "openstack_compute_flavor_v2" "m1-smaller" {
  name = "m1.smaller"
}

data "openstack_compute_flavor_v2" "m1-large" {
  name = "m1.large"
}

# Data sources to get the existing keypairs information
data "openstack_compute_keypair_v2" "s1" {
  name = "s1"
}

data "openstack_compute_keypair_v2" "s2" {
  name = "s2"
}

data "openstack_compute_keypair_v2" "s3" {
  name = "s3"
}

data "openstack_compute_keypair_v2" "administrador" {
  name = "administrador"
}

data "openstack_compute_keypair_v2" "bbdd" {
  name = "bbdd"
}



