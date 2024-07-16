#!/bin/bash

# Recibir el argumento server_number
server_number="$1"

# Ejecutar Terraform para aplicar solo el archivo principal main.tf
ssh root@tf-node << EOF
    cd shared/instance-module
    echo "El nuevo servidor es: s"$server_number
    terraform init 
    terraform apply -auto-approve -var="server_number=${server_number}" 
EOF

