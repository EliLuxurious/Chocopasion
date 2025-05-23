-- Crear base de datos
CREATE DATABASE chocopasion;
USE chocopasion;

-- Tabla de productos
-- Tabla de productos
CREATE TABLE productos (
    id_producto INT AUTO_INCREMENT PRIMARY KEY,
    codigo VARCHAR(50) NOT NULL UNIQUE,
    nombre VARCHAR(100) NOT NULL,
    descripcion TEXT
);

-- Insertar productos con códigos y descripciones
INSERT INTO productos (codigo, nombre, descripcion) VALUES
('SAB_COCO', 'COCO', 'Cacao 60%, coco'),
('SAB_AGUA', 'AGUAYMANTO', 'Cacao 60%, aguaymanto'),
('SUB_CACAO', 'NIBS DE CACAO', 'Fragmentos de grano de cacao tostado'),
('SUB_CAFE', 'NIBS DE CAFÉ', 'Cacao 60%, café'),
('SAB_LECHE', 'LECHE', 'Cacao 60%, leche'),
('SAB_CAFELE', 'CAFÉ CON LECHE', 'Cacao 60%, leche, café'),
('OSC_BIT60', 'BITTER 60 %', '60% cacao'),
('OSC_BIT80', 'BITTER 80 %', '80% cacao'),
('OSC_BIT82', 'BITTER 82 %', '82% cacao'),
('OSC_BIT75', 'BITTER 75 %', '75% cacao'),
('SAB_MANI', 'MANI', 'Cacao 60%, maní'),
('SAB_CAMU', 'CAMU CAMU', 'Cacao 60%, camu camu'),
('PURO_100', 'PASTA 100 %', '100% cacao (para taza)'),
('DER_MANT', 'MANTECA', 'Grasa natural del cacao'),
('DER_POLVO', 'POLVO', 'Polvo de cacao'),
('SOL_CHUCHO', 'CHUPETE CHOCOLATE', 'Cacao 60%, molde en chupete'),
('BEB_MUCIL', 'BEBIDA DE MUCILAGO', 'Mucílago de cacao (liquido)'),
('SAB_SALAM', 'SAL AMAZÓNICO', 'Cacao 60%, sal amazónica'),
('SAB_MLECHE', 'MANI CON LECHE', 'Cacao 60%, maní, leche'),
('SAB_ARAND', 'ARANDANO', 'Cacao 60%, arandano'),
('SAB_NARAN', 'NARANJA', 'Cacao 60%, naranja'),
('OSC_PURO60', 'PURO 60 %', '60% cacao'),
('SAB_SALQUI', 'SAL Y QUINUA', 'Cacao 60%, sal, quinua'),
('SAB_LECHE45', 'LECHE 45%', 'Cacao 45%, leche'),
('SAB_PIÑA', 'PIÑA', 'Cacao 60%, piña'),
('PURO_SEL', 'CACAO SELECCIONADO', 'Granos de cacao seleccionados 100%'),
('SAB_BLANC', 'CHOCOLATE BLANCO', 'Manteca de cacao, leche, azúcar'),
('SUB_CASCA', 'CASCARILLA', 'Cáscara de grano de cacao tostado'),
('INS_TOSTADO', 'CACAO TOSTADO', 'Grano de cacao 100% tostado');

-- Tabla de presentaciones
CREATE TABLE presentaciones (
    id_presentacion INT AUTO_INCREMENT PRIMARY KEY,
    descripcion VARCHAR(20) NOT NULL
);

-- Tabla de producción
CREATE TABLE produccion (
    id_produccion INT AUTO_INCREMENT PRIMARY KEY,
    fecha DATE NOT NULL,
    id_producto INT NOT NULL,
    id_presentacion INT NOT NULL,
    cantidad INT NOT NULL,
    responsables TEXT,
    FOREIGN KEY (id_producto) REFERENCES productos(id_producto),
    FOREIGN KEY (id_presentacion) REFERENCES presentaciones(id_presentacion)
);

-- Insertar presentaciones
INSERT INTO presentaciones (descripcion) VALUES
('90 GR'),
('50 GR'),
('25 GR'),
('20 GR'),
('1 KG'),
('0.5 KG'),
('0.25 KG'),
('0.15 KG');


-- Tabla de usuarios
CREATE TABLE usuarios (
    id_usuario INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    apellido VARCHAR(100) NOT NULL,
    email VARCHAR(100) NOT NULL UNIQUE
);

-- Insertar usuarios de ejemplo
INSERT INTO usuarios (nombre, apellido, email) VALUES
('Elia', 'Aquino', 'elia.aquino@gmail.com'),
('Mariela', 'Hernadez', 'mariela@gmail.com'),
('Elia', 'Silva', 'elia.silva@gmail.com');