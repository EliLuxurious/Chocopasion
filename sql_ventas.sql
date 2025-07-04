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

-- Insertar ventas de ejemplo
INSERT IGNORE INTO ventas (fecha, id_producto, id_presentacion, cantidad, precio_unitario) VALUES
('2025-07-01', 1, 1, 5, 15.50),
('2025-07-01', 1, 2, 3, 35.00),
('2025-07-02', 2, 1, 8, 18.00),
('2025-07-03', 1, 3, 2, 65.00);
