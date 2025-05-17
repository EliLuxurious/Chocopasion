-- Crear la base de datos si no existe
CREATE DATABASE IF NOT EXISTS chocopasion;

-- Usar la base de datos
USE chocopasion;

-- Crear la tabla de producción
CREATE TABLE IF NOT EXISTS produccion (
    id INT PRIMARY KEY AUTO_INCREMENT,
    fecha DATE,
    codigo VARCHAR(50),
    producto VARCHAR(100),
    presentacion VARCHAR(50),
    cantidad INT,
    unidad VARCHAR(20),
    responsables TEXT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci; 