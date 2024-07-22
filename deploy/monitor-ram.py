import subprocess
import time
import pandas as pd
import mysql.connector
from mysql.connector import errorcode
import tkinter as tk
from tkinter import messagebox

# Límites a considerar
SAMPLE_NUMBER = 3
MAX_SERVERS = 5
MIN_SERVERS = 2

# Considerar valores estandar de RAM en torno a 165 MB
HIGH_RAM_THRESHOLD = 300
AVG_HIGH_RAM_THRESHOLD = 200
LOW_RAM_THRESHOLD = 100
AVG_LOW_RAM_THRESHOLD = 150

# Define the path to your existing script
create_tables_script = "deploy/create-ram-tables.py"
drop_tables_script = "deploy/drop-tables.py"
deploy_instance_script = "deploy/deploy-instance.sh"  # Ruta al script deploy-instance.sh

# Define the commands to create and delete tables
create_tables_command = f"python3 {create_tables_script}"
delete_tables_command = f"python3 {drop_tables_script}"
deploy_instance_command = f"bash {deploy_instance_script}"  # Comando para ejecutar el script deploy-instance.sh

# Configuración de la conexión a MySQL
config = {
    'user': 'pabloreal',
    'password': 'xxxx',
    'host': '10.0.0.2',
    'database': 'gnocchi',
}

# Configuración del mensaje de alerta que salta cuando se detecta un uso excesivo de RAM    
def show_alert(title, message):
    root = tk.Tk()
    root.withdraw()  # Oculta la ventana principal de Tkinter
    messagebox.showwarning(title, message)
    root.destroy()  # Destruye la ventana después de mostrar la alerta

# Establecer conexión a MySQL
def connect_to_mysql():
    try:
        cnx = mysql.connector.connect(**config)
        cursor = cnx.cursor()
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
    except mysql.connector.Error as err:
        if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
            print("Error en la desconexión de MySQL. Revisa tu nombre de usuario y contraseña")
        elif err.errno == errorcode.ER_BAD_DB_ERROR:
            print("La base de datos no existe")
        else:
            print(err)
        exit(1)

# Obtiene los últimos {SAMPLE_NUMBER} valores de la columna value de una tabla de uso de RAM específica.
def get_last_ram_values(cursor, table_name):
    try:
        cursor.execute(f"SELECT value FROM {table_name} ORDER BY timestamp DESC LIMIT {SAMPLE_NUMBER}")
        results = cursor.fetchall()
        if results:
            last_values = [result[0] for result in results]  # Lista de los últimos valores de la columna 'value'
            return last_values
        else:
            return []
    except mysql.connector.Error as err:
        print(f"Error al obtener los últimos valores de {table_name}: {err}")
        return []


# Obtener el número de servidores cuyo nombre sigue el patron s_i, utilizando REGEX
def get_server_count(cursor):
    try:
        cursor.execute("SELECT COUNT(*) FROM servers WHERE Name REGEXP '^s[0-9]{1}$'")
        result = cursor.fetchone()
        if result:
            server_count = max(3, result[0]) # Asumiendo que siempre hay al menos 3 servidores (s1, s2, s3)
            print(f"Número actual de servidores en el escenario: {server_count}")
            return server_count  
        else:
            return 0
    except mysql.connector.Error as err:
        print(f"Error al obtener el número de servidores: {err}")
        return 0


# Main function to run the commands every 60 seconds
def main():
    while True:
        try:
            # Execute the command to delete tables
            print("Ejecutando el comando para eliminar tablas...")
            subprocess.run(delete_tables_command, shell=True, check=True)

            # Execute the command to recreate tables
            print("Ejecutando el comando para recrear tablas...")
            subprocess.run(create_tables_command, shell=True, check=True)
            print("Tablas recreadas exitosamente.")

            # Conectarse a mysql
            cnx, cursor = connect_to_mysql()

            # Store the number of servers s{i}
            print(f"-----------------------------------------------")
            server_number = get_server_count(cursor)
            print(f"-----------------------------------------------")

            # Check RAM values for each table ram_s{i} to see which server is causing the increment
            print(f"Muestra de los últimos {SAMPLE_NUMBER} valores de uso de memoria RAM:")
            for i in range(1, 6):
                table_name = f"ram_s{i}"
                last_values = get_last_ram_values(cursor, table_name)
                print(f"    Uso de RAM en s{i}: {last_values}")
            
                # Verificar si alguno de los últimos valores es mayor que el threshold
                if any(value > HIGH_RAM_THRESHOLD for value in last_values):
                    print(f"*** Detectado un uso excesivo de RAM en el servidor s{i} ***")
                
                # Verificar si alguno de los últimos valores es mayor que el threshold
                elif any(value < LOW_RAM_THRESHOLD for value in last_values):
                    print(f"*** Detectado un uso insuficiente de RAM en el servidor s{i} ***")

            # Check RAM values for the table ram_average to see if upscaling is needed
            table_name_avg = "ram_average"
            last_values_avg = get_last_ram_values(cursor, table_name_avg)
            print(f"    Valor medio del uso de RAM en los {server_number} servidores del escenario: {last_values_avg}")

            # Verificar si alguno de los últimos valores es mayor que el threshold
            if any(value_avg > AVG_HIGH_RAM_THRESHOLD for value_avg in last_values_avg):
                print(f"*** Detectado un valor medio excesivo de uso de RAM ***")
                show_alert("ALARMA: Uso Excesivo de RAM", "Detectado un uso excesivo de memoria en los servidores del escenario. Escalando hacia arriba...")
            
                # Verificar si ya está creado el máximo número de servidores
                if(server_number >= MAX_SERVERS):
                    show_alert("ALARMA: Número Máximo de Servidores Alcanzado", "Se ha alcanzado el número máximo de servidores definido. Deteniendo la ejecución del script")
                    print(f"Ya está desplegado el máximo número de servidores. Deteniendo la ejecución del script...")
                    disconnect_to_mysql(cnx, cursor)
                    exit()
                else:
                    server_list = [f'"{i}"' for i in range(1, server_number + 2)]
                    server_list_str = "[" + ", ".join(server_list) + "]"
                    subprocess.run(f'{deploy_instance_command} "{server_list_str}"', shell=True, check=True)
                    print(f"Instancia adicional creada. Deteniendo la ejecución del script...")
                    disconnect_to_mysql(cnx, cursor)
                    exit() 
            
            # Verificar si alguno de los últimos valores es mayor que el threshold
            elif any(value_avg < AVG_LOW_RAM_THRESHOLD for value_avg in last_values_avg):
                print(f"*** Detectado un valor medio insuficiente de uso de RAM ***")
                show_alert("ALARMA: Uso Insuficiente de RAM", "Detectado un uso insuficiente de memoria en los servidores del escenario. Escalando hacia abajo...")
            
                # Verificar si ya está creado el mínimo número de servidores
                if(server_number <= MIN_SERVERS):
                    show_alert("ALARMA: Número Mínimo de Servidores Alcanzado", "Se ha alcanzado el número mínimo de servidores definido. Deteniendo la ejecución del script")
                    print(f"Ya está desplegado el mínimo número de servidores. Deteniendo la ejecución del script...")
                    disconnect_to_mysql(cnx, cursor)
                    exit()
                else:
                    server_list = [f'"{i}"' for i in range(1, server_number)]
                    server_list_str = "[" + ", ".join(server_list) + "]"
                    subprocess.run(f'{deploy_instance_command} "{server_list_str}"', shell=True, check=True)
                    print(f"Instancia adicional eliminada. Deteniendo la ejecución del script...")
                    disconnect_to_mysql(cnx, cursor)
                    exit() 
            
            # Confirmar los cambios y cerrar la conexión
            disconnect_to_mysql(cnx, cursor)

        except subprocess.CalledProcessError as e:
            print(f"Error al ejecutar los comandos: {e}")

        # Wait for 60 seconds
        print(f"-----------------------------------------------")
        print("Esperando 60 segundos antes de la siguiente ejecución...")
        time.sleep(60)


if __name__ == "__main__":
    main()
