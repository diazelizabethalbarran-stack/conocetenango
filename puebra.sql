USE conoce_tenango;

SELECT id_evento, nombre, fecha, precio
FROM eventos;

USE conoce_tenango;

SELECT id_lugar, nombre, latitud, longitud
FROM lugares;

USE conoce_tenango;

INSERT INTO lugares
(nombre, categoria, descripcion, direccion, telefono, horario)
VALUES
(
    'Parque Humboldt',
    'Lugar turístico',
    'Parque para visitar en Tenango del Valle.',
    'Centro de Tenango del Valle',
    NULL,
    'Horario por confirmar'
);

USE conoce_tenango;

INSERT INTO eventos
(id_lugar, nombre, descripcion, fecha, hora, lugar, precio)
VALUES
(
    1,
    'Festival Cultural del Quinto Sol',
    'Evento cultural relacionado con la historia y las tradiciones de Tenango del Valle.',
    '2026-11-15',
    '10:00:00',
    'Parque Humboldt, Tenango del Valle',
    50.00
);

USE conoce_tenango;

SELECT DATABASE();

SELECT id_usuario, nombre, correo, password_hash
FROM usuarios;

USE conoce_tenango;

SELECT * FROM usuarios;
SELECT * FROM lugares;
SELECT * FROM eventos;
SELECT * FROM compras;
SELECT * FROM mensajes_contacto;
SELECT * FROM reservaciones;


USE conoce_tenango;

ALTER TABLE lugares
ADD COLUMN latitud DECIMAL(10,7) NULL,
ADD COLUMN longitud DECIMAL(10,7) NULL;
USE conoce_tenango;

DESCRIBE lugares;

USE conoce_tenango;

UPDATE lugares
SET latitud = 19.10330,
    longitud = -99.59470
WHERE id_lugar = 1
  AND nombre = 'Parque Humboldt';
  
  USE conoce_tenango;

ALTER TABLE reservaciones
ADD COLUMN fecha_salida DATETIME NULL,
ADD COLUMN personas INT NOT NULL DEFAULT 1,
ADD COLUMN fecha_entrada DATETIME NULL;

USE conoce_tenango;
DESCRIBE reservaciones;
  
  USE conoce_tenango;

SELECT
    id_reserva,
    nombre_cliente,
    correo,
    fecha_entrada,
    fecha_salida,
    personas,
    estado
FROM reservaciones
ORDER BY id_reserva DESC;

USE conoce_tenango;

SELECT DATABASE();

SELECT *
FROM reservaciones
ORDER BY id_reserva DESC;

USE conoce_tenango;

DESCRIBE lugares;



USE conoce_tenango;

INSERT INTO lugares
(nombre, categoria, descripcion, direccion, horario, latitud, longitud)

SELECT n.nombre, n.categoria, n.descripcion, n.direccion,
       n.horario, n.latitud, n.longitud
FROM (
    SELECT 'Zona Arqueológica de Teotenango' AS nombre,
           'Lugar turístico' AS categoria,
           'Zona arqueológica con vestigios de la cultura matlatzinca.' AS descripcion,
           'Cerro Tetépetl, Tenango del Valle' AS direccion,
           'Consultar horario oficial' AS horario,
           NULL AS latitud, NULL AS longitud

    UNION ALL SELECT 'Museo Arqueológico Dr. Román Piña Chan',
           'Lugar turístico',
           'Museo con piezas arqueológicas de la región.',
           'Cerca de la Zona Arqueológica de Teotenango',
           'Consultar horario oficial', NULL, NULL

    UNION ALL SELECT 'Parroquia de la Asunción de María',
           'Lugar turístico',
           'Templo histórico del centro de Tenango del Valle.',
           'Centro de Tenango del Valle', 'Por confirmar', NULL, NULL

    UNION ALL SELECT 'Teatro Municipal Abundio Gómez',
           'Lugar turístico',
           'Recinto cultural para actividades artísticas.',
           'Centro de Tenango del Valle', 'Según eventos', NULL, NULL

    UNION ALL SELECT 'Kiosco Municipal',
           'Lugar turístico',
           'Kiosco ubicado en la plaza principal.',
           'Plaza principal de Tenango del Valle', 'Acceso público', NULL, NULL

    UNION ALL SELECT 'Templo del Calvario',
           'Lugar turístico',
           'Templo de interés cultural y religioso.',
           'Tenango del Valle, Estado de México', 'Por confirmar', NULL, NULL

    UNION ALL SELECT 'Centro Cultural León Guzmán',
           'Lugar turístico',
           'Espacio dedicado a actividades culturales.',
           'Tenango del Valle, Estado de México', 'Por confirmar', NULL, NULL

    UNION ALL SELECT 'Escuela Primaria Benito Juárez',
           'Lugar turístico',
           'Institución educativa de la comunidad.',
           'Centro de Tenango del Valle', 'Horario escolar', NULL, NULL

    UNION ALL SELECT 'Capilla de la Virgen de Guadalupe',
           'Lugar turístico',
           'Capilla de interés religioso para la comunidad.',
           'Tenango del Valle, Estado de México', 'Por confirmar', NULL, NULL

    UNION ALL SELECT 'Capilla de San Salvador',
           'Lugar turístico',
           'Capilla local de interés cultural y religioso.',
           'Tenango del Valle, Estado de México', 'Por confirmar', NULL, NULL

    UNION ALL SELECT 'Parque Ecológico León Guzmán',
           'Lugar turístico',
           'Espacio al aire libre para disfrutar de la naturaleza.',
           'Tenango del Valle, Estado de México', 'Por confirmar', NULL, NULL

    UNION ALL SELECT 'Restaurante Bar Xoly',
           'Restaurante', 'Establecimiento de comida y bebidas.',
           'Tenango del Valle, Estado de México', 'Por confirmar', NULL, NULL

    UNION ALL SELECT 'Las Piñas',
           'Restaurante', 'Establecimiento de comida.',
           'Tenango del Valle, Estado de México', 'Por confirmar', NULL, NULL

    UNION ALL SELECT 'Restaurante Laurent''s',
           'Restaurante', 'Restaurante para disfrutar de alimentos.',
           'Tenango del Valle, Estado de México', 'Por confirmar', NULL, NULL

    UNION ALL SELECT 'Don Regio Cortes & Grill',
           'Restaurante', 'Restaurante de cortes y comida a la parrilla.',
           'Tenango del Valle, Estado de México', 'Por confirmar', NULL, NULL

    UNION ALL SELECT 'CALIFORNIA COUNTRY',
           'Restaurante', 'Establecimiento de comida.',
           'Tenango del Valle, Estado de México', 'Por confirmar', NULL, NULL

    UNION ALL SELECT 'La Niña de las Hamburguesas',
           'Restaurante', 'Establecimiento especializado en hamburguesas.',
           'Tenango del Valle, Estado de México', 'Por confirmar', NULL, NULL

    UNION ALL SELECT 'Valle Rustico',
           'Restaurante', 'Establecimiento de comida.',
           'Tenango del Valle, Estado de México', 'Por confirmar', NULL, NULL

    UNION ALL SELECT 'Hotel Boutique Roble del Valle',
           'Hotel', 'Establecimiento de hospedaje.',
           'Tenango del Valle, Estado de México',
           'Consultar disponibilidad', NULL, NULL

    UNION ALL SELECT 'Hotel Room',
           'Hotel', 'Establecimiento de hospedaje.',
           'Tenango del Valle, Estado de México',
           'Consultar disponibilidad', NULL, NULL

    UNION ALL SELECT 'Suites San José',
           'Hotel', 'Establecimiento de hospedaje tipo suites.',
           'Tenango del Valle, Estado de México',
           'Consultar disponibilidad', NULL, NULL

    UNION ALL SELECT 'Hotel Quinto Sol',
           'Hotel', 'Establecimiento de hospedaje.',
           'Tenango del Valle, Estado de México',
           'Consultar disponibilidad', NULL, NULL

    UNION ALL SELECT 'Hotel & Villas La Paloma',
           'Hotel', 'Establecimiento de hospedaje.',
           'Tenango del Valle, Estado de México',
           'Consultar disponibilidad', NULL, NULL

    UNION ALL SELECT 'Hotel Linda Vista',
           'Hotel', 'Establecimiento de hospedaje.',
           'Tenango del Valle, Estado de México',
           'Consultar disponibilidad', NULL, NULL

    UNION ALL SELECT 'Hotel Cataleya',
           'Hotel', 'Establecimiento de hospedaje.',
           'Tenango del Valle, Estado de México',
           'Consultar disponibilidad', NULL, NULL
) AS n
WHERE NOT EXISTS (
    SELECT 1
    FROM lugares AS l
    WHERE LOWER(TRIM(l.nombre)) = LOWER(TRIM(n.nombre))
);

SELECT id_lugar, nombre, categoria
FROM lugares
ORDER BY id_lugar;


USE conoce_tenango;

DESCRIBE mensajes_contacto;

USE conoce_tenango;
DESCRIBE eventos;

SELECT * FROM eventos;

SELECT id_evento, id_lugar, nombre, descripcion, fecha, hora, lugar, precio
FROM eventos

USE conoce_tenango;

DESCRIBE compras;

USE conoce_tenango;

ALTER TABLE compras
ADD COLUMN token_qr VARCHAR(64) UNIQUE NULL;

USE conoce_tenango;

DESCRIBE usuarios;
DESCRIBE lugares;


USE conoce_tenango;

INSERT IGNORE INTO puntos_lugares (id_lugar, puntos_visita)
SELECT id_lugar,
       CASE
           WHEN categoria = 'Hotel' THEN 30
           WHEN categoria = 'Restaurante' THEN 20
           ELSE 10
       END
FROM lugares;

-- Crear el registro de puntos para usuarios existentes
INSERT IGNORE INTO puntos_usuarios (id_usuario, puntos)
SELECT id_usuario, 0
FROM usuarios;

USE conoce_tenango;

INSERT INTO administradores (nombre, correo, password_hash)
SELECT nombre, correo, password_hash
FROM usuarios
WHERE rol = 'admin'
  AND correo NOT IN (
      SELECT correo FROM (
          SELECT correo FROM administradores
      ) AS admins_existentes
  );

USE conoce_tenango;

SHOW COLUMNS FROM usuarios;
SHOW COLUMNS FROM lugares;
SHOW COLUMNS FROM puntos_usuarios;
SHOW COLUMNS FROM puntos_lugares;
SHOW COLUMNS FROM visitas;

SHOW COLUMNS FROM usuarios LIKE 'qr_token';

USE conoce_tenango;

SELECT * FROM puntos_usuarios;
SELECT * FROM puntos_lugares;
SELECT * FROM visitas;

USE conoce_tenango;

UPDATE usuarios
SET qr_token = REPLACE(UUID(), '-', '')
WHERE qr_token IS NULL OR qr_token = '';

USE conoce_tenango;
SHOW COLUMNS FROM compras;

SHOW CREATE TABLE visitas;

SHOW INDEX FROM visitas;

USE conoce_tenango;

SELECT
    CONSTRAINT_NAME,
    COLUMN_NAME,
    REFERENCED_TABLE_NAME,
    REFERENCED_COLUMN_NAME
FROM information_schema.KEY_COLUMN_USAGE
WHERE TABLE_SCHEMA = 'conoce_tenango'
  AND TABLE_NAME = 'visitas'
  AND REFERENCED_TABLE_NAME IS NOT NULL;
  
  SHOW CREATE TABLE visitas;
  
  USE conoce_tenango;

SELECT
    CONSTRAINT_NAME,
    TABLE_NAME,
    COLUMN_NAME,
    REFERENCED_TABLE_NAME,
    REFERENCED_COLUMN_NAME
FROM information_schema.KEY_COLUMN_USAGE
WHERE CONSTRAINT_SCHEMA = 'conoce_tenango'
  AND TABLE_NAME = 'visitas'
  AND CONSTRAINT_NAME = 'uq_visita_usuario_lugar';
  
  SHOW CREATE TABLE visitas;
  
  USE conoce_tenango;

ALTER TABLE visitas
DROP INDEX uq_visita_usuario_lugar;

SHOW INDEX FROM visitas;

USE conoce_tenango;

ALTER TABLE visitas
DROP INDEX uq_visita_usuario_lugar;

USE conoce_tenango;

SELECT
    TABLE_NAME,
    CONSTRAINT_NAME,
    COLUMN_NAME,
    REFERENCED_TABLE_NAME,
    REFERENCED_COLUMN_NAME
FROM information_schema.KEY_COLUMN_USAGE
WHERE CONSTRAINT_SCHEMA = 'conoce_tenango'
  AND (
      (TABLE_NAME = 'visitas'
       AND COLUMN_NAME IN ('id_usuario', 'id_lugar'))
      OR
      (REFERENCED_TABLE_NAME = 'visitas')
  );
  
  SHOW CREATE TABLE visitas;
  
  ALTER TABLE visitas
DROP FOREIGN KEY visitas_ibfk_1;

ALTER TABLE visitas
DROP INDEX uq_visita_usuario_lugar,
ADD INDEX idx_visitas_usuario (id_usuario);

ALTER TABLE visitas
ADD CONSTRAINT visitas_ibfk_1
FOREIGN KEY (id_usuario)
REFERENCES usuarios(id_usuario);

SHOW INDEX FROM visitas;

SHOW CREATE TABLE visitas;
SELECT * FROM puntos_lugares;

SELECT pl.id_lugar, l.nombre, pl.puntos_visita
FROM puntos_lugares pl
JOIN lugares l ON l.id_lugar = pl.id_lugar
WHERE l.nombre = 'CALIFORNIA COUNTRY';

USE conoce_tenango;

SHOW TABLES;

DESCRIBE visitas;
DESCRIBE puntos_usuarios;
DESCRIBE usuarios;
DESCRIBE establecimientos;


USE conoce_tenango;

DESCRIBE visitas;

DESCRIBE puntos_usuarios;

DESCRIBE usuarios;
