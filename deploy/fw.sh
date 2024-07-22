#!/bin/bash
# Ejecucion: source deploy/fw.sh -X, donde X es el parámetro a introducir.
source conf/admin-openrc.sh

if [ "$1" == "-s" ]; then
    subnet1_id=$(openstack subnet list --network Net1 -c ID -f value)
    subnet1_cidr=$(openstack subnet show subnet1 -c cidr -f value)
    router_port=$(openstack port list --router firewall_router --fixed-ip subnet=$subnet1_id -c ID -f value)
    ip_port_admin1=$(openstack port show port_admin1 -c fixed_ips -f json | jq -r '.fixed_ips[0].ip_address')
    lb_ip=$(openstack loadbalancer list --name load_balancer -c vip_address -f value)

    openstack firewall group rule create --protocol tcp --destination-ip-address $ip_port_admin1 --destination-port 2022 --action allow --name ssh_admin 
    openstack firewall group rule create --protocol tcp --destination-ip-address $lb_ip --destination-port 80 --action allow --name www_lb 
    openstack firewall group rule create --protocol any --source-ip-address $subnet1_cidr --action allow --name server_connection 
    openstack firewall group policy create --firewall-rule ssh_admin --firewall-rule www_lb firewall_ingress_policy 
    openstack firewall group policy create --firewall-rule server_connection firewall_egress_policy
    openstack firewall group create --ingress-firewall-policy firewall_ingress_policy --egress-firewall-policy  firewall_egress_policy --port $router_port --name firewall_group
    
    echo "Se ha configurado el firewall"

elif [ "$1" == "-n" ]; then
    openstack firewall group set --no-ingress-firewall-policy firewall_group
    openstack firewall group set --no-egress-firewall-policy firewall_group   
    echo "Se ha deshabilitado el firewall"

else 
    echo "Se ha introducido un parámetro no válido. Solamente se permiten las siguientes opciones:"
    echo "- Parámetro -s: Permitir acceso por SSH al puerto 2022 del administrador"
    echo "- Parámetro -n: Denegar acceso por SSH al puerto 2022 del administrador"
fi
