import openstack
import time
from datetime import datetime, timedelta

# Configura tu conexión a OpenStack
conn = openstack.connection.Connection(
    auth_url="http://10.0.0.11:5000/v3",
    project_name="admin",
    username="admin",
    password="xxxx",
    region_name="RegionOne",
    user_domain_name="Default",
    project_domain_name="Default"
)

# Umbrales de CPU para escalado
CPU_THRESHOLD_UP = 70
CPU_THRESHOLD_DOWN = 30
MIN_INSTANCES = 3
MAX_INSTANCES = 5
CHECK_INTERVAL = 60  # En segundos

# Obtener el ID de la imagen y el flavor
image = conn.compute.find_image('focal-servers-vnx')
flavor = conn.compute.find_flavor('m1.large')

# Redes
net1 = conn.network.find_network('Net1')
net2 = conn.network.find_network('Net2')

# Obtener el uso de CPU promedio
def get_cpu_usage(server):
    diagnostics = conn.compute.get_server_diagnostics(server)
    return diagnostics['cpu0_time'] if 'cpu0_time' in diagnostics else 0

def scale_up():
    if len(conn.compute.servers(details=True)) < MAX_INSTANCES:
        server_name = f's{len(conn.compute.servers(details=True)) + 1}'
        port1 = conn.network.create_port(network_id=net1.id)
        port2 = conn.network.create_port(network_id=net2.id)

        conn.compute.create_server(
            name=server_name,
            image_id=image.id,
            flavor_id=flavor.id,
            networks=[{"port": port1.id}, {"port": port2.id}],
            key_name=server_name,
            user_data='''#!/bin/bash
            systemctl start apache2
            echo "<h1>Bienvenidos al {} Server</h1>" > /var/www/html/index.html
            '''.format(server_name)
        )
        print(f"Scaled up: {server_name} created.")

def scale_down():
    servers = conn.compute.servers(details=True)
    if len(servers) > MIN_INSTANCES:
        server_to_remove = servers[-1]
        conn.compute.delete_server(server_to_remove)
        print(f"Scaled down: {server_to_remove.name} removed.")

def main():
    while True:
        servers = [server for server in conn.compute.servers(details=True) if server.name.startswith('s')]
        total_cpu_usage = sum(get_cpu_usage(server) for server in servers)
        avg_cpu_usage = total_cpu_usage / len(servers)

        print(f"Average CPU usage: {avg_cpu_usage}%")

        if avg_cpu_usage > CPU_THRESHOLD_UP:
            scale_up()
        elif avg_cpu_usage < CPU_THRESHOLD_DOWN and len(servers) > MIN_INSTANCES:
            scale_down()
        
        time.sleep(CHECK_INTERVAL)

if __name__ == "__main__":
    main()
