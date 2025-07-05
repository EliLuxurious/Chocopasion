-- ============================================
-- Script SQL para el módulo de Ventas y Precios
-- ============================================

-- Tabla de presentaciones (si no existe)
CREATE TABLE IF NOT EXISTS presentaciones (
    id_presentacion INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL UNIQUE,
    descripcion TEXT,
    INDEX idx_nombre (nombre)
);

-- Tabla de precios por producto y presentación (sin fechas)
CREATE TABLE IF NOT EXISTS precios (
    id_precio INT AUTO_INCREMENT PRIMARY KEY,
    id_producto INT NOT NULL,
    id_presentacion INT NOT NULL,
    precio_unitario DECIMAL(10,2) NOT NULL,
    FOREIGN KEY (id_producto) REFERENCES productos(id_producto),
    FOREIGN KEY (id_presentacion) REFERENCES presentaciones(id_presentacion),
    UNIQUE (id_producto, id_presentacion),
    INDEX idx_producto_presentacion (id_producto, id_presentacion)
);

-- Tabla de ventas (nueva estructura)
CREATE TABLE IF NOT EXISTS ventas (
    id_venta INT AUTO_INCREMENT PRIMARY KEY,
    fecha DATE NOT NULL,
    id_producto INT NOT NULL,
    id_presentacion INT NOT NULL,
    cantidad INT NOT NULL CHECK (cantidad > 0),
    precio_unitario DECIMAL(10,2) NOT NULL,
    total DECIMAL(10,2) GENERATED ALWAYS AS (cantidad * precio_unitario) STORED,
    FOREIGN KEY (id_producto) REFERENCES productos(id_producto),
    FOREIGN KEY (id_presentacion) REFERENCES presentaciones(id_presentacion),
    INDEX idx_fecha (fecha),
    INDEX idx_producto (id_producto),
    INDEX idx_presentacion (id_presentacion)
);

-- Insertar presentaciones de ejemplo
INSERT IGNORE INTO presentaciones (nombre, descripcion) VALUES
('100g', 'Presentación de 100 gramos'),
('250g', 'Presentación de 250 gramos'),
('500g', 'Presentación de 500 gramos'),
('1kg', 'Presentación de 1 kilogramo'),
('Caja 12 unidades', 'Caja con 12 unidades individuales'),
('Bolsa familiar', 'Bolsa familiar grande');

-- Insertar precios de ejemplo (ajustar según productos existentes)
-- Nota: Estos datos dependen de que existan productos en la tabla productos
INSERT IGNORE INTO precios (id_producto, id_presentacion, precio_unitario) VALUES
(1, 1, 15.50),  -- Producto 1, Presentación 100g
(1, 2, 35.00),  -- Producto 1, Presentación 250g
(1, 3, 65.00),  -- Producto 1, Presentación 500g
(2, 1, 18.00),  -- Producto 2, Presentación 100g
(2, 2, 42.00);  -- Producto 2, Presentación 250g

-- Insertar ventas de ejemplo para el dashboard
INSERT IGNORE INTO ventas (fecha, id_producto, id_presentacion, cantidad, precio_unitario) VALUES
-- Ventas del mes actual
('2024-12-01', 1, 1, 10, 14.00),
('2024-12-01', 2, 2, 15, 8.00),
('2024-12-01', 3, 3, 20, 5.00),
('2024-12-02', 1, 2, 12, 8.00),
('2024-12-02', 4, 1, 8, 14.00),
('2024-12-02', 5, 4, 25, 3.00),
('2024-12-03', 2, 1, 6, 14.00),
('2024-12-03', 3, 2, 18, 8.00),
('2024-12-03', 6, 3, 22, 5.00),
('2024-12-04', 1, 3, 14, 5.00),
('2024-12-04', 7, 1, 9, 14.00),
('2024-12-04', 8, 2, 16, 8.00),
('2024-12-05', 2, 4, 30, 3.00),
('2024-12-05', 3, 1, 11, 14.00),
('2024-12-05', 9, 3, 19, 5.00),
('2024-12-06', 4, 2, 13, 8.00),
('2024-12-06', 5, 1, 7, 14.00),
('2024-12-06', 10, 4, 28, 3.00),
('2024-12-07', 1, 1, 15, 14.00),
('2024-12-07', 6, 2, 17, 8.00),
('2024-12-07', 7, 3, 21, 5.00),
('2024-12-08', 2, 1, 9, 14.00),
('2024-12-08', 8, 4, 24, 3.00),
('2024-12-08', 3, 2, 12, 8.00),
('2024-12-09', 4, 3, 18, 5.00),
('2024-12-09', 9, 1, 10, 14.00),
('2024-12-09', 5, 2, 14, 8.00),
('2024-12-10', 1, 4, 32, 3.00),
('2024-12-10', 10, 1, 8, 14.00),
('2024-12-10', 6, 3, 16, 5.00),
('2024-12-11', 2, 2, 11, 8.00),
('2024-12-11', 7, 1, 13, 14.00),
('2024-12-11', 8, 4, 26, 3.00),
('2024-12-12', 3, 3, 20, 5.00),
('2024-12-12', 9, 2, 15, 8.00),
('2024-12-12', 4, 1, 7, 14.00),
('2024-12-13', 5, 4, 29, 3.00),
('2024-12-13', 10, 3, 17, 5.00),
('2024-12-13', 1, 2, 12, 8.00),
('2024-12-14', 6, 1, 9, 14.00),
('2024-12-14', 7, 4, 23, 3.00),
('2024-12-14', 2, 3, 19, 5.00),
('2024-12-15', 8, 2, 14, 8.00),
('2024-12-15', 3, 1, 11, 14.00),
('2024-12-15', 9, 4, 27, 3.00),
-- Ventas de enero 2025
('2025-01-01', 1, 1, 18, 14.00),
('2025-01-01', 2, 2, 22, 8.00),
('2025-01-01', 3, 3, 25, 5.00),
('2025-01-02', 4, 1, 12, 14.00),
('2025-01-02', 5, 4, 35, 3.00),
('2025-01-02', 6, 2, 16, 8.00),
('2025-01-03', 1, 3, 20, 5.00),
('2025-01-03', 7, 1, 14, 14.00),
('2025-01-03', 8, 4, 28, 3.00),
('2025-01-04', 2, 2, 19, 8.00),
('2025-01-04', 9, 3, 23, 5.00),
('2025-01-04', 10, 1, 10, 14.00),
-- Ventas recientes (últimos 7 días)
('2025-07-01', 1, 1, 25, 14.00),
('2025-07-01', 2, 2, 30, 8.00),
('2025-07-01', 3, 3, 35, 5.00),
('2025-07-02', 1, 2, 20, 8.00),
('2025-07-02', 4, 1, 15, 14.00),
('2025-07-02', 5, 4, 40, 3.00),
('2025-07-03', 2, 1, 12, 14.00),
('2025-07-03', 6, 3, 28, 5.00),
('2025-07-03', 7, 2, 22, 8.00),
('2025-07-04', 1, 3, 18, 5.00),
('2025-07-04', 8, 1, 16, 14.00),
('2025-07-04', 3, 4, 45, 3.00);
