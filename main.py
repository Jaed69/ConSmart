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
from src.ui.views import DashboardView, EntryView, HistoryView, AdminView, LoginView
from src.logic import get_auth


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
    
    # Servicio de autenticación
    auth = get_auth()
    
    # Estado de navegación
    current_route = "/"
    
    # Contenedor principal (cambia entre login y app)
    main_container = ft.Container(expand=True)
    
    def construir_app_principal():
        """Construye la interfaz principal de la aplicación."""
        
        sesion = auth.sesion
        
        # Información del usuario en el header del rail
        user_header = ft.Container(
            content=ft.Column([
                ft.Icon(ft.Icons.ACCOUNT_BALANCE_WALLET, size=32, color=AppTheme.PRIMARY),
                ft.Text("ConSmart", size=12, weight=ft.FontWeight.BOLD),
                ft.Divider(height=8),
                ft.Row([
                    ft.Icon(ft.Icons.PERSON, size=14, color=AppTheme.ACCENT),
                    ft.Text(
                        sesion.username if sesion else "",
                        size=10,
                        color=AppTheme.TEXT_SECONDARY,
                    ),
                ], spacing=4, alignment=ft.MainAxisAlignment.CENTER),
                ft.Text(
                    sesion.rol_nombre if sesion else "",
                    size=9,
                    color=AppTheme.TEXT_SECONDARY,
                    italic=True,
                ),
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=2),
            padding=ft.padding.symmetric(vertical=12),
        )
        
        # Determinar destinos disponibles según permisos
        destinations = []
        route_map = {}
        
        # Dashboard siempre visible
        destinations.append(ft.NavigationRailDestination(
            icon=Icons.DASHBOARD,
            selected_icon=Icons.DASHBOARD,
            label="Dashboard",
        ))
        route_map[len(destinations) - 1] = ("dashboard", lambda: DashboardView(page).build())
        
        # Registro - solo si puede registrar
        if auth.puede('puede_registrar'):
            destinations.append(ft.NavigationRailDestination(
                icon=Icons.MONEY,
                selected_icon=Icons.MONEY,
                label="Registro",
            ))
            route_map[len(destinations) - 1] = ("registro", lambda: EntryView(page).build())
        
        # Historial - solo si puede ver historial
        if auth.puede('puede_ver_historial'):
            destinations.append(ft.NavigationRailDestination(
                icon=Icons.HISTORY,
                selected_icon=Icons.HISTORY,
                label="Historial",
            ))
            route_map[len(destinations) - 1] = ("historial", lambda: HistoryView(page).build())
        
        # Config - si puede gestionar config o usuarios
        if auth.puede('puede_gestionar_config') or auth.puede('puede_gestionar_usuarios') or auth.es_admin():
            destinations.append(ft.NavigationRailDestination(
                icon=Icons.SETTINGS,
                selected_icon=Icons.SETTINGS,
                label="Config",
            ))
            route_map[len(destinations) - 1] = ("admin", lambda: AdminView(page).build())
        
        # Contenedor de vistas
        vista_container = ft.Container(
            expand=True,
            padding=20,
            bgcolor=AppTheme.BACKGROUND,
        )
        
        def cambiar_vista(index: int):
            """Cambia la vista según el índice."""
            if index in route_map:
                _, builder = route_map[index]
                vista_container.content = builder()
                page.update()
        
        # Barra de navegación
        rail = ft.NavigationRail(
            selected_index=0,
            label_type=ft.NavigationRailLabelType.ALL,
            min_width=80,
            min_extended_width=200,
            leading=user_header,
            trailing=ft.Container(
                content=ft.Column([
                    ft.IconButton(
                        icon=ft.Icons.LOGOUT,
                        icon_color=AppTheme.ERROR,
                        tooltip="Cerrar sesión",
                        on_click=lambda e: cerrar_sesion(),
                    ),
                ]),
                padding=ft.padding.only(bottom=16),
            ),
            destinations=destinations,
            on_change=lambda e: cambiar_vista(e.control.selected_index),
            bgcolor=ft.Colors.WHITE,
        )
        
        # Vista inicial
        cambiar_vista(0)
        
        return ft.Row([
            rail,
            ft.VerticalDivider(width=1),
            vista_container,
        ], expand=True)
    
    def mostrar_login():
        """Muestra la pantalla de login."""
        login_view = LoginView(page, on_login_success=on_login_exitoso)
        main_container.content = login_view.build()
        page.update()
    
    def on_login_exitoso():
        """Callback cuando el login es exitoso."""
        main_container.content = construir_app_principal()
        page.title = f"{APP_CONFIG['nombre']} - {auth.sesion.nombre_completo}"
        page.update()
    
    def cerrar_sesion():
        """Cierra la sesión actual."""
        auth.logout()
        page.title = f"{APP_CONFIG['nombre']} v{APP_CONFIG['version']}"
        mostrar_login()
    
    # Verificar si ya hay sesión activa
    if auth.esta_autenticado():
        main_container.content = construir_app_principal()
    else:
        mostrar_login()
    
    # Agregar contenedor principal
    page.add(main_container)


if __name__ == "__main__":
    ft.app(target=main)
