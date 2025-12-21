"""
ConSmart - Vista de Registro de Movimientos
============================================
Pantalla principal tipo Excel para ingreso de movimientos.
"""

import flet as ft
from datetime import date

from src.ui.theme import AppTheme, Styles, Icons
from src.ui.components import ExcelRow, MovimientosTable, SaldoCard
from src.logic import MovimientoService, ConfigService


class EntryView(ft.UserControl):
    """
    Vista principal de ingreso de movimientos tipo Excel.
    Incluye la fila de entrada y el historial con saldo.
    """
    
    def __init__(self, page: ft.Page):
        super().__init__()
        self.page = page
        self.mov_service = MovimientoService()
        self.config_service = ConfigService()
        
        # Cuenta/hoja actualmente seleccionada
        self._hoja_seleccionada_id: int = None
    
    def build(self):
        # Cargar datos iniciales
        self.hojas = self.config_service.obtener_hojas()
        self.locales = self.config_service.obtener_locales()
        
        # Selector de cuenta para ver historial
        self.dd_cuenta_historial = ft.Dropdown(
            label="Ver historial de",
            options=[ft.dropdown.Option(key=str(h['id']), text=h['nombre']) for h in self.hojas],
            width=200,
            on_change=self._on_cuenta_change,
        )
        
        # Tarjeta de saldo
        self.saldo_card = SaldoCard("Saldo Actual", 0.0)
        
        # Fila de ingreso tipo Excel
        self.excel_row = ExcelRow(
            hojas=self.hojas,
            locales=self.locales,
            on_submit=self._guardar_movimiento,
            obtener_categorias=self._obtener_categorias,
            descripciones_sugeridas=self.mov_service.obtener_descripciones_sugeridas(),
        )
        
        # Tabla de historial
        self.tabla = MovimientosTable(
            on_edit=self._editar_movimiento,
            on_delete=self._eliminar_movimiento,
        )
        
        # Filtros de fecha
        self.filtro_fecha_inicio = ft.TextField(
            label="Desde",
            width=130,
            hint_text="YYYY-MM-DD",
            **Styles.input_excel(),
        )
        
        self.filtro_fecha_fin = ft.TextField(
            label="Hasta",
            width=130,
            value=date.today().strftime("%Y-%m-%d"),
            hint_text="YYYY-MM-DD",
            **Styles.input_excel(),
        )
        
        self.btn_filtrar = ft.ElevatedButton(
            "Filtrar",
            icon=Icons.FILTER,
            on_click=self._aplicar_filtro,
        )
        
        self.btn_exportar = ft.OutlinedButton(
            "Exportar",
            icon=Icons.EXPORT,
            on_click=self._exportar_excel,
        )
        
        return ft.Column([
            # Header
            ft.Container(
                content=ft.Row([
                    ft.Text("📊 Registro de Movimientos", **Styles.titulo_pagina()),
                    ft.Row([
                        self.dd_cuenta_historial,
                        self.saldo_card,
                    ], spacing=20),
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                padding=ft.padding.only(bottom=16),
            ),
            
            # Fila de ingreso
            ft.Container(
                content=ft.Column([
                    ft.Text("Nuevo Movimiento", **Styles.subtitulo()),
                    self.excel_row,
                ]),
                padding=ft.padding.only(bottom=16),
            ),
            
            ft.Divider(),
            
            # Filtros y acciones del historial
            ft.Container(
                content=ft.Row([
                    ft.Text("Historial", **Styles.subtitulo()),
                    ft.Row([
                        self.filtro_fecha_inicio,
                        self.filtro_fecha_fin,
                        self.btn_filtrar,
                        self.btn_exportar,
                    ], spacing=8),
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                padding=ft.padding.symmetric(vertical=12),
            ),
            
            # Tabla de movimientos
            ft.Container(
                content=self.tabla,
                expand=True,
                bgcolor=ft.colors.WHITE,
                border_radius=8,
                padding=8,
            ),
        ], expand=True)
    
    def _obtener_categorias(self, local_id: int):
        """Obtiene categorías filtradas por local."""
        return self.config_service.obtener_categorias_por_local(local_id)
    
    def _guardar_movimiento(self, datos: dict):
        """Guarda un nuevo movimiento."""
        exito, nuevo_id, errores = self.mov_service.crear_movimiento(datos)
        
        if exito:
            # Actualizar historial si hay cuenta seleccionada
            if self._hoja_seleccionada_id:
                self._refrescar_historial()
            
            # Mostrar snackbar de éxito
            self.page.snack_bar = ft.SnackBar(
                content=ft.Text("✅ Movimiento guardado correctamente"),
                bgcolor=AppTheme.SUCCESS,
            )
            self.page.snack_bar.open = True
            self.page.update()
        else:
            # Mostrar errores
            self.page.snack_bar = ft.SnackBar(
                content=ft.Text(f"❌ {', '.join(errores)}"),
                bgcolor=AppTheme.ERROR,
            )
            self.page.snack_bar.open = True
            self.page.update()
    
    def _on_cuenta_change(self, e):
        """Cuando cambia la cuenta seleccionada para ver historial."""
        if self.dd_cuenta_historial.value:
            self._hoja_seleccionada_id = int(self.dd_cuenta_historial.value)
            self._refrescar_historial()
    
    def _refrescar_historial(self):
        """Refresca la tabla de historial y el saldo."""
        if not self._hoja_seleccionada_id:
            return
        
        # Obtener fechas de filtro
        fecha_inicio = None
        fecha_fin = None
        
        if self.filtro_fecha_inicio.value:
            try:
                from datetime import datetime
                fecha_inicio = datetime.strptime(self.filtro_fecha_inicio.value, "%Y-%m-%d").date()
            except:
                pass
        
        if self.filtro_fecha_fin.value:
            try:
                from datetime import datetime
                fecha_fin = datetime.strptime(self.filtro_fecha_fin.value, "%Y-%m-%d").date()
            except:
                pass
        
        # Cargar datos
        df = self.mov_service.obtener_historial(
            self._hoja_seleccionada_id,
            fecha_inicio,
            fecha_fin
        )
        
        self.tabla.cargar_datos(df)
        
        # Actualizar saldo
        saldo = self.mov_service.obtener_saldo_actual(self._hoja_seleccionada_id)
        
        # Encontrar la hoja para saber la moneda
        hoja = next((h for h in self.hojas if h['id'] == self._hoja_seleccionada_id), None)
        moneda = "S/" if hoja and hoja.get('moneda') == 'PEN' else "$"
        
        self.saldo_card.titulo = f"Saldo {hoja['nombre'] if hoja else ''}"
        self.saldo_card.saldo = saldo
        self.saldo_card.moneda = moneda
        self.saldo_card.update()
    
    def _aplicar_filtro(self, e):
        """Aplica los filtros de fecha al historial."""
        self._refrescar_historial()
    
    def _editar_movimiento(self, movimiento_id: int):
        """Abre diálogo para editar un movimiento."""
        # TODO: Implementar diálogo de edición
        print(f"Editar movimiento {movimiento_id}")
    
    def _eliminar_movimiento(self, movimiento_id: int):
        """Confirma y elimina un movimiento."""
        def confirmar_eliminar(e):
            # TODO: Implementar eliminación real
            dialog.open = False
            self.page.update()
            self._refrescar_historial()
        
        def cancelar(e):
            dialog.open = False
            self.page.update()
        
        dialog = ft.AlertDialog(
            title=ft.Text("Confirmar eliminación"),
            content=ft.Text("¿Está seguro de eliminar este movimiento?"),
            actions=[
                ft.TextButton("Cancelar", on_click=cancelar),
                ft.ElevatedButton("Eliminar", on_click=confirmar_eliminar, bgcolor=AppTheme.ERROR),
            ],
        )
        
        self.page.dialog = dialog
        dialog.open = True
        self.page.update()
    
    def _exportar_excel(self, e):
        """Exporta el historial a Excel."""
        # TODO: Implementar exportación
        self.page.snack_bar = ft.SnackBar(
            content=ft.Text("📥 Función de exportación próximamente..."),
            bgcolor=AppTheme.INFO,
        )
        self.page.snack_bar.open = True
        self.page.update()
