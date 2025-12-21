"""
ConSmart - Vista de Administración
==================================
Panel para gestionar hojas, locales y categorías.
"""

import flet as ft

from src.ui.theme import AppTheme, Styles, Icons
from src.logic import ConfigService


class AdminView(ft.UserControl):
    """
    Vista de administración del sistema.
    Permite gestionar hojas, locales y categorías.
    """
    
    def __init__(self, page: ft.Page):
        super().__init__()
        self.page = page
        self.config_service = ConfigService()
    
    def build(self):
        # Tabs para cada sección
        self.tabs = ft.Tabs(
            selected_index=0,
            tabs=[
                ft.Tab(text="Hojas/Cuentas", icon=Icons.ACCOUNT),
                ft.Tab(text="Locales", icon=Icons.STORE),
                ft.Tab(text="Categorías", icon=Icons.CATEGORY),
            ],
            on_change=self._on_tab_change,
        )
        
        # Contenido de cada tab
        self.tab_hojas = self._crear_tab_hojas()
        self.tab_locales = self._crear_tab_locales()
        self.tab_categorias = self._crear_tab_categorias()
        
        # Contenedor de contenido
        self.contenido = ft.Container(
            content=self.tab_hojas,
            expand=True,
        )
        
        return ft.Column([
            ft.Container(
                content=ft.Text("⚙️ Configuración del Sistema", **Styles.titulo_pagina()),
                padding=ft.padding.only(bottom=16),
            ),
            self.tabs,
            ft.Divider(),
            self.contenido,
        ], expand=True)
    
    def _on_tab_change(self, e):
        """Cambia el contenido según el tab seleccionado."""
        tabs_contenido = [self.tab_hojas, self.tab_locales, self.tab_categorias]
        self.contenido.content = tabs_contenido[self.tabs.selected_index]
        self.contenido.update()
    
    # ==================== TAB HOJAS ====================
    
    def _crear_tab_hojas(self) -> ft.Control:
        """Crea el contenido del tab de hojas."""
        self.input_hoja_nombre = ft.TextField(
            label="Nombre de la cuenta",
            width=250,
            **Styles.input_excel(),
        )
        
        self.dd_hoja_tipo = ft.Dropdown(
            label="Tipo",
            options=[
                ft.dropdown.Option("banco", "Banco"),
                ft.dropdown.Option("efectivo", "Efectivo"),
            ],
            value="banco",
            width=150,
        )
        
        self.dd_hoja_moneda = ft.Dropdown(
            label="Moneda",
            options=[
                ft.dropdown.Option("PEN", "Soles (PEN)"),
                ft.dropdown.Option("USD", "Dólares (USD)"),
            ],
            value="PEN",
            width=150,
        )
        
        self.lista_hojas = ft.ListView(expand=True, spacing=8)
        self._cargar_hojas()
        
        return ft.Column([
            ft.Container(
                content=ft.Row([
                    self.input_hoja_nombre,
                    self.dd_hoja_tipo,
                    self.dd_hoja_moneda,
                    ft.ElevatedButton(
                        "Agregar",
                        icon=Icons.ADD,
                        on_click=self._agregar_hoja,
                    ),
                ], spacing=12),
                padding=ft.padding.symmetric(vertical=16),
            ),
            ft.Text("Cuentas registradas:", **Styles.subtitulo()),
            ft.Container(
                content=self.lista_hojas,
                expand=True,
                bgcolor=ft.colors.WHITE,
                border_radius=8,
                padding=12,
            ),
        ], expand=True)
    
    def _cargar_hojas(self):
        """Carga las hojas en la lista."""
        hojas = self.config_service.obtener_hojas()
        self.lista_hojas.controls = [
            self._crear_item_hoja(h) for h in hojas
        ]
    
    def _crear_item_hoja(self, hoja: dict) -> ft.Control:
        """Crea un item de la lista de hojas."""
        moneda_texto = "S/" if hoja['moneda'] == 'PEN' else "$"
        tipo_texto = "🏦 Banco" if hoja['tipo'] == 'banco' else "💵 Efectivo"
        
        return ft.Container(
            content=ft.Row([
                ft.Icon(Icons.ACCOUNT, color=AppTheme.PRIMARY),
                ft.Column([
                    ft.Text(hoja['nombre'], weight=ft.FontWeight.W_600),
                    ft.Text(f"{tipo_texto} • {moneda_texto}", size=12, color=AppTheme.TEXT_SECONDARY),
                ], spacing=2),
                ft.Row([
                    ft.IconButton(
                        icon=Icons.DELETE,
                        icon_color=AppTheme.ERROR,
                        tooltip="Eliminar",
                        on_click=lambda e, id=hoja['id']: self._eliminar_hoja(id),
                    ),
                ]),
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            padding=12,
            border=ft.border.all(1, AppTheme.DIVIDER),
            border_radius=8,
        )
    
    def _agregar_hoja(self, e):
        """Agrega una nueva hoja."""
        nombre = self.input_hoja_nombre.value.strip()
        if not nombre:
            self._mostrar_error("Ingrese un nombre para la cuenta")
            return
        
        exito, _, error = self.config_service.crear_hoja(
            nombre,
            self.dd_hoja_tipo.value,
            self.dd_hoja_moneda.value
        )
        
        if exito:
            self.input_hoja_nombre.value = ""
            self._cargar_hojas()
            self.lista_hojas.update()
            self._mostrar_exito("Cuenta agregada correctamente")
        else:
            self._mostrar_error(error)
    
    def _eliminar_hoja(self, hoja_id: int):
        """Elimina una hoja."""
        self.config_service.eliminar_hoja(hoja_id)
        self._cargar_hojas()
        self.lista_hojas.update()
    
    # ==================== TAB LOCALES ====================
    
    def _crear_tab_locales(self) -> ft.Control:
        """Crea el contenido del tab de locales."""
        self.input_local_nombre = ft.TextField(
            label="Nombre del local",
            width=300,
            **Styles.input_excel(),
        )
        
        self.lista_locales = ft.ListView(expand=True, spacing=8)
        self._cargar_locales()
        
        return ft.Column([
            ft.Container(
                content=ft.Row([
                    self.input_local_nombre,
                    ft.ElevatedButton(
                        "Agregar",
                        icon=Icons.ADD,
                        on_click=self._agregar_local,
                    ),
                ], spacing=12),
                padding=ft.padding.symmetric(vertical=16),
            ),
            ft.Text("Locales registrados:", **Styles.subtitulo()),
            ft.Container(
                content=self.lista_locales,
                expand=True,
                bgcolor=ft.colors.WHITE,
                border_radius=8,
                padding=12,
            ),
        ], expand=True)
    
    def _cargar_locales(self):
        """Carga los locales en la lista."""
        locales = self.config_service.obtener_locales()
        self.lista_locales.controls = [
            self._crear_item_local(l) for l in locales
        ]
    
    def _crear_item_local(self, local: dict) -> ft.Control:
        """Crea un item de la lista de locales."""
        return ft.Container(
            content=ft.Row([
                ft.Icon(Icons.STORE, color=AppTheme.SECONDARY),
                ft.Text(local['nombre'], weight=ft.FontWeight.W_600),
                ft.IconButton(
                    icon=Icons.DELETE,
                    icon_color=AppTheme.ERROR,
                    tooltip="Eliminar",
                    on_click=lambda e, id=local['id']: self._eliminar_local(id),
                ),
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            padding=12,
            border=ft.border.all(1, AppTheme.DIVIDER),
            border_radius=8,
        )
    
    def _agregar_local(self, e):
        """Agrega un nuevo local."""
        nombre = self.input_local_nombre.value.strip()
        if not nombre:
            self._mostrar_error("Ingrese un nombre para el local")
            return
        
        exito, _, error = self.config_service.crear_local(nombre)
        
        if exito:
            self.input_local_nombre.value = ""
            self._cargar_locales()
            self.lista_locales.update()
            self._mostrar_exito("Local agregado correctamente")
        else:
            self._mostrar_error(error)
    
    def _eliminar_local(self, local_id: int):
        """Elimina un local."""
        self.config_service.eliminar_local(local_id)
        self._cargar_locales()
        self.lista_locales.update()
    
    # ==================== TAB CATEGORÍAS ====================
    
    def _crear_tab_categorias(self) -> ft.Control:
        """Crea el contenido del tab de categorías."""
        locales = self.config_service.obtener_locales()
        
        self.dd_cat_local = ft.Dropdown(
            label="Local",
            options=[ft.dropdown.Option(key=str(l['id']), text=l['nombre']) for l in locales],
            width=200,
            on_change=self._on_cat_local_change,
        )
        
        self.input_cat_nombre = ft.TextField(
            label="Nombre de la categoría",
            width=250,
            **Styles.input_excel(),
        )
        
        self.dd_cat_tipo = ft.Dropdown(
            label="Tipo",
            options=[
                ft.dropdown.Option("ingreso", "Solo Ingreso"),
                ft.dropdown.Option("egreso", "Solo Egreso"),
                ft.dropdown.Option("ambos", "Ambos"),
            ],
            value="ambos",
            width=150,
        )
        
        self.lista_categorias = ft.ListView(expand=True, spacing=8)
        
        return ft.Column([
            ft.Container(
                content=ft.Row([
                    self.dd_cat_local,
                    self.input_cat_nombre,
                    self.dd_cat_tipo,
                    ft.ElevatedButton(
                        "Agregar",
                        icon=Icons.ADD,
                        on_click=self._agregar_categoria,
                    ),
                ], spacing=12),
                padding=ft.padding.symmetric(vertical=16),
            ),
            ft.Text("Categorías del local seleccionado:", **Styles.subtitulo()),
            ft.Container(
                content=self.lista_categorias,
                expand=True,
                bgcolor=ft.colors.WHITE,
                border_radius=8,
                padding=12,
            ),
        ], expand=True)
    
    def _on_cat_local_change(self, e):
        """Cuando cambia el local, carga sus categorías."""
        if self.dd_cat_local.value:
            self._cargar_categorias(int(self.dd_cat_local.value))
            self.lista_categorias.update()
    
    def _cargar_categorias(self, local_id: int):
        """Carga las categorías de un local."""
        categorias = self.config_service.obtener_categorias_por_local(local_id)
        self.lista_categorias.controls = [
            self._crear_item_categoria(c) for c in categorias
        ]
    
    def _crear_item_categoria(self, categoria: dict) -> ft.Control:
        """Crea un item de la lista de categorías."""
        tipo_icono = {
            "ingreso": ("↗️", AppTheme.INGRESO),
            "egreso": ("↘️", AppTheme.EGRESO),
            "ambos": ("↔️", AppTheme.INFO),
        }
        icono, color = tipo_icono.get(categoria.get('tipo', 'ambos'), ("↔️", AppTheme.INFO))
        
        return ft.Container(
            content=ft.Row([
                ft.Text(icono, size=16),
                ft.Text(categoria['nombre'], weight=ft.FontWeight.W_600),
                ft.Text(categoria.get('tipo', ''), size=12, color=color),
                ft.IconButton(
                    icon=Icons.DELETE,
                    icon_color=AppTheme.ERROR,
                    tooltip="Eliminar",
                    on_click=lambda e, id=categoria['id']: self._eliminar_categoria(id),
                ),
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            padding=12,
            border=ft.border.all(1, AppTheme.DIVIDER),
            border_radius=8,
        )
    
    def _agregar_categoria(self, e):
        """Agrega una nueva categoría."""
        if not self.dd_cat_local.value:
            self._mostrar_error("Seleccione un local")
            return
        
        nombre = self.input_cat_nombre.value.strip()
        if not nombre:
            self._mostrar_error("Ingrese un nombre para la categoría")
            return
        
        exito, _, error = self.config_service.crear_categoria(
            nombre,
            int(self.dd_cat_local.value),
            self.dd_cat_tipo.value
        )
        
        if exito:
            self.input_cat_nombre.value = ""
            self._cargar_categorias(int(self.dd_cat_local.value))
            self.lista_categorias.update()
            self._mostrar_exito("Categoría agregada correctamente")
        else:
            self._mostrar_error(error)
    
    def _eliminar_categoria(self, categoria_id: int):
        """Elimina una categoría."""
        self.config_service.eliminar_categoria(categoria_id)
        if self.dd_cat_local.value:
            self._cargar_categorias(int(self.dd_cat_local.value))
            self.lista_categorias.update()
    
    # ==================== HELPERS ====================
    
    def _mostrar_error(self, mensaje: str):
        """Muestra un mensaje de error."""
        self.page.snack_bar = ft.SnackBar(
            content=ft.Text(f"❌ {mensaje}"),
            bgcolor=AppTheme.ERROR,
        )
        self.page.snack_bar.open = True
        self.page.update()
    
    def _mostrar_exito(self, mensaje: str):
        """Muestra un mensaje de éxito."""
        self.page.snack_bar = ft.SnackBar(
            content=ft.Text(f"✅ {mensaje}"),
            bgcolor=AppTheme.SUCCESS,
        )
        self.page.snack_bar.open = True
        self.page.update()
