"""Test mínimo de la UI para diagnosticar el problema."""
import flet as ft
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from src.database import get_db
from src.logic import get_auth
from src.ui.theme import AppTheme, Icons
from src.ui.views import DashboardView

def main(page: ft.Page):
    page.title = "Test UI"
    page.padding = 0
    
    db = get_db()
    auth = get_auth()
    
    def mostrar_app_principal():
        print("DEBUG: Login...")
        exito, msg = auth.login('admin', 'admin123')
        print(f"DEBUG: Login result: {exito} - {msg}")
        
        print("DEBUG: Construyendo dashboard...")
        try:
            dashboard = DashboardView(page).build()
            print(f"DEBUG: Dashboard tipo: {type(dashboard)}")
        except Exception as e:
            print(f"ERROR construyendo dashboard: {e}")
            import traceback
            traceback.print_exc()
            dashboard = ft.Text(f"Error: {e}")
        
        # Crear navegación simple
        rail = ft.NavigationRail(
            selected_index=0,
            label_type=ft.NavigationRailLabelType.ALL,
            destinations=[
                ft.NavigationRailDestination(
                    icon=ft.Icons.HOME,
                    label="Home",
                ),
            ],
            bgcolor=ft.Colors.WHITE,
        )
        
        contenido = ft.Container(
            content=dashboard,
            expand=True,
            padding=20,
            bgcolor="#FAFAFA",
        )
        
        app_row = ft.Row(
            controls=[
                rail,
                ft.VerticalDivider(width=1),
                contenido,
            ],
            expand=True,
        )
        
        print("DEBUG: Limpiando página...")
        page.clean()
        print("DEBUG: Agregando contenido...")
        page.add(app_row)
        print("DEBUG: Listo!")
    
    def on_login_click(e):
        print("DEBUG: Login clicked")
        mostrar_app_principal()
    
    # Mostrar "login" simple
    login_btn = ft.ElevatedButton(
        content=ft.Text("Iniciar Sesión"),
        on_click=on_login_click,
    )
    
    login_view = ft.Container(
        content=ft.Column([
            ft.Text("Login Test", size=32),
            login_btn,
        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
        expand=True,
        alignment=ft.Alignment(0, 0),
    )
    
    page.add(login_view)


if __name__ == "__main__":
    ft.run(main)
