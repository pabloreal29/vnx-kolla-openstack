import subprocess
import time
import pandas as pd
import mysql.connector
from mysql.connector import errorcode

# Límites a considerar
SAMPLE_NUMBER = 5
CPU_THRESHOLD = 300

# Define the path to your existing script
create_tables_script = "deploy/create-ram-tables.py"
drop_tables_script = "deploy/drop-tables.py"

# Define the commands to create and delete tables
create_tables_command = f"python3 {create_tables_script}"
delete_tables_command = f"python3 {drop_tables_script}"

# Configuración de la conexión a MySQL
config = {
    'user': 'pabloreal',
    'password': 'xxxx',
    'host': 'localhost',
    'database': 'gnocchi',
}

# Conexión a MySQL
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


# Obtiene los últimos 3 valores de la columna value de una tabla ram_s{i} específica.
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


# Main function to run the commands every 60 seconds
def main():
    while True:
        try:
            # Execute the command to delete tables
            print("Ejecutando el comando para eliminar tablas...")
            subprocess.run(delete_tables_command, shell=True, check=True)
            print("Tablas eliminadas exitosamente.")

            # Execute the command to recreate tables
            print("Ejecutando el comando para recrear tablas...")
            subprocess.run(create_tables_command, shell=True, check=True)
            print("Tablas recreadas exitosamente.")

            # Conectarse a mysql
            cnx, cursor = connect_to_mysql()

            # Check RAM values for each table ram_s{i}
            print(f"Muestra de los últimos {SAMPLE_NUMBER} valores de uso de memoria RAM")
            for i in range(1, 6):
                table_name = f"ram_s{i}"
                last_values = get_last_ram_values(cursor, table_name)
                print(f"Uso de RAM en s{i}: {last_values}")

                # Verificar si alguno de los últimos valores es mayor que 300
                if any(value > CPU_THRESHOLD for value in last_values):
                    print(f"***ALARM. Detectado un uso excesivo de RAM en el servidor s{i}***")
            
            # Confirmar los cambios y cerrar la conexión
            cnx.commit()
            cursor.close()
            cnx.close()

        except subprocess.CalledProcessError as e:
            print(f"Error al ejecutar los comandos: {e}")

        # Wait for 60 seconds
        print("Esperando 60 segundos antes de la siguiente ejecución...")
        time.sleep(60)


if __name__ == "__main__":
    main()



