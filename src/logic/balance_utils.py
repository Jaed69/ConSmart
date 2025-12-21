"""
ConSmart - Utilidades de Cálculo de Saldos
==========================================
Funciones para cálculos contables y análisis de saldos.
"""

from datetime import date, timedelta
from typing import List, Dict, Optional
import pandas as pd

from src.database import MovimientoRepository, ConfigRepository


class BalanceCalculator:
    """Calcula saldos y métricas contables."""
    
    def __init__(self):
        self.mov_repo = MovimientoRepository()
        self.config_repo = ConfigRepository()
    
    def obtener_saldo_cuenta(self, hoja_id: int) -> float:
        """Obtiene el saldo actual de una cuenta/hoja."""
        return self.mov_repo.obtener_saldo_actual(hoja_id)
    
    def obtener_saldos_todas_cuentas(self) -> List[Dict]:
        """Obtiene el saldo de todas las cuentas activas."""
        hojas = self.config_repo.obtener_hojas()
        
        saldos = []
        for hoja in hojas:
            saldo = self.mov_repo.obtener_saldo_actual(hoja['id'])
            saldos.append({
                "id": hoja['id'],
                "nombre": hoja['nombre'],
                "tipo": hoja['tipo'],
                "moneda": hoja['moneda'],
                "saldo": saldo
            })
        
        return saldos
    
    def obtener_resumen_periodo(self, hoja_id: int, 
                                 fecha_inicio: date,
                                 fecha_fin: date) -> Dict:
        """
        Obtiene resumen de un período específico.
        
        Returns:
            Dict con total_ingresos, total_egresos, balance
        """
        df = self.mov_repo.obtener_historial_con_saldo(
            hoja_id, fecha_inicio, fecha_fin
        )
        
        if df.empty:
            return {
                "total_ingresos": 0,
                "total_egresos": 0,
                "balance": 0,
                "num_movimientos": 0
            }
        
        return {
            "total_ingresos": df['ingreso'].sum(),
            "total_egresos": df['egreso'].sum(),
            "balance": df['ingreso'].sum() - df['egreso'].sum(),
            "num_movimientos": len(df)
        }
    
    def obtener_resumen_mensual(self, hoja_id: int, año: int, mes: int) -> Dict:
        """Obtiene resumen de un mes específico."""
        from calendar import monthrange
        
        fecha_inicio = date(año, mes, 1)
        ultimo_dia = monthrange(año, mes)[1]
        fecha_fin = date(año, mes, ultimo_dia)
        
        return self.obtener_resumen_periodo(hoja_id, fecha_inicio, fecha_fin)
    
    def calcular_proyeccion_cierre(self, hoja_id: int, 
                                    dias_proyeccion: int = 30) -> Dict:
        """
        Proyecta el saldo futuro basado en tendencias pasadas.
        
        Usa promedio de últimos 30 días para proyectar.
        """
        fecha_fin = date.today()
        fecha_inicio = fecha_fin - timedelta(days=30)
        
        resumen = self.obtener_resumen_periodo(hoja_id, fecha_inicio, fecha_fin)
        
        if resumen['num_movimientos'] == 0:
            return {
                "saldo_actual": self.obtener_saldo_cuenta(hoja_id),
                "promedio_diario": 0,
                "proyeccion_30_dias": self.obtener_saldo_cuenta(hoja_id),
                "tendencia": "estable"
            }
        
        promedio_diario = resumen['balance'] / 30
        saldo_actual = self.obtener_saldo_cuenta(hoja_id)
        proyeccion = saldo_actual + (promedio_diario * dias_proyeccion)
        
        if promedio_diario > 0:
            tendencia = "positiva"
        elif promedio_diario < 0:
            tendencia = "negativa"
        else:
            tendencia = "estable"
        
        return {
            "saldo_actual": saldo_actual,
            "promedio_diario": promedio_diario,
            "proyeccion_30_dias": proyeccion,
            "tendencia": tendencia
        }
    
    def detectar_anomalias(self, hoja_id: int, umbral_desviacion: float = 2.0) -> List[Dict]:
        """
        Detecta movimientos inusuales basados en desviación estándar.
        
        Args:
            hoja_id: ID de la cuenta
            umbral_desviacion: Cuántas desviaciones estándar para considerar anomalía
            
        Returns:
            Lista de movimientos sospechosos
        """
        # Obtener últimos 90 días
        fecha_fin = date.today()
        fecha_inicio = fecha_fin - timedelta(days=90)
        
        df = self.mov_repo.obtener_historial_con_saldo(
            hoja_id, fecha_inicio, fecha_fin
        )
        
        if df.empty or len(df) < 5:
            return []  # No hay suficientes datos
        
        # Calcular montos totales por movimiento
        df['monto'] = df['ingreso'] + df['egreso']
        
        media = df['monto'].mean()
        std = df['monto'].std()
        
        # Encontrar anomalías
        anomalias = df[df['monto'] > (media + umbral_desviacion * std)]
        
        return anomalias.to_dict('records')
    
    def verificar_cuadre(self, hoja_id: int, saldo_esperado: float) -> Dict:
        """
        Verifica si el saldo calculado coincide con un saldo esperado.
        
        Útil para conciliación bancaria.
        
        Returns:
            Dict con resultado de la verificación
        """
        saldo_sistema = self.obtener_saldo_cuenta(hoja_id)
        diferencia = saldo_sistema - saldo_esperado
        
        return {
            "saldo_sistema": saldo_sistema,
            "saldo_esperado": saldo_esperado,
            "diferencia": diferencia,
            "cuadra": abs(diferencia) < 0.01,  # Tolerancia de 1 centavo
            "mensaje": "✅ Cuadra correctamente" if abs(diferencia) < 0.01 
                      else f"⚠️ Diferencia de {diferencia:.2f}"
        }
