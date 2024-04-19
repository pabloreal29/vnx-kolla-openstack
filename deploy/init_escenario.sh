#!/bin/bash

#Borrar la línea que incluye la ruta /home/giros dentro de ./filesystems/rootfs_lxc_ubuntu64-ostack-controller/config
# sudo sed -i '/lxc.mount.entry = \/home\/giros\/vnx-lab-openstack-antelope\/shared \/root\/.vnx\/scenarios\/openstack_lab-antelope\/vms\/controller\/mnt\/rootfs\/\/root\/shared none bind 0 0/d' ./filesystems/rootfs_lxc_ubuntu64-ostack-controller/config

# sudo vnx -f openstack_lab.xml -v --create
# sudo vnx -f openstack_lab.xml -x start-all,load-img

#Habilitar NAT para tener conectividad con el exterior
source deploy/habilitar-nat.sh

#Crear usuario
openstack --os-cloud kolla-admin user create myuser --project admin --password xxxx
openstack --os-cloud kolla-admin role add admin --user myuser --project admin 
source deploy/myuser-openrc.sh

#Crear parejas de claves
rm -rf ./tmp/keys
mkdir -p ./tmp/keys
openstack keypair create admin > ./tmp/keys/admin
openstack keypair create bbdd > ./tmp/keys/bbdd
openstack keypair create s1 > ./tmp/keys/s1
openstack keypair create s2 > ./tmp/keys/s2
openstack keypair create s3 > ./tmp/keys/s3

#Proteger las claves privadas para que solo las pueda utilizar el owner
chmod 700 ./tmp/keys/admin
chmod 700 ./tmp/keys/bbdd
chmod 700 ./tmp/keys/s1
chmod 700 ./tmp/keys/s2
chmod 700 ./tmp/keys/s3

#Importar imagenes de las VMs
openstack image create "focal-servers-vnx" --file /home/pabloreal/openstack-images/servers_image.qcow2 --disk-format qcow2 --container-format bare --public --progress
openstack image create "focal-bbdd-vnx" --file /home/pabloreal/openstack-images/bbdd_image.qcow2 --disk-format qcow2 --container-format bare --public --progress
openstack image create "focal-admin-vnx" --file /home/pabloreal/openstack-images/admin_image.qcow2 --disk-format qcow2 --container-format bare --public --progress

#Crear el flavor de la bbdd (con el m1.smaller no puede ejecutar Mongo, necesita mas capacidad)
openstack flavor create m1.large --vcpus 1 --ram 512 --disk 5

#Crear el stack con todos los elementos del escenario
openstack stack create -t deploy/escenarioTF.yml stackTF

# # Borrar el stack
# openstack stack delete -y stackTF

#Esperar a que se cree el router del escenario antes de asignarle el firewall 
sleep 120

#Configuración del firewall
router_port=$(openstack port list --router firewall_router --fixed-ip ip-address=10.1.1.1 -c ID -f value)
openstack firewall group rule create --protocol tcp --destination-ip-address 10.1.1.57 --destination-port 2022 --action allow --name ssh_admin 
openstack firewall group rule create --protocol tcp --destination-ip-address 10.1.1.23 --destination-port 80 --action allow --name www_lb 
openstack firewall group rule create --protocol any --source-ip-address 10.1.1.0/24 --action allow --name server_connection 
openstack firewall group policy create --firewall-rule ssh_admin --firewall-rule www_lb grupo1_policy_ingress 
openstack firewall group policy create --firewall-rule server_connection grupo1_policy_egress
openstack firewall group create --ingress-firewall-policy grupo1_policy_ingress --egress-firewall-policy  grupo1_policy_egress --port $router_port --name grupo1_firewall_group

# # #Añadir servidores extra con autoescalado al escenario
# # openstack stack create -t /home/p.realb/Desktop/CNVR/TF/autoScalingGroup.yml stackExtra