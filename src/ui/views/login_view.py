"""
ConSmart - Vista de Login
=========================
Pantalla de inicio de sesión.
"""

import flet as ft
from typing import Callable, Optional

from src.ui.theme import AppTheme, Styles, Icons
from src.logic import get_auth


class LoginView:
    """
    Vista de inicio de sesión.
    """
    
    def __init__(self, page: ft.Page, on_login_success: Callable):
        self.page = page
        self.on_login_success = on_login_success
        self.auth = get_auth()
        
        # Campos del formulario
        self.txt_usuario: Optional[ft.TextField] = None
        self.txt_password: Optional[ft.TextField] = None
        self.lbl_error: Optional[ft.Text] = None
        self.btn_login: Optional[ft.ElevatedButton] = None
    
    def build(self) -> ft.Control:
        """Construye la vista de login."""
        
        self.txt_usuario = ft.TextField(
            label="Usuario",
            prefix_icon=Icons.PERSON,
            width=300,
            autofocus=True,
            on_submit=lambda e: self.txt_password.focus(),
        )
        
        self.txt_password = ft.TextField(
            label="Contraseña",
            prefix_icon=Icons.LOCK,
            password=True,
            can_reveal_password=True,
            width=300,
            on_submit=lambda e: self._intentar_login(e),
        )
        
        self.lbl_error = ft.Text(
            "",
            color=AppTheme.ERROR,
            size=14,
            text_align=ft.TextAlign.CENTER,
        )
        
        self.btn_login = ft.Button(
            content=ft.Text("Iniciar Sesión"),
            icon=Icons.LOGIN,
            width=300,
            height=45,
            style=ft.ButtonStyle(
                bgcolor=AppTheme.PRIMARY,
                color=ft.Colors.WHITE,
            ),
            on_click=self._intentar_login,
        )
        
        # Card de login
        login_card = ft.Card(
            content=ft.Container(
                content=ft.Column([
                    # Logo/Header
                    ft.Container(
                        content=ft.Column([
                            ft.Icon(
                                ft.Icons.ACCOUNT_BALANCE_WALLET,
                                size=64,
                                color=AppTheme.PRIMARY,
                            ),
                            ft.Text(
                                "ConSmart",
                                size=28,
                                weight=ft.FontWeight.BOLD,
                                color=AppTheme.PRIMARY,
                            ),
                            ft.Text(
                                "Sistema de Control Contable",
                                size=14,
                                color=AppTheme.TEXT_SECONDARY,
                            ),
                        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=4),
                        padding=ft.Padding.only(bottom=24),
                    ),
                    
                    # Formulario
                    self.txt_usuario,
                    ft.Container(height=8),
                    self.txt_password,
                    ft.Container(height=8),
                    self.lbl_error,
                    ft.Container(height=16),
                    self.btn_login,
                    
                    # Credenciales por defecto (solo para desarrollo)
                    ft.Container(
                        content=ft.Column([
                            ft.Divider(),
                            ft.Text(
                                "Credenciales por defecto:",
                                size=11,
                                color=AppTheme.TEXT_SECONDARY,
                                italic=True,
                            ),
                            ft.Text(
                                "Usuario: admin  |  Contraseña: admin123",
                                size=11,
                                color=AppTheme.TEXT_SECONDARY,
                                selectable=True,
                            ),
                        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=4),
                        padding=ft.Padding.only(top=16),
                    ),
                ], 
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=0,
                ),
                padding=40,
                width=380,
            ),
            elevation=8,
        )
        
        # Layout centrado
        return ft.Container(
            content=ft.Column([
                login_card,
            ], 
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            alignment=ft.MainAxisAlignment.CENTER,
            ),
            expand=True,
            bgcolor=AppTheme.BACKGROUND,
            alignment=ft.Alignment(0, 0),
        )
    
    def _intentar_login(self, e):
        """Intenta iniciar sesión."""
        username = self.txt_usuario.value.strip() if self.txt_usuario.value else ""
        password = self.txt_password.value or ""
        
        # Validaciones básicas
        if not username:
            self._mostrar_error("Ingrese su usuario")
            self.txt_usuario.focus()
            return
        
        if not password:
            self._mostrar_error("Ingrese su contraseña")
            self.txt_password.focus()
            return
        
        # Deshabilitar botón mientras procesa
        self.btn_login.disabled = True
        self.btn_login.content = ft.Text("Verificando...")
        self.page.update()
        
        # Intentar login
        exito, mensaje = self.auth.login(username, password)
        
        if exito:
            self.lbl_error.value = ""
            self.lbl_error.color = AppTheme.SUCCESS
            self.lbl_error.value = f"✓ {mensaje}"
            self.page.update()
            
            # Llamar callback de éxito y salir
            self.on_login_success()
            return
        else:
            self._mostrar_error(mensaje)
            self.btn_login.disabled = False
            self.btn_login.content = ft.Text("Iniciar Sesión")
            self.txt_password.value = ""
            self.txt_password.focus()
            self.page.update()
    
    def _mostrar_error(self, mensaje: str):
        """Muestra un mensaje de error."""
        self.lbl_error.color = AppTheme.ERROR
        self.lbl_error.value = mensaje
        self.page.update()
