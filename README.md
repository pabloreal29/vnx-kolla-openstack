# VNX Kolla-OpenStack

OpenStack scenario deployed with Kolla-ansible. The OpenStack platform is provisioned on a VNX-based virtual scenario - inspired by the [VNX Openstack Stein Lab](https://web.dit.upm.es/vnxwiki/index.php/Vnx-labo-openstack-4nodes-classic-ovs-stein).

> **IMPORTANT NOTE:**
>
> This scenario installs OpenStack **Antelope** release.
>

## Setup

### Pre-requisites

- (Tested with) Ubuntu 22.04 LTS (aka "jammy")
- Python 3 (tested with Python 3.10.12)
- VNX ([Installation guide for Ubuntu](https://web.dit.upm.es/vnxwiki/index.php/Vnx-install-ubuntu3))

### Quick recipe (for the impatient)

1. OpenStack cluster startup and requirements installation:
```bash
git clone --branch antelope git@github.com:giros-dit/vnx-kolla-openstack.git
cd vnx-kolla-openstack/
ssh-keygen -t rsa -f conf/ssh/id_rsa -q -N ""
sudo chown 644 conf/ssh/id_rsa
# Choose the scenario version to use
OSTACKLAB=openstack_kolla_ansible_2024_1.xml      # Multiple net interfaces: TunnNet (eth2), VlanNet (eth3), ExtNet (eth4)
OSTACKLAB=openstack_kolla_ansible-vlan.xml  # VLAN based net interfaces: TunnNet (eth5.20), VlanNet (eth5.30), ExtNet (eth5.10)
sudo vnx -f $OSTACKLAB -v --create
sudo vnx -f $OSTACKLAB -x config-admin
```
2. OpenStack cluster configuration (execution of Kolla playbooks):
```bash
ssh root@admin
./deploy-ostack    # Tarda 15 minutos. Use "./deploy-ostack 3n" for implementing network functionallity in compute1 node (no network node)
```
Note: deploy-ostack scripts executes the following commands:
```bash
source /root/kolla/bin/activate
kolla-ansible -i /root/kolla/share/kolla-ansible/ansible/inventory/multinode --configdir /etc/kolla/ bootstrap-servers
kolla-ansible -i /root/kolla/share/kolla-ansible/ansible/inventory/multinode --configdir /etc/kolla/ prechecks
kolla-ansible -i /root/kolla/share/kolla-ansible/ansible/inventory/multinode --configdir /etc/kolla/ deploy
kolla-ansible post-deploy
```
3. The keys to access the cluster are located in /etc/kolla directory of admin node:
 - admin-openrc.sh: shellscript that populate environment variables with credentials and other data
 - clouds.yaml: this file can be copied to /etc/openstack or $HOME/.config/openstack directories to allow the execution of openstack client commands using "--os-cloud=kolla-admin" option. For example:
```bash
rm -rf $HOME/.config/openstack/
mkdir $HOME/.config/openstack/
scp root@admin:/etc/kolla/clouds.yaml $HOME/.config/openstack/
openstack --os-cloud kolla-admin service list
```
4. You can access the cluster by:
- Graphical user interface, by connecting to http://10.0.0.11 from a web browser
- Command line, by using openstack commands. For that, you have to install the OpenStack client:
```bash
pip install python-openstackclient -c https://releases.openstack.org/constraints/upper/2023.1
```
5. Deploy Self-service network based testing scenarios:
 - Load vm images with:
```bash
sudo vnx -f $OSTACKLAB -x load-img
```
 - Create external network with:
```bash
sudo vnx -f $OSTACKLAB -x create-extnet
```
- Config NAT to provide Internet access to virtual machines (change eno1 by the name of the network interface that provides Internet connectivity to the host machine):
```bash
sudo vnx_config_nat ExtNet eno1
```
- Deploy simple demo scenario (one virtual network with one virtual machine):
```bash
sudo vnx -f $OSTACKLAB -x create-demo-scenario
```
- Deploy additional virtual machines:
```bash
sudo vnx -f $OSTACKLAB -x create-demo-vm2,create-demo-vm3,create-demo-vm4
```
6. Deploy Provider network based testing scenarios:
```bash
[ "$OSTACKLAB" == 'openstack_kolla_ansible.xml' ] && OSTACKVLANLAB=openstack_lab-vms-vlan.xml || OSTACKVLANLAB=openstack_lab-vms-vlan-vlan.xml
sudo vnx -f $OSTACKLAB -x create-vlan-demo-scenario
sudo vnx -f $OSTACKVLANLAB --create
```

### Cambios

Para hacer cambios no hace falta borrar el escenario, solo editar el fichero /etc/kolla/globals.yml. Para ello, seguir los siguientes pasos:

1. Realizar cambios dentro de openstack_kolla_ansible_2024_1.xml, mirar el apartado Mis cambios:

2. Ejecutar los cambios sobre el escenario: 
```bash
sudo vnx -f openstack_kolla_ansible_2024_1.xml -x config-admin
```

3. Acceder al nodo admin:
```bash
ssh root@admin
```

4. Volver a desplegar OpenStack, simplemente se actualiza el escenario con los nuevos cambios, el resto se mantiene: 
```bash
./deploy-ostack
```

### Parar el escenario y crear las imágenes

```
source ./create-vnx-images
```

Se ha desplegado el escenario de kolla y se han realizado las acciones de crear la red externa, importar imágenes, importar configuración de Octavia y Trove y crear el usuario myuser.
Todo esto antes de congelar las imágenes.