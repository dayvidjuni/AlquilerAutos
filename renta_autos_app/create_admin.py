# File: create_admin.py
# Propósito: Crear o resetear la contraseña del usuario administrador para asegurar el acceso.
# Ejecútalo una sola vez desde tu terminal con: python create_admin.py

from database_manager import DatabaseManager
from auth_manager import AuthManager
import sys

def setup_admin_user():
    """
    Este script verifica si el 'admin_user' existe.
    - Si existe, actualiza su contraseña para asegurar que sea correcta.
    - Si no existe, lo crea con la contraseña correcta.
    """
    print("--- Iniciando script de creación/actualización de admin ---")

    # 1. Inicializar los gestores
    db_manager = DatabaseManager()
    if not db_manager.pool:
        print("Error: No se pudo conectar a la base de datos. Verifica tu archivo .env")
        sys.exit(1) # Salir del script si no hay conexión

    auth_manager = AuthManager(db_manager)

    # 2. Definir los datos del admin
    admin_username = "admin_user"
    admin_password = "admin123"
    admin_email = "admin@secure.com"
    admin_nombre = "Admin"
    admin_apellido = "Sistema"
    admin_rol = "admin"

    # 3. Hashear la contraseña usando el método de AuthManager
    hashed_password = auth_manager.hash_password(admin_password)
    print(f"La contraseña '{admin_password}' ha sido hasheada correctamente.")

    # 4. Verificar si el usuario ya existe
    print(f"Buscando si el usuario '{admin_username}' ya existe...")
    user_query = "SELECT id_usuario FROM usuarios WHERE username = %s"
    existing_user = db_manager.execute_query(user_query, (admin_username,))

    if existing_user:
        # El usuario existe, vamos a ACTUALIZAR su contraseña.
        user_id = existing_user[0]['id_usuario']
        print(f"El usuario '{admin_username}' ya existe (ID: {user_id}). Se actualizará su contraseña.")
        
        update_query = "UPDATE usuarios SET password_hash = %s WHERE id_usuario = %s"
        db_manager.execute_modification(update_query, (hashed_password, user_id))
        
        print(f"¡Éxito! La contraseña para '{admin_username}' ha sido actualizada a '{admin_password}'.")
    else:
        # El usuario no existe, vamos a CREARLO.
        print(f"El usuario '{admin_username}' no existe. Se procederá a crearlo...")

        # Obtener el id_rol para 'admin'
        rol_query = "SELECT id_rol FROM roles WHERE nombre = %s"
        rol_result = db_manager.execute_query(rol_query, (admin_rol,))
        
        if not rol_result:
            print(f"Error fatal: El rol '{admin_rol}' no se encontró en la base de datos.")
            sys.exit(1)
        
        id_rol = rol_result[0]['id_rol']
        
        # Insertar el nuevo usuario
        insert_query = """
            INSERT INTO usuarios (id_rol, username, password_hash, email, nombre, apellido, activo)
            VALUES (%s, %s, %s, %s, %s, %s, TRUE)
        """
        params_insert = (id_rol, admin_username, hashed_password, admin_email, admin_nombre, admin_apellido)
        
        user_id = db_manager.execute_modification(insert_query, params_insert)

        if user_id:
            print(f"¡Éxito! Usuario '{admin_username}' creado con la contraseña '{admin_password}'.")
        else:
            print("Error: No se pudo crear el usuario administrador.")

    print("\n--- Script finalizado. Ahora puedes ejecutar 'python main.py' e intentar iniciar sesión. ---")


if __name__ == "__main__":
    setup_admin_user()