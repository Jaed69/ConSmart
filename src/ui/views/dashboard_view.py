"""
ConSmart - Vista de Dashboard
=============================
Panel principal con resumen de cuentas y métricas.
"""

import flet as ft
from datetime import date, timedelta

from src.ui.theme import AppTheme, Styles, Icons
from src.logic import BalanceCalculator, ConfigService


class DashboardView:
    """
    Dashboard principal con resumen de todas las cuentas.
    """
    
    def __init__(self, page: ft.Page):
        self.page = page
        self.calculator = BalanceCalculator()
        self.config_service = ConfigService()
    
    def build(self) -> ft.Control:
        """Construye y retorna el control."""
        return ft.Column([
            ft.Container(
                content=ft.Text("🏠 Dashboard", **Styles.titulo_pagina()),
                padding=ft.padding.only(bottom=16),
            ),
            
            # Resumen de saldos
            ft.Text("Saldos de Cuentas", **Styles.subtitulo()),
            self._crear_grid_saldos(),
            
            ft.Divider(height=32),
            
            # Acciones rápidas
            ft.Text("Acciones Rápidas", **Styles.subtitulo()),
            self._crear_acciones_rapidas(),
        ], expand=True, scroll=ft.ScrollMode.AUTO)
    
    def _crear_grid_saldos(self) -> ft.Control:
        """Crea el grid con las tarjetas de saldo."""
        saldos = self.calculator.obtener_saldos_todas_cuentas()
        
        tarjetas = []
        for cuenta in saldos:
            moneda = "S/" if cuenta['moneda'] == 'PEN' else "$"
            color = AppTheme.SALDO_POSITIVO if cuenta['saldo'] >= 0 else AppTheme.SALDO_NEGATIVO
            tipo_icon = Icons.ACCOUNT if cuenta['tipo'] == 'banco' else Icons.MONEY
            
            tarjeta = ft.Container(
                content=ft.Column([
                    ft.Row([
                        ft.Icon(tipo_icon, color=AppTheme.PRIMARY, size=20),
                        ft.Text(cuenta['nombre'], weight=ft.FontWeight.W_600),
                    ]),
                    ft.Text(
                        cuenta['tipo'].capitalize(),
                        size=12,
                        color=AppTheme.TEXT_SECONDARY,
                    ),
                    ft.Container(height=8),
                    ft.Text(
                        f"{moneda} {cuenta['saldo']:,.2f}",
                        size=22,
                        weight=ft.FontWeight.BOLD,
                        color=color,
                    ),
                ]),
                padding=16,
                bgcolor=ft.Colors.WHITE,
                border_radius=12,
                border=ft.border.all(1, AppTheme.DIVIDER),
                width=220,
                height=130,
            )
            tarjetas.append(tarjeta)
        
        if not tarjetas:
            return ft.Container(
                content=ft.Text(
                    "No hay cuentas configuradas. Ve a Configuración para agregar.",
                    color=AppTheme.TEXT_SECONDARY,
                ),
                padding=20,
            )
        
        return ft.Container(
            content=ft.Row(tarjetas, wrap=True, spacing=16, run_spacing=16),
            padding=ft.padding.symmetric(vertical=16),
        )
    
    def _crear_acciones_rapidas(self) -> ft.Control:
        """Crea botones de acciones rápidas."""
        return ft.Container(
            content=ft.Row([
                ft.ElevatedButton(
                    "Nuevo Movimiento",
                    icon=Icons.ADD,
                    on_click=lambda e: self._navegar("/registro"),
                ),
                ft.OutlinedButton(
                    "Ver Historial",
                    icon=Icons.HISTORY,
                    on_click=lambda e: self._navegar("/registro"),
                ),
                ft.OutlinedButton(
                    "Configuración",
                    icon=Icons.SETTINGS,
                    on_click=lambda e: self._navegar("/admin"),
                ),
            ], spacing=12),
            padding=ft.padding.symmetric(vertical=16),
        )
    
    def _navegar(self, ruta: str):
        """Navega a otra vista."""
        self.page.go(ruta)
