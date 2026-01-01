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
    
    def construir_app_principal():
        """Construye la interfaz principal de la aplicación."""
        
        sesion = auth.sesion
        
        # Contenedor para las vistas
        vista_actual = [None]  # Usar lista para permitir modificación en closure
        
        def crear_vista_dashboard():
            print("DEBUG: Creando vista Dashboard")
            v = DashboardView(page).build()
            print(f"DEBUG: Dashboard creado: {type(v)}")
            return v
        
        def crear_vista_registro():
            print("DEBUG: Creando vista Registro")
            v = EntryView(page).build()
            print(f"DEBUG: Registro creado: {type(v)}")
            return v
        
        def crear_vista_historial():
            print("DEBUG: Creando vista Historial")
            v = HistoryView(page).build()
            print(f"DEBUG: Historial creado: {type(v)}")
            return v
        
        def crear_vista_admin():
            print("DEBUG: Creando vista Admin")
            v = AdminView(page).build()
            print(f"DEBUG: Admin creado: {type(v)}")
            return v
        
        # Mapeo de índice a vista
        vistas = [crear_vista_dashboard]
        destinations = [
            ft.NavigationRailDestination(icon=ft.Icons.DASHBOARD, label="Dashboard"),
        ]
        
        if auth.puede('puede_registrar'):
            destinations.append(ft.NavigationRailDestination(icon=ft.Icons.ADD_CIRCLE, label="Registro"))
            vistas.append(crear_vista_registro)
        
        if auth.puede('puede_ver_historial'):
            destinations.append(ft.NavigationRailDestination(icon=ft.Icons.HISTORY, label="Historial"))
            vistas.append(crear_vista_historial)
        
        if auth.puede('puede_gestionar_config') or auth.es_admin():
            destinations.append(ft.NavigationRailDestination(icon=ft.Icons.SETTINGS, label="Config"))
            vistas.append(crear_vista_admin)
        
        # Contenedor de contenido
        contenido = ft.Container(
            content=crear_vista_dashboard(),
            expand=True,
            padding=20,
            bgcolor="#FAFAFA",
        )
        
        def cambiar_vista(e):
            idx = e.control.selected_index
            if idx < len(vistas):
                try:
                    nueva_vista = vistas[idx]()
                    contenido.content = nueva_vista
                    page.update()
                except Exception as ex:
                    print(f"ERROR en vista {idx}: {ex}")
                    import traceback
                    traceback.print_exc()
        
        # Header del rail
        header = ft.Container(
            content=ft.Column([
                ft.Icon(ft.Icons.ACCOUNT_BALANCE_WALLET, size=32, color=AppTheme.PRIMARY),
                ft.Text("ConSmart", size=11, weight=ft.FontWeight.BOLD),
                ft.Text(sesion.username if sesion else "", size=9, color=AppTheme.TEXT_SECONDARY),
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=2),
            padding=10,
        )
        
        # Footer del rail
        footer = ft.Container(
            content=ft.IconButton(
                icon=ft.Icons.LOGOUT,
                icon_color=AppTheme.ERROR,
                tooltip="Cerrar sesión",
                on_click=lambda e: cerrar_sesion(),
            ),
            padding=10,
        )
        
        rail = ft.NavigationRail(
            selected_index=0,
            label_type=ft.NavigationRailLabelType.ALL,
            min_width=80,
            leading=header,
            trailing=footer,
            destinations=destinations,
            on_change=cambiar_vista,
            bgcolor=ft.Colors.WHITE,
        )
        
        return ft.Row(
            controls=[rail, ft.VerticalDivider(width=1), contenido],
            expand=True,
        )
    
    def mostrar_login():
        """Muestra la pantalla de login simple."""
        
        txt_usuario = ft.TextField(label="Usuario", width=300)
        txt_password = ft.TextField(label="Contraseña", password=True, width=300)
        lbl_error = ft.Text("", color=AppTheme.ERROR)
        
        def hacer_login(e):
            username = txt_usuario.value or ""
            password = txt_password.value or ""
            
            if not username or not password:
                lbl_error.value = "Complete todos los campos"
                page.update()
                return
            
            exito, mensaje = auth.login(username, password)
            if exito:
                on_login_exitoso()
            else:
                lbl_error.value = mensaje
                page.update()
        
        login_card = ft.Card(
            content=ft.Container(
                content=ft.Column([
                    ft.Icon(ft.Icons.ACCOUNT_BALANCE_WALLET, size=64, color=AppTheme.PRIMARY),
                    ft.Text("ConSmart", size=24, weight=ft.FontWeight.BOLD),
                    ft.Container(height=20),
                    txt_usuario,
                    txt_password,
                    lbl_error,
                    ft.Container(height=10),
                    ft.Button(
                        content=ft.Text("Iniciar Sesión"),
                        width=300,
                        on_click=hacer_login,
                    ),
                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                padding=40,
            ),
        )
        
        page.clean()
        page.add(
            ft.Container(
                content=login_card,
                expand=True,
                alignment=ft.Alignment(0, 0),
            )
        )
    
    def on_login_exitoso():
        """Callback cuando el login es exitoso."""
        print("DEBUG: on_login_exitoso llamado")
        try:
            page.clean()
            app_content = construir_app_principal()
            print(f"DEBUG: app_content tipo: {type(app_content)}")
            page.add(app_content)
            page.title = f"{APP_CONFIG['nombre']} - {auth.sesion.nombre_completo}"
            print("DEBUG: page.add() completado")
        except Exception as e:
            print(f"ERROR en on_login_exitoso: {e}")
            import traceback
            traceback.print_exc()
    
    def cerrar_sesion():
        """Cierra la sesión actual."""
        auth.logout()
        page.title = f"{APP_CONFIG['nombre']} v{APP_CONFIG['version']}"
        mostrar_login()
    
    # Verificar si ya hay sesión activa
    if auth.esta_autenticado():
        page.add(construir_app_principal())
    else:
        mostrar_login()


if __name__ == "__main__":
    ft.run(main)
