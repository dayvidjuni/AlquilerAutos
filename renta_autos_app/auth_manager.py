import bcrypt
from datetime import datetime, timedelta
import uuid

# Importamos la clase que creamos en el paso anterior
from database_manager import DatabaseManager

class AuthManager:
    """
    Gestiona la autenticación de usuarios, registro y sesiones.
    """
    def __init__(self, db_manager: DatabaseManager):
        """
        Inicializa el AuthManager con una instancia del DatabaseManager.
        """
        self.db_manager = db_manager

    @staticmethod
    def hash_password(password: str) -> str:
        """
        Hashea una contraseña usando bcrypt.
        - password: La contraseña en texto plano.
        - Retorna: La contraseña hasheada como una cadena de texto.
        """
        salt = bcrypt.gensalt()
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt)
        return hashed_password.decode('utf-8')

    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """
        Verifica si una contraseña en texto plano coincide con un hash.
        - plain_password: La contraseña que introduce el usuario.
        - hashed_password: La contraseña hasheada guardada en la BD.
        - Retorna: True si coinciden, False en caso contrario.
        """
        return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))

    def register_user(self, username, password, email, nombre, apellido, rol='cliente'):
        """
        Registra un nuevo usuario en la base de datos usando el procedimiento almacenado.
        Retorna un diccionario con el resultado.
        """
        if not all([username, password, email, nombre, apellido]):
            return {'success': False, 'message': 'Todos los campos son obligatorios.'}

        # Hashear la contraseña antes de enviarla a la BD
        password_hash = self.hash_password(password)

        # Parámetros para el procedimiento almacenado
        # El último parámetro ('') es un placeholder para la variable OUT p_resultado
        params = (username, password_hash, email, nombre, apellido, rol, '')
        
        try:
            # Nuestro db_manager no está diseñado para capturar parámetros OUT directamente.
            # Una forma más sencilla y controlada es manejar la lógica en Python.
            # Verificamos si el usuario o email ya existen primero.
            
            # Revisar si el username existe
            query_user = "SELECT id_usuario FROM usuarios WHERE username = %s"
            if self.db_manager.execute_query(query_user, (username,)):
                return {'success': False, 'message': 'El nombre de usuario ya está en uso.'}

            # Revisar si el email existe
            query_email = "SELECT id_usuario FROM usuarios WHERE email = %s"
            if self.db_manager.execute_query(query_email, (email,)):
                return {'success': False, 'message': 'El correo electrónico ya está registrado.'}
            
            # Obtener el id_rol
            query_rol = "SELECT id_rol FROM roles WHERE nombre = %s"
            rol_result = self.db_manager.execute_query(query_rol, (rol,))
            if not rol_result:
                 return {'success': False, 'message': f'El rol "{rol}" no es válido.'}
            id_rol = rol_result[0]['id_rol']

            # Insertar el nuevo usuario
            insert_query = """
                INSERT INTO usuarios (id_rol, username, password_hash, email, nombre, apellido)
                VALUES (%s, %s, %s, %s, %s, %s)
            """
            params_insert = (id_rol, username, password_hash, email, nombre, apellido)
            user_id = self.db_manager.execute_modification(insert_query, params_insert)

            if user_id:
                return {'success': True, 'message': f'Usuario registrado con ID: {user_id}', 'user_id': user_id}
            else:
                return {'success': False, 'message': 'Ocurrió un error durante el registro.'}

        except Exception as e:
            print(f"Error en register_user: {e}")
            return {'success': False, 'message': f'Error de sistema: {e}'}

    def login(self, username, password, ip_address='127.0.0.1'):
        """
        Autentica a un usuario y crea una sesión si las credenciales son correctas.
        """
        # Registrar el intento de login
        log_attempt_query = "INSERT INTO intentos_login (username, direccion_ip, exitoso) VALUES (%s, %s, %s)"
        
        query = """
            SELECT u.id_usuario, u.password_hash, u.activo, r.nombre as rol
            FROM usuarios u
            JOIN roles r ON u.id_rol = r.id_rol
            WHERE u.username = %s
        """
        user_data = self.db_manager.execute_query(query, (username,))
        
        if not user_data:
            self.db_manager.execute_modification(log_attempt_query, (username, ip_address, False))
            return {'success': False, 'message': 'Usuario o contraseña incorrectos.'}

        user = user_data[0] # execute_query devuelve una lista

        if not user['activo']:
            self.db_manager.execute_modification(log_attempt_query, (username, ip_address, False))
            return {'success': False, 'message': 'La cuenta de usuario está desactivada.'}

        if self.verify_password(password, user['password_hash']):
            # Contraseña correcta, intento exitoso
            self.db_manager.execute_modification(log_attempt_query, (username, ip_address, True))
            
            # Crear la sesión
            token = str(uuid.uuid4())
            fecha_expiracion = datetime.now() + timedelta(hours=8) # Sesión válida por 8 horas
            
            session_query = """
                INSERT INTO sesiones (id_usuario, token, fecha_expiracion, direccion_ip)
                VALUES (%s, %s, %s, %s)
            """
            session_params = (user['id_usuario'], token, fecha_expiracion, ip_address)
            session_id = self.db_manager.execute_modification(session_query, session_params)
            
            if not session_id:
                return {'success': False, 'message': 'Error al crear la sesión.'}

            # Actualizar último login del usuario
            update_login_query = "UPDATE usuarios SET ultimo_login = NOW() WHERE id_usuario = %s"
            self.db_manager.execute_modification(update_login_query, (user['id_usuario'],))

            return {
                'success': True,
                'user_id': user['id_usuario'],
                'rol': user['rol'],
                'token': token
            }
        else:
            # Contraseña incorrecta
            self.db_manager.execute_modification(log_attempt_query, (username, ip_address, False))
            return {'success': False, 'message': 'Usuario o contraseña incorrectos.'}
            
    def logout(self, token: str):
        """
        Cierra una sesión marcándola como inactiva en la base de datos.
        """
        query = "UPDATE sesiones SET activa = FALSE, fecha_expiracion = NOW() WHERE token = %s AND activa = TRUE"
        self.db_manager.execute_modification(query, (token,))
        print(f"Sesión con token {token} cerrada.")
        return True

# --- Ejemplo de uso (para probar el módulo de forma independiente) ---
if __name__ == '__main__':
    db_manager = DatabaseManager()
    auth_manager = AuthManager(db_manager)

    # --- Prueba de registro ---
    print("--- Probando registro de nuevo cliente ---")
    # Genera un usuario único cada vez que se ejecuta para evitar errores de duplicado
    unique_user = f"cliente_prueba_{datetime.now().strftime('%H%M%S')}"
    unique_email = f"cliente_{datetime.now().strftime('%H%M%S')}@test.com"
    
    # registro_resultado = auth_manager.register_user(unique_user, 'claveSegura123', unique_email, 'NombrePrueba', 'ApellidoPrueba')
    # print(registro_resultado)

    # --- Prueba de login ---
    print("\n--- Probando login (usuario creado desde SQL) ---")
    # Nota: Asegúrate de tener un usuario 'admin_user' con contraseña 'admin123' en tu BD.
    # Si no lo tienes, puedes crearlo con el script SQL o usar la función de registro.
    
    # Crea un usuario admin si no existe para la prueba
    if not db_manager.execute_query("SELECT id_usuario FROM usuarios WHERE username = 'admin_user'"):
        print("Creando usuario 'admin_user' para la prueba...")
        auth_manager.register_user('admin_user', 'admin123', 'admin@secure.com', 'Admin', 'Sistema', rol='admin')

    login_resultado = auth_manager.login('admin_user', 'admin123')
    print(login_resultado)

    if login_resultado['success']:
        print("\n--- Probando logout ---")
        token_a_cerrar = login_resultado['token']
        auth_manager.logout(token_a_cerrar)

    print("\n--- Probando login con datos incorrectos ---")
    login_fallido = auth_manager.login('usuario_inexistente', 'clavemala')
    print(login_fallido)