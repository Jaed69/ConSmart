# ConSmart 📊

Sistema contable ligero y moderno con **Flet 0.80** (v1) y DuckDB.

## ✨ Características

- 🎯 **Interfaz moderna** con Flet v1 (Flutter-based)
- 💾 **Base de datos DuckDB** - Rápida y eficiente
- 📊 **Dashboard interactivo** con métricas en tiempo real
- 📝 **Registro de movimientos** con validación
- 📜 **Historial con filtros** y paginación
- 📤 **Exportación a Excel** con openpyxl
- 🔐 **Sistema de autenticación** y permisos
- ⚙️ **Panel de administración** completo

---

## 🚀 Inicio Rápido

### Opción 1: Script de inicio (recomendado)
```bash
./run.sh
```

### Opción 2: Con uv
```bash
uv run flet run main.py
```

### Opción 3: Con flet directamente
```bash
flet run main.py
```

---

## 📋 Requisitos

- **Python:** 3.12+ (3.10+ compatible)
- **Flet:** 0.80.0+ (Flet v1)
- **Sistema operativo:** Linux, macOS, Windows

---

## 🔧 Instalación

### Opción 1: Con uv (recomendado)
```bash
# Clonar el repositorio
cd /home/luciel/Documentos/GitHub/ConSmart

# Sincronizar dependencias
uv sync

# Verificar instalación
uv run python3 verificar_flet.py
```

### Opción 2: Con pip
```bash
# Instalar dependencias
pip install -r requirements.txt

# Verificar instalación
python3 verificar_flet.py
```

---

## 📁 Estructura del Proyecto

```
ConSmart/
├── main.py                     # Punto de entrada
├── run.sh                      # Script de inicio rápido
├── verificar_flet.py          # Script de verificación
├── pyproject.toml             # Configuración uv/pip
├── requirements.txt           # Dependencias
├── uv.lock                    # Lock file de uv
│
├── src/
│   ├── config/               # Configuración y datos iniciales
│   │   └── settings.py
│   ├── database/             # Conexión DuckDB y repositorios
│   │   ├── connection.py
│   │   └── repositories/
│   ├── logic/                # Validadores y servicios
│   │   ├── auth_service.py
│   │   ├── balance_utils.py
│   │   ├── services.py
│   │   └── validators.py
│   └── ui/                   # Interfaz de usuario
│       ├── theme.py
│       ├── components/       # Componentes reutilizables
│       │   ├── data_table.py
│       │   ├── excel_grid.py
│       │   └── excel_row.py
│       └── views/            # Vistas principales
│           ├── login_view.py
│           ├── dashboard_view.py
│           ├── entry_view.py
│           ├── history_view.py
│           ├── admin_view.py
│           └── usuarios_view.py
│
├── data/                     # Base de datos
│   └── consmart.duckdb
│
└── assets/                   # Recursos estáticos
```

---

## 🛠️ Desarrollo

### Ejecutar en modo desarrollo (recarga automática)
```bash
uv run flet run -d main.py
```

### Verificar estado
```bash
uv run python3 verificar_flet.py
```

### Actualizar dependencias
```bash
uv sync
```

---

## 📚 Documentación

- **[RESUMEN_ACTUALIZACION.md](RESUMEN_ACTUALIZACION.md)** - Resumen de actualización a Flet 0.80
- **[MIGRATION_FLET_0.80.md](MIGRATION_FLET_0.80.md)** - Guía completa de migración a Flet v1
- **[Documentación Flet](https://flet.dev/docs/)** - Documentación oficial de Flet
- **[Releases Flet](https://github.com/flet-dev/flet/releases)** - Notas de versión

---

## 🎯 Funcionalidades Principales

### 🏠 Dashboard
- Resumen de saldo actual
- Métricas de ingresos y egresos
- Gráficos visuales
- Últimos movimientos

### ➕ Registro de Movimientos
- Validación de datos
- Selección de categorías
- Selección de hojas/locales
- Guardado automático

### 📜 Historial
- Búsqueda por texto
- Filtros por fecha
- Filtros por categoría
- Paginación
- Edición de movimientos
- Eliminación con confirmación
- Exportación a Excel

### ⚙️ Administración
- Gestión de hojas contables
- Gestión de locales
- Gestión de categorías
- Gestión de usuarios
- Configuración de permisos

---

## 🔐 Sistema de Usuarios

ConSmart incluye un sistema de autenticación con 3 roles:

| Rol | Permisos |
|-----|----------|
| **Admin** | Acceso total a todas las funciones |
| **Usuario** | Registro de movimientos + historial |
| **Visualizador** | Solo lectura (dashboard + historial) |

**Usuario por defecto:**
- Usuario: `admin`
- Contraseña: `admin123`

---

## 🆕 Actualización a Flet 0.80

ConSmart ha sido actualizado a **Flet 0.80 (v1)**. 

### Cambios principales:
- ✅ Métodos `_async` eliminados (ahora todos son síncronos)
- ⚠️ `Button` y `ElevatedButton` intercambiaron roles
- ✅ Nuevas características disponibles (ContextMenu, RadarChart, Testing, etc.)

Ver [MIGRATION_FLET_0.80.md](MIGRATION_FLET_0.80.md) para más detalles.

---

## 🐛 Solución de Problemas

### La aplicación no inicia
```bash
# Verificar instalación
uv run python3 verificar_flet.py

# Reinstalar dependencias
uv sync --reinstall
```

### Error "Module not found"
```bash
# Asegúrate de usar uv run
uv run flet run main.py
```

### Base de datos no inicializa
```bash
# Eliminar y recrear
rm data/consmart.duckdb
uv run flet run main.py
```

---

## 📞 Soporte

- **Flet Discord:** https://discord.gg/dzWXP8SHG8
- **Flet GitHub:** https://github.com/flet-dev/flet
- **Flet Discussions:** https://github.com/flet-dev/flet/discussions

---

## 📝 Pendiente / Roadmap

- [ ] Tests unitarios con framework de testing de Flet v1
- [ ] Exportación a PDF
- [ ] Gráficos avanzados (usando nuevos charts de Flet 0.80)
- [ ] Modo oscuro
- [ ] Backup automático de base de datos
- [ ] Importación desde Excel
- [ ] API REST para integración
- [ ] Reportes personalizados

---

## 📄 Licencia

Este proyecto es de código abierto. Consulta el archivo LICENSE para más detalles.

---

## 🤝 Contribuir

Las contribuciones son bienvenidas. Por favor:
1. Fork el proyecto
2. Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

---

## ⭐ Agradecimientos

- **Flet Team** - Por el increíble framework
- **DuckDB Team** - Por la base de datos ultrarrápida
- **Flutter Team** - Por el motor UI subyacente

---

**Versión:** 0.1.0  
**Flet Version:** 0.80.0  
**Última actualización:** Enero 2026
