#!/bin/bash

# Obtener el nombre de la interfaz de red que sigue el patron enoX o enpXXX
interface=$(ip -o link show | awk -F': ' '{print $2}' | grep -E '^(eno|enp)[0-9]+')

# Verificar si se ha encontrado una interfaz
if [ -n "$interface" ]; then
    # Configurar NAT en la interfaz encontrada
    sudo vnx_config_nat ExtNet "$interface"
    echo "NAT configurado en la interfaz $interface"
else
    echo "No se ha encontrado una interfaz de red que siga el patrón enoX o enpXXX."
fi
