-- Creación de la base de datos
CREATE DATABASE IF NOT EXISTS renta_autos_secure 
CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE renta_autos_secure;

-- ==================== TABLAS PRINCIPALES ====================

-- Tabla de roles
CREATE TABLE roles (
    id_rol INT PRIMARY KEY AUTO_INCREMENT,
    nombre VARCHAR(20) NOT NULL UNIQUE,
    descripcion VARCHAR(100)
);

-- Insertar roles básicos
INSERT INTO roles (nombre, descripcion) VALUES 
('admin', 'Administrador del sistema con todos los permisos'),
('empleado', 'Personal autorizado para gestionar alquileres'),
('cliente', 'Usuarios que alquilan vehículos');

-- Tabla de usuarios (para todos los tipos de usuarios)
CREATE TABLE usuarios (
    id_usuario INT PRIMARY KEY AUTO_INCREMENT,
    id_rol INT NOT NULL DEFAULT 3, -- Por defecto cliente
    username VARCHAR(50) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL, -- Almacenará contraseñas encriptadas
    email VARCHAR(100) UNIQUE NOT NULL,
    nombre VARCHAR(50) NOT NULL,
    apellido VARCHAR(50) NOT NULL,
    telefono VARCHAR(15),
    fecha_registro DATETIME DEFAULT CURRENT_TIMESTAMP,
    ultimo_login DATETIME,
    activo BOOLEAN DEFAULT TRUE,
    FOREIGN KEY (id_rol) REFERENCES roles(id_rol),
    CONSTRAINT chk_email_valido CHECK (email LIKE '%@%.%')
);

-- Tabla de marcas de vehículos
CREATE TABLE marcas (
    id_marca INT PRIMARY KEY AUTO_INCREMENT,
    nombre VARCHAR(50) NOT NULL UNIQUE
);

-- Tabla de modelos de vehículos
CREATE TABLE modelos (
    id_modelo INT PRIMARY KEY AUTO_INCREMENT,
    id_marca INT NOT NULL,
    nombre VARCHAR(50) NOT NULL,
    tipo_combustible ENUM('gasolina', 'diésel', 'eléctrico', 'híbrido'),
    capacidad_pasajeros TINYINT NOT NULL,
    FOREIGN KEY (id_marca) REFERENCES marcas(id_marca),
    CONSTRAINT uc_modelo_marca UNIQUE (id_marca, nombre)
);

-- Tabla de vehículos
CREATE TABLE vehiculos (
    id_vehiculo INT PRIMARY KEY AUTO_INCREMENT,
    id_modelo INT NOT NULL,
    placa VARCHAR(15) NOT NULL UNIQUE,
    anio YEAR NOT NULL,
    color VARCHAR(30) NOT NULL,
    kilometraje INT NOT NULL DEFAULT 0,
    precio_diario DECIMAL(8,2) NOT NULL,
    estado ENUM('disponible', 'alquilado', 'mantenimiento') DEFAULT 'disponible',
    foto_principal VARCHAR(255),
    FOREIGN KEY (id_modelo) REFERENCES modelos(id_modelo),
    CONSTRAINT chk_precio_positivo CHECK (precio_diario > 0),
    CONSTRAINT chk_kilometraje_valido CHECK (kilometraje >= 0)
);

-- Tabla de alquileres
CREATE TABLE alquileres (
    id_alquiler INT PRIMARY KEY AUTO_INCREMENT,
    id_cliente INT NOT NULL,
    id_vehiculo INT NOT NULL,
    id_empleado INT, -- Empleado que gestionó el alquiler
    fecha_inicio DATETIME NOT NULL,
    fecha_fin DATETIME NOT NULL,
    costo_total DECIMAL(10,2) NOT NULL,
    estado ENUM('reservado', 'en_curso', 'finalizado', 'cancelado') NOT NULL,
    FOREIGN KEY (id_cliente) REFERENCES usuarios(id_usuario),
    FOREIGN KEY (id_vehiculo) REFERENCES vehiculos(id_vehiculo),
    FOREIGN KEY (id_empleado) REFERENCES usuarios(id_usuario),
    CONSTRAINT chk_fechas_validas CHECK (fecha_fin > fecha_inicio)
);

-- ==================== TABLAS DE SEGURIDAD ====================

-- Tabla para tokens de sesión (para autenticación desde Python)
CREATE TABLE sesiones (
    id_sesion INT PRIMARY KEY AUTO_INCREMENT,
    id_usuario INT NOT NULL,
    token VARCHAR(255) NOT NULL UNIQUE,
    fecha_creacion DATETIME DEFAULT CURRENT_TIMESTAMP,
    fecha_expiracion DATETIME NOT NULL,
    direccion_ip VARCHAR(45),
    activa BOOLEAN DEFAULT TRUE,
    FOREIGN KEY (id_usuario) REFERENCES usuarios(id_usuario)
);

-- Tabla de intentos fallidos de login
CREATE TABLE intentos_login (
    id_intento INT PRIMARY KEY AUTO_INCREMENT,
    username VARCHAR(50) NOT NULL,
    direccion_ip VARCHAR(45) NOT NULL,
    fecha_intento DATETIME DEFAULT CURRENT_TIMESTAMP,
    exitoso BOOLEAN DEFAULT FALSE
);

