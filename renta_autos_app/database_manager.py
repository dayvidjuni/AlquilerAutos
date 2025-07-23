import mysql.connector
from mysql.connector import Error
import os
from dotenv import load_dotenv

# Cargar las variables de entorno desde el archivo .env
load_dotenv()

class DatabaseManager:
    """
    Gestiona todas las interacciones con la base de datos MySQL.
    Utiliza un pool de conexiones para eficiencia y seguridad.
    """
    def __init__(self):
        try:
            self.pool = mysql.connector.pooling.MySQLConnectionPool(
                pool_name="renta_autos_pool",
                pool_size=5,  # Número de conexiones que se mantendrán abiertas
                host=os.getenv('DB_HOST'),
                user=os.getenv('DB_USER'),
                password=os.getenv('DB_PASSWORD'),
                database=os.getenv('DB_NAME')
            )
            print("Pool de conexiones creado exitosamente.")
        except Error as e:
            print(f"Error al crear el pool de conexiones: {e}")
            self.pool = None

    def get_connection(self):
        """Obtiene una conexión del pool."""
        if self.pool:
            try:
                return self.pool.get_connection()
            except Error as e:
                print(f"Error al obtener una conexión del pool: {e}")
                return None
        return None

    def execute_query(self, query, params=None):
        """
        Ejecuta consultas de tipo SELECT que devuelven datos.
        - query: La consulta SQL con placeholders (%s).
        - params: Una tupla de parámetros para la consulta.
        - Retorna: Los resultados de la consulta.
        """
        conn = self.get_connection()
        if conn is None:
            return None
        
        cursor = conn.cursor(dictionary=True) # Devuelve resultados como diccionarios
        results = None
        try:
            cursor.execute(query, params)
            results = cursor.fetchall()
            # print("Consulta ejecutada con éxito.") # Descomentar para depuración
        except Error as e:
            print(f"Error al ejecutar la consulta: {e}")
        finally:
            cursor.close()
            conn.close() # Devuelve la conexión al pool
        return results

    def execute_modification(self, query, params=None):
        """
        Ejecuta consultas de tipo INSERT, UPDATE, DELETE.
        - query: La consulta SQL con placeholders (%s).
        - params: Una tupla de parámetros para la consulta.
        - Retorna: El ID de la última fila insertada si aplica, o None.
        """
        conn = self.get_connection()
        if conn is None:
            return None
            
        cursor = conn.cursor()
        last_row_id = None
        try:
            cursor.execute(query, params)
            conn.commit() # Confirma los cambios en la base de datos
            last_row_id = cursor.lastrowid
            # print("Modificación ejecutada con éxito.") # Descomentar para depuración
        except Error as e:
            print(f"Error al ejecutar la modificación: {e}")
            conn.rollback() # Revierte los cambios en caso de error
        finally:
            cursor.close()
            conn.close() # Devuelve la conexión al pool
        return last_row_id
        
    def execute_procedure(self, procedure_name, params=None):
        """
        Ejecuta un procedimiento almacenado.
        - procedure_name: El nombre del procedimiento.
        - params: Una tupla de parámetros para el procedimiento.
        - Retorna: El resultado del procedimiento.
        """
        conn = self.get_connection()
        if conn is None:
            return None

        cursor = conn.cursor()
        results = None
        try:
            # Los procedimientos almacenados se llaman con callproc
            cursor.callproc(procedure_name, params)
            conn.commit() # Importante para que los cambios del SP se guarden
            
            # Para obtener los resultados de los parámetros OUT
            for result in cursor.stored_results():
                results = result.fetchall()
            
            # print(f"Procedimiento '{procedure_name}' ejecutado con éxito.")
        except Error as e:
            print(f"Error al ejecutar el procedimiento almacenado: {e}")
            conn.rollback()
        finally:
            cursor.close()
            conn.close()
        
        return results


# --- Ejemplo de uso (esto se puede eliminar más tarde) ---
if __name__ == '__main__':
    db_manager = DatabaseManager()
    
    if db_manager.pool:
        print("\nProbando una consulta SELECT a la tabla 'roles':")
        roles = db_manager.execute_query("SELECT * FROM roles")
        if roles:
            for rol in roles:
                print(rol)