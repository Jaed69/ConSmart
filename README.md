# ConSmart

Sistema contable ligero con Flet y DuckDB.

## Requisitos
- Python 3.10+
- flet 0.28+

## Instalación
```
pip install -r requirements.txt
```

## Ejecutar
```
flet run main.py
```

## Estructura
- src/config: configuración y datos iniciales
- src/database: conexión DuckDB y repositorios
- src/logic: validadores y servicios de negocio
- src/ui: tema, componentes y vistas (dashboard, registro, admin)

## Pendiente
- Ajustar componentes a API Flet 0.28 (UserControl deprecado)
- Exportar historial a Excel/PDF
- Diálogo de edición/eliminación de movimientos
