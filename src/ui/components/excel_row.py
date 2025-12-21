"""
ConSmart - Componente Fila Excel
================================
Fila de entrada tipo Excel para ingresar movimientos.
"""

import flet as ft
from datetime import date, datetime
from typing import Callable, Optional, List, Dict

from src.ui.theme import AppTheme, Styles, Icons
from src.logic import MovimientoValidator


class ExcelRow(ft.UserControl):
    """
    Componente que simula una fila de Excel para ingreso rápido de movimientos.
    Incluye validación en tiempo real y filtros dependientes.
    """
    
    def __init__(
        self,
        hojas: List[Dict],
        locales: List[Dict],
        on_submit: Callable[[dict], None],
        obtener_categorias: Callable[[int], List[Dict]],
        descripciones_sugeridas: List[str] = None,
    ):
        super().__init__()
        self.hojas = hojas
        self.locales = locales
        self.on_submit = on_submit
        self.obtener_categorias = obtener_categorias
        self.descripciones_sugeridas = descripciones_sugeridas or []
        
        # Estado interno
        self._categorias_actuales: List[Dict] = []
    
    def build(self):
        # Dropdown de Hoja
        self.dd_hoja = ft.Dropdown(
            label="Hoja",
            options=[ft.dropdown.Option(key=str(h['id']), text=h['nombre']) for h in self.hojas],
            width=140,
            **Styles.dropdown_excel(),
        )
        
        # Campo de Fecha con DatePicker
        self.txt_fecha = ft.TextField(
            label="Fecha",
            value=date.today().strftime("%Y-%m-%d"),
            width=120,
            read_only=True,
            on_focus=self._abrir_date_picker,
            **Styles.input_excel(),
        )
        
        self.date_picker = ft.DatePicker(
            on_change=self._on_fecha_change,
            first_date=datetime(2020, 1, 1),
            last_date=datetime.now(),
        )
        
        # Dropdown de Local (dispara filtro de categorías)
        self.dd_local = ft.Dropdown(
            label="Local",
            options=[ft.dropdown.Option(key=str(l['id']), text=l['nombre']) for l in self.locales],
            width=140,
            on_change=self._on_local_change,
            **Styles.dropdown_excel(),
        )
        
        # Dropdown de Categoría (se filtra según local)
        self.dd_categoria = ft.Dropdown(
            label="Categoría",
            options=[],
            width=160,
            **Styles.dropdown_excel(),
        )
        
        # Número de documento
        self.txt_doc = ft.TextField(
            label="N° Doc",
            width=100,
            **Styles.input_excel(),
        )
        
        # Responsable
        self.txt_responsable = ft.TextField(
            label="Responsable",
            width=130,
            **Styles.input_excel(),
        )
        
        # Descripción con autocompletado
        self.txt_descripcion = ft.TextField(
            label="Descripción",
            width=200,
            hint_text="Escriba o elija...",
            **Styles.input_excel(),
        )
        
        # Ingreso
        self.txt_ingreso = ft.TextField(
            label="Ingreso",
            value="0",
            width=100,
            text_align=ft.TextAlign.RIGHT,
            keyboard_type=ft.KeyboardType.NUMBER,
            on_change=self._on_ingreso_change,
            **Styles.input_excel(),
        )
        
        # Egreso
        self.txt_egreso = ft.TextField(
            label="Egreso",
            value="0",
            width=100,
            text_align=ft.TextAlign.RIGHT,
            keyboard_type=ft.KeyboardType.NUMBER,
            on_change=self._on_egreso_change,
            **Styles.input_excel(),
        )
        
        # Botón de agregar
        self.btn_agregar = ft.IconButton(
            icon=Icons.ADD,
            icon_color=ft.colors.WHITE,
            bgcolor=AppTheme.SUCCESS,
            tooltip="Agregar movimiento (Enter)",
            on_click=self._on_submit,
        )
        
        # Botón limpiar
        self.btn_limpiar = ft.IconButton(
            icon=Icons.CLEAR,
            icon_color=AppTheme.TEXT_SECONDARY,
            tooltip="Limpiar campos",
            on_click=self._limpiar_campos,
        )
        
        # Mensaje de error/éxito
        self.mensaje = ft.Text(
            "",
            size=12,
            visible=False,
        )
        
        return ft.Column([
            ft.Container(
                content=ft.Row(
                    controls=[
                        self.dd_hoja,
                        self.txt_fecha,
                        self.dd_local,
                        self.dd_categoria,
                        self.txt_doc,
                        self.txt_responsable,
                        self.txt_descripcion,
                        self.txt_ingreso,
                        self.txt_egreso,
                        self.btn_agregar,
                        self.btn_limpiar,
                    ],
                    scroll=ft.ScrollMode.AUTO,
                    spacing=8,
                ),
                padding=ft.padding.symmetric(horizontal=10, vertical=8),
                bgcolor=ft.colors.WHITE,
                border_radius=8,
                border=ft.border.all(1, AppTheme.DIVIDER),
            ),
            self.mensaje,
            self.date_picker,
        ])
    
    def _abrir_date_picker(self, e):
        """Abre el selector de fecha."""
        self.date_picker.pick_date()
    
    def _on_fecha_change(self, e):
        """Cuando cambia la fecha seleccionada."""
        if e.control.value:
            self.txt_fecha.value = e.control.value.strftime("%Y-%m-%d")
            self.txt_fecha.update()
    
    def _on_local_change(self, e):
        """Cuando cambia el local, actualiza las categorías disponibles."""
        if self.dd_local.value:
            local_id = int(self.dd_local.value)
            self._categorias_actuales = self.obtener_categorias(local_id)
            
            self.dd_categoria.options = [
                ft.dropdown.Option(key=str(c['id']), text=c['nombre'])
                for c in self._categorias_actuales
            ]
            self.dd_categoria.value = None
            self.dd_categoria.update()
    
    def _on_ingreso_change(self, e):
        """Si se ingresa un valor en ingreso, limpia egreso."""
        valor = self.txt_ingreso.value.strip()
        if valor and valor != "0":
            self.txt_egreso.value = "0"
            self.txt_egreso.update()
    
    def _on_egreso_change(self, e):
        """Si se ingresa un valor en egreso, limpia ingreso."""
        valor = self.txt_egreso.value.strip()
        if valor and valor != "0":
            self.txt_ingreso.value = "0"
            self.txt_ingreso.update()
    
    def _validar_monto(self, valor_str: str) -> float:
        """Convierte y valida un monto."""
        if not valor_str or valor_str.strip() == "":
            return 0.0
        try:
            return float(valor_str.replace(",", "").strip())
        except ValueError:
            return 0.0
    
    def _on_submit(self, e):
        """Procesa el envío del formulario."""
        datos = self._obtener_datos()
        
        # Validar
        es_valido, errores = MovimientoValidator.validar(datos)
        
        if not es_valido:
            self._mostrar_error("\n".join(errores))
            return
        
        # Llamar callback
        if self.on_submit:
            self.on_submit(datos)
            self._mostrar_exito("✓ Guardado")
            self._limpiar_campos(None)
    
    def _obtener_datos(self) -> dict:
        """Recopila los datos del formulario."""
        return {
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
    
    def _limpiar_campos(self, e):
        """Limpia todos los campos para un nuevo ingreso."""
        # Mantener hoja y fecha
        self.dd_local.value = None
        self.dd_categoria.value = None
        self.dd_categoria.options = []
        self.txt_doc.value = ""
        self.txt_responsable.value = ""
        self.txt_descripcion.value = ""
        self.txt_ingreso.value = "0"
        self.txt_egreso.value = "0"
        self.mensaje.visible = False
        self.update()
    
    def _mostrar_error(self, texto: str):
        """Muestra mensaje de error."""
        self.mensaje.value = texto
        self.mensaje.color = AppTheme.ERROR
        self.mensaje.visible = True
        self.mensaje.update()
    
    def _mostrar_exito(self, texto: str):
        """Muestra mensaje de éxito."""
        self.mensaje.value = texto
        self.mensaje.color = AppTheme.SUCCESS
        self.mensaje.visible = True
        self.mensaje.update()
