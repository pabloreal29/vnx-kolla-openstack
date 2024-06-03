#!/bin/bash
# Ejecucion: source deploy/ssh.sh -X, donde X es el parámetro a introducir.
source deploy/myuser-openrc.sh

if [ "$1" == "-s" ]; then
    openstack firewall group rule set ssh_admin --enable-rule
    echo "Se ha permitido el acceso por SSH al servidor de administración por el puerto 2022"
elif [ "$1" == "-n" ]; then
    openstack firewall group rule set ssh_admin --disable-rule
    echo "Se ha bloqueado el acceso por SSH al servidor de administración por el puerto 2022"
else 
    echo "Se ha introducido un parámetro no válido. Solamente se permiten las siguientes opciones:"
    echo "- Parámetro -s: Permitir acceso por SSH al puerto 2022 de admin."
    echo "- Parámetro -n: Denegar el acceso."
fi


