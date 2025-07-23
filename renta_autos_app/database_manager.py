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
                pool_size=5,
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
        if self.pool:
            try:
                return self.pool.get_connection()
            except Error as e:
                print(f"Error al obtener una conexión del pool: {e}")
                return None
        return None

    def execute_query(self, query, params=None):
        conn = self.get_connection()
        if conn is None: return None
        cursor = conn.cursor(dictionary=True)
        results = None
        try:
            cursor.execute(query, params)
            results = cursor.fetchall()
        except Error as e:
            print(f"Error al ejecutar la consulta: {e}")
        finally:
            cursor.close()
            conn.close()
        return results

    def execute_modification(self, query, params=None):
        conn = self.get_connection()
        if conn is None: return None
        cursor = conn.cursor()
        last_row_id = None
        try:
            cursor.execute(query, params)
            conn.commit()
            last_row_id = cursor.lastrowid
        except Error as e:
            print(f"Error al ejecutar la modificación: {e}")
            conn.rollback()
        finally:
            cursor.close()
            conn.close()
        return last_row_id
    
    def get_all_models_for_dropdown(self):
        query = """
            SELECT m.id_modelo, CONCAT(b.nombre, ' ', m.nombre) AS display_name
            FROM modelos m
            JOIN marcas b ON m.id_marca = b.id_marca
            ORDER BY display_name;
        """
        return self.execute_query(query)

    # --- NUEVAS FUNCIONES PARA ALQUILERES ---
    
    def get_available_vehicles_for_dropdown(self):
        """Obtiene vehículos con estado 'disponible' para los alquileres."""
        query = """
            SELECT 
                v.id_vehiculo,
                v.precio_diario,
                CONCAT(b.nombre, ' ', m.nombre, ' (', v.placa, ')') AS display_name
            FROM vehiculos v
            JOIN modelos m ON v.id_modelo = m.id_modelo
            JOIN marcas b ON m.id_marca = b.id_marca
            WHERE v.estado = 'disponible'
            ORDER BY display_name;
        """
        return self.execute_query(query)

    def get_clients_for_dropdown(self):
        """Obtiene todos los usuarios que son clientes."""
        query = """
            SELECT u.id_usuario, CONCAT(u.nombre, ' ', u.apellido, ' (', u.username, ')') AS display_name
            FROM usuarios u
            JOIN roles r ON u.id_rol = r.id_rol
            WHERE r.nombre = 'cliente' AND u.activo = TRUE
            ORDER BY u.apellido;
        """
        return self.execute_query(query)