import pandas as pd
import numpy as np
import mysql.connector
from mysql.connector import errorcode
import subprocess
import io

# Configuración de la conexión a MySQL
config = {
    'user': 'pabloreal',
    'password': 'xxxx',
    'host': '10.0.0.2',
    'database': 'gnocchi',
}

# Numero de muestras mas recientes que se quiere almacenar por cada tabla
NUM_REGISTROS = 100

# Funcion para ejecutar comando y obtener la salida
def execute_command(command):
    try:
        result = subprocess.run(command, shell=True, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return result.stdout.decode('utf-8')
    except subprocess.CalledProcessError as e:
        print(f"Error al ejecutar el comando '{command}': {e}")
        return None

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

# Función para eliminar tablas
def drop_tables(cursor):
    tables = ["servers", "metrics", "ram_s1", "ram_s2", "ram_s3", "ram_s4", "ram_s5", "ram_average"]
    for table in tables:
        try:
            cursor.execute(f"DROP TABLE IF EXISTS {table}")
        except mysql.connector.Error as err:
            print(f"Error al eliminar la tabla {table}: {err}")
    
# Creación de las tablas necesarias
def create_servers_table(cursor):
    try:
        cursor.execute("CREATE DATABASE IF NOT EXISTS gnocchi")
        cursor.execute("USE gnocchi")
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
        print(f"Tabla servers creada exitosamente.")
    except mysql.connector.Error as err:
        print(f"Error: {err}")
        exit(1)

def create_metrics_table(cursor):
    try:
        cursor.execute("CREATE DATABASE IF NOT EXISTS gnocchi")
        cursor.execute("USE gnocchi")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS metrics (
                id VARCHAR(36) PRIMARY KEY,
                archive_policy_name VARCHAR(255),
                name VARCHAR(255),
                unit VARCHAR(50),
                resource_id VARCHAR(36)
            )
        """)
        print(f"Tabla metrics creada exitosamente.")
    except mysql.connector.Error as err:
        print(f"Error: {err}")
        exit(1)

def create_measures_table(cursor):
    for i in range(1, 6):
        table_name = f"ram_s{i}"
        try:
            cursor.execute("CREATE DATABASE IF NOT EXISTS gnocchi")
            cursor.execute("USE gnocchi")
            cursor.execute(f"""
                CREATE TABLE IF NOT EXISTS {table_name} (
                    timestamp DATETIME NOT NULL PRIMARY KEY,
                    granularity FLOAT,
                    value DOUBLE
                )
            """)
            print(f"Tabla {table_name} creada exitosamente.")
        except mysql.connector.Error as err:
            print(f"Error al crear la tabla {table_name}: {err}")

# Creación de la tabla ram_average
def create_ram_average_table(cursor):
    try:
        cursor.execute("CREATE DATABASE IF NOT EXISTS gnocchi")
        cursor.execute("USE gnocchi")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS ram_average (
                timestamp DATETIME NOT NULL PRIMARY KEY,
                granularity FLOAT,
                value DOUBLE
            )
        """)
        print(f"Tabla ram_average creada exitosamente.")
    except mysql.connector.Error as err:
        print(f"Error al crear la tabla ram_average: {err}")

# Calcular la media aritmética de las tablas ram_s{i} y almacenar en ram_average
def calculate_and_store_averages(cursor, num_tables):
    try:
        # Crear una lista de nombres de tabla ram_s{i}
        table_names = [f"ram_s{i}" for i in range(1, num_tables + 1)]

        # Construir la consulta SQL dinámicamente para hacer el JOIN y calcular las medias
        query = f"""
            INSERT INTO ram_average (timestamp, granularity, value)
            SELECT 
                s1.timestamp,
                s1.granularity,
                (
                    s1.value {'+'.join([f'+s{i}.value' for i in range(2, num_tables + 1)])}
                ) / {num_tables} AS average_value
            FROM 
                {table_names[0]} s1
        """
        
        # Hacer INNER JOIN con las demás tablas ram_s{i}
        for i in range(2, num_tables + 1):
            query += f"""
            INNER JOIN 
                {table_names[i-1]} s{i} ON s1.timestamp = s{i}.timestamp
            """

        query += ";"

        cursor.execute(query)
        print(f"Media aritmética calculada y almacenada en ram_average para {num_tables} tablas exitosamente.")
    except mysql.connector.Error as err:
        print(f"Error al calcular y almacenar las medias aritméticas: {err}")


# Función principal
def main():
    cnx, cursor = connect_to_mysql()

    # Llamar a los métodos definidos anteriormente
    create_servers_table(cursor)
    create_metrics_table(cursor)
    create_measures_table(cursor)
    create_ram_average_table(cursor)

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

    # Ejecutar el comando para obtener las metricas y obtener el resultado como CSV
    gnocchi_command = "gnocchi metric list --sort-column name --sort-descending -f csv"
    output2 = execute_command(gnocchi_command)

    if output2:
        # Leer el CSV usando pandas
        df = pd.read_csv(io.StringIO(output2))
        df = df.replace({np.nan: None})

        # Insertar los datos en la tabla metrics
        for _, row in df.iterrows():
            try:
                cursor.execute("""
                    INSERT IGNORE INTO metrics (id, archive_policy_name, name, unit, resource_id)
                    VALUES (%s, %s, %s, %s, %s)
                    ON DUPLICATE KEY UPDATE
                        archive_policy_name = VALUES(archive_policy_name),
                        name = VALUES(name),
                        unit = VALUES(unit),
                        resource_id = VALUES(resource_id)
                """, (row['id'], row['archive_policy/name'], row['name'], row['unit'], row['resource_id']))
            except mysql.connector.Error as err:
                print(f"Error al insertar la métrica con ID {row['id']}: {err}")

        # Confirmar los cambios y cerrar la conexión
        cnx.commit()

        print("Datos de métricas insertados exitosamente.")
    else:
        print("No se pueden obtener los datos de las métricas desde gnocchi.")

    # Consultas SQL para obtener los IDs de métricas de memoria para 's1', 's2', 's3', 's4' y 's5' 
    server_names = ['s1', 's2', 's3', 's4', 's5']

    # Lista para almacenar las queries para obtener los datos de cada tabla
    queries = []

    for server in server_names:
        query = f"SELECT metrics.id FROM metrics INNER JOIN servers ON metrics.resource_id = servers.ID WHERE metrics.name = 'memory.usage' AND servers.name = '{server}';"
        queries.append(query)

    # Lista para almacenar los IDs de métricas
    ram_ids = []

    # Ejecutar las consultas y obtener los IDs de métricas
    for query in queries:
        try:
            cursor.execute(query)
            results = cursor.fetchall()
            if results:
                ram_ids.append(results[0][0])  # Agregar el primer resultado de la primera fila a la lista
        except mysql.connector.Error as err:
            print(f"Error al ejecutar la consulta SQL: {err}")

    # Imprimir los IDs obtenidos
    for i, ram_id in enumerate(ram_ids, start=1):
        print(f"El ID de la métrica correspondiente al uso de RAM en el servidor s{i} es:", ram_id)

    # Contador para verificar el numero de servidores con datos insertados
    servers_with_data = 0

    # Ejecutar el comando para obtener las medidas y obtener el resultado como CSV
    for i, ram_id in enumerate(ram_ids, start=1):
        measures_command = f"gnocchi measures show --aggregation mean {ram_id} --sort-column timestamp --sort-descending -f csv"
        output_servers = execute_command(measures_command)

        if output_servers:
            try:
                # Leer el CSV usando pandas
                df = pd.read_csv(io.StringIO(output_servers))
                df = df.replace({np.nan: None})
                
                # Asegurar que las columnas esperadas estén presentes en el DataFrame
                if 'timestamp' in df.columns and 'granularity' in df.columns and 'value' in df.columns:

                    # Obtener los últimos 30 registros para cada servidor
                    df_last_30 = df.head(NUM_REGISTROS)

                    # Insertar los datos en la tabla ram_s{i}
                    table_name = f"ram_s{i}"
                    for _, row in df_last_30.iterrows():
                        try:
                            cursor.execute(f"""
                                INSERT IGNORE INTO {table_name} (timestamp, granularity, value)
                                VALUES (%s, %s, %s)
                            """, (row['timestamp'], row['granularity'], row['value']))
                        except mysql.connector.Error as err:
                            print(f"Error al insertar datos en {table_name}: {err}")
                    cnx.commit()

                    # Comprobar si la tabla no está vacía
                    cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
                    count = cursor.fetchone()[0]
                    
                    if count > 0:
                        servers_with_data += 1
                        print(f"Datos del uso de la RAM en {table_name} insertados exitosamente.")
                    else:
                        print(f"Por el momento, no existen datos de uso de RAM que se puedan almacenar en la tabla {table_name}.")
                else:
                    print(f"El DataFrame no contiene las columnas esperadas: {df.columns}")
            except pd.errors.EmptyDataError:
                print(f"No se encontraron datos en la salida del comando para {table_name}.")
        else:
            print(f"No se pudo obtener el resultado de las medidas del uso de la RAM en s{i}.")

    # Crear la tabla ram_average, que contiene la media aritmética de uso de RAM de los servidores
    calculate_and_store_averages(cursor, servers_with_data)

    # Confirmar los cambios y cerrar la conexión
    cnx.commit()

    # Cerrar cursor y conexión
    cursor.close()
    cnx.close()

if __name__ == "__main__":
    main()
