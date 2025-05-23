-- Crear base de datos
CREATE DATABASE chocopasion;
USE chocopasion;

-- Tabla de productos
CREATE TABLE productos (
    id_producto INT AUTO_INCREMENT PRIMARY KEY,
    codigo VARCHAR(50) NOT NULL UNIQUE,
    nombre VARCHAR(100) NOT NULL
);

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

-- Insertar productos con códigos
INSERT INTO productos (codigo, nombre) VALUES
('SAB_COCO', 'COCO'),
('SAB_AGUA', 'AGUAYMANTO'),
('SUB_CACAO', 'NIBS DE CACAO'),
('SUB_CAFE', 'NIBS DE CAFÉ'),
('SAB_LECHE', 'LECHE'),
('SAB_CAFELE', 'CAFÉ CON LECHE'),
('OSC_BIT60', 'BITTER 60 %'),
('OSC_BIT80', 'BITTER 80 %'),
('OSC_BIT82', 'BITTER 82 %'),
('OSC_BIT75', 'BITTER 75 %'),
('SAB_MANI', 'MANI'),
('SAB_CAMU', 'CAMU CAMU'),
('PURO_100', 'PASTA 100 %'),
('DER_MANT', 'MANTECA'),
('DER_POLVO', 'POLVO'),
('SOL_CHUCHO', 'CHUPETE CHOCOLATE'),
('BEB_MUCIL', 'BEBIDA DE MUCILAGO'),
('SAB_SALAM', 'SAL AMAZÓNICO'),
('SAB_MLECHE', 'MANI CON LECHE'),
('SAB_ARAND', 'ARANDANO'),
('SAB_NARAN', 'NARANJA'),
('OSC_PURO60', 'PURO 60 %'),
('SAB_SALQUI', 'SAL Y QUINUA'),
('SAB_LECHE45', 'LECHE 45%'),
('SAB_PIÑA', 'PIÑA'),
('PURO_SEL', 'CACAO SELECCIONADO'),
('SAB_BLANC', 'CHOCOLATE BLANCO'),
('SUB_CASCA', 'CASCARILLA'),
('INS_TOSTADO', 'CACAO TOSTADO');

-- Crear tabla de roles
CREATE TABLE roles (
    id_rol INT AUTO_INCREMENT PRIMARY KEY,
    nombre_rol VARCHAR(50) NOT NULL UNIQUE
);

-- Insertar roles de ejemplo
INSERT INTO roles (nombre_rol) VALUES
('empleado'),
('administrador');

-- Tabla de usuarios
CREATE TABLE usuarios (
    id_usuario INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    apellido VARCHAR(100) NOT NULL,
    email VARCHAR(100) NOT NULL UNIQUE
);

-- Modificar la tabla de usuarios para incluir la referencia a roles
ALTER TABLE usuarios
ADD COLUMN id_rol INT,
ADD FOREIGN KEY (id_rol) REFERENCES roles(id_rol);

-- Insertar usuarios de ejemplo con roles
INSERT INTO usuarios (nombre, apellido, email, id_rol, contraseña) VALUES
('Empleado', 'Aquino', 'empleado@gmail.com', 1, 'contraseña_empleado'), -- 1 es el id_rol para 'empleado'
('Administrador', 'Hernadez', 'admin@gmail.com', 2, 'contraseña_admin'); -- 2 es el id_rol para 'administrador'
