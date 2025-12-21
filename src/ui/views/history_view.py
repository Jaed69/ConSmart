"""
ConSmart - Vista de Historial y Reportes
========================================
Pantalla para revisar, filtrar y analizar movimientos.
"""

import flet as ft
from datetime import date, datetime, timedelta
from typing import Optional

from src.ui.theme import AppTheme, Styles, Icons
from src.ui.components import MovimientosTable, SaldoCard
from src.logic import MovimientoService, ConfigService, BalanceCalculator


class HistoryView:
    """
    Vista de historial con filtros avanzados, estadísticas y visualización mejorada.
    """
    
    def __init__(self, page: ft.Page):
        self.page = page
        self.mov_service = MovimientoService()
        self.config_service = ConfigService()
        self.calculator = BalanceCalculator()
        
        self._hoja_seleccionada_id: int = None
        self._local_seleccionado_id: int = None
    
    def build(self) -> ft.Control:
        """Construye y retorna el control."""
        # Cargar datos iniciales
        self.hojas = self.config_service.obtener_hojas()
        self.locales = self.config_service.obtener_locales()
        
        # ===== FILTROS =====
        self.dd_cuenta = ft.Dropdown(
            label="Cuenta",
            options=[ft.dropdown.Option(key="", text="Todas")] + 
                    [ft.dropdown.Option(key=str(h['id']), text=h['nombre']) for h in self.hojas],
            value="",
            width=150,
            on_change=self._on_filtro_change,
            dense=True,
        )
        
        self.dd_local = ft.Dropdown(
            label="Local",
            options=[ft.dropdown.Option(key="", text="Todos")] +
                    [ft.dropdown.Option(key=str(l['id']), text=l['nombre']) for l in self.locales],
            value="",
            width=150,
            on_change=self._on_filtro_change,
            dense=True,
        )
        
        # Filtros de fecha con opciones rápidas
        self.dd_periodo = ft.Dropdown(
            label="Período",
            options=[
                ft.dropdown.Option(key="hoy", text="Hoy"),
                ft.dropdown.Option(key="semana", text="Esta semana"),
                ft.dropdown.Option(key="mes", text="Este mes"),
                ft.dropdown.Option(key="mes_anterior", text="Mes anterior"),
                ft.dropdown.Option(key="trimestre", text="Últimos 3 meses"),
                ft.dropdown.Option(key="año", text="Este año"),
                ft.dropdown.Option(key="personalizado", text="Personalizado"),
            ],
            value="mes",
            width=140,
            on_change=self._on_periodo_change,
            dense=True,
        )
        
        self.txt_fecha_desde = ft.TextField(
            label="Desde",
            width=120,
            value=date.today().replace(day=1).strftime("%Y-%m-%d"),
            dense=True,
            text_size=12,
            visible=False,
        )
        
        self.txt_fecha_hasta = ft.TextField(
            label="Hasta",
            width=120,
            value=date.today().strftime("%Y-%m-%d"),
            dense=True,
            text_size=12,
            visible=False,
        )
        
        self.txt_buscar = ft.TextField(
            label="Buscar descripción",
            width=200,
            prefix_icon=Icons.SEARCH,
            dense=True,
            text_size=12,
            on_change=self._on_buscar_change,
        )
        
        self.btn_aplicar = ft.ElevatedButton(
            "Aplicar filtros",
            icon=Icons.FILTER,
            on_click=self._aplicar_filtros,
            bgcolor=AppTheme.PRIMARY,
            color=ft.Colors.WHITE,
        )
        
        self.btn_limpiar_filtros = ft.TextButton(
            "Limpiar",
            on_click=self._limpiar_filtros,
        )
        
        # ===== TARJETAS DE RESUMEN =====
        self.card_total_ingresos = self._crear_card_resumen(
            "Total Ingresos", "S/ 0.00", Icons.ADD, AppTheme.INGRESO
        )
        self.card_total_egresos = self._crear_card_resumen(
            "Total Egresos", "S/ 0.00", Icons.DELETE, AppTheme.EGRESO
        )
        self.card_saldo_periodo = self._crear_card_resumen(
            "Balance del Período", "S/ 0.00", Icons.ACCOUNT, AppTheme.PRIMARY
        )
        self.card_num_movimientos = self._crear_card_resumen(
            "N° Movimientos", "0", Icons.HISTORY, AppTheme.INFO
        )
        
        # ===== TABLA DE MOVIMIENTOS =====
        self.tabla = MovimientosTable(
            on_edit=self._editar_movimiento,
            on_delete=self._eliminar_movimiento,
            page=self.page,
        )
        
        # ===== PAGINACIÓN =====
        self.lbl_paginacion = ft.Text(
            "Mostrando 0 de 0 movimientos",
            size=12,
            color=AppTheme.TEXT_SECONDARY,
        )
        
        self.btn_exportar = ft.ElevatedButton(
            "📥 Exportar a Excel",
            on_click=self._exportar_excel,
            bgcolor=AppTheme.SUCCESS,
            color=ft.Colors.WHITE,
        )
        
        # ===== LAYOUT PRINCIPAL =====
        return ft.Column([
            # Header
            ft.Container(
                content=ft.Row([
                    ft.Row([
                        ft.Icon(Icons.HISTORY, color=AppTheme.PRIMARY, size=28),
                        ft.Text("Historial de Movimientos", **Styles.titulo_pagina()),
                    ], spacing=12),
                    self.btn_exportar,
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                padding=ft.padding.only(bottom=16),
            ),
            
            # Barra de filtros
            ft.Container(
                content=ft.Column([
                    ft.Row([
                        self.dd_cuenta,
                        self.dd_local,
                        self.dd_periodo,
                        self.txt_fecha_desde,
                        self.txt_fecha_hasta,
                        self.txt_buscar,
                        self.btn_aplicar,
                        self.btn_limpiar_filtros,
                    ], spacing=12, wrap=True),
                ]),
                padding=16,
                bgcolor=ft.Colors.WHITE,
                border_radius=8,
                border=ft.border.all(1, AppTheme.DIVIDER),
            ),
            
            ft.Container(height=16),
            
            # Tarjetas de resumen
            ft.Row([
                self.card_total_ingresos,
                self.card_total_egresos,
                self.card_saldo_periodo,
                self.card_num_movimientos,
            ], spacing=16, wrap=True),
            
            ft.Container(height=16),
            
            # Tabla de movimientos
            ft.Container(
                content=ft.Column([
                    ft.Row([
                        ft.Text("Movimientos", **Styles.subtitulo()),
                        self.lbl_paginacion,
                    ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                    ft.Container(height=8),
                    ft.Container(
                        content=self.tabla.build(),
                        expand=True,
                    ),
                ], expand=True),
                expand=True,
                bgcolor=ft.Colors.WHITE,
                border_radius=8,
                padding=16,
                border=ft.border.all(1, AppTheme.DIVIDER),
            ),
        ], expand=True, scroll=ft.ScrollMode.AUTO)
    
    def _crear_card_resumen(self, titulo: str, valor: str, icono: str, color: str) -> ft.Container:
        """Crea una tarjeta de resumen."""
        return ft.Container(
            content=ft.Column([
                ft.Row([
                    ft.Icon(icono, color=color, size=20),
                    ft.Text(titulo, size=12, color=AppTheme.TEXT_SECONDARY),
                ], spacing=8),
                ft.Text(
                    valor,
                    size=20,
                    weight=ft.FontWeight.BOLD,
                    color=color,
                ),
            ], spacing=4),
            padding=16,
            bgcolor=ft.Colors.WHITE,
            border_radius=8,
            border=ft.border.all(1, AppTheme.DIVIDER),
            width=180,
            data={"titulo": titulo},  # Para identificar la tarjeta
        )
    
    def _actualizar_card(self, card: ft.Container, valor: str):
        """Actualiza el valor de una tarjeta."""
        card.content.controls[1].value = valor
        if self.page:
            card.update()
    
    def _on_periodo_change(self, e):
        """Cuando cambia el período seleccionado."""
        periodo = self.dd_periodo.value
        hoy = date.today()
        
        if periodo == "personalizado":
            self.txt_fecha_desde.visible = True
            self.txt_fecha_hasta.visible = True
        else:
            self.txt_fecha_desde.visible = False
            self.txt_fecha_hasta.visible = False
            
            if periodo == "hoy":
                fecha_desde = hoy
                fecha_hasta = hoy
            elif periodo == "semana":
                fecha_desde = hoy - timedelta(days=hoy.weekday())
                fecha_hasta = hoy
            elif periodo == "mes":
                fecha_desde = hoy.replace(day=1)
                fecha_hasta = hoy
            elif periodo == "mes_anterior":
                primer_dia_mes = hoy.replace(day=1)
                fecha_hasta = primer_dia_mes - timedelta(days=1)
                fecha_desde = fecha_hasta.replace(day=1)
            elif periodo == "trimestre":
                fecha_desde = hoy - timedelta(days=90)
                fecha_hasta = hoy
            elif periodo == "año":
                fecha_desde = hoy.replace(month=1, day=1)
                fecha_hasta = hoy
            else:
                fecha_desde = hoy.replace(day=1)
                fecha_hasta = hoy
            
            self.txt_fecha_desde.value = fecha_desde.strftime("%Y-%m-%d")
            self.txt_fecha_hasta.value = fecha_hasta.strftime("%Y-%m-%d")
        
        if self.page:
            self.page.update()
    
    def _on_filtro_change(self, e):
        """Cuando cambia un filtro."""
        pass  # Esperar a que el usuario presione "Aplicar"
    
    def _on_buscar_change(self, e):
        """Cuando cambia el texto de búsqueda."""
        pass  # Búsqueda en tiempo real podría ser muy pesada
    
    def _aplicar_filtros(self, e):
        """Aplica los filtros y actualiza la tabla."""
        self._cargar_datos()
    
    def _limpiar_filtros(self, e):
        """Limpia todos los filtros."""
        self.dd_cuenta.value = ""
        self.dd_local.value = ""
        self.dd_periodo.value = "mes"
        self.txt_buscar.value = ""
        self._on_periodo_change(None)
        
        if self.page:
            self.page.update()
        
        self._cargar_datos()
    
    def _cargar_datos(self):
        """Carga los datos según los filtros aplicados."""
        # Obtener parámetros de filtro
        hoja_id = int(self.dd_cuenta.value) if self.dd_cuenta.value else None
        local_id = int(self.dd_local.value) if self.dd_local.value else None
        
        fecha_desde = None
        fecha_hasta = None
        
        try:
            if self.txt_fecha_desde.value:
                fecha_desde = datetime.strptime(self.txt_fecha_desde.value, "%Y-%m-%d").date()
            if self.txt_fecha_hasta.value:
                fecha_hasta = datetime.strptime(self.txt_fecha_hasta.value, "%Y-%m-%d").date()
        except:
            pass
        
        texto_busqueda = self.txt_buscar.value.strip() if self.txt_buscar.value else None
        
        # Cargar datos
        df = self.mov_service.obtener_historial_filtrado(
            hoja_id=hoja_id,
            local_id=local_id,
            fecha_inicio=fecha_desde,
            fecha_fin=fecha_hasta,
            texto_busqueda=texto_busqueda,
        )
        
        self.tabla.cargar_datos(df)
        
        # Actualizar estadísticas
        if not df.empty:
            total_ingresos = df['ingreso'].sum() if 'ingreso' in df.columns else 0
            total_egresos = df['egreso'].sum() if 'egreso' in df.columns else 0
            balance = total_ingresos - total_egresos
            num_movimientos = len(df)
            
            # Determinar moneda
            moneda = "S/"
            if hoja_id:
                hoja = next((h for h in self.hojas if h['id'] == hoja_id), None)
                if hoja and hoja.get('moneda') == 'USD':
                    moneda = "$"
            
            self._actualizar_card(self.card_total_ingresos, f"{moneda} {total_ingresos:,.2f}")
            self._actualizar_card(self.card_total_egresos, f"{moneda} {total_egresos:,.2f}")
            self._actualizar_card(self.card_saldo_periodo, f"{moneda} {balance:,.2f}")
            self._actualizar_card(self.card_num_movimientos, str(num_movimientos))
            
            self.lbl_paginacion.value = f"Mostrando {num_movimientos} movimientos"
        else:
            self._actualizar_card(self.card_total_ingresos, "S/ 0.00")
            self._actualizar_card(self.card_total_egresos, "S/ 0.00")
            self._actualizar_card(self.card_saldo_periodo, "S/ 0.00")
            self._actualizar_card(self.card_num_movimientos, "0")
            self.lbl_paginacion.value = "No hay movimientos"
        
        if self.page:
            self.lbl_paginacion.update()
    
    def _editar_movimiento(self, movimiento_id: int):
        """Abre diálogo para editar un movimiento."""
        # Cargar datos del movimiento
        mov = self.mov_service.obtener_movimiento(movimiento_id)
        if not mov:
            return
        
        # Crear campos del formulario
        txt_fecha = ft.TextField(label="Fecha", value=str(mov.get('fecha', '')), width=200)
        txt_descripcion = ft.TextField(label="Descripción", value=mov.get('descripcion', ''), width=300)
        txt_ingreso = ft.TextField(label="Ingreso", value=str(mov.get('ingreso', 0)), width=150)
        txt_egreso = ft.TextField(label="Egreso", value=str(mov.get('egreso', 0)), width=150)
        
        def guardar_cambios(e):
            # Actualizar movimiento
            datos = {
                'fecha': txt_fecha.value,
                'descripcion': txt_descripcion.value,
                'ingreso': float(txt_ingreso.value or 0),
                'egreso': float(txt_egreso.value or 0),
            }
            exito = self.mov_service.actualizar_movimiento(movimiento_id, datos)
            
            dialog.open = False
            self.page.update()
            
            if exito:
                self._cargar_datos()
                self.page.snack_bar = ft.SnackBar(
                    content=ft.Text("✅ Movimiento actualizado"),
                    bgcolor=AppTheme.SUCCESS,
                )
                self.page.snack_bar.open = True
                self.page.update()
        
        def cerrar(e):
            dialog.open = False
            self.page.update()
        
        dialog = ft.AlertDialog(
            title=ft.Text("Editar Movimiento"),
            content=ft.Column([
                txt_fecha,
                txt_descripcion,
                ft.Row([txt_ingreso, txt_egreso], spacing=16),
            ], tight=True, spacing=16),
            actions=[
                ft.TextButton("Cancelar", on_click=cerrar),
                ft.ElevatedButton("Guardar", on_click=guardar_cambios, bgcolor=AppTheme.PRIMARY),
            ],
        )
        
        self.page.dialog = dialog
        dialog.open = True
        self.page.update()
    
    def _eliminar_movimiento(self, movimiento_id: int):
        """Confirma y elimina un movimiento."""
        def confirmar(e):
            exito = self.mov_service.eliminar_movimiento(movimiento_id)
            dialog.open = False
            self.page.update()
            
            if exito:
                self._cargar_datos()
                self.page.snack_bar = ft.SnackBar(
                    content=ft.Text("✅ Movimiento eliminado"),
                    bgcolor=AppTheme.SUCCESS,
                )
                self.page.snack_bar.open = True
                self.page.update()
        
        def cancelar(e):
            dialog.open = False
            self.page.update()
        
        dialog = ft.AlertDialog(
            title=ft.Text("Confirmar eliminación"),
            content=ft.Text("¿Está seguro de eliminar este movimiento? Esta acción no se puede deshacer."),
            actions=[
                ft.TextButton("Cancelar", on_click=cancelar),
                ft.ElevatedButton("Eliminar", on_click=confirmar, bgcolor=AppTheme.ERROR, color=ft.Colors.WHITE),
            ],
        )
        
        self.page.dialog = dialog
        dialog.open = True
        self.page.update()
    
    def _exportar_excel(self, e):
        """Exporta los datos filtrados a Excel."""
        # TODO: Implementar exportación real
        self.page.snack_bar = ft.SnackBar(
            content=ft.Text("📥 Exportando a Excel... (próximamente)"),
            bgcolor=AppTheme.INFO,
        )
        self.page.snack_bar.open = True
        self.page.update()
