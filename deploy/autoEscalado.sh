#!/bin/bash

source conf/admin-openrc.sh

# Obtener IDs de s1, s2 y s3
s1_id=$(openstack server show s1 -c id -f value)
s2_id=$(openstack server show s2 -c id -f value)
s3_id=$(openstack server show s3 -c id -f value)

# Obtener el id de la metrica (cpu) correspondiente a cada servidor

# Obtener el último valor de consumo de cpu de cada servidor
gnocchi measures show --aggregation mean $s1_id --sort-column timestamp --sort-descending | awk 'NR==4 {print $6}'
gnocchi measures show --aggregation mean $s2_id --sort-column timestamp --sort-descending | awk 'NR==4 {print $6}'
gnocchi measures show --aggregation mean $s3_id --sort-column timestamp --sort-descending | awk 'NR==4 {print $6}'