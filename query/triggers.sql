use renta_autos_secure;
-- Primero, ampliamos la tabla sesiones para registrar actividades
ALTER TABLE sesiones 
ADD COLUMN accion VARCHAR(255) AFTER token,
ADD COLUMN tabla_afectada VARCHAR(50) AFTER accion,
ADD COLUMN id_registro_afectado INT AFTER tabla_afectada;

-- Trigger para registrar cambios en vehículos
DELIMITER $$
CREATE TRIGGER audit_vehiculos_update
AFTER UPDATE ON vehiculos
FOR EACH ROW
BEGIN
    DECLARE v_usuario_id INT;
    
    -- Obtener ID de usuario activo (simplificado)
    SELECT id_usuario INTO v_usuario_id FROM sesiones 
    WHERE activa = TRUE ORDER BY fecha_creacion DESC LIMIT 1;
    
    -- Registrar cambios importantes
    IF OLD.precio_diario <> NEW.precio_diario THEN
        INSERT INTO sesiones (id_usuario, token, accion, tabla_afectada, id_registro_afectado, fecha_creacion, fecha_expiracion)
        VALUES (
            v_usuario_id,
            UUID(), -- Generamos un token único para cada registro
            CONCAT('Cambio de precio de $', OLD.precio_diario, ' a $', NEW.precio_diario),
            'vehiculos',
            NEW.id_vehiculo,
            NOW(),
            NOW() + INTERVAL 1 YEAR
        );
    END IF;
    
    IF OLD.estado <> NEW.estado THEN
        INSERT INTO sesiones (id_usuario, token, accion, tabla_afectada, id_registro_afectado, fecha_creacion, fecha_expiracion)
        VALUES (
            v_usuario_id,
            UUID(),
            CONCAT('Cambio de estado de "', OLD.estado, '" a "', NEW.estado, '"'),
            'vehiculos',
            NEW.id_vehiculo,
            NOW(),
            NOW() + INTERVAL 1 YEAR
        );
    END IF;
END$$
DELIMITER ;

-- Trigger para registrar cambios en alquileres
DELIMITER $$
CREATE TRIGGER audit_alquileres_update
AFTER UPDATE ON alquileres
FOR EACH ROW
BEGIN
    DECLARE v_usuario_id INT;
    
    SELECT id_usuario INTO v_usuario_id FROM sesiones 
    WHERE activa = TRUE ORDER BY fecha_creacion DESC LIMIT 1;
    
    IF OLD.estado <> NEW.estado THEN
        INSERT INTO sesiones (id_usuario, token, accion, tabla_afectada, id_registro_afectado, fecha_creacion, fecha_expiracion)
        VALUES (
            v_usuario_id,
            UUID(),
            CONCAT('Cambio de estado de alquiler de "', OLD.estado, '" a "', NEW.estado, '"'),
            'alquileres',
            NEW.id_alquiler,
            NOW(),
            NOW() + INTERVAL 1 YEAR
        );
    END IF;
    
    IF OLD.costo_total <> NEW.costo_total THEN
        INSERT INTO sesiones (id_usuario, token, accion, tabla_afectada, id_registro_afectado, fecha_creacion, fecha_expiracion)
        VALUES (
            v_usuario_id,
            UUID(),
            CONCAT('Ajuste de costo de $', OLD.costo_total, ' a $', NEW.costo_total),
            'alquileres',
            NEW.id_alquiler,
            NOW(),
            NOW() + INTERVAL 1 YEAR
        );
    END IF;
END$$
DELIMITER ;