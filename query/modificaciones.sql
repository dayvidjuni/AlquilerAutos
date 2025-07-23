-- ==================== PROCEDIMIENTOS ALMACENADOS ====================

-- Eliminar el procedimiento anterior si existe
DROP PROCEDURE IF EXISTS registrar_usuario;

-- Crear nuevo procedimiento simplificado
DELIMITER $$
CREATE PROCEDURE registrar_usuario(
    IN p_username VARCHAR(50),
    IN p_password_hash VARCHAR(255),
    IN p_email VARCHAR(100),
    IN p_nombre VARCHAR(50),
    IN p_apellido VARCHAR(50),
    IN p_rol VARCHAR(20),
    OUT p_resultado VARCHAR(200)
)
BEGIN
    DECLARE v_id_rol INT DEFAULT NULL;
    
    -- Obtener ID del rol de forma segura
    SELECT id_rol INTO v_id_rol FROM roles WHERE nombre = p_rol LIMIT 1;
    
    IF v_id_rol IS NULL THEN
        SET p_resultado = 'Error: Rol no válido';
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Rol especificado no existe';
    ELSE
        -- Verificar si el usuario ya existe
        IF EXISTS (SELECT 1 FROM usuarios WHERE username = p_username LIMIT 1) THEN
            SET p_resultado = 'Error: Username ya existe';
            SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'El nombre de usuario ya está registrado';
        ELSEIF EXISTS (SELECT 1 FROM usuarios WHERE email = p_email LIMIT 1) THEN
            SET p_resultado = 'Error: Email ya registrado';
            SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'El email ya está registrado';
        ELSE
            -- Insertar el nuevo usuario
            INSERT INTO usuarios (id_rol, username, password_hash, email, nombre, apellido)
            VALUES (v_id_rol, p_username, p_password_hash, p_email, p_nombre, p_apellido);
            
            SET p_resultado = CONCAT('Éxito: Usuario registrado con ID ', LAST_INSERT_ID());
        END IF;
    END IF;
END$$
DELIMITER ;

-- ==================== ÍNDICES Y SEGURIDAD ====================

-- Índices para mejor rendimiento
CREATE INDEX idx_usuarios_username ON usuarios(username);
CREATE INDEX idx_usuarios_email ON usuarios(email);
CREATE INDEX idx_vehiculos_estado ON vehiculos(estado);
CREATE INDEX idx_alquileres_estado ON alquileres(estado, fecha_inicio);

-- Crear usuario con permisos limitados para Python
CREATE USER 'renta_python'@'%' IDENTIFIED BY 'Un4C0ntr4s3n14F0rt3!';
GRANT SELECT, INSERT, UPDATE ON renta_autos_secure.* TO 'renta_python'@'%';
GRANT EXECUTE ON PROCEDURE registrar_usuario TO 'renta_python'@'%';
FLUSH PRIVILEGES;