"""
ConSmart - Servicios de Negocio
===============================
Orquesta las operaciones combinando repositorios y validadores.
"""

from datetime import date
from typing import Dict, List, Tuple, Optional
import pandas as pd

from src.database import MovimientoRepository, ConfigRepository
from .validators import MovimientoValidator
from .balance_utils import BalanceCalculator


class MovimientoService:
    """Servicio para gestionar movimientos contables."""
    
    def __init__(self):
        self.repo = MovimientoRepository()
        self.config_repo = ConfigRepository()
        self.calculator = BalanceCalculator()
    
    def crear_movimiento(self, datos: dict) -> Tuple[bool, int, List[str]]:
        """
        Crea un nuevo movimiento con validación completa.
        
        Args:
            datos: Diccionario con los campos del movimiento
            
        Returns:
            Tupla (exito, id_creado, errores)
        """
        # Validar datos
        es_valido, errores = MovimientoValidator.validar(datos)
        
        if not es_valido:
            return (False, 0, errores)
        
        # Crear movimiento
        try:
            nuevo_id = self.repo.crear(datos)
            return (True, nuevo_id, [])
        except Exception as e:
            return (False, 0, [f"Error al guardar: {str(e)}"])
    
    def obtener_historial(self, hoja_id: int,
                          fecha_inicio: date = None,
                          fecha_fin: date = None) -> pd.DataFrame:
        """Obtiene el historial con saldo calculado."""
        return self.repo.obtener_historial_con_saldo(
            hoja_id, fecha_inicio, fecha_fin
        )
    
    def obtener_historial_filtrado(self, hoja_id: int = None,
                                    local_id: int = None,
                                    fecha_inicio: date = None,
                                    fecha_fin: date = None,
                                    texto_busqueda: str = None) -> pd.DataFrame:
        """Obtiene el historial con múltiples filtros."""
        return self.repo.obtener_historial_filtrado(
            hoja_id=hoja_id,
            local_id=local_id,
            fecha_inicio=fecha_inicio,
            fecha_fin=fecha_fin,
            texto_busqueda=texto_busqueda
        )
    
    def obtener_movimiento(self, movimiento_id: int) -> Optional[Dict]:
        """Obtiene un movimiento por ID."""
        return self.repo.obtener_por_id(movimiento_id)
    
    def actualizar_movimiento(self, movimiento_id: int, datos: dict) -> bool:
        """Actualiza un movimiento existente."""
        try:
            return self.repo.actualizar(movimiento_id, datos)
        except Exception as e:
            print(f"Error al actualizar movimiento: {e}")
            return False
    
    def eliminar_movimiento(self, movimiento_id: int) -> bool:
        """Elimina un movimiento."""
        try:
            return self.repo.eliminar(movimiento_id)
        except Exception as e:
            print(f"Error al eliminar movimiento: {e}")
            return False
    
    def contar_movimientos_hoy(self) -> int:
        """Cuenta los movimientos registrados hoy."""
        return self.repo.contar_movimientos_por_fecha(date.today())
    
    def obtener_saldo_actual(self, hoja_id: int) -> float:
        """Obtiene el saldo actual de una cuenta."""
        return self.repo.obtener_saldo_actual(hoja_id)
    
    def obtener_descripciones_sugeridas(self) -> List[str]:
        """Obtiene descripciones frecuentes para autocompletado."""
        return self.repo.obtener_descripciones_frecuentes(15)


class ConfigService:
    """Servicio para gestionar configuración del sistema."""
    
    def __init__(self):
        self.repo = ConfigRepository()
    
    # ==================== HOJAS ====================
    
    def obtener_hojas(self) -> List[Dict]:
        """Obtiene todas las hojas activas."""
        return self.repo.obtener_hojas(solo_activas=True)
    
    def crear_hoja(self, nombre: str, tipo: str = "banco", 
                   moneda: str = "PEN") -> Tuple[bool, int, str]:
        """Crea una nueva hoja."""
        # Verificar si ya existe
        existentes = [h['nombre'] for h in self.repo.obtener_hojas(solo_activas=False)]
        
        if nombre.strip().lower() in [e.lower() for e in existentes]:
            return (False, 0, f"La hoja '{nombre}' ya existe")
        
        try:
            nuevo_id = self.repo.crear_hoja(nombre, tipo, moneda)
            return (True, nuevo_id, "")
        except Exception as e:
            return (False, 0, str(e))
    
    def eliminar_hoja(self, hoja_id: int) -> bool:
        """Desactiva una hoja."""
        return self.repo.eliminar_hoja(hoja_id)
    
    # ==================== LOCALES ====================
    
    def obtener_locales(self) -> List[Dict]:
        """Obtiene todos los locales activos."""
        return self.repo.obtener_locales(solo_activos=True)
    
    def crear_local(self, nombre: str) -> Tuple[bool, int, str]:
        """Crea un nuevo local."""
        existentes = [l['nombre'] for l in self.repo.obtener_locales(solo_activos=False)]
        
        if nombre.strip().lower() in [e.lower() for e in existentes]:
            return (False, 0, f"El local '{nombre}' ya existe")
        
        try:
            nuevo_id = self.repo.crear_local(nombre)
            return (True, nuevo_id, "")
        except Exception as e:
            return (False, 0, str(e))
    
    def eliminar_local(self, local_id: int) -> bool:
        """Desactiva un local."""
        return self.repo.eliminar_local(local_id)
    
    # ==================== CATEGORÍAS ====================
    
    def obtener_categorias_por_local(self, local_id: int) -> List[Dict]:
        """Obtiene categorías filtradas por local."""
        return self.repo.obtener_categorias_por_local(local_id)
    
    def obtener_todas_categorias(self) -> List[Dict]:
        """Obtiene todas las categorías."""
        return self.repo.obtener_categorias()
    
    def crear_categoria(self, nombre: str, local_id: int, 
                        tipo: str = "ambos") -> Tuple[bool, int, str]:
        """Crea una nueva categoría."""
        # Verificar duplicado en el mismo local
        existentes = self.repo.obtener_categorias_por_local(local_id)
        
        if nombre.strip().lower() in [c['nombre'].lower() for c in existentes]:
            return (False, 0, f"La categoría '{nombre}' ya existe en este local")
        
        try:
            nuevo_id = self.repo.crear_categoria(nombre, local_id, tipo)
            return (True, nuevo_id, "")
        except Exception as e:
            return (False, 0, str(e))
    
    def eliminar_categoria(self, categoria_id: int) -> bool:
        """Desactiva una categoría."""
        return self.repo.eliminar_categoria(categoria_id)
