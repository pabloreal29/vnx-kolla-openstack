#!/bin/bash

# Recibir el argumento server_number
server_list="$1"

# Ejecutar Terraform para aplicar solo el archivo principal main.tf
ssh root@tf-node << EOF
    cd shared
    echo "La nueva lista de servidores es: "$server_list
    terraform init 
    terraform apply -auto-approve -var="server_list=${server_list}" 
EOF

