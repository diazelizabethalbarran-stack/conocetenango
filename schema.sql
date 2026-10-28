CREATE DATABASE IF NOT EXISTS conoce_tenango
  CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE conoce_tenango;

CREATE TABLE usuarios (
    id_usuario INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    correo VARCHAR(150) NOT NULL UNIQUE,
    telefono VARCHAR(20),
    password_hash VARCHAR(255) NOT NULL,
    rol ENUM('admin','usuario') NOT NULL DEFAULT 'usuario',
    creado_en TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE lugares (
    id_lugar INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(150) NOT NULL,
    categoria ENUM('Lugar turístico','Restaurante','Hotel') NOT NULL,
    descripcion TEXT,
    direccion VARCHAR(255),
    horario VARCHAR(150)
);

CREATE TABLE eventos (
    id_evento INT AUTO_INCREMENT PRIMARY KEY,
    id_lugar INT NOT NULL,
    nombre VARCHAR(150) NOT NULL,
    descripcion TEXT,
    fecha DATE,
    hora TIME,
    lugar VARCHAR(180),
    precio DECIMAL(10,2) NOT NULL DEFAULT 0.00,
    foreign key (id_lugar) 
		REFERENCES lugares(id_lugar)
        ON UPDATE CASCADE
        ON DELETE RESTRICT
);

CREATE TABLE reservaciones (
    id_reserva INT AUTO_INCREMENT PRIMARY KEY,
    id_usuario INT,
    id_lugar INT NOT NULL,
    nombre_cliente VARCHAR(100) NOT NULL,
    correo VARCHAR(150) NOT NULL,
    telefono VARCHAR(20) NOT NULL,
    fecha DATETIME NOT NULL,
    comentarios TEXT,
    estado ENUM('Pendiente','Confirmada','Cancelada') NOT NULL DEFAULT 'Pendiente',
    FOREIGN KEY (id_usuario) REFERENCES usuarios(id_usuario) ON UPDATE CASCADE ON DELETE SET NULL,
    FOREIGN KEY (id_lugar) REFERENCES lugares(id_lugar) ON UPDATE CASCADE ON DELETE RESTRICT
);

CREATE TABLE compras (
    id_compra INT AUTO_INCREMENT PRIMARY KEY,
    id_usuario INT NOT NULL,
    id_evento INT NOT NULL,
    cantidad INT NOT NULL DEFAULT 1,
    total DECIMAL(10,2) NOT NULL DEFAULT 0.00,
    estado ENUM('Registrada','Cancelada') NOT NULL DEFAULT 'Registrada',
    fecha_compra TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (id_usuario) REFERENCES usuarios(id_usuario) ON UPDATE CASCADE ON DELETE RESTRICT,
    FOREIGN KEY (id_evento) REFERENCES eventos(id_evento) ON UPDATE CASCADE ON DELETE RESTRICT,
    CHECK (cantidad > 0),
    CHECK (total >= 0)
);

CREATE TABLE mensajes_contacto (
    id_mensaje INT AUTO_INCREMENT PRIMARY KEY,
    id_usuario INT,
    nombre VARCHAR(100) NOT NULL,
    correo VARCHAR(150) NOT NULL,
    mensaje TEXT NOT NULL,
    estado ENUM('Pendiente','Atendido') NOT NULL DEFAULT 'Pendiente',
    fecha_envio TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (id_usuario) REFERENCES usuarios(id_usuario) ON DELETE SET NULL
);


USE conoce_tenango;

-- Puntos acumulados por cada usuario
CREATE TABLE IF NOT EXISTS puntos_usuarios (
    id_usuario INT PRIMARY KEY,
    puntos INT NOT NULL DEFAULT 0,
    FOREIGN KEY (id_usuario)
        REFERENCES usuarios(id_usuario)
        ON DELETE CASCADE
);

-- Puntos que otorga cada lugar
CREATE TABLE IF NOT EXISTS puntos_lugares (
    id_lugar INT PRIMARY KEY,
    puntos_visita INT NOT NULL DEFAULT 10,
    FOREIGN KEY (id_lugar)
        REFERENCES lugares(id_lugar)
        ON DELETE CASCADE
);

-- Registro de visitas validadas
CREATE TABLE IF NOT EXISTS visitas (
    id_visita INT AUTO_INCREMENT PRIMARY KEY,
    id_usuario INT NOT NULL,
    id_lugar INT NOT NULL,
    puntos_obtenidos INT NOT NULL,
    fecha_visita TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (id_usuario)
        REFERENCES usuarios(id_usuario),
    FOREIGN KEY (id_lugar)
        REFERENCES lugares(id_lugar)
);


USE conoce_tenango;

CREATE TABLE IF NOT EXISTS administradores (
    id_administrador INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    correo VARCHAR(150) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    creado_en TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);


USE conoce_tenango;

CREATE TABLE IF NOT EXISTS establecimientos (
    id_establecimiento INT AUTO_INCREMENT PRIMARY KEY,
    id_lugar INT NOT NULL UNIQUE,
    nombre VARCHAR(150) NOT NULL,
    correo VARCHAR(150) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    activo BOOLEAN NOT NULL DEFAULT TRUE,
    creado_en TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (id_lugar)
        REFERENCES lugares(id_lugar)
        ON UPDATE CASCADE
        ON DELETE RESTRICT
);

ALTER TABLE visitas
DROP INDEX uq_visita_usuario_lugar;