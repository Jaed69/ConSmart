"""
ConSmart - Sistema Contable
===========================
Punto de entrada principal de la aplicación.

Ejecutar con: flet run main.py
"""

import flet as ft
import sys
from pathlib import Path

# Agregar src al path
sys.path.insert(0, str(Path(__file__).parent))

from src.config import APP_CONFIG, UI_CONFIG
from src.database import get_db
from src.ui.theme import AppTheme, Icons
from src.ui.views import DashboardView, EntryView, HistoryView, AdminView


def main(page: ft.Page):
    """Función principal de la aplicación."""
    
    # Configuración de la ventana
    page.title = f"{APP_CONFIG['nombre']} v{APP_CONFIG['version']}"
    page.window.width = UI_CONFIG['window_width']
    page.window.height = UI_CONFIG['window_height']
    page.theme_mode = ft.ThemeMode.LIGHT
    page.theme = AppTheme.get_theme()
    page.padding = 0
    
    # Inicializar base de datos
    db = get_db()
    print("✅ Base de datos inicializada")
    
    # Estado de navegación
    current_route = "/"
    
    # Barra de navegación lateral
    rail = ft.NavigationRail(
        selected_index=0,
        label_type=ft.NavigationRailLabelType.ALL,
        min_width=80,
        min_extended_width=200,
        leading=ft.Container(
            content=ft.Column([
                ft.Icon(ft.Icons.ACCOUNT_BALANCE_WALLET, size=32, color=AppTheme.PRIMARY),
                ft.Text("ConSmart", size=12, weight=ft.FontWeight.BOLD),
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=4),
            padding=ft.padding.symmetric(vertical=16),
        ),
        destinations=[
            ft.NavigationRailDestination(
                icon=Icons.DASHBOARD,
                selected_icon=Icons.DASHBOARD,
                label="Dashboard",
            ),
            ft.NavigationRailDestination(
                icon=Icons.MONEY,
                selected_icon=Icons.MONEY,
                label="Registro",
            ),
            ft.NavigationRailDestination(
                icon=Icons.HISTORY,
                selected_icon=Icons.HISTORY,
                label="Historial",
            ),
            ft.NavigationRailDestination(
                icon=Icons.SETTINGS,
                selected_icon=Icons.SETTINGS,
                label="Config",
            ),
        ],
        on_change=lambda e: cambiar_vista(e.control.selected_index),
        bgcolor=ft.Colors.WHITE,
    )
    
    # Contenedor principal de vistas
    vista_container = ft.Container(
        expand=True,
        padding=20,
        bgcolor=AppTheme.BACKGROUND,
    )
    
    def cambiar_vista(index: int):
        """Cambia la vista según el índice del rail."""
        nonlocal current_route
        
        if index == 0:
            vista_container.content = DashboardView(page).build()
            current_route = "/"
        elif index == 1:
            vista_container.content = EntryView(page).build()
            current_route = "/registro"
        elif index == 2:
            vista_container.content = HistoryView(page).build()
            current_route = "/historial"
        elif index == 3:
            vista_container.content = AdminView(page).build()
            current_route = "/admin"
        
        page.update()
    
    def route_change(e):
        """Maneja cambios de ruta programáticos."""
        if page.route == "/registro":
            rail.selected_index = 1
            cambiar_vista(1)
        elif page.route == "/historial":
            rail.selected_index = 2
            cambiar_vista(2)
        elif page.route == "/admin":
            rail.selected_index = 3
            cambiar_vista(3)
        else:
            rail.selected_index = 0
            cambiar_vista(0)
    
    page.on_route_change = route_change
    
    # Vista inicial
    cambiar_vista(0)
    
    # Layout principal
    page.add(
        ft.Row([
            rail,
            ft.VerticalDivider(width=1),
            vista_container,
        ], expand=True)
    )


if __name__ == "__main__":
    ft.app(target=main)
