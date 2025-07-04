# Módulos de Ventas y Precios - Chocopasión

Este proyecto incluye dos módulos integrados para gestionar las ventas y precios del negocio de chocolates, siguiendo la estructura de base de datos con productos, presentaciones y precios vigentes.

## 📋 Módulos Incluidos

### 🛒 Módulo de Ventas
Gestiona las ventas individuales de productos con presentaciones específicas.

### 💰 Módulo de Precios  
Administra los precios de productos por presentación con vigencias configurables.

## 🎯 Funcionalidades Principales

### Módulo de Precios
- ✅ **Gestión de Precios**: Crear, editar y eliminar precios por producto/presentación
- ✅ **Vigencias**: Configurar fechas de inicio y fin para cada precio
- ✅ **Histórico de Precios**: Mantener registro de cambios de precios
- ✅ **Precios Vigentes**: Consulta automática del precio actual
- ✅ **Validaciones**: Control de fechas y solapamientos

### Módulo de Ventas  
- ✅ **Registro de Ventas**: Una venta = un producto + presentación + cantidad
- ✅ **Integración con Precios**: Obtención automática de precios vigentes
- ✅ **Cálculo Automático**: Total calculado automáticamente en BD
- ✅ **Búsqueda por Fechas**: Filtros de ventas por rango de fechas
- ✅ **Comprobantes**: Visualización e impresión de tickets

## 🗂️ Estructura de la Base de Datos

### Tabla `presentaciones`
```sql
id_presentacion (INT, PRIMARY KEY)
nombre (VARCHAR(100), UNIQUE)
descripcion (TEXT)
```

### Tabla `precios`
```sql
id_precio (INT, PRIMARY KEY)
id_producto (INT, FK → productos)
id_presentacion (INT, FK → presentaciones)  
precio_unitario (DECIMAL(10,2))
fecha_inicio (DATE)
fecha_fin (DATE, NULLABLE)
```

### Tabla `ventas`
```sql
id_venta (INT, PRIMARY KEY)
fecha (DATE)
id_producto (INT, FK → productos)
id_presentacion (INT, FK → presentaciones)
cantidad (INT, CHECK > 0)
precio_unitario (DECIMAL(10,2))
total (DECIMAL(10,2), CALCULATED)
```

## 🚀 Instalación y Configuración

### 1. Ejecutar Script SQL
```bash
mysql -u root -p chocopasion1 < sql_ventas.sql
```

### 2. Módulos Registrados Automáticamente
Los blueprints están registrados en `main.py`:
```python
app.register_blueprint(precios_bp, url_prefix="/precios")
app.register_blueprint(ventas_bp, url_prefix="/ventas")
```

### 3. Acceso a los Módulos
- **Precios**: `http://localhost:5000/precios/`
- **Ventas**: `http://localhost:5000/ventas/`
- Enlaces disponibles en el menú lateral

## 📁 Estructura de Archivos

```
modules/
├── precios/
│   ├── model.py          # Modelo de datos Precio
│   ├── repository.py     # Acceso a datos MySQL
│   ├── service.py        # Lógica de negocio
│   └── controller.py     # Rutas Flask
└── ventas/
    ├── model.py          # Modelo de datos Venta (simplificado)
    ├── repository.py     # Acceso a datos MySQL
    ├── service.py        # Lógica de negocio
    └── controller.py     # Rutas Flask

templates/
├── precios/
│   ├── index.html        # Lista de precios
│   ├── agregar.html      # Formulario nuevo precio
│   └── editar.html       # Formulario editar precio
└── ventas/
    ├── index.html        # Lista de ventas
    ├── agregar.html      # Formulario nueva venta
    └── ver.html          # Detalles de venta
```

## 🔄 Flujo de Trabajo

### 1. Configurar Precios
1. Ir a **Precios** → **Nuevo Precio**
2. Seleccionar producto y presentación
3. Establecer precio y vigencia
4. Guardar

### 2. Registrar Ventas
1. Ir a **Ventas** → **Nueva Venta**
2. Seleccionar fecha, producto y presentación
3. Ingresar cantidad
4. Obtener precio vigente automáticamente (o manual)
5. Guardar venta

### 3. Consultar Información
- **Precios**: Ver histórico y vigencias
- **Ventas**: Filtrar por fechas, ver detalles, imprimir

## 🛠️ Características Técnicas

### API Endpoints
- `/precios/api/precio-vigente` - Obtener precio vigente
- `/ventas/api/precio-vigente` - Consulta de precios para ventas

### Validaciones
- ✅ Fechas coherentes (inicio ≤ fin)
- ✅ Precios mayores a 0
- ✅ Cantidades positivas
- ✅ Productos y presentaciones válidos

### Características de UX
- 🎨 Interfaz moderna con Bootstrap 5
- 📱 Diseño responsive
- ⚡ Cálculos automáticos en tiempo real
- 🔍 Búsquedas y filtros intuitivos
- 🖨️ Impresión de comprobantes

## 🔮 Funcionalidades Futuras

### Precios
- [ ] Precios por volumen/descuentos
- [ ] Importación masiva de precios
- [ ] Alertas de vencimiento de precios
- [ ] Comparación de precios históricos

### Ventas
- [ ] Ventas múltiples (carrito)
- [ ] Integración con inventario
- [ ] Reportes de ventas
- [ ] Análisis de tendencias
- [ ] Facturación electrónica
- [ ] Devoluciones y cancelaciones

## 📊 Ventajas del Nuevo Modelo

1. **Flexibilidad**: Precios independientes por presentación
2. **Histórico**: Mantenimiento de cambios de precios
3. **Escalabilidad**: Fácil adición de nuevas presentaciones
4. **Integridad**: Relaciones consistentes en BD
5. **Automatización**: Cálculos automáticos y validaciones
6. **Trazabilidad**: Registro completo de transacciones

Este sistema proporciona una base sólida para la gestión comercial de Chocopasión con capacidad de crecimiento y adaptación a nuevas necesidades del negocio.
