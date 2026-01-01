"""
ConSmart - Configuración de Tema y Estilos
==========================================
Estilos consistentes para toda la aplicación.
"""

import flet as ft


class AppTheme:
    """Configuración del tema Material 3."""
    
    # Colores principales
    PRIMARY = "#1976D2"          # Azul
    PRIMARY_LIGHT = "#42A5F5"
    PRIMARY_DARK = "#0D47A1"
    
    SECONDARY = "#FF9800"        # Naranja
    SECONDARY_LIGHT = "#FFB74D"
    ACCENT = "#7C4DFF"           # Púrpura (accent)
    
    SUCCESS = "#4CAF50"          # Verde
    ERROR = "#F44336"            # Rojo
    WARNING = "#FFC107"          # Amarillo
    INFO = "#2196F3"             # Azul claro
    
    # Colores de texto
    TEXT_PRIMARY = "#212121"
    TEXT_SECONDARY = "#757575"
    TEXT_DISABLED = "#BDBDBD"
    
    # Fondos
    BACKGROUND = "#FAFAFA"
    SURFACE = "#FFFFFF"
    DIVIDER = "#E0E0E0"
    
    # Colores contables
    INGRESO = "#2E7D32"          # Verde oscuro
    EGRESO = "#C62828"           # Rojo oscuro
    SALDO_POSITIVO = "#1B5E20"
    SALDO_NEGATIVO = "#B71C1C"
    
    @classmethod
    def get_theme(cls) -> ft.Theme:
        """Retorna el tema configurado para Flet."""
        return ft.Theme(
            color_scheme=ft.ColorScheme(
                primary=cls.PRIMARY,
                secondary=cls.SECONDARY,
                surface=cls.SURFACE,
                surface_container=cls.BACKGROUND,
            ),
            font_family="Roboto",
        )


class Styles:
    """Estilos predefinidos para componentes."""
    
    # Estilos de texto
    @staticmethod
    def titulo_pagina() -> dict:
        return {
            "size": 24,
            "weight": ft.FontWeight.BOLD,
            "color": AppTheme.TEXT_PRIMARY,
        }
    
    @staticmethod
    def subtitulo() -> dict:
        return {
            "size": 18,
            "weight": ft.FontWeight.W_600,
            "color": AppTheme.TEXT_SECONDARY,
        }
    
    @staticmethod
    def texto_normal() -> dict:
        return {
            "size": 14,
            "color": AppTheme.TEXT_PRIMARY,
        }
    
    @staticmethod
    def texto_pequeño() -> dict:
        return {
            "size": 12,
            "color": AppTheme.TEXT_SECONDARY,
        }
    
    # Estilos de montos
    @staticmethod
    def monto_ingreso() -> dict:
        return {
            "size": 14,
            "weight": ft.FontWeight.W_600,
            "color": AppTheme.INGRESO,
        }
    
    @staticmethod
    def monto_egreso() -> dict:
        return {
            "size": 14,
            "weight": ft.FontWeight.W_600,
            "color": AppTheme.EGRESO,
        }
    
    @staticmethod
    def monto_saldo(valor: float) -> dict:
        return {
            "size": 14,
            "weight": ft.FontWeight.BOLD,
            "color": AppTheme.SALDO_POSITIVO if valor >= 0 else AppTheme.SALDO_NEGATIVO,
        }
    
    # Estilos de campos
    @staticmethod
    def input_excel() -> dict:
        """Estilo para campos tipo Excel (sin bordes pesados)."""
        return {
            "border_color": AppTheme.DIVIDER,
            "focused_border_color": AppTheme.PRIMARY,
            "border_radius": 4,
            "content_padding": ft.Padding.symmetric(horizontal=8, vertical=4),
            "text_size": 13,
        }
    
    @staticmethod
    def dropdown_excel() -> dict:
        """Estilo para dropdowns tipo Excel."""
        return {
            "border_color": AppTheme.DIVIDER,
            "focused_border_color": AppTheme.PRIMARY,
            "border_radius": 4,
            "content_padding": ft.Padding.symmetric(horizontal=8, vertical=0),
            "text_size": 13,
        }


class Icons:
    """Iconos usados en la aplicación."""
    
    ADD = "add"
    SAVE = "save"
    DELETE = "delete"
    EDIT = "edit"
    REFRESH = "refresh"
    FILTER = "filter_list"
    EXPORT = "file_download"
    SETTINGS = "settings"
    DASHBOARD = "dashboard"
    HISTORY = "history"
    CALENDAR = "calendar_today"
    MONEY = "attach_money"
    ACCOUNT = "account_balance"
    STORE = "store"
    CATEGORY = "category"
    SEARCH = "search"
    CLEAR = "clear"
    CHECK = "check_circle"
    WARNING = "warning"
    ERROR = "error"
    INFO = "info"
    PERSON = "person"
    PEOPLE = "people"
    LOCK = "lock"
    LOGOUT = "logout"
    LOGIN = "login"
    SECURITY = "security"
    ADMIN = "admin_panel_settings"
