"""
ConSmart - Repositorio de Configuración
========================================
CRUD para tablas de configuración: hojas, locales, categorías.
"""

from typing import Optional
from src.database.connection import get_db


class ConfigRepository:
    """Maneja las tablas de configuración del sistema."""
    
    def __init__(self):
        self.db = get_db()
    
    # ==================== HOJAS ====================
    
    def obtener_hojas(self, solo_activas: bool = True) -> list:
        """Obtiene todas las hojas/cuentas."""
        query = "SELECT id, nombre, tipo, moneda, activo FROM hojas"
        if solo_activas:
            query += " WHERE activo = TRUE"
        query += " ORDER BY nombre"
        
        results = self.db.fetchall(query)
        return [
            {"id": r[0], "nombre": r[1], "tipo": r[2], "moneda": r[3], "activo": r[4]}
            for r in results
        ]
    
    def crear_hoja(self, nombre: str, tipo: str = "banco", moneda: str = "PEN") -> int:
        """Crea una nueva hoja/cuenta."""
        result = self.db.execute("""
            INSERT INTO hojas (nombre, tipo, moneda) VALUES (?, ?, ?)
            RETURNING id
        """, [nombre, tipo, moneda])
        return result.fetchone()[0]
    
    def actualizar_hoja(self, hoja_id: int, **kwargs) -> bool:
        """Actualiza una hoja existente."""
        campos = []
        valores = []
        
        for campo in ['nombre', 'tipo', 'moneda', 'activo']:
            if campo in kwargs:
                campos.append(f"{campo} = ?")
                valores.append(kwargs[campo])
        
        if not campos:
            return False
        
        valores.append(hoja_id)
        query = f"UPDATE hojas SET {', '.join(campos)} WHERE id = ?"
        self.db.execute(query, valores)
        return True
    
    def eliminar_hoja(self, hoja_id: int) -> bool:
        """Desactiva una hoja (soft delete)."""
        self.db.execute("UPDATE hojas SET activo = FALSE WHERE id = ?", [hoja_id])
        return True
    
    # ==================== LOCALES ====================
    
    def obtener_locales(self, solo_activos: bool = True) -> list:
        """Obtiene todos los locales."""
        query = "SELECT id, nombre, activo FROM locales"
        if solo_activos:
            query += " WHERE activo = TRUE"
        query += " ORDER BY nombre"
        
        results = self.db.fetchall(query)
        return [
            {"id": r[0], "nombre": r[1], "activo": r[2]}
            for r in results
        ]
    
    def obtener_local_por_id(self, local_id: int) -> Optional[dict]:
        """Obtiene un local por su ID."""
        result = self.db.fetchone(
            "SELECT id, nombre, activo FROM locales WHERE id = ?", 
            [local_id]
        )
        if result:
            return {"id": result[0], "nombre": result[1], "activo": result[2]}
        return None
    
    def crear_local(self, nombre: str) -> int:
        """Crea un nuevo local."""
        result = self.db.execute("""
            INSERT INTO locales (nombre) VALUES (?)
            RETURNING id
        """, [nombre])
        return result.fetchone()[0]
    
    def actualizar_local(self, local_id: int, **kwargs) -> bool:
        """Actualiza un local existente."""
        campos = []
        valores = []
        
        for campo in ['nombre', 'activo']:
            if campo in kwargs:
                campos.append(f"{campo} = ?")
                valores.append(kwargs[campo])
        
        if not campos:
            return False
        
        valores.append(local_id)
        query = f"UPDATE locales SET {', '.join(campos)} WHERE id = ?"
        self.db.execute(query, valores)
        return True
    
    def eliminar_local(self, local_id: int) -> bool:
        """Desactiva un local (soft delete)."""
        self.db.execute("UPDATE locales SET activo = FALSE WHERE id = ?", [local_id])
        return True
    
    # ==================== CATEGORÍAS ====================
    
    def obtener_categorias(self, local_id: int = None, solo_activas: bool = True) -> list:
        """
        Obtiene categorías, opcionalmente filtradas por local.
        
        Args:
            local_id: Si se proporciona, filtra por este local
            solo_activas: Si True, solo retorna categorías activas
        """
        query = """
            SELECT c.id, c.nombre, c.local_id, c.tipo, c.activo, l.nombre as local_nombre
            FROM categorias c
            LEFT JOIN locales l ON c.local_id = l.id
            WHERE 1=1
        """
        params = []
        
        if local_id:
            query += " AND c.local_id = ?"
            params.append(local_id)
        
        if solo_activas:
            query += " AND c.activo = TRUE"
        
        query += " ORDER BY c.nombre"
        
        results = self.db.fetchall(query, params)
        return [
            {
                "id": r[0], 
                "nombre": r[1], 
                "local_id": r[2], 
                "tipo": r[3], 
                "activo": r[4],
                "local_nombre": r[5]
            }
            for r in results
        ]
    
    def obtener_categorias_por_local(self, local_id: int) -> list:
        """Atajo para obtener categorías de un local específico."""
        return self.obtener_categorias(local_id=local_id)
    
    def crear_categoria(self, nombre: str, local_id: int, tipo: str = "ambos") -> int:
        """Crea una nueva categoría."""
        result = self.db.execute("""
            INSERT INTO categorias (nombre, local_id, tipo) VALUES (?, ?, ?)
            RETURNING id
        """, [nombre, local_id, tipo])
        return result.fetchone()[0]
    
    def actualizar_categoria(self, categoria_id: int, **kwargs) -> bool:
        """Actualiza una categoría existente."""
        campos = []
        valores = []
        
        for campo in ['nombre', 'local_id', 'tipo', 'activo']:
            if campo in kwargs:
                campos.append(f"{campo} = ?")
                valores.append(kwargs[campo])
        
        if not campos:
            return False
        
        valores.append(categoria_id)
        query = f"UPDATE categorias SET {', '.join(campos)} WHERE id = ?"
        self.db.execute(query, valores)
        return True
    
    def eliminar_categoria(self, categoria_id: int) -> bool:
        """Desactiva una categoría (soft delete)."""
        self.db.execute(
            "UPDATE categorias SET activo = FALSE WHERE id = ?", 
            [categoria_id]
        )
        return True
    
    # ==================== TIPO DE CAMBIO ====================
    
    def obtener_tipo_cambio(self, fecha=None) -> Optional[dict]:
        """Obtiene el tipo de cambio para una fecha (o el más reciente)."""
        if fecha:
            result = self.db.fetchone(
                "SELECT fecha, compra, venta FROM tipo_cambio WHERE fecha = ?",
                [fecha]
            )
        else:
            result = self.db.fetchone(
                "SELECT fecha, compra, venta FROM tipo_cambio ORDER BY fecha DESC LIMIT 1"
            )
        
        if result:
            return {"fecha": result[0], "compra": result[1], "venta": result[2]}
        return None
    
    def guardar_tipo_cambio(self, fecha, compra: float, venta: float) -> bool:
        """Guarda o actualiza el tipo de cambio para una fecha."""
        self.db.execute("""
            INSERT INTO tipo_cambio (fecha, compra, venta) VALUES (?, ?, ?)
            ON CONFLICT (fecha) DO UPDATE SET compra = ?, venta = ?
        """, [fecha, compra, venta, compra, venta])
        return True
