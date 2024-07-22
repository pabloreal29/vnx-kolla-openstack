import mysql.connector
import paramiko
import json
import time
import subprocess
from mysql.connector import errorcode
import pandas as pd
import numpy as np
import io
import tkinter as tk
from tkinter import messagebox

# Límites a considerar
MAX_SERVERS = 5
MIN_SERVERS = 2

# Considerar valores estándar de RAM en torno a 165 MB
HIGH_RAM_THRESHOLD = 500
LOW_RAM_THRESHOLD = 100

# Define el path al script existente
deploy_instance_script = "deploy/deploy-instance.sh"
deploy_instance_command = f"bash {deploy_instance_script}"

# Configuración de la conexión a MySQL
config = {
    'user': 'pabloreal',
    'password': 'xxxx',
    'host': '10.0.0.2',
    'database': 'ssh',
}

# Configuración del mensaje de alerta que salta cuando se detecta un uso excesivo de RAM    
def show_alert(title, message):
    root = tk.Tk()
    root.withdraw()  # Oculta la ventana principal de Tkinter
    messagebox.showwarning(title, message)
    root.destroy()  # Destruye la ventana después de mostrar la alerta

# Conexión a MySQL
def connect_to_mysql():
    try:
        cnx = mysql.connector.connect(**config)
        cursor = cnx.cursor()
        print("Conexión a MySQL exitosa.")
        return cnx, cursor
    except mysql.connector.Error as err:
        if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
            print("Error en el acceso a MySQL. Revisa tu nombre de usuario y contraseña")
        elif err.errno == errorcode.ER_BAD_DB_ERROR:
            print("La base de datos no existe")
        else:
            print(err)
        exit(1)

# Cerrar conexión con MySQL
def disconnect_to_mysql(cnx, cursor):
    try:
        cnx.commit()
        cursor.close()
        cnx.close()
        print("Conexión a MySQL cerrada.")
    except mysql.connector.Error as err:
        print(f"Error en la desconexión de MySQL: {err}")

# Función para ejecutar comando y obtener la salida
def execute_command(command):
    try:
        result = subprocess.run(command, shell=True, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return result.stdout.decode('utf-8')
    except subprocess.CalledProcessError as e:
        print(f"Error al ejecutar el comando '{command}': {e}")
        return None

# Creación de las tablas necesarias
def create_servers_table(cursor):
    try:
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS servers (
                ID VARCHAR(36) PRIMARY KEY,
                Name VARCHAR(255),
                Status VARCHAR(50),
                Networks VARCHAR(255),
                Image VARCHAR(255),
                Flavor VARCHAR(50)
            )
        """)
        print("Tabla servers creada exitosamente.")
    except mysql.connector.Error as err:
        print(f"Error al crear la tabla servers: {err}")

# Verificar y actualizar la estructura de la tabla
def ensure_table_structure(cursor, table_name):
    try:
        cursor.execute(f"""
            CREATE TABLE IF NOT EXISTS {table_name} (
                id INT AUTO_INCREMENT PRIMARY KEY,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                total_memory INT,
                used_memory INT,
                free_memory INT,
                free_memory_percent FLOAT
            )
        """)
        print(f"Tabla {table_name} verificada/creada.")
    except mysql.connector.Error as err:
        print(f"Error al verificar/crear la tabla {table_name}: {err}")

# Obtener detalles de servidores y IP del administrador
def get_server_details(cursor):
    try:
        cursor.execute("SELECT Name, Networks FROM servers WHERE Name REGEXP '^s[0-9]{1}$'")
        servers = cursor.fetchall()
        print("Detalles de los servidores obtenidos.")

        cursor.execute("SELECT Networks FROM servers WHERE Name='administrador'")
        admin_networks = cursor.fetchone()

        admin_networks_dict = json.loads(admin_networks[0].replace("'", "\""))
        admin_ip = admin_networks_dict['Net1'][1]  # Usar la segunda IP de Net1
        print("IP del administrador obtenida:", admin_ip)
        return servers, admin_ip
    except mysql.connector.Error as err:
        print(f"Error al obtener los detalles de los servidores: {err}")
        return [], None

# Obtener el número de servidores cuyo nombre sigue el patrón s_i, utilizando REGEX
def get_server_count(cursor):
    try:
        cursor.execute("SELECT COUNT(*) FROM servers WHERE Name REGEXP '^s[0-9]{1}$'")
        result = cursor.fetchone()
        if result:
            server_count = max(3, result[0])  # Asumiendo que siempre hay al menos 3 servidores (s1, s2, s3)
            print(f"Número actual de servidores en el escenario: {server_count}")
            return server_count
        else:
            return 0
    except mysql.connector.Error as err:
        print(f"Error al obtener el número de servidores: {err}")
        return 0

# Obtener información de memoria desde el servidor
def get_memory_info_from_server(ssh, server_ip, username, password):
    try:
        transport = ssh.get_transport()
        dest_addr = (server_ip, 22)
        local_addr = ('127.0.0.1', 0)
        channel = transport.open_channel("direct-tcpip", dest_addr, local_addr)

        ssh_server = paramiko.SSHClient()
        ssh_server.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh_server.connect(server_ip, username=username, password=password, sock=channel)

        stdin, stdout, stderr = ssh_server.exec_command("free -t --mega | grep 'Total'")
        output = stdout.read().strip().decode('utf-8')
        ssh_server.close()

        parts = output.split()
        total_mem = int(parts[1])
        free_mem = int(parts[3])
        used_mem = total_mem - free_mem
        free_mem_percent = (free_mem / total_mem) * 100

        print(f"Memoria del servidor {server_ip}: Total {total_mem} MB, Usada {used_mem} MB, Libre {free_mem} MB")

        return total_mem, used_mem, free_mem, free_mem_percent
    except Exception as e:
        print(f"Error al obtener la información del servidor {server_ip}: {e}")
        return None, None, None, None

# Almacenar datos de memoria en la base de datos
def store_memory_data(cursor, server_name, total_mem, used_mem, free_mem, free_mem_percent):
    try:
        table_name = f"ram_{server_name}"
        ensure_table_structure(cursor, table_name)
        cursor.execute(f"""
            INSERT INTO {table_name} (timestamp, total_memory, used_memory, free_memory, free_memory_percent)
            VALUES (NOW(), %s, %s, %s, %s)
        """, (total_mem, used_mem, free_mem, free_mem_percent))
        print(f"Datos de memoria almacenados para {server_name}.")
    except mysql.connector.Error as err:
        print(f"Error al almacenar los datos de memoria para {server_name}: {err}")

# Función principal
def main():
    cnx, cursor = connect_to_mysql()

    try:
        # Crear la tabla servers si no existe
        create_servers_table(cursor)

        # Actualizar datos en la tabla servers
        # Ejecutar el comando para obtener los servidores y obtener el resultado como CSV
        subprocess.run(["bash", "conf/admin-openrc.sh"])
        servers_command = "openstack server list -f csv"
        output1 = execute_command(servers_command)

        if output1:
            # Leer el CSV usando pandas
            df = pd.read_csv(io.StringIO(output1))
            df = df.replace({np.nan: None})

            # Insertar los datos en la tabla servers
            for _, row in df.iterrows():
                try:
                    cursor.execute("""
                        INSERT IGNORE INTO servers (ID, Name, Status, Networks, Image, Flavor)
                        VALUES (%s, %s, %s, %s, %s, %s)
                    """, (row['ID'], row['Name'], row['Status'], row['Networks'], row['Image'], row['Flavor']))
                except mysql.connector.Error as err:
                    print(f"Error al insertar el servidor con ID {row['ID']}: {err}")

            # Confirmar los cambios y cerrar la conexión
            cnx.commit()

            print("Datos de servidores insertados exitosamente.")
        else:
            print("No se pueden obtener los datos de los servidores desde nova.")

        # Obtener detalles de servidores y IP del administrador
        servers, admin_ip = get_server_details(cursor)

        # Parámetros de SSH
        username = 'root'
        password = 'xxxx'

        # Conectarse al servidor administrador
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(admin_ip, username=username, password=password, port=2022)
        print(f"Conectado al servidor administrador {admin_ip} por SSH.")

        while True:
            # Recolectar y almacenar datos de memoria y RAM
            print(f"-----------------------------------------------")
            server_number = get_server_count(cursor)
            print(f"-----------------------------------------------")

            for server in servers:
                server_name = server[0]
                networks_dict = json.loads(server[1].replace("'", "\""))
                server_ip = networks_dict['Net1'][0]  # Usar la primera IP de Net1

                total_mem, used_mem, free_mem, free_mem_percent = get_memory_info_from_server(ssh, server_ip, username, password)

                if total_mem is not None:
                    store_memory_data(cursor, server_name, total_mem, used_mem, free_mem, free_mem_percent)

                    # Evaluar si es necesario añadir o eliminar servidores
                    if used_mem > HIGH_RAM_THRESHOLD and get_server_count(cursor) < MAX_SERVERS:
                        show_alert("ALARMA: Uso Excesivo de RAM", "Detectado un uso excesivo de RAM en un servidor del escenario. Escalando hacia arriba...")
                        print(f"Memoria alta en el servidor {server_name}. Desplegando nueva instancia.")
                        server_list = [f'"{i}"' for i in range(1, server_number + 2)]
                        server_list_str = "[" + ", ".join(server_list) + "]"
                        subprocess.run(f'{deploy_instance_command} "{server_list_str}"', shell=True, check=True)
                        
                    elif used_mem < LOW_RAM_THRESHOLD and get_server_count(cursor) > MIN_SERVERS:
                        show_alert("ALARMA: Uso Insuficiente de RAM", "Detectado un uso insuficiente de RAM en un servidor del escenario. Escalando hacia abajo...")
                        print(f"Memoria baja en el servidor {server_name}. Eliminando una instancia.")
                        server_list = [f'"{i}"' for i in range(1, server_number)]
                        server_list_str = "[" + ", ".join(server_list) + "]"
                        subprocess.run(f'{deploy_instance_command} "{server_list_str}"', shell=True, check=True)

            print(f"-----------------------------------------------")
            print("Esperando 60 segundos antes de la siguiente ejecución...")
            time.sleep(60)

    except Exception as e:
        print(f"Error en la ejecución principal: {e}")
    finally:
        disconnect_to_mysql(cnx, cursor)

if __name__ == "__main__":
    main()
