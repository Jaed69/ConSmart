"""
ConSmart - Conexión y Esquema de Base de Datos
===============================================
Maneja la conexión a DuckDB y la creación del esquema.
"""

import duckdb
from pathlib import Path
from typing import Optional
import sys

# Añadir el path del proyecto
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.config import DB_PATH, DATA_DIR, DATOS_INICIALES


class DatabaseConnection:
    """Singleton para manejar la conexión a DuckDB."""
    
    _instance: Optional['DatabaseConnection'] = None
    _connection: Optional[duckdb.DuckDBPyConnection] = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if self._connection is None:
            self._inicializar_conexion()
    
    def _inicializar_conexion(self):
        """Crea la conexión y el esquema de la base de datos."""
        # Asegurar que existe el directorio
        DATA_DIR.mkdir(parents=True, exist_ok=True)
        
        # Conectar a DuckDB
        self._connection = duckdb.connect(str(DB_PATH))
        
        # Crear esquema
        self._crear_esquema()
        
        # Poblar datos iniciales si es primera vez
        self._poblar_datos_iniciales()
    
    def _crear_esquema(self):
        """Crea todas las tablas necesarias."""
        
        # Secuencia para IDs
        self._connection.execute("""
            CREATE SEQUENCE IF NOT EXISTS seq_movimiento_id START 1
        """)
        
        # Tabla de Hojas (cuentas bancarias, efectivo)
        self._connection.execute("""
            CREATE TABLE IF NOT EXISTS hojas (
                id INTEGER PRIMARY KEY DEFAULT nextval('seq_movimiento_id'),
                nombre VARCHAR NOT NULL UNIQUE,
                tipo VARCHAR CHECK(tipo IN ('banco', 'efectivo')),
                moneda VARCHAR(3) DEFAULT 'PEN',
                activo BOOLEAN DEFAULT TRUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Tabla de Locales
        self._connection.execute("""
            CREATE TABLE IF NOT EXISTS locales (
                id INTEGER PRIMARY KEY DEFAULT nextval('seq_movimiento_id'),
                nombre VARCHAR NOT NULL UNIQUE,
                activo BOOLEAN DEFAULT TRUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Tabla de Categorías (relacionada con Locales)
        self._connection.execute("""
            CREATE TABLE IF NOT EXISTS categorias (
                id INTEGER PRIMARY KEY DEFAULT nextval('seq_movimiento_id'),
                nombre VARCHAR NOT NULL,
                local_id INTEGER REFERENCES locales(id),
                tipo VARCHAR CHECK(tipo IN ('ingreso', 'egreso', 'ambos')) DEFAULT 'ambos',
                activo BOOLEAN DEFAULT TRUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(nombre, local_id)
            )
        """)
        
        # Tabla principal de Movimientos
        self._connection.execute("""
            CREATE TABLE IF NOT EXISTS movimientos (
                id INTEGER PRIMARY KEY DEFAULT nextval('seq_movimiento_id'),
                fecha DATE NOT NULL,
                hoja_id INTEGER REFERENCES hojas(id),
                local_id INTEGER REFERENCES locales(id),
                categoria_id INTEGER REFERENCES categorias(id),
                num_documento VARCHAR,
                responsable VARCHAR,
                descripcion TEXT,
                ingreso DECIMAL(15,2) DEFAULT 0,
                egreso DECIMAL(15,2) DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP,
                created_by VARCHAR,
                CHECK(ingreso >= 0),
                CHECK(egreso >= 0)
            )
        """)
        
        # Tabla de Tipo de Cambio (para dólares)
        self._connection.execute("""
            CREATE TABLE IF NOT EXISTS tipo_cambio (
                fecha DATE PRIMARY KEY,
                compra DECIMAL(5,3),
                venta DECIMAL(5,3),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Tabla de Descripciones Favoritas (autocompletado)
        self._connection.execute("""
            CREATE TABLE IF NOT EXISTS descripciones_favoritas (
                id INTEGER PRIMARY KEY DEFAULT nextval('seq_movimiento_id'),
                texto VARCHAR NOT NULL UNIQUE,
                uso_count INTEGER DEFAULT 1,
                ultima_vez TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Tabla de Auditoría
        self._connection.execute("""
            CREATE TABLE IF NOT EXISTS audit_log (
                id INTEGER PRIMARY KEY DEFAULT nextval('seq_movimiento_id'),
                tabla VARCHAR NOT NULL,
                registro_id INTEGER,
                accion VARCHAR CHECK(accion IN ('INSERT', 'UPDATE', 'DELETE')),
                datos_anteriores VARCHAR,
                datos_nuevos VARCHAR,
                usuario VARCHAR,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Tabla de Roles
        self._connection.execute("""
            CREATE TABLE IF NOT EXISTS roles (
                id INTEGER PRIMARY KEY DEFAULT nextval('seq_movimiento_id'),
                nombre VARCHAR NOT NULL UNIQUE,
                descripcion VARCHAR,
                puede_registrar BOOLEAN DEFAULT TRUE,
                puede_ver_historial BOOLEAN DEFAULT TRUE,
                puede_editar_movimientos BOOLEAN DEFAULT FALSE,
                puede_eliminar_movimientos BOOLEAN DEFAULT FALSE,
                puede_modificar_saldos BOOLEAN DEFAULT FALSE,
                puede_gestionar_config BOOLEAN DEFAULT FALSE,
                puede_gestionar_usuarios BOOLEAN DEFAULT FALSE,
                es_admin BOOLEAN DEFAULT FALSE,
                activo BOOLEAN DEFAULT TRUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Tabla de Usuarios
        self._connection.execute("""
            CREATE TABLE IF NOT EXISTS usuarios (
                id INTEGER PRIMARY KEY DEFAULT nextval('seq_movimiento_id'),
                username VARCHAR NOT NULL UNIQUE,
                password_hash VARCHAR NOT NULL,
                nombre_completo VARCHAR,
                email VARCHAR,
                rol_id INTEGER REFERENCES roles(id),
                activo BOOLEAN DEFAULT TRUE,
                ultimo_login TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                created_by INTEGER
            )
        """)
        
        # Índices para rendimiento
        self._connection.execute("""
            CREATE INDEX IF NOT EXISTS idx_mov_fecha ON movimientos(fecha)
        """)
        self._connection.execute("""
            CREATE INDEX IF NOT EXISTS idx_mov_hoja ON movimientos(hoja_id, fecha)
        """)
        self._connection.execute("""
            CREATE INDEX IF NOT EXISTS idx_cat_local ON categorias(local_id)
        """)
    
    def _poblar_datos_iniciales(self):
        """Inserta datos iniciales si las tablas están vacías."""
        
        # Verificar si ya hay datos
        count = self._connection.execute("SELECT COUNT(*) FROM hojas").fetchone()[0]
        if count > 0:
            # Aún así verificar si hay roles/usuarios
            self._crear_roles_y_admin_default()
            return  # Ya hay datos, no hacer nada más
        
        # Insertar Hojas
        for hoja in DATOS_INICIALES["hojas"]:
            self._connection.execute("""
                INSERT INTO hojas (nombre, tipo, moneda) VALUES (?, ?, ?)
            """, [hoja["nombre"], hoja["tipo"], hoja["moneda"]])
        
        # Insertar Locales
        for local in DATOS_INICIALES["locales"]:
            self._connection.execute("""
                INSERT INTO locales (nombre) VALUES (?)
            """, [local["nombre"]])
        
        # Insertar Categorías
        for local_nombre, categorias in DATOS_INICIALES["categorias"].items():
            # Obtener ID del local
            result = self._connection.execute(
                "SELECT id FROM locales WHERE nombre = ?", [local_nombre]
            ).fetchone()
            
            if result:
                local_id = result[0]
                for cat_nombre in categorias:
                    self._connection.execute("""
                        INSERT INTO categorias (nombre, local_id) VALUES (?, ?)
                    """, [cat_nombre, local_id])
        
        # Crear roles y usuario admin por defecto
        self._crear_roles_y_admin_default()
        
        print("✅ Datos iniciales cargados correctamente")
    
    def _crear_roles_y_admin_default(self):
        """Crea los roles por defecto y el usuario administrador."""
        import hashlib
        
        # Verificar si ya existen roles
        count = self._connection.execute("SELECT COUNT(*) FROM roles").fetchone()[0]
        if count > 0:
            return  # Ya hay roles
        
        # Rol Administrador (todos los permisos)
        self._connection.execute("""
            INSERT INTO roles (nombre, descripcion, puede_registrar, puede_ver_historial,
                puede_editar_movimientos, puede_eliminar_movimientos, puede_modificar_saldos,
                puede_gestionar_config, puede_gestionar_usuarios, es_admin)
            VALUES ('Administrador', 'Control total del sistema', TRUE, TRUE, TRUE, TRUE, TRUE, TRUE, TRUE, TRUE)
        """)
        
        # Rol Supervisor (puede editar pero no eliminar ni gestionar usuarios)
        self._connection.execute("""
            INSERT INTO roles (nombre, descripcion, puede_registrar, puede_ver_historial,
                puede_editar_movimientos, puede_eliminar_movimientos, puede_modificar_saldos,
                puede_gestionar_config, puede_gestionar_usuarios, es_admin)
            VALUES ('Supervisor', 'Puede editar movimientos y modificar saldos', TRUE, TRUE, TRUE, FALSE, TRUE, TRUE, FALSE, FALSE)
        """)
        
        # Rol Operador (solo registrar y ver)
        self._connection.execute("""
            INSERT INTO roles (nombre, descripcion, puede_registrar, puede_ver_historial,
                puede_editar_movimientos, puede_eliminar_movimientos, puede_modificar_saldos,
                puede_gestionar_config, puede_gestionar_usuarios, es_admin)
            VALUES ('Operador', 'Solo puede registrar y ver historial', TRUE, TRUE, FALSE, FALSE, FALSE, FALSE, FALSE, FALSE)
        """)
        
        # Rol Solo Lectura
        self._connection.execute("""
            INSERT INTO roles (nombre, descripcion, puede_registrar, puede_ver_historial,
                puede_editar_movimientos, puede_eliminar_movimientos, puede_modificar_saldos,
                puede_gestionar_config, puede_gestionar_usuarios, es_admin)
            VALUES ('Solo Lectura', 'Solo puede ver información', FALSE, TRUE, FALSE, FALSE, FALSE, FALSE, FALSE, FALSE)
        """)
        
        # Obtener ID del rol admin
        admin_rol_id = self._connection.execute(
            "SELECT id FROM roles WHERE nombre = 'Administrador'"
        ).fetchone()[0]
        
        # Crear usuario admin por defecto (password: admin123)
        password_hash = hashlib.sha256("admin123".encode()).hexdigest()
        self._connection.execute("""
            INSERT INTO usuarios (username, password_hash, nombre_completo, rol_id)
            VALUES ('admin', ?, 'Administrador del Sistema', ?)
        """, [password_hash, admin_rol_id])
        
        print("✅ Roles y usuario administrador creados (usuario: admin, contraseña: admin123)")
    
    @property
    def con(self) -> duckdb.DuckDBPyConnection:
        """Retorna la conexión activa."""
        return self._connection
    
    def execute(self, query: str, params: list = None):
        """Ejecuta una consulta SQL."""
        if params:
            return self._connection.execute(query, params)
        return self._connection.execute(query)
    
    def fetchall(self, query: str, params: list = None) -> list:
        """Ejecuta y retorna todos los resultados."""
        result = self.execute(query, params)
        return result.fetchall()
    
    def fetchone(self, query: str, params: list = None):
        """Ejecuta y retorna un solo resultado."""
        result = self.execute(query, params)
        return result.fetchone()
    
    def fetchdf(self, query: str, params: list = None):
        """Ejecuta y retorna un DataFrame de Pandas."""
        result = self.execute(query, params)
        return result.df()
    
    def close(self):
        """Cierra la conexión."""
        if self._connection:
            self._connection.close()
            self._connection = None


# Instancia global
def get_db() -> DatabaseConnection:
    """Obtiene la instancia de la base de datos."""
    return DatabaseConnection()
