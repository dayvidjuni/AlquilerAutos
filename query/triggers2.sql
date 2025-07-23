
use renta_autos_secure;
-- Para ver todos los triggers existentes
-- SHOW TRIGGERS FROM renta_autos_secure;

-- Para eliminar un trigger si es necesario
-- DROP TRIGGER IF EXISTS before_alquiler_insert;
/*
-- Trigger para Validar Inserción de Alquiler
DELIMITER $$
CREATE TRIGGER before_alquiler_insert
BEFORE INSERT ON alquileres
FOR EACH ROW
BEGIN
    DECLARE v_estado_vehiculo VARCHAR(20);
    DECLARE v_precio_diario DECIMAL(8,2);
    DECLARE v_id_empleado INT;
    
    -- Verificar disponibilidad del vehículo
    SELECT estado, precio_diario INTO v_estado_vehiculo, v_precio_diario
    FROM vehiculos WHERE id_vehiculo = NEW.id_vehiculo;
    
    IF v_estado_vehiculo != 'disponible' THEN
        SIGNAL SQLSTATE '45000' 
        SET MESSAGE_TEXT = 'No se puede alquilar el vehículo: no está disponible';
    END IF;
    
    -- Calcular costo total automáticamente
    SET NEW.costo_total = v_precio_diario * DATEDIFF(NEW.fecha_fin, NEW.fecha_inicio);
    
    -- Asignar empleado si es NULL (el que realiza la acción)
    IF NEW.id_empleado IS NULL THEN
        -- Buscar el último usuario activo en sesiones
        SELECT id_usuario INTO v_id_empleado FROM sesiones 
        WHERE activa = TRUE ORDER BY fecha_creacion DESC LIMIT 1;
        
        -- Asignar solo si encontró un usuario
        IF v_id_empleado IS NOT NULL THEN
            SET NEW.id_empleado = v_id_empleado;
        END IF;
    END IF;
END$$
DELIMITER ;*/


-- Trigger Post-Inserción de Alquiler
/*
DELIMITER $$
CREATE TRIGGER after_alquiler_insert
AFTER INSERT ON alquileres
FOR EACH ROW
BEGIN
    -- Cambiar estado del vehículo a 'alquilado'
    UPDATE vehiculos SET estado = 'alquilado' WHERE id_vehiculo = NEW.id_vehiculo;
    
    -- Registrar en sesiones/auditoría
    INSERT INTO sesiones (id_usuario, token, accion, tabla_afectada, id_registro_afectado, fecha_creacion, fecha_expiracion)
    SELECT 
        NEW.id_empleado,
        UUID(),
        CONCAT('Nuevo alquiler creado para vehículo ', NEW.id_vehiculo),
        'alquileres',
        NEW.id_alquiler,
        NOW(),
        NOW() + INTERVAL 1 YEAR;
END$$
DELIMITER ;*/

/*
-- Trigger para Validar Fechas
DELIMITER $$
CREATE TRIGGER before_alquiler_fechas
BEFORE INSERT ON alquileres
FOR EACH ROW
BEGIN
    -- Validar que la fecha fin sea mayor a fecha inicio
    IF NEW.fecha_fin <= NEW.fecha_inicio THEN
        SIGNAL SQLSTATE '45000' 
        SET MESSAGE_TEXT = 'La fecha de fin debe ser posterior a la fecha de inicio';
    END IF;
    
    -- Validar que no haya solapamiento con otros alquileres
    IF EXISTS (
        SELECT 1 FROM alquileres 
        WHERE id_vehiculo = NEW.id_vehiculo 
        AND estado IN ('reservado', 'en_curso')
        AND (
            (NEW.fecha_inicio BETWEEN fecha_inicio AND fecha_fin) OR
            (NEW.fecha_fin BETWEEN fecha_inicio AND fecha_fin) OR
            (fecha_inicio BETWEEN NEW.fecha_inicio AND NEW.fecha_fin)
        )
    ) THEN
        SIGNAL SQLSTATE '45000' 
        SET MESSAGE_TEXT = 'El vehículo ya está alquilado en ese período';
    END IF;
END$$
DELIMITER ;

-- Trigger de Actualización de Alquiler
DELIMITER $$
CREATE TRIGGER after_alquiler_update
AFTER UPDATE ON alquileres
FOR EACH ROW
BEGIN
    -- Si el alquiler se marca como finalizado o cancelado
    IF (OLD.estado = 'en_curso' OR OLD.estado = 'reservado') AND 
       (NEW.estado = 'finalizado' OR NEW.estado = 'cancelado') THEN
        
        -- Liberar el vehículo
        UPDATE vehiculos SET estado = 'disponible' WHERE id_vehiculo = NEW.id_vehiculo;
        
        -- Registrar devolución
        INSERT INTO sesiones (id_usuario, token, accion, tabla_afectada, id_registro_afectado, fecha_creacion, fecha_expiracion)
        SELECT 
            NEW.id_empleado,
            UUID(),
            CONCAT('Alquiler ', NEW.estado, ' para vehículo ', NEW.id_vehiculo),
            'alquileres',
            NEW.id_alquiler,
            NOW(),
            NOW() + INTERVAL 1 YEAR;
    END IF;
END$$
DELIMITER ;*/
/*
DELIMITER $$
CREATE TRIGGER before_alquiler_role_check
BEFORE INSERT ON alquileres
FOR EACH ROW
BEGIN
    DECLARE v_rol VARCHAR(20);
    
    SELECT r.nombre INTO v_rol 
    FROM usuarios u
    JOIN roles r ON u.id_rol = r.id_rol
    WHERE u.id_usuario = NEW.id_empleado;
    
    IF v_rol NOT IN ('empleado', 'admin') THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Solo empleados o administradores pueden crear alquileres';
    END IF;
END$$
DELIMITER ;*/