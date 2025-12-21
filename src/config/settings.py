"""
ConSmart - Configuración del Sistema
=====================================
Configuraciones centralizadas para toda la aplicación.
"""

import os
from pathlib import Path

# Rutas base
BASE_DIR = Path(__file__).parent.parent.parent
DATA_DIR = BASE_DIR / "data"
ASSETS_DIR = BASE_DIR / "assets"

# Base de datos
DB_PATH = DATA_DIR / "consmart.duckdb"

# Configuración de la aplicación
APP_CONFIG = {
    "nombre": "ConSmart",
    "version": "1.0.0",
    "autor": "Tu Empresa",
    "moneda_principal": "PEN",  # Soles peruanos
    "moneda_secundaria": "USD",  # Dólares
}

# Configuración de UI
UI_CONFIG = {
    "window_width": 1400,
    "window_height": 900,
    "theme_mode": "light",  # light, dark, system
}

# Datos iniciales para poblar la base de datos
DATOS_INICIALES = {
    "hojas": [
        {"nombre": "B1_BBVA", "tipo": "banco", "moneda": "PEN"},
        {"nombre": "B1_BCP", "tipo": "banco", "moneda": "PEN"},
        {"nombre": "Efectivo_Soles", "tipo": "efectivo", "moneda": "PEN"},
        {"nombre": "Efectivo_Dolares", "tipo": "efectivo", "moneda": "USD"},
    ],
    "locales": [
        {"nombre": "Marcavalle"},
        {"nombre": "Amauta"},
        {"nombre": "Garcilaso"},
        {"nombre": "Hotel"},
        {"nombre": "Oficina"},
    ],
    "categorias": {
        "Hotel": [
            "Adelanto", "Caja Chica", "Compra Dolares", 
            "Devolución Huespedes", "Ingreso", "Venta Dolares", "Vuelto Dolares"
        ],
        "Marcavalle": [
            "Adelanto", "Caja Chica", "Combustible", 
            "Compra Tiendas", "Egreso", "Gas Tiendas", "Pan Sunat"
        ],
        "Amauta": [
            "Adelanto", "Caja Chica", "Combustible", 
            "Compra Tiendas", "Egreso", "Gas Tiendas"
        ],
        "Garcilaso": [
            "Adelanto", "Caja Chica", "Combustible", 
            "Compra Tiendas", "Egreso", "Gas Tiendas"
        ],
        "Oficina": [
            "Adelanto", "Alquiler", "Caja Chica", 
            "Compra Proveedores", "Faltante Oficina", "Gas Oficina", "Sobrante Oficina"
        ],
    }
}
