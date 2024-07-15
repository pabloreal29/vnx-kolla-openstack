import mysql.connector
from mysql.connector import errorcode

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

# Función para eliminar tablas
def drop_tables(cursor):
    tables = ["servers", "metrics", "cpu_s1", "cpu_s2", "cpu_s3", "cpu_s4", "cpu_s5", "cpu_average", "ram_s1", "ram_s2", "ram_s3", "ram_s4", "ram_s5", "ram_average"]
    for table in tables:
        try:
            cursor.execute(f"DROP TABLE IF EXISTS {table}")
            print(f"Tabla {table} eliminada exitosamente.")
        except mysql.connector.Error as err:
            print(f"Error al eliminar la tabla {table}: {err}")

# Función principal
def main():
    cnx, cursor = connect_to_mysql()

    drop_tables(cursor)
    cnx.commit()

    # Cerrar cursor y conexión
    cursor.close()
    cnx.close()

if __name__ == "__main__":
    main()
