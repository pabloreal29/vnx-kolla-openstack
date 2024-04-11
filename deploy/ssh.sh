#!/bin/bash
# Ejecucion: /home/p.realb/Desktop/CNVR/TF/ssh.sh -X, donde X es el parámetro a introducir.

if [ "$1" == "-s" ]; then
    openstack firewall group rule set ssh_admin --enable-rule
elif [ "$1" == "-n" ]; then
    openstack firewall group rule set ssh_admin --disable-rule
else 
    echo "Se ha introducido un parámetro no válido. Solamente se permiten las siguientes opciones:"
    echo "- Parámetro -s: Permitir acceso por SSH al puerto 2022 de admin."
    echo "- Parámetro -n: Denegar el acceso."
fi


