"""
ConSmart - Vista de Gestión de Usuarios
========================================
Panel para administrar usuarios y roles.
"""

import flet as ft
from typing import Optional, Dict, Any

from src.ui.theme import AppTheme, Styles, Icons
from src.logic import get_auth


class UsuariosView:
    """
    Vista para gestionar usuarios del sistema.
    Solo accesible para administradores.
    """
    
    def __init__(self, page: ft.Page):
        self.page = page
        self.auth = get_auth()
        
        # Controles
        self.lista_usuarios: Optional[ft.ListView] = None
        self.form_container: Optional[ft.Container] = None
        self.usuario_editando: Optional[Dict[str, Any]] = None
    
    def build(self) -> ft.Control:
        """Construye la vista de usuarios."""
        
        # Verificar permiso
        if not self.auth.puede('puede_gestionar_usuarios'):
            return ft.Container(
                content=ft.Column([
                    ft.Icon(ft.Icons.LOCK, size=64, color=AppTheme.TEXT_SECONDARY),
                    ft.Text(
                        "Acceso Restringido",
                        size=24,
                        weight=ft.FontWeight.BOLD,
                        color=AppTheme.TEXT_SECONDARY,
                    ),
                    ft.Text(
                        "No tiene permiso para gestionar usuarios",
                        color=AppTheme.TEXT_SECONDARY,
                    ),
                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=16),
                alignment=ft.Alignment(0, 0),
                expand=True,
            )
        
        # Lista de usuarios
        self.lista_usuarios = ft.ListView(expand=True, spacing=8, padding=8)
        self._cargar_usuarios()
        
        # Contenedor del formulario (oculto inicialmente)
        self.form_container = ft.Container(visible=False)
        
        return ft.Column([
            # Header
            ft.Container(
                content=ft.Row([
                    ft.Text("👥 Gestión de Usuarios", **Styles.titulo_pagina()),
                    ft.Button(
                        content=ft.Text("Nuevo Usuario"),
                        icon=Icons.ADD,
                        style=ft.ButtonStyle(bgcolor=AppTheme.PRIMARY, color=ft.Colors.WHITE),
                        on_click=self._abrir_formulario_nuevo,
                    ),
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                padding=ft.Padding.only(bottom=16),
            ),
            
            # Contenido principal (lista + formulario)
            ft.Row([
                # Lista de usuarios
                ft.Container(
                    content=ft.Column([
                        ft.Text("Usuarios Registrados", **Styles.subtitulo()),
                        ft.Container(
                            content=self.lista_usuarios,
                            expand=True,
                            bgcolor=ft.Colors.WHITE,
                            border_radius=8,
                            padding=8,
                        ),
                    ], expand=True),
                    expand=2,
                ),
                
                # Formulario (panel lateral)
                ft.Container(
                    content=self.form_container,
                    expand=1,
                    visible=True,
                ),
            ], expand=True, spacing=16),
        ], expand=True)
    
    def _cargar_usuarios(self):
        """Carga la lista de usuarios."""
        usuarios = self.auth.obtener_usuarios()
        self.lista_usuarios.controls = [
            self._crear_item_usuario(u) for u in usuarios
        ]
        # Solo actualizar si el control ya está en la página
        try:
            self.lista_usuarios.update()
        except RuntimeError:
            pass  # El control aún no está en la página
    
    def _crear_item_usuario(self, usuario: Dict[str, Any]) -> ft.Control:
        """Crea un item de la lista de usuarios."""
        es_activo = usuario.get('activo', True)
        es_yo = self.auth.sesion and self.auth.sesion.id == usuario['id']
        
        # Determinar color e icono según estado/rol
        if not es_activo:
            color = AppTheme.TEXT_SECONDARY
            icon_color = AppTheme.TEXT_SECONDARY
        elif usuario.get('rol_nombre') == 'Administrador':
            color = AppTheme.PRIMARY
            icon_color = AppTheme.PRIMARY
        else:
            color = AppTheme.TEXT_PRIMARY
            icon_color = AppTheme.ACCENT
        
        return ft.Container(
            content=ft.Row([
                ft.Icon(
                    ft.Icons.ADMIN_PANEL_SETTINGS if usuario.get('rol_nombre') == 'Administrador'
                    else ft.Icons.PERSON,
                    color=icon_color,
                ),
                ft.Column([
                    ft.Row([
                        ft.Text(
                            usuario['nombre_completo'] or usuario['username'],
                            weight=ft.FontWeight.W_600,
                            color=color,
                        ),
                        ft.Text(
                            "(Tú)" if es_yo else "",
                            size=12,
                            italic=True,
                            color=AppTheme.ACCENT,
                        ),
                    ], spacing=8),
                    ft.Text(
                        f"@{usuario['username']} • {usuario.get('rol_nombre', 'Sin rol')}",
                        size=12,
                        color=AppTheme.TEXT_SECONDARY,
                    ),
                ], spacing=2, expand=True),
                
                # Indicador de estado
                ft.Container(
                    content=ft.Text(
                        "Activo" if es_activo else "Inactivo",
                        size=11,
                        color=ft.Colors.WHITE if es_activo else AppTheme.TEXT_SECONDARY,
                    ),
                    bgcolor=AppTheme.SUCCESS if es_activo else AppTheme.DIVIDER,
                    padding=ft.Padding.symmetric(horizontal=8, vertical=4),
                    border_radius=12,
                ),
                
                # Botones de acción
                ft.Row([
                    ft.IconButton(
                        icon=Icons.EDIT,
                        icon_color=AppTheme.ACCENT,
                        tooltip="Editar",
                        on_click=lambda e, u=usuario: self._abrir_formulario_editar(u),
                    ),
                    ft.IconButton(
                        icon=ft.Icons.KEY,
                        icon_color=AppTheme.WARNING,
                        tooltip="Cambiar contraseña",
                        on_click=lambda e, u=usuario: self._abrir_cambio_password(u),
                    ) if not es_yo else ft.Container(),
                    ft.IconButton(
                        icon=ft.Icons.BLOCK if es_activo else ft.Icons.CHECK_CIRCLE,
                        icon_color=AppTheme.ERROR if es_activo else AppTheme.SUCCESS,
                        tooltip="Desactivar" if es_activo else "Activar",
                        on_click=lambda e, u=usuario: self._toggle_activo(u),
                    ) if not es_yo else ft.Container(),
                ], spacing=0),
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            padding=12,
            border=ft.border.all(1, AppTheme.DIVIDER),
            border_radius=8,
            bgcolor=ft.Colors.WHITE if es_activo else ft.Colors.GREY_100,
        )
    
    def _abrir_formulario_nuevo(self, e):
        """Abre el formulario para crear nuevo usuario."""
        self.usuario_editando = None
        self._mostrar_formulario()
    
    def _abrir_formulario_editar(self, usuario: Dict[str, Any]):
        """Abre el formulario para editar un usuario."""
        self.usuario_editando = usuario
        self._mostrar_formulario()
    
    def _mostrar_formulario(self):
        """Muestra el formulario de usuario."""
        roles = self.auth.obtener_roles()
        es_nuevo = self.usuario_editando is None
        
        # Campos del formulario
        txt_username = ft.TextField(
            label="Nombre de usuario",
            value="" if es_nuevo else self.usuario_editando.get('username', ''),
            disabled=not es_nuevo,  # No se puede cambiar username
        )
        
        txt_nombre = ft.TextField(
            label="Nombre completo",
            value="" if es_nuevo else self.usuario_editando.get('nombre_completo', ''),
        )
        
        txt_email = ft.TextField(
            label="Email (opcional)",
            value="" if es_nuevo else (self.usuario_editando.get('email') or ''),
        )
        
        txt_password = ft.TextField(
            label="Contraseña" if es_nuevo else "Nueva contraseña (dejar vacío para mantener)",
            password=True,
            can_reveal_password=True,
        )
        
        txt_password_confirm = ft.TextField(
            label="Confirmar contraseña",
            password=True,
            can_reveal_password=True,
        ) if es_nuevo else None
        
        dd_rol = ft.Dropdown(
            label="Rol",
            options=[
                ft.dropdown.Option(str(r['id']), r['nombre']) for r in roles
            ],
            value=str(self.usuario_editando.get('rol_id', '')) if not es_nuevo else None,
        )
        
        lbl_error = ft.Text("", color=AppTheme.ERROR, size=12)
        
        def guardar(e):
            """Guarda el usuario."""
            # Validaciones
            if es_nuevo:
                if not txt_username.value or not txt_username.value.strip():
                    lbl_error.value = "El nombre de usuario es requerido"
                    self.page.update()
                    return
                
                if not txt_password.value:
                    lbl_error.value = "La contraseña es requerida"
                    self.page.update()
                    return
                
                if txt_password.value != txt_password_confirm.value:
                    lbl_error.value = "Las contraseñas no coinciden"
                    self.page.update()
                    return
            
            if not dd_rol.value:
                lbl_error.value = "Debe seleccionar un rol"
                self.page.update()
                return
            
            if es_nuevo:
                exito, mensaje = self.auth.crear_usuario(
                    username=txt_username.value.strip(),
                    password=txt_password.value,
                    nombre_completo=txt_nombre.value.strip() if txt_nombre.value else None,
                    rol_id=int(dd_rol.value),
                    email=txt_email.value.strip() if txt_email.value else None,
                )
            else:
                exito, mensaje = self.auth.actualizar_usuario(
                    user_id=self.usuario_editando['id'],
                    nombre_completo=txt_nombre.value.strip() if txt_nombre.value else None,
                    email=txt_email.value.strip() if txt_email.value else None,
                    rol_id=int(dd_rol.value),
                )
            
            if exito:
                self._cerrar_formulario()
                self._cargar_usuarios()
                self.page.snack_bar = ft.SnackBar(
                    content=ft.Text(mensaje),
                    bgcolor=AppTheme.SUCCESS,
                )
                self.page.snack_bar.open = True
                self.page.update()
            else:
                lbl_error.value = mensaje
                self.page.update()
        
        # Formulario
        form_content = ft.Column([
            ft.Text(
                "Nuevo Usuario" if es_nuevo else f"Editar: {self.usuario_editando.get('username')}",
                **Styles.subtitulo(),
            ),
            ft.Divider(),
            txt_username,
            txt_nombre,
            txt_email,
            txt_password,
            txt_password_confirm if es_nuevo else ft.Container(),
            dd_rol,
            lbl_error,
            ft.Row([
                ft.TextButton(content=ft.Text("Cancelar"), on_click=lambda e: self._cerrar_formulario()),
                ft.Button(
                    content=ft.Text("Guardar"),
                    icon=Icons.SAVE,
                    style=ft.ButtonStyle(bgcolor=AppTheme.PRIMARY, color=ft.Colors.WHITE),
                    on_click=guardar,
                ),
            ], alignment=ft.MainAxisAlignment.END),
        ], spacing=12)
        
        self.form_container.content = ft.Card(
            content=ft.Container(
                content=form_content,
                padding=20,
            ),
            elevation=4,
        )
        self.form_container.visible = True
        self.page.update()
    
    def _cerrar_formulario(self):
        """Cierra el formulario."""
        self.form_container.visible = False
        self.form_container.content = None
        self.usuario_editando = None
        self.page.update()
    
    def _abrir_cambio_password(self, usuario: Dict[str, Any]):
        """Abre diálogo para cambiar contraseña."""
        txt_nueva = ft.TextField(
            label="Nueva contraseña",
            password=True,
            can_reveal_password=True,
        )
        txt_confirmar = ft.TextField(
            label="Confirmar contraseña",
            password=True,
            can_reveal_password=True,
        )
        lbl_error = ft.Text("", color=AppTheme.ERROR, size=12)
        
        def cambiar(e):
            if not txt_nueva.value:
                lbl_error.value = "Ingrese la nueva contraseña"
                self.page.update()
                return
            
            if txt_nueva.value != txt_confirmar.value:
                lbl_error.value = "Las contraseñas no coinciden"
                self.page.update()
                return
            
            exito, mensaje = self.auth.cambiar_password_usuario(usuario['id'], txt_nueva.value)
            
            if exito:
                self.page.close(dlg)
                self.page.snack_bar = ft.SnackBar(
                    content=ft.Text(f"Contraseña de {usuario['username']} cambiada"),
                    bgcolor=AppTheme.SUCCESS,
                )
                self.page.snack_bar.open = True
                self.page.update()
            else:
                lbl_error.value = mensaje
                self.page.update()
        
        dlg = ft.AlertDialog(
            title=ft.Text(f"Cambiar contraseña: {usuario['username']}"),
            content=ft.Column([
                txt_nueva,
                txt_confirmar,
                lbl_error,
            ], tight=True, spacing=12),
            actions=[
                ft.TextButton(content=ft.Text("Cancelar"), on_click=lambda e: self.page.close(dlg)),
                ft.Button(content=ft.Text("Cambiar"), on_click=cambiar),
            ],
        )
        self.page.open(dlg)
    
    def _toggle_activo(self, usuario: Dict[str, Any]):
        """Activa/desactiva un usuario."""
        es_activo = usuario.get('activo', True)
        
        if es_activo:
            exito, mensaje = self.auth.desactivar_usuario(usuario['id'])
        else:
            exito, mensaje = self.auth.actualizar_usuario(usuario['id'], activo=True)
        
        if exito:
            self._cargar_usuarios()
            self.page.snack_bar = ft.SnackBar(
                content=ft.Text(f"Usuario {'desactivado' if es_activo else 'activado'}"),
                bgcolor=AppTheme.SUCCESS if not es_activo else AppTheme.WARNING,
            )
            self.page.snack_bar.open = True
            self.page.update()


class RolesInfoView:
    """
    Vista informativa de roles y permisos.
    """
    
    def __init__(self, page: ft.Page):
        self.page = page
        self.auth = get_auth()
    
    def build(self) -> ft.Control:
        """Construye la vista de información de roles."""
        roles = self.auth.obtener_roles()
        
        # Crear cards para cada rol
        roles_cards = []
        for rol in roles:
            permisos_lista = []
            permisos_checks = [
                ('puede_registrar', 'Registrar movimientos', ft.Icons.ADD_BOX),
                ('puede_ver_historial', 'Ver historial', ft.Icons.HISTORY),
                ('puede_editar_movimientos', 'Editar movimientos', ft.Icons.EDIT),
                ('puede_eliminar_movimientos', 'Eliminar movimientos', ft.Icons.DELETE),
                ('puede_modificar_saldos', 'Modificar saldos', ft.Icons.ACCOUNT_BALANCE),
                ('puede_gestionar_config', 'Gestionar configuración', ft.Icons.SETTINGS),
                ('puede_gestionar_usuarios', 'Gestionar usuarios', ft.Icons.PEOPLE),
            ]
            
            for key, label, icon in permisos_checks:
                tiene = rol.get(key, False)
                permisos_lista.append(
                    ft.Row([
                        ft.Icon(
                            ft.Icons.CHECK_CIRCLE if tiene else ft.Icons.CANCEL,
                            color=AppTheme.SUCCESS if tiene else AppTheme.DIVIDER,
                            size=16,
                        ),
                        ft.Text(label, size=12, color=AppTheme.TEXT_PRIMARY if tiene else AppTheme.TEXT_SECONDARY),
                    ], spacing=8)
                )
            
            roles_cards.append(
                ft.Card(
                    content=ft.Container(
                        content=ft.Column([
                            ft.Row([
                                ft.Icon(
                                    ft.Icons.ADMIN_PANEL_SETTINGS if rol.get('es_admin') else ft.Icons.PERSON,
                                    color=AppTheme.PRIMARY if rol.get('es_admin') else AppTheme.ACCENT,
                                ),
                                ft.Text(rol['nombre'], weight=ft.FontWeight.BOLD, size=16),
                            ], spacing=8),
                            ft.Text(
                                rol.get('descripcion') or "Sin descripción",
                                size=12,
                                color=AppTheme.TEXT_SECONDARY,
                                italic=True,
                            ),
                            ft.Divider(height=8),
                            ft.Column(permisos_lista, spacing=4),
                        ], spacing=8),
                        padding=16,
                    ),
                    width=280,
                )
            )
        
        return ft.Column([
            ft.Text("🔐 Roles y Permisos", **Styles.subtitulo()),
            ft.Text(
                "Estos son los roles disponibles y sus permisos en el sistema",
                size=12,
                color=AppTheme.TEXT_SECONDARY,
            ),
            ft.Container(height=8),
            ft.Row(
                roles_cards,
                wrap=True,
                spacing=16,
                run_spacing=16,
            ),
        ], spacing=8)
