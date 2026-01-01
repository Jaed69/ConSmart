"""
ConSmart - Vista de Registro de Movimientos
============================================
Pantalla simplificada tipo Excel para ingreso masivo de movimientos.
"""

import flet as ft
from datetime import date

from src.ui.theme import AppTheme, Styles, Icons
from src.ui.components import ExcelGrid, SaldoCard
from src.logic import MovimientoService, ConfigService, BalanceCalculator


class EntryView:
    """
    Vista de ingreso masivo de movimientos tipo Excel.
    Optimizada para ingresar múltiples movimientos rápidamente.
    """
    
    def __init__(self, page: ft.Page):
        self.page = page
        self.mov_service = MovimientoService()
        self.config_service = ConfigService()
        self.calculator = BalanceCalculator()
    
    def build(self) -> ft.Control:
        """Construye y retorna el control."""
        # Cargar datos iniciales
        self.hojas = self.config_service.obtener_hojas()
        self.locales = self.config_service.obtener_locales()
        
        # Obtener saldos de todas las cuentas
        saldos = self.calculator.obtener_saldos_todas_cuentas()
        
        # Grid de ingreso masivo tipo Excel
        self.excel_grid = ExcelGrid(
            hojas=self.hojas,
            locales=self.locales,
            on_submit_all=self._guardar_movimientos,
            obtener_categorias=self._obtener_categorias,
            page=self.page,
            filas_iniciales=5,
        )
        
        # Contador de movimientos del día
        movimientos_hoy = self.mov_service.contar_movimientos_hoy()
        
        # Construir grid
        grid_content = self.excel_grid.build()
        
        return ft.Column([
            # Header compacto
            ft.Container(
                content=ft.Row([
                    ft.Row([
                        ft.Icon(Icons.MONEY, color=AppTheme.PRIMARY, size=24),
                        ft.Text("Registro de Movimientos", **Styles.titulo_pagina()),
                    ], spacing=8),
                    ft.Container(
                        content=ft.Row([
                            ft.Icon(Icons.CALENDAR, size=14, color=AppTheme.TEXT_SECONDARY),
                            ft.Text(
                                f"Hoy: {date.today().strftime('%d/%m/%Y')} • {movimientos_hoy} mov.",
                                size=11,
                                color=AppTheme.TEXT_SECONDARY,
                            ),
                        ], spacing=6),
                        padding=ft.Padding.symmetric(horizontal=10, vertical=4),
                        bgcolor=ft.Colors.GREY_100,
                        border_radius=12,
                    ),
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                padding=ft.Padding.only(bottom=12),
            ),
            
            # Grid de ingreso masivo (área principal)
            ft.Container(
                content=grid_content,
                expand=True,
                bgcolor=ft.Colors.WHITE,
            ),
            
            # Barra inferior con saldos compactos
            ft.Container(
                content=ft.Row([
                    ft.Row([
                        ft.Text("💰 Saldos:", size=11, weight=ft.FontWeight.W_600, color=AppTheme.TEXT_SECONDARY),
                    ] + [
                        self._crear_chip_saldo(cuenta['nombre'], cuenta['saldo'], 
                                              "S/" if cuenta.get('moneda') == 'PEN' else "$")
                        for cuenta in saldos
                    ] if saldos else [
                        ft.Text("Sin cuentas", size=11, color=AppTheme.TEXT_DISABLED)
                    ], spacing=8, wrap=True),
                    ft.Text(
                        "Tab: siguiente campo • Seleccione Local para ver Categorías",
                        size=10,
                        color=AppTheme.TEXT_DISABLED,
                    ),
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN, wrap=True),
                padding=ft.Padding.symmetric(horizontal=12, vertical=8),
                bgcolor=ft.Colors.GREY_50,
                border_radius=ft.border_radius.only(top_left=8, top_right=8),
                border=ft.border.only(top=ft.border.BorderSide(1, AppTheme.DIVIDER)),
            ),
        ], expand=True)
    
    def _crear_chip_saldo(self, nombre: str, saldo: float, moneda: str) -> ft.Container:
        """Crea un chip compacto de saldo."""
        color = AppTheme.SALDO_POSITIVO if saldo >= 0 else AppTheme.SALDO_NEGATIVO
        
        return ft.Container(
            content=ft.Row([
                ft.Text(nombre, size=10, color=AppTheme.TEXT_SECONDARY),
                ft.Text(
                    f"{moneda}{saldo:,.0f}",
                    size=11,
                    weight=ft.FontWeight.BOLD,
                    color=color,
                ),
            ], spacing=4),
            padding=ft.Padding.symmetric(horizontal=8, vertical=3),
            bgcolor=ft.Colors.WHITE,
            border_radius=12,
            border=ft.border.all(1, AppTheme.DIVIDER),
        )
    
    def _obtener_categorias(self, local_id: int):
        """Obtiene categorías filtradas por local."""
        return self.config_service.obtener_categorias_por_local(local_id)
    
    def _guardar_movimientos(self, movimientos: list):
        """Guarda múltiples movimientos a la vez."""
        guardados = 0
        errores_total = []
        
        for datos in movimientos:
            exito, nuevo_id, errores = self.mov_service.crear_movimiento(datos)
            if exito:
                guardados += 1
            else:
                errores_total.extend(errores)
        
        if guardados > 0:
            # Mostrar snackbar de éxito
            self.page.snack_bar = ft.SnackBar(
                content=ft.Text(f"✅ {guardados} movimiento(s) guardado(s) correctamente"),
                bgcolor=AppTheme.SUCCESS,
            )
            self.page.snack_bar.open = True
            self.page.update()
            
            # Limpiar filas guardadas
            self.excel_grid.limpiar_guardados()
            
            # Actualizar saldos (reconstruir la vista sería mejor, pero por ahora solo notificamos)
            self._actualizar_saldos()
        
        if errores_total:
            self.page.snack_bar = ft.SnackBar(
                content=ft.Text(f"⚠️ Errores: {', '.join(errores_total[:3])}"),
                bgcolor=AppTheme.WARNING,
            )
            self.page.snack_bar.open = True
            self.page.update()
    
    def _actualizar_saldos(self):
        """Notifica que los saldos se actualizaron."""
        # Los saldos se actualizarán al recargar la vista
        # Por ahora solo actualizamos la página
        if self.page:
            self.page.update()
