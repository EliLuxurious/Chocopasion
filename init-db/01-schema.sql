-- ══════════════════════════════════════════════════════════════════════════════
-- Chocopasión — Script de Inicialización de Base de Datos
-- Ejecutado automáticamente por Docker al crear el contenedor MySQL
-- ══════════════════════════════════════════════════════════════════════════════

-- Usar la base de datos creada por Docker vía MYSQL_DATABASE
USE chocopasion2;

-- ============================================
-- 1. Tablas básicas sin dependencias
-- ============================================

CREATE TABLE IF NOT EXISTS roles (
    id_rol INT AUTO_INCREMENT PRIMARY KEY,
    nombre_rol VARCHAR(50) NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS presentaciones (
    id_presentacion INT AUTO_INCREMENT PRIMARY KEY,
    descripcion VARCHAR(20) NOT NULL
);

CREATE TABLE IF NOT EXISTS productos (
    id_producto INT AUTO_INCREMENT PRIMARY KEY,
    codigo VARCHAR(50) NOT NULL UNIQUE,
    nombre VARCHAR(100) NOT NULL,
    descripcion TEXT
);

CREATE TABLE IF NOT EXISTS responsables (
    id_responsable INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    apellido VARCHAR(100) NOT NULL,
    email VARCHAR(100) NOT NULL UNIQUE
);

-- ============================================
-- 2. Tablas con dependencias
-- ============================================

CREATE TABLE IF NOT EXISTS usuarios (
    id_usuario INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    apellido VARCHAR(100) NOT NULL,
    email VARCHAR(100) NOT NULL UNIQUE,
    id_rol INT,
    contrasena VARCHAR(255) NOT NULL,
    FOREIGN KEY (id_rol) REFERENCES roles(id_rol)
);

CREATE TABLE IF NOT EXISTS produccion (
    id_produccion INT AUTO_INCREMENT PRIMARY KEY,
    fecha DATE NOT NULL,
    id_producto INT NOT NULL,
    id_presentacion INT NOT NULL,
    cantidad INT NOT NULL CHECK (cantidad > 0),
    FOREIGN KEY (id_producto) REFERENCES productos(id_producto),
    FOREIGN KEY (id_presentacion) REFERENCES presentaciones(id_presentacion)
);

CREATE TABLE IF NOT EXISTS produccion_responsable (
    id_produccion INT NOT NULL,
    id_responsable INT NOT NULL,
    PRIMARY KEY (id_produccion, id_responsable),
    FOREIGN KEY (id_produccion) REFERENCES produccion(id_produccion) ON DELETE CASCADE,
    FOREIGN KEY (id_responsable) REFERENCES responsables(id_responsable) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS precios (
    id_precio INT AUTO_INCREMENT PRIMARY KEY,
    id_producto INT NOT NULL,
    id_presentacion INT NOT NULL,
    precio_unitario DECIMAL(10,2) NOT NULL,
    FOREIGN KEY (id_producto) REFERENCES productos(id_producto),
    FOREIGN KEY (id_presentacion) REFERENCES presentaciones(id_presentacion)
);


-- ============================================
-- 3. Datos iniciales
-- ============================================

INSERT IGNORE INTO roles (nombre_rol) VALUES ('empleado'), ('administrador');

INSERT IGNORE INTO presentaciones (descripcion) VALUES
('90 GR'), ('50 GR'), ('25 GR'), ('20 GR'),
('1 KG'), ('0.5 KG'), ('0.25 KG'), ('0.15 KG'), ('UNIDAD');

INSERT IGNORE INTO productos (codigo, nombre, descripcion) VALUES
('SAB_COCO', 'COCO', 'Cacao 60%, coco'),
('SAB_AGUA', 'AGUAYMANTO', 'Cacao 60%, aguaymanto'),
('SUB_CACAO', 'NIBS DE CACAO', 'Fragmentos de grano de cacao tostado'),
('SUB_CAFE', 'NIBS DE CAFÉ', 'Cacao 60%, café'),
('SAB_LECHE', 'LECHE', 'Cacao 60%, leche'),
('SAB_CAFELE', 'CAFÉ CON LECHE', 'Cacao 60%, leche, café'),
('OSC_BIT60', 'BITTER 60%', '60% cacao'),
('OSC_BIT80', 'BITTER 80%', '80% cacao'),
('OSC_BIT82', 'BITTER 82%', '82% cacao'),
('OSC_BIT75', 'BITTER 75%', '75% cacao'),
('SAB_MANI', 'MANI', 'Cacao 60%, maní'),
('SAB_CAMU', 'CAMU CAMU', 'Cacao 60%, camu camu'),
('PURO_100', 'PASTA 100%', '100% cacao (para taza)'),
('DER_MANT', 'MANTECA', 'Grasa natural del cacao'),
('DER_POLVO', 'POLVO', 'Polvo de cacao'),
('SOL_CHUCHO', 'CHUPETE CHOCOLATE', 'Cacao 60%, molde en chupete'),
('BEB_MUCIL', 'BEBIDA DE MUCILAGO', 'Mucílago de cacao (liquido)'),
('SAB_SALAM', 'SAL AMAZÓNICO', 'Cacao 60%, sal amazónica'),
('SAB_MLECHE', 'MANI CON LECHE', 'Cacao 60%, maní, leche'),
('SAB_ARAND', 'ARANDANO', 'Cacao 60%, arandano'),
('SAB_NARAN', 'NARANJA', 'Cacao 60%, naranja'),
('OSC_PURO60', 'PURO 60%', '60% cacao'),
('SAB_SALQUI', 'SAL Y QUINUA', 'Cacao 60%, sal, quinua'),
('SAB_LECHE45', 'LECHE 45%', 'Cacao 45%, leche'),
('SAB_PIÑA', 'PIÑA', 'Cacao 60%, piña'),
('PURO_SEL', 'CACAO SELECCIONADO', 'Granos de cacao seleccionados 100%'),
('SAB_BLANC', 'CHOCOLATE BLANCO', 'Manteca de cacao, leche, azúcar'),
('SUB_CASCA', 'CASCARILLA', 'Cáscara de grano de cacao tostado'),
('INS_TOSTADO', 'CACAO TOSTADO', 'Grano de cacao 100% tostado');

INSERT IGNORE INTO responsables (nombre, apellido, email) VALUES
('ELIA', 'AQUINO', 'elia.aquino@chocopasion.com'),
('ELIA', 'SILVA', 'elia.silva@chocopasion.com'),
('DARWIN', 'AQUINO', 'darwin.aquino@chocopasion.com'),
('JACKELIN', 'AGUIRRE', 'jackelin.aguirre@chocopasion.com'),
('GELEN', 'MANYA', 'gelen.manya@chocopasion.com'),
('ELENA', 'CASTRO', 'elena.castro@chocopasion.com'),
('DENIS', 'POLINAR', 'denis.polinar@chocopasion.com'),
('MARIELA', 'SILVA', 'mariela.silva@chocopasion.com'),
('YONALA', 'GONZALES', 'yonala.castro@chocopasion.com');

INSERT IGNORE INTO usuarios (nombre, apellido, email, id_rol, contrasena) VALUES
('Empleado', 'Stefan', 'empleado@gmail.com', 1, '123456789'),
('Administrador', 'Helena', 'admin@gmail.com', 2, '987654321');

INSERT IGNORE INTO precios (id_producto, id_presentacion, precio_unitario) VALUES
(1,1,14),(1,2,8),(1,3,5),(1,4,3),
(2,1,14),(2,2,8),(2,3,5),(2,4,3),
(3,1,14),(3,2,8),(3,3,5),(3,4,3),
(4,1,14),(4,2,8),(4,3,5),(4,4,3),
(5,1,14),(5,2,8),(5,3,5),(5,4,3),
(6,1,14),(6,2,8),(6,3,5),(6,4,3),
(7,1,14),(7,2,8),(7,3,5),(7,4,3),
(8,1,14),(8,2,8),(8,3,5),(8,4,3),
(9,1,14),(9,2,8),(9,3,5),(9,4,3),
(10,1,14),(10,2,8),(10,3,5),(10,4,3),
(11,1,14),(11,2,8),(11,3,5),(11,4,3),
(12,1,14),(12,2,8),(12,3,5),(12,4,3),
(13,1,14),(13,2,8),(13,3,5),(13,4,3),
(14,1,14),(14,2,8),(14,3,5),(14,4,3),
(15,1,14),(15,2,8),(15,3,5),(15,4,3),
(16,1,14),(16,2,8),(16,3,5),(16,4,3),
(17,1,14),(17,2,8),(17,3,5),(17,4,3),
(18,1,14),(18,2,8),(18,3,5),(18,4,3),
(19,1,14),(19,2,8),(19,3,5),(19,4,3),
(20,1,14),(20,2,8),(20,3,5),(20,4,3),
(21,6,35),(21,7,20),(21,5,65),
(22,6,25),(22,5,45),
(23,7,25),(23,8,15),
(24,9,2),(25,9,3),
(26,6,20),(26,5,35),
(27,6,22),(27,5,40),
(28,7,15),(28,6,25);
