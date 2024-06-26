#!/bin/bash

#Borrar la línea que incluye la ruta /home/giros dentro de ./filesystems/rootfs_lxc_ubuntu64-ostack-controller/config
# sudo sed -i '/lxc.mount.entry = \/home\/giros\/vnx-lab-openstack-antelope\/shared \/root\/.vnx\/scenarios\/openstack_lab-antelope\/vms\/controller\/mnt\/rootfs\/\/root\/shared none bind 0 0/d' ./filesystems/rootfs_lxc_ubuntu64-ostack-controller/config

# Almacenar las claves del nodo admin
rm -rf $HOME/.config/openstack/
mkdir $HOME/.config/openstack/
scp root@admin:/etc/kolla/clouds.yaml $HOME/.config/openstack/
openstack --os-cloud kolla-admin service list

#Habilitar NAT para tener conectividad con el exterior
source deploy/habilitar-nat.sh

#Cargar imagenes y crear red externa
OSTACKLAB=openstack_kolla_ansible_2024_1.xml
sudo vnx -f $OSTACKLAB -x create-extnet
sudo vnx -f $OSTACKLAB -x load-trove
sudo vnx -f $OSTACKLAB -x load-octavia
sudo vnx -f $OSTACKLAB -x load-img

#Crear mi usuario
openstack --os-cloud kolla-admin user create myuser --project admin --password xxxx
openstack --os-cloud kolla-admin role add admin --user myuser --project admin 
source deploy/myuser-openrc.sh

#Crear parejas de claves
rm -rf ./tmp/keys
mkdir -p ./tmp/keys
openstack keypair create administrador > ./tmp/keys/administrador
openstack keypair create bbdd > ./tmp/keys/bbdd
openstack keypair create s1 > ./tmp/keys/s1
openstack keypair create s2 > ./tmp/keys/s2
openstack keypair create s3 > ./tmp/keys/s3

#Proteger las claves privadas para que solo las pueda utilizar el owner
chmod 700 ./tmp/keys/administrador
chmod 700 ./tmp/keys/bbdd
chmod 700 ./tmp/keys/s1
chmod 700 ./tmp/keys/s2
chmod 700 ./tmp/keys/s3

#Importar imagenes de las VMs
openstack image create focal-servers-vnx --file /home/pabloreal/openstack-images/asg_servers_image.qcow2 --disk-format qcow2 --container-format bare --public --progress
openstack image create focal-bbdd-vnx --file /home/pabloreal/openstack-images/bbdd_image.qcow2 --disk-format qcow2 --container-format bare --public --progress
openstack image create focal-administrador-vnx --file /home/pabloreal/openstack-images/administrador_image.qcow2 --disk-format qcow2 --container-format bare --public --progress

#Crear el flavor de la bbdd (con el m1.smaller no puede ejecutar Mongo, necesita mas capacidad)
#Nota: he reducido las vcpus y la ram respecto al trabajo de cnvr
openstack flavor create m1.large --vcpus 1 --ram 512 --disk 5

#Crear un contenedor con una copia de la bbdd de estudiantes
openstack container create students-container
openstack object create students-container --name studentsBBDD.json deploy/students.json

# #Crear el stack con todos los elementos del escenario
# openstack stack create -t deploy/escenarioTF_ASG.yaml my_stack

# #Esperar a que se cree el router del escenario antes de asignarle el firewall 
# sleep 60

# #Configuracion del firewall
# subnet1_id=$(openstack subnet list --network Net1 -c ID -f value)
# subnet1_cidr=$(openstack subnet show subnet1 -c cidr -f value)
# router_port=$(openstack port list --router firewall_router --fixed-ip subnet=$subnet1_id -c ID -f value)
# ip_port_admin1=$(openstack port show port_admin1 -c fixed_ips -f json | jq -r '.fixed_ips[0].ip_address')
# lb_ip=$(openstack loadbalancer list --name load_balancer -c vip_address -f value)

# openstack firewall group rule create --protocol tcp --destination-ip-address $ip_port_admin1 --destination-port 2022 --action allow --name ssh_admin 
# openstack firewall group rule create --protocol tcp --destination-ip-address $lb_ip --destination-port 80 --action allow --name www_lb 
# openstack firewall group rule create --protocol any --source-ip-address $subnet1_cidr --action allow --name server_connection 
# openstack firewall group policy create --firewall-rule ssh_admin --firewall-rule www_lb my_policy_ingress 
# openstack firewall group policy create --firewall-rule server_connection my_policy_egress
# openstack firewall group create --ingress-firewall-policy my_policy_ingress --egress-firewall-policy  my_policy_egress --port $router_port --name my_fw_group

# # Borrar el stack
# openstack stack delete -y my_stack

# # Borrar el contenedor y los objetos que contiene
# openstack container delete -r students-container