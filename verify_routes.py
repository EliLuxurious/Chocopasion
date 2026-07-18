import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from infrastructure.database import app, conectar

print("=== INICIANDO PRUEBAS DE RUTAS ===")

client = app.test_client()

# 1. Probar ruta de Login (GET)
print("Probando GET /login...")
response = client.get('/login')
assert response.status_code == 200, f"Error en GET /login: {response.status_code}"
print("✅ GET /login exitoso (200)")

# 2. Probar Login de Administrador
print("Probando login de administrador...")
response = client.post('/login', data={
    'email': 'admin@gmail.com',
    'password': '987654321'
}, follow_redirects=True)
assert response.status_code == 200, f"Error en login admin: {response.status_code}"
# Verificar que en el HTML no hay referencias a ventas
html = response.get_data(as_text=True)
assert "Panel de Control" in html or "Dashboard" in html, "No se cargó el dashboard del administrador"
assert "ventasProductoChart" not in html, "⚠️ ALERTA: El gráfico de Ventas Producto sigue apareciendo en el Dashboard!"
print("✅ Login de administrador y carga de dashboard (sin ventas) exitosos")

# 3. Probar GET /dashboard/filtrar con sesión de Admin
print("Probando GET /dashboard/filtrar con filtros básicos...")
response = client.get('/dashboard/filtrar?fecha_inicio=2023-01-01&fecha_fin=2026-07-17&producto=0&responsable=0', follow_redirects=True)
assert response.status_code == 200, f"Error en filtrar: {response.status_code}"
html = response.get_data(as_text=True)
assert "Resultados del Filtro" in html, "No se muestran resultados de filtro"
print("✅ Filtrado del dashboard exitoso")

# 4. Probar Login de Empleado
print("Probando login de empleado...")
# Limpiar cookies/sesión
client.cookie_jar.clear()
response = client.post('/login', data={
    'email': 'empleado@gmail.com',
    'password': '123456789'
}, follow_redirects=True)
assert response.status_code == 200, f"Error en login empleado: {response.status_code}"
html = response.get_data(as_text=True)
assert "Bienvenido" in html, "No se cargó la página de inicio del empleado"
assert "Ventas" not in html, "⚠️ ALERTA: El módulo 'Ventas' sigue apareciendo en la página de inicio del empleado!"
assert "Producción" in html, "Debería mostrarse el módulo de Producción"
assert "Productos" in html, "Debería mostrarse el módulo de Productos"
print("✅ Login de empleado y carga de home (sin ventas) exitosos")

# 5. Probar que no se puede acceder a / como empleado (debe redirigir a /produccion)
print("Probando restricción de rol en / para empleados...")
response = client.get('/', follow_redirects=True)
assert response.status_code == 200, f"Error al acceder a /: {response.status_code}"
html = response.get_data(as_text=True)
# Si es redirigido a producción, debe mostrar la tabla de producción o el título
assert "Producción" in html, "El empleado no fue redirigido correctamente al módulo de producción"
print("✅ Restricción de rol y redirección correctas")

print("=== TODAS LAS PRUEBAS DE RUTAS PASARON CON ÉXITO ===")
