"""
ConSmart - Componente Grid Excel
================================
Grid de entrada tipo Excel para ingresar múltiples movimientos simultáneamente.
"""

import flet as ft
from datetime import date, datetime
from typing import Callable, Optional, List, Dict
import uuid

from src.ui.theme import AppTheme, Styles, Icons
from src.logic import MovimientoValidator


class ExcelGridRow:
    """Una fila individual del grid de Excel."""
    
    def __init__(
        self,
        row_id: str,
        hojas: List[Dict],
        locales: List[Dict],
        obtener_categorias: Callable[[int], List[Dict]],
        on_delete: Callable[[str], None],
        page: ft.Page = None,
        default_hoja_id: str = None,
        default_fecha: str = None,
    ):
        self.row_id = row_id
        self.hojas = hojas
        self.locales = locales
        self.obtener_categorias = obtener_categorias
        self.on_delete = on_delete
        self.page = page
        self.default_hoja_id = default_hoja_id
        self.default_fecha = default_fecha or date.today().strftime("%Y-%m-%d")
        self._categorias_actuales: List[Dict] = []
        self._control: ft.Control = None
    
    def build(self) -> ft.Control:
        """Construye y retorna la fila."""
        # Número de fila
        self.lbl_numero = ft.Text(
            "1",
            size=12,
            color=AppTheme.TEXT_SECONDARY,
            width=25,
            text_align=ft.TextAlign.CENTER,
        )
        
        # Dropdown de Hoja
        self.dd_hoja = ft.Dropdown(
            options=[ft.dropdown.Option(key=str(h['id']), text=h['nombre']) for h in self.hojas],
            value=self.default_hoja_id,
            width=120,
            dense=True,
            content_padding=ft.padding.symmetric(horizontal=8, vertical=0),
            text_size=12,
        )
        
        # Campo de Fecha
        self.txt_fecha = ft.TextField(
            value=self.default_fecha,
            width=100,
            dense=True,
            content_padding=ft.padding.symmetric(horizontal=8, vertical=4),
            text_size=12,
        )
        
        # Dropdown de Local
        self.dd_local = ft.Dropdown(
            options=[ft.dropdown.Option(key=str(l['id']), text=l['nombre']) for l in self.locales],
            width=120,
            dense=True,
            content_padding=ft.padding.symmetric(horizontal=8, vertical=0),
            text_size=12,
            on_change=self._on_local_change,
        )
        
        # Dropdown de Categoría
        self.dd_categoria = ft.Dropdown(
            options=[],
            width=130,
            dense=True,
            content_padding=ft.padding.symmetric(horizontal=8, vertical=0),
            text_size=12,
        )
        
        # Número de documento
        self.txt_doc = ft.TextField(
            width=80,
            dense=True,
            content_padding=ft.padding.symmetric(horizontal=8, vertical=4),
            text_size=12,
        )
        
        # Responsable
        self.txt_responsable = ft.TextField(
            width=100,
            dense=True,
            content_padding=ft.padding.symmetric(horizontal=8, vertical=4),
            text_size=12,
        )
        
        # Descripción
        self.txt_descripcion = ft.TextField(
            width=150,
            dense=True,
            content_padding=ft.padding.symmetric(horizontal=8, vertical=4),
            text_size=12,
        )
        
        # Ingreso
        self.txt_ingreso = ft.TextField(
            value="",
            width=90,
            dense=True,
            text_align=ft.TextAlign.RIGHT,
            keyboard_type=ft.KeyboardType.NUMBER,
            content_padding=ft.padding.symmetric(horizontal=8, vertical=4),
            text_size=12,
            on_change=self._on_ingreso_change,
        )
        
        # Egreso
        self.txt_egreso = ft.TextField(
            value="",
            width=90,
            dense=True,
            text_align=ft.TextAlign.RIGHT,
            keyboard_type=ft.KeyboardType.NUMBER,
            content_padding=ft.padding.symmetric(horizontal=8, vertical=4),
            text_size=12,
            on_change=self._on_egreso_change,
        )
        
        # Indicador de estado
        self.estado = ft.Container(
            width=8,
            height=8,
            border_radius=4,
            bgcolor=AppTheme.DIVIDER,
            tooltip="Pendiente",
        )
        
        # Botón eliminar fila
        self.btn_eliminar = ft.IconButton(
            icon=Icons.DELETE,
            icon_size=16,
            icon_color=AppTheme.TEXT_SECONDARY,
            tooltip="Eliminar fila",
            on_click=lambda e: self.on_delete(self.row_id),
        )
        
        self._control = ft.Container(
            content=ft.Row(
                controls=[
                    self.lbl_numero,
                    self.dd_hoja,
                    self.txt_fecha,
                    self.dd_local,
                    self.dd_categoria,
                    self.txt_doc,
                    self.txt_responsable,
                    self.txt_descripcion,
                    self.txt_ingreso,
                    self.txt_egreso,
                    self.estado,
                    self.btn_eliminar,
                ],
                spacing=4,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            padding=ft.padding.symmetric(horizontal=8, vertical=4),
            border=ft.border.only(bottom=ft.border.BorderSide(1, AppTheme.DIVIDER)),
        )
        
        return self._control
    
    def set_numero(self, numero: int):
        """Establece el número de fila."""
        self.lbl_numero.value = str(numero)
    
    def _on_local_change(self, e):
        """Cuando cambia el local, actualiza las categorías."""
        if self.dd_local.value:
            local_id = int(self.dd_local.value)
            self._categorias_actuales = self.obtener_categorias(local_id)
            self.dd_categoria.options = [
                ft.dropdown.Option(key=str(c['id']), text=c['nombre'])
                for c in self._categorias_actuales
            ]
            self.dd_categoria.value = None
            if self.page:
                self.dd_categoria.update()
    
    def _on_ingreso_change(self, e):
        """Si se ingresa un valor en ingreso, limpia egreso."""
        valor = self.txt_ingreso.value.strip()
        if valor and valor != "0" and valor != "":
            self.txt_egreso.value = ""
            if self.page:
                self.txt_egreso.update()
    
    def _on_egreso_change(self, e):
        """Si se ingresa un valor en egreso, limpia ingreso."""
        valor = self.txt_egreso.value.strip()
        if valor and valor != "0" and valor != "":
            self.txt_ingreso.value = ""
            if self.page:
                self.txt_ingreso.update()
    
    def _validar_monto(self, valor_str: str) -> float:
        """Convierte y valida un monto."""
        if not valor_str or valor_str.strip() == "":
            return 0.0
        try:
            return float(valor_str.replace(",", "").strip())
        except ValueError:
            return 0.0
    
    def obtener_datos(self) -> dict:
        """Obtiene los datos de la fila."""
        return {
            'row_id': self.row_id,
            'hoja_id': int(self.dd_hoja.value) if self.dd_hoja.value else None,
            'fecha': self.txt_fecha.value,
            'local_id': int(self.dd_local.value) if self.dd_local.value else None,
            'categoria_id': int(self.dd_categoria.value) if self.dd_categoria.value else None,
            'num_documento': self.txt_doc.value or "",
            'responsable': self.txt_responsable.value or "",
            'descripcion': self.txt_descripcion.value or "",
            'ingreso': self._validar_monto(self.txt_ingreso.value),
            'egreso': self._validar_monto(self.txt_egreso.value),
        }
    
    def esta_vacia(self) -> bool:
        """Verifica si la fila está vacía (sin datos significativos)."""
        datos = self.obtener_datos()
        return (
            not datos['local_id'] and
            not datos['categoria_id'] and
            not datos['descripcion'] and
            datos['ingreso'] == 0 and
            datos['egreso'] == 0
        )
    
    def marcar_exito(self):
        """Marca la fila como guardada exitosamente."""
        self.estado.bgcolor = AppTheme.SUCCESS
        self.estado.tooltip = "Guardado"
        if self.page:
            self.estado.update()
    
    def marcar_error(self, mensaje: str):
        """Marca la fila con error."""
        self.estado.bgcolor = AppTheme.ERROR
        self.estado.tooltip = mensaje
        if self.page:
            self.estado.update()
    
    def resetear_estado(self):
        """Resetea el indicador de estado."""
        self.estado.bgcolor = AppTheme.DIVIDER
        self.estado.tooltip = "Pendiente"
        if self.page:
            self.estado.update()


class ExcelGrid:
    """
    Grid tipo Excel para ingreso masivo de movimientos.
    Permite agregar múltiples filas y guardarlas todas juntas.
    """
    
    def __init__(
        self,
        hojas: List[Dict],
        locales: List[Dict],
        on_submit_all: Callable[[List[dict]], None],
        obtener_categorias: Callable[[int], List[Dict]],
        page: ft.Page = None,
        filas_iniciales: int = 5,
    ):
        self.hojas = hojas
        self.locales = locales
        self.on_submit_all = on_submit_all
        self.obtener_categorias = obtener_categorias
        self.page = page
        self.filas_iniciales = filas_iniciales
        
        self._filas: Dict[str, ExcelGridRow] = {}
        self._filas_orden: List[str] = []
        self._control: ft.Control = None
    
    def build(self) -> ft.Control:
        """Construye y retorna el grid."""
        
        # Header del grid
        self.header = ft.Container(
            content=ft.Row(
                controls=[
                    ft.Text("#", size=11, weight=ft.FontWeight.BOLD, width=25, text_align=ft.TextAlign.CENTER),
                    ft.Text("Hoja", size=11, weight=ft.FontWeight.BOLD, width=120),
                    ft.Text("Fecha", size=11, weight=ft.FontWeight.BOLD, width=100),
                    ft.Text("Local", size=11, weight=ft.FontWeight.BOLD, width=120),
                    ft.Text("Categoría", size=11, weight=ft.FontWeight.BOLD, width=130),
                    ft.Text("N° Doc", size=11, weight=ft.FontWeight.BOLD, width=80),
                    ft.Text("Responsable", size=11, weight=ft.FontWeight.BOLD, width=100),
                    ft.Text("Descripción", size=11, weight=ft.FontWeight.BOLD, width=150),
                    ft.Text("Ingreso", size=11, weight=ft.FontWeight.BOLD, width=90, text_align=ft.TextAlign.RIGHT),
                    ft.Text("Egreso", size=11, weight=ft.FontWeight.BOLD, width=90, text_align=ft.TextAlign.RIGHT),
                    ft.Text("", width=8),  # Estado
                    ft.Text("", width=40),  # Acciones
                ],
                spacing=4,
            ),
            padding=ft.padding.symmetric(horizontal=8, vertical=8),
            bgcolor=ft.Colors.GREY_100,
            border_radius=ft.border_radius.only(top_left=8, top_right=8),
        )
        
        # Contenedor de filas
        self.filas_container = ft.Column(
            controls=[],
            spacing=0,
            scroll=ft.ScrollMode.AUTO,
        )
        
        # Agregar filas iniciales
        for _ in range(self.filas_iniciales):
            self._agregar_fila()
        
        # Barra de acciones
        self.barra_acciones = ft.Container(
            content=ft.Row(
                controls=[
                    ft.ElevatedButton(
                        "➕ Agregar fila",
                        on_click=lambda e: self._agregar_fila(),
                        bgcolor=AppTheme.BACKGROUND,
                        color=AppTheme.PRIMARY,
                    ),
                    ft.ElevatedButton(
                        "➕➕ Agregar 5 filas",
                        on_click=lambda e: self._agregar_multiples_filas(5),
                        bgcolor=AppTheme.BACKGROUND,
                        color=AppTheme.PRIMARY,
                    ),
                    ft.Container(expand=True),
                    ft.Text("", size=12, color=AppTheme.TEXT_SECONDARY),  # Contador
                    ft.ElevatedButton(
                        "🗑️ Limpiar todo",
                        on_click=self._limpiar_todo,
                        bgcolor=AppTheme.BACKGROUND,
                        color=AppTheme.ERROR,
                    ),
                    ft.ElevatedButton(
                        "💾 Guardar todo",
                        on_click=self._guardar_todo,
                        bgcolor=AppTheme.SUCCESS,
                        color=ft.Colors.WHITE,
                        style=ft.ButtonStyle(
                            padding=ft.padding.symmetric(horizontal=24, vertical=12),
                        ),
                    ),
                ],
                spacing=12,
            ),
            padding=ft.padding.symmetric(horizontal=8, vertical=12),
            bgcolor=ft.Colors.WHITE,
            border_radius=ft.border_radius.only(bottom_left=8, bottom_right=8),
            border=ft.border.only(top=ft.border.BorderSide(1, AppTheme.DIVIDER)),
        )
        
        # Mensaje de estado
        self.mensaje = ft.Container(
            content=ft.Text("", size=12),
            visible=False,
            padding=ft.padding.symmetric(horizontal=12, vertical=8),
            border_radius=4,
        )
        
        self._control = ft.Column([
            ft.Container(
                content=ft.Column([
                    self.header,
                    ft.Container(
                        content=self.filas_container,
                        bgcolor=ft.Colors.WHITE,
                        height=300,  # Altura fija con scroll
                    ),
                    self.barra_acciones,
                ], spacing=0),
                border=ft.border.all(1, AppTheme.DIVIDER),
                border_radius=8,
            ),
            self.mensaje,
        ])
        
        self._actualizar_numeros()
        return self._control
    
    def _agregar_fila(self, default_hoja_id: str = None, default_fecha: str = None):
        """Agrega una nueva fila al grid."""
        row_id = str(uuid.uuid4())
        
        # Obtener valores por defecto de la última fila si existe
        if self._filas_orden and not default_hoja_id:
            ultima_fila = self._filas[self._filas_orden[-1]]
            default_hoja_id = ultima_fila.dd_hoja.value
            default_fecha = ultima_fila.txt_fecha.value
        
        fila = ExcelGridRow(
            row_id=row_id,
            hojas=self.hojas,
            locales=self.locales,
            obtener_categorias=self.obtener_categorias,
            on_delete=self._eliminar_fila,
            page=self.page,
            default_hoja_id=default_hoja_id,
            default_fecha=default_fecha,
        )
        
        self._filas[row_id] = fila
        self._filas_orden.append(row_id)
        self.filas_container.controls.append(fila.build())
        
        self._actualizar_numeros()
        
        if self.page:
            self.page.update()
    
    def _agregar_multiples_filas(self, cantidad: int):
        """Agrega múltiples filas."""
        for _ in range(cantidad):
            self._agregar_fila()
    
    def _eliminar_fila(self, row_id: str):
        """Elimina una fila del grid."""
        if row_id in self._filas and len(self._filas) > 1:
            # Encontrar índice
            idx = self._filas_orden.index(row_id)
            
            # Eliminar de las estructuras
            del self._filas[row_id]
            self._filas_orden.remove(row_id)
            del self.filas_container.controls[idx]
            
            self._actualizar_numeros()
            
            if self.page:
                self.page.update()
    
    def _actualizar_numeros(self):
        """Actualiza los números de fila."""
        for i, row_id in enumerate(self._filas_orden):
            self._filas[row_id].set_numero(i + 1)
    
    def _limpiar_todo(self, e):
        """Limpia todas las filas y deja solo las iniciales."""
        # Limpiar estructuras
        self._filas.clear()
        self._filas_orden.clear()
        self.filas_container.controls.clear()
        
        # Agregar filas iniciales nuevas
        for _ in range(self.filas_iniciales):
            self._agregar_fila()
        
        self._ocultar_mensaje()
        
        if self.page:
            self.page.update()
    
    def _guardar_todo(self, e):
        """Valida y guarda todos los movimientos."""
        # Recolectar datos de filas no vacías
        movimientos = []
        errores_filas = []
        
        for row_id in self._filas_orden:
            fila = self._filas[row_id]
            fila.resetear_estado()
            
            if not fila.esta_vacia():
                datos = fila.obtener_datos()
                
                # Validar
                es_valido, errores = MovimientoValidator.validar(datos)
                
                if es_valido:
                    movimientos.append(datos)
                else:
                    fila.marcar_error(", ".join(errores))
                    errores_filas.append((fila.lbl_numero.value, errores))
        
        if errores_filas:
            # Mostrar errores
            msg = f"❌ Errores en {len(errores_filas)} fila(s). Revise los indicadores rojos."
            self._mostrar_mensaje(msg, AppTheme.ERROR)
            return
        
        if not movimientos:
            self._mostrar_mensaje("⚠️ No hay movimientos para guardar", AppTheme.WARNING)
            return
        
        # Llamar callback con todos los movimientos
        if self.on_submit_all:
            self.on_submit_all(movimientos)
            
            # Marcar filas guardadas como exitosas
            for mov in movimientos:
                if mov['row_id'] in self._filas:
                    self._filas[mov['row_id']].marcar_exito()
            
            self._mostrar_mensaje(f"✅ {len(movimientos)} movimiento(s) guardado(s)", AppTheme.SUCCESS)
    
    def _mostrar_mensaje(self, texto: str, color: str):
        """Muestra un mensaje de estado."""
        self.mensaje.content.value = texto
        self.mensaje.content.color = color
        self.mensaje.bgcolor = f"{color}20"
        self.mensaje.visible = True
        if self.page:
            self.mensaje.update()
    
    def _ocultar_mensaje(self):
        """Oculta el mensaje de estado."""
        self.mensaje.visible = False
        if self.page:
            self.mensaje.update()
    
    def limpiar_guardados(self):
        """Limpia las filas que fueron guardadas exitosamente."""
        filas_a_eliminar = []
        
        for row_id in self._filas_orden:
            fila = self._filas[row_id]
            if fila.estado.bgcolor == AppTheme.SUCCESS:
                filas_a_eliminar.append(row_id)
        
        for row_id in filas_a_eliminar:
            if len(self._filas) > 1:
                idx = self._filas_orden.index(row_id)
                del self._filas[row_id]
                self._filas_orden.remove(row_id)
                del self.filas_container.controls[idx]
        
        # Si quedó muy pocas filas, agregar más
        while len(self._filas) < 3:
            self._agregar_fila()
        
        self._actualizar_numeros()
        
        if self.page:
            self.page.update()
