import subprocess
import json
from datetime import datetime, timedelta
from openstack import connection

provider "openstack" {
  user_name   = "admin"
  tenant_name = "admin"
  password    = "xxxx"
  auth_url    = "http://10.0.0.11:5000/v3"
  region      = "RegionOne"
}

# Configura tu conexión a OpenStack
conn = connection.Connection(
    auth_url="http://10.0.0.11:5000/v3",
    project_name="admin",
    username="admin",
    password="yxxxx",
    region_name="RegionOne",
    user_domain_name="Default",
    project_domain_name="Default"
)

# Umbrales de CPU para escalado
CPU_THRESHOLD_UP = 70
CPU_THRESHOLD_DOWN = 30
MIN_INSTANCES = 3
MAX_INSTANCES = 5

def get_metric_id():
    result = subprocess.run(['gnocchi', 'metric', 'list', '--sort-column', 'name', '--sort-ascending'], stdout=subprocess.PIPE)
    metrics = json.loads(result.stdout)
    # Elegimos la metrica de CPU
    for metric in metrics:
        if metric['name'] == 'cpu':
            return metric['id']
    return None

def get_cpu_usage(metric_id):
    current_time = datetime.utcnow()
    start_time = (current_time - timedelta(minutes=1)).isoformat()
    result = subprocess.run(['gnocchi', 'measures', 'show', '--aggregation', 'mean', '--granularity', '60', metric_id, '--start', start_time], stdout=subprocess.PIPE)
    measures = json.loads(result.stdout)
    if measures:
        return measures[-1][2]  # Valor medio de la CPU en el ultimo minuto
    return 0

def scale_up():
    if len(conn.compute.servers(details=True)) < MAX_INSTANCES:
        conn.compute.create_server(
            name=f'example-instance-{len(conn.compute.servers(details=True)) + 1}',
            image_id=conn.compute.find_image('ubuntu').id,
            flavor_id=conn.compute.find_flavor('m1.small').id,
            networks=[{"uuid": conn.network.find_network('public').id}]
        )
        print("Scaled up: new instance created.")

def scale_down():
    servers = conn.compute.servers(details=True)
    if len(servers) > MIN_INSTANCES:
        conn.compute.delete_server(servers[-1].id)
        print("Scaled down: instance removed.")

def main():
    metric_id = get_metric_id()
    if metric_id is None:
        print("CPU metric not found")
        return
    
    servers = conn.compute.servers(details=True)
    total_cpu_usage = sum(get_cpu_usage(metric_id) for _ in servers)
    avg_cpu_usage = total_cpu_usage / len(servers)
    
    if avg_cpu_usage > CPU_THRESHOLD_UP:
        scale_up()
    elif avg_cpu_usage < CPU_THRESHOLD_DOWN:
        scale_down()

if __name__ == "__main__":
    main()
