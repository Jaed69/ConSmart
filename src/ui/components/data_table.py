"""
ConSmart - Componente Tabla de Movimientos
==========================================
Tabla con historial de movimientos y saldo acumulado.
"""

import flet as ft
from typing import Callable, Optional
import pandas as pd

from src.ui.theme import AppTheme, Styles, Icons


class MovimientosTable:
    """
    Tabla para mostrar movimientos con saldo acumulado.
    Incluye ordenamiento, paginación y formato de moneda.
    """
    
    def __init__(
        self,
        on_edit: Callable[[int], None] = None,
        on_delete: Callable[[int], None] = None,
        page: ft.Page = None,
    ):
        self.on_edit = on_edit
        self.on_delete = on_delete
        self.page = page
        self._data: pd.DataFrame = pd.DataFrame()
        self._control: ft.Control = None
    
    def build(self) -> ft.Control:
        """Construye y retorna el control."""
        self.data_table = ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("Fecha", weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("Local", weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("Categoría", weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("Descripción", weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("Ingreso", weight=ft.FontWeight.BOLD), numeric=True),
                ft.DataColumn(ft.Text("Egreso", weight=ft.FontWeight.BOLD), numeric=True),
                ft.DataColumn(ft.Text("Saldo", weight=ft.FontWeight.BOLD), numeric=True),
                ft.DataColumn(ft.Text("", weight=ft.FontWeight.BOLD)),  # Acciones
            ],
            rows=[],
            border=ft.border.all(1, AppTheme.DIVIDER),
            border_radius=8,
            vertical_lines=ft.border.BorderSide(1, AppTheme.DIVIDER),
            horizontal_lines=ft.border.BorderSide(1, AppTheme.DIVIDER),
            heading_row_color=ft.Colors.GREY_100,
            heading_row_height=45,
            data_row_min_height=40,
            data_row_max_height=50,
        )
        
        self.mensaje_vacio = ft.Container(
            content=ft.Column([
                ft.Icon(Icons.HISTORY, size=48, color=AppTheme.TEXT_DISABLED),
                ft.Text(
                    "No hay movimientos registrados",
                    color=AppTheme.TEXT_SECONDARY,
                    size=14,
                ),
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
            padding=40,
            visible=True,
        )
        
        return ft.Column([
            ft.Container(
                content=self.data_table,
                visible=False,
            ),
            self.mensaje_vacio,
        ], scroll=ft.ScrollMode.AUTO, expand=True)
    
    def cargar_datos(self, df: pd.DataFrame):
        """Carga un DataFrame en la tabla."""
        self._data = df
        self._actualizar_filas()
    
    def _actualizar_filas(self):
        """Actualiza las filas de la tabla."""
        if self._data.empty:
            self.data_table.parent.visible = False
            self.mensaje_vacio.visible = True
        else:
            self.data_table.parent.visible = True
            self.mensaje_vacio.visible = False
            
            filas = []
            for _, row in self._data.iterrows():
                filas.append(self._crear_fila(row))
            
            self.data_table.rows = filas
        
        if self.page:
            self.page.update()
    
    def _crear_fila(self, row) -> ft.DataRow:
        """Crea una fila de la tabla a partir de un registro."""
        # Formato de fecha
        fecha_str = str(row['fecha']) if 'fecha' in row else ""
        
        # Colores según tipo de movimiento
        ingreso = float(row.get('ingreso', 0))
        egreso = float(row.get('egreso', 0))
        saldo = float(row.get('saldo', 0))
        
        return ft.DataRow(
            cells=[
                ft.DataCell(ft.Text(fecha_str, size=12)),
                ft.DataCell(ft.Text(str(row.get('local', '')), size=12)),
                ft.DataCell(ft.Text(str(row.get('categoria', '')), size=12)),
                ft.DataCell(
                    ft.Container(
                        content=ft.Text(
                            str(row.get('descripcion', ''))[:30], 
                            size=12,
                            overflow=ft.TextOverflow.ELLIPSIS,
                        ),
                        width=150,
                    )
                ),
                ft.DataCell(self._crear_monto_ingreso(ingreso)),
                ft.DataCell(self._crear_monto_egreso(egreso)),
                ft.DataCell(self._crear_monto_saldo(saldo)),
                ft.DataCell(
                    ft.Row([
                        ft.IconButton(
                            icon=Icons.EDIT,
                            icon_size=16,
                            icon_color=AppTheme.INFO,
                            tooltip="Editar",
                            on_click=lambda e, id=row['id']: self._on_edit_click(id),
                        ),
                        ft.IconButton(
                            icon=Icons.DELETE,
                            icon_size=16,
                            icon_color=AppTheme.ERROR,
                            tooltip="Eliminar",
                            on_click=lambda e, id=row['id']: self._on_delete_click(id),
                        ),
                    ], spacing=0)
                ),
            ],
        )
    
    def _crear_monto_ingreso(self, valor: float) -> ft.Text:
        """Crea texto formateado para ingreso."""
        if valor > 0:
            return ft.Text(
                f"{valor:,.2f}",
                size=12,
                color=AppTheme.INGRESO,
                weight=ft.FontWeight.W_500,
            )
        return ft.Text("-", size=12, color=AppTheme.TEXT_DISABLED)
    
    def _crear_monto_egreso(self, valor: float) -> ft.Text:
        """Crea texto formateado para egreso."""
        if valor > 0:
            return ft.Text(
                f"{valor:,.2f}",
                size=12,
                color=AppTheme.EGRESO,
                weight=ft.FontWeight.W_500,
            )
        return ft.Text("-", size=12, color=AppTheme.TEXT_DISABLED)
    
    def _crear_monto_saldo(self, valor: float) -> ft.Text:
        """Crea texto formateado para saldo."""
        color = AppTheme.SALDO_POSITIVO if valor >= 0 else AppTheme.SALDO_NEGATIVO
        return ft.Text(
            f"{valor:,.2f}",
            size=12,
            color=color,
            weight=ft.FontWeight.BOLD,
        )
    
    def _on_edit_click(self, id: int):
        """Maneja clic en editar."""
        if self.on_edit:
            self.on_edit(id)
    
    def _on_delete_click(self, id: int):
        """Maneja clic en eliminar."""
        if self.on_delete:
            self.on_delete(id)


class SaldoCard:
    """Tarjeta que muestra el saldo actual de una cuenta."""
    
    def __init__(self, titulo: str, saldo: float, moneda: str = "S/", page: ft.Page = None):
        self.titulo = titulo
        self.saldo = saldo
        self.moneda = moneda
        self.page = page
        self._control: ft.Control = None
    
    def build(self) -> ft.Control:
        """Construye y retorna el control."""
        color_saldo = AppTheme.SALDO_POSITIVO if self.saldo >= 0 else AppTheme.SALDO_NEGATIVO
        
        return ft.Container(
            content=ft.Column([
                ft.Text(self.titulo, size=14, color=AppTheme.TEXT_SECONDARY),
                ft.Text(
                    f"{self.moneda} {self.saldo:,.2f}",
                    size=24,
                    weight=ft.FontWeight.BOLD,
                    color=color_saldo,
                ),
            ]),
            padding=16,
            bgcolor=ft.Colors.WHITE,
            border_radius=8,
            border=ft.border.all(1, AppTheme.DIVIDER),
            width=200,
        )
    
    def actualizar_saldo(self, nuevo_saldo: float):
        """Actualiza el saldo mostrado."""
        self.saldo = nuevo_saldo
        if self.page:
            self.page.update()
