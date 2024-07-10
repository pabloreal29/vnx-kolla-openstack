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

# Data source to get the existing network information
data "openstack_networking_network_v2" "extnet" {
  name = "ExtNet"
}
