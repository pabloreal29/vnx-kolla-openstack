import subprocess
import time

# Define the path to your existing script
create_tables_script = "deploy/create-cpu-tables.py"
drop_tables_script = "deploy/drop-tables.py"

# Define the commands to create and delete tables
create_tables_command = f"python3 {create_tables_script}"
delete_tables_command = f"python3 {drop_tables_script}"

# Restart the kolla-ceilometer service via SSH
def restart_kolla_ceilometer():
    try:
        ssh_command = "ssh root@controller 'systemctl restart kolla-ceilometer*'"
        result = subprocess.run(ssh_command, shell=True, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        print(result.stdout.decode())
        if result.stderr:
            print(result.stderr.decode())
        print("Servicio kolla-ceilometer reiniciado exitosamente.")
    except subprocess.CalledProcessError as e:
        print(f"Error al reiniciar el servicio kolla-ceilometer: {e}")

# Main function to run the commands every 60 seconds
def main():
    while True:
        try:
            # Restart the kolla-ceilometer service
            print("Reiniciando el servicio kolla-ceilometer...")
            restart_kolla_ceilometer()

            # Execute the command to delete tables
            print("Ejecutando el comando para eliminar tablas...")
            subprocess.run(delete_tables_command, shell=True, check=True)
            print("Tablas eliminadas exitosamente.")

            # Execute the command to recreate tables
            print("Ejecutando el comando para recrear tablas...")
            subprocess.run(create_tables_command, shell=True, check=True)
            print("Tablas recreadas exitosamente.")

        except subprocess.CalledProcessError as e:
            print(f"Error al ejecutar los comandos: {e}")

        # Wait for 60 seconds
        print("Esperando 60 segundos antes de la siguiente ejecución...")
        time.sleep(60)

if __name__ == "__main__":
    main()

