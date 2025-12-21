"""
ConSmart - Repositorio de Movimientos
======================================
CRUD y consultas para la tabla de movimientos.
"""

from datetime import date
from typing import Optional
import pandas as pd

from src.database.connection import get_db


class MovimientoRepository:
    """Maneja todas las operaciones de la tabla movimientos."""
    
    def __init__(self):
        self.db = get_db()
    
    def crear(self, datos: dict) -> int:
        """
        Crea un nuevo movimiento.
        
        Args:
            datos: Diccionario con los campos del movimiento
            
        Returns:
            ID del movimiento creado
        """
        query = """
            INSERT INTO movimientos 
            (fecha, hoja_id, local_id, categoria_id, num_documento, 
             responsable, descripcion, ingreso, egreso, created_by)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            RETURNING id
        """
        
        result = self.db.execute(query, [
            datos.get('fecha', date.today()),
            datos.get('hoja_id'),
            datos.get('local_id'),
            datos.get('categoria_id'),
            datos.get('num_documento', ''),
            datos.get('responsable', ''),
            datos.get('descripcion', ''),
            float(datos.get('ingreso', 0)),
            float(datos.get('egreso', 0)),
            datos.get('created_by', 'sistema'),
        ])
        
        nuevo_id = result.fetchone()[0]
        
        # Actualizar descripción favorita si tiene texto
        if datos.get('descripcion'):
            self._actualizar_descripcion_favorita(datos['descripcion'])
        
        return nuevo_id
    
    def obtener_por_id(self, movimiento_id: int) -> Optional[dict]:
        """Obtiene un movimiento por su ID."""
        query = """
            SELECT m.*, h.nombre as hoja_nombre, l.nombre as local_nombre, 
                   c.nombre as categoria_nombre
            FROM movimientos m
            LEFT JOIN hojas h ON m.hoja_id = h.id
            LEFT JOIN locales l ON m.local_id = l.id
            LEFT JOIN categorias c ON m.categoria_id = c.id
            WHERE m.id = ?
        """
        result = self.db.fetchone(query, [movimiento_id])
        if result:
            columns = ['id', 'fecha', 'hoja_id', 'local_id', 'categoria_id',
                      'num_documento', 'responsable', 'descripcion', 'ingreso',
                      'egreso', 'created_at', 'updated_at', 'created_by',
                      'hoja_nombre', 'local_nombre', 'categoria_nombre']
            return dict(zip(columns, result))
        return None
    
    def obtener_historial_con_saldo(self, hoja_id: int, 
                                     fecha_inicio: date = None,
                                     fecha_fin: date = None) -> pd.DataFrame:
        """
        Obtiene el historial de movimientos con saldo acumulado.
        Usa Window Functions de DuckDB para cálculo eficiente.
        
        Args:
            hoja_id: ID de la hoja/cuenta
            fecha_inicio: Filtro opcional de fecha inicio
            fecha_fin: Filtro opcional de fecha fin
            
        Returns:
            DataFrame con movimientos y saldo acumulado
        """
        query = """
            SELECT 
                m.id,
                m.fecha,
                l.nombre as local,
                c.nombre as categoria,
                m.num_documento,
                m.responsable,
                m.descripcion,
                m.ingreso,
                m.egreso,
                SUM(m.ingreso - m.egreso) OVER (
                    PARTITION BY m.hoja_id 
                    ORDER BY m.fecha, m.id
                    ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
                ) as saldo
            FROM movimientos m
            LEFT JOIN locales l ON m.local_id = l.id
            LEFT JOIN categorias c ON m.categoria_id = c.id
            WHERE m.hoja_id = ?
        """
        
        params = [hoja_id]
        
        if fecha_inicio:
            query += " AND m.fecha >= ?"
            params.append(fecha_inicio)
        
        if fecha_fin:
            query += " AND m.fecha <= ?"
            params.append(fecha_fin)
        
        query += " ORDER BY m.fecha DESC, m.id DESC"
        
        return self.db.fetchdf(query, params)
    
    def obtener_saldo_actual(self, hoja_id: int) -> float:
        """Calcula el saldo actual de una hoja."""
        query = """
            SELECT COALESCE(SUM(ingreso - egreso), 0) as saldo
            FROM movimientos
            WHERE hoja_id = ?
        """
        result = self.db.fetchone(query, [hoja_id])
        return float(result[0]) if result else 0.0
    
    def obtener_resumen_por_local(self, hoja_id: int, 
                                   fecha_inicio: date = None,
                                   fecha_fin: date = None) -> pd.DataFrame:
        """Obtiene resumen agrupado por local."""
        query = """
            SELECT 
                l.nombre as local,
                SUM(m.ingreso) as total_ingresos,
                SUM(m.egreso) as total_egresos,
                SUM(m.ingreso - m.egreso) as balance
            FROM movimientos m
            LEFT JOIN locales l ON m.local_id = l.id
            WHERE m.hoja_id = ?
        """
        
        params = [hoja_id]
        
        if fecha_inicio:
            query += " AND m.fecha >= ?"
            params.append(fecha_inicio)
        
        if fecha_fin:
            query += " AND m.fecha <= ?"
            params.append(fecha_fin)
        
        query += " GROUP BY l.nombre ORDER BY balance DESC"
        
        return self.db.fetchdf(query, params)
    
    def actualizar(self, movimiento_id: int, datos: dict) -> bool:
        """Actualiza un movimiento existente."""
        campos = []
        valores = []
        
        campos_permitidos = ['fecha', 'hoja_id', 'local_id', 'categoria_id',
                            'num_documento', 'responsable', 'descripcion',
                            'ingreso', 'egreso']
        
        for campo in campos_permitidos:
            if campo in datos:
                campos.append(f"{campo} = ?")
                valores.append(datos[campo])
        
        if not campos:
            return False
        
        campos.append("updated_at = CURRENT_TIMESTAMP")
        valores.append(movimiento_id)
        
        query = f"""
            UPDATE movimientos 
            SET {', '.join(campos)}
            WHERE id = ?
        """
        
        self.db.execute(query, valores)
        return True
    
    def eliminar(self, movimiento_id: int) -> bool:
        """Elimina un movimiento (soft delete recomendado en producción)."""
        # Por ahora hacemos hard delete
        self.db.execute("DELETE FROM movimientos WHERE id = ?", [movimiento_id])
        return True
    
    def _actualizar_descripcion_favorita(self, texto: str):
        """Actualiza o crea una descripción favorita para autocompletado."""
        try:
            # Intentar actualizar
            self.db.execute("""
                INSERT INTO descripciones_favoritas (texto, uso_count, ultima_vez)
                VALUES (?, 1, CURRENT_TIMESTAMP)
                ON CONFLICT (texto) DO UPDATE SET
                    uso_count = descripciones_favoritas.uso_count + 1,
                    ultima_vez = CURRENT_TIMESTAMP
            """, [texto])
        except:
            pass  # Ignorar errores de duplicados
    
    def obtener_descripciones_frecuentes(self, limite: int = 10) -> list:
        """Obtiene las descripciones más usadas para autocompletado."""
        query = """
            SELECT texto FROM descripciones_favoritas
            ORDER BY uso_count DESC, ultima_vez DESC
            LIMIT ?
        """
        results = self.db.fetchall(query, [limite])
        return [r[0] for r in results]
