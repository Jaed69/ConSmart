"""
ConSmart - Servicio de Autenticación
=====================================
Maneja la autenticación y sesión de usuarios.
"""

from typing import Optional, Dict, Any, Callable
from dataclasses import dataclass, field

from src.database.repositories import UsuarioRepository, RolRepository


@dataclass
class Permisos:
    """Clase de permisos del usuario actual."""
    puede_registrar: bool = False
    puede_ver_historial: bool = False
    puede_editar_movimientos: bool = False
    puede_eliminar_movimientos: bool = False
    puede_modificar_saldos: bool = False
    puede_gestionar_config: bool = False
    puede_gestionar_usuarios: bool = False
    es_admin: bool = False
    
    def tiene_permiso(self, permiso: str) -> bool:
        """Verifica si tiene un permiso específico."""
        if self.es_admin:
            return True  # Admin tiene todos los permisos
        return getattr(self, permiso, False)


@dataclass
class SesionUsuario:
    """Representa la sesión del usuario actual."""
    id: int
    username: str
    nombre_completo: str
    email: Optional[str]
    rol_id: int
    rol_nombre: str
    permisos: Permisos
    
    def es_admin(self) -> bool:
        """Verifica si es administrador."""
        return self.permisos.es_admin
    
    def puede(self, accion: str) -> bool:
        """Verifica si puede realizar una acción."""
        return self.permisos.tiene_permiso(accion)


class AuthService:
    """
    Servicio singleton para manejar autenticación y sesión.
    """
    _instance: Optional['AuthService'] = None
    _sesion_actual: Optional[SesionUsuario] = None
    _observers: list = []
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._observers = []
        return cls._instance
    
    def __init__(self):
        self.usuario_repo = UsuarioRepository()
        self.rol_repo = RolRepository()
    
    def login(self, username: str, password: str) -> tuple[bool, str]:
        """
        Intenta iniciar sesión.
        
        Returns:
            Tuple[bool, str]: (éxito, mensaje)
        """
        usuario_data = self.usuario_repo.autenticar(username, password)
        
        if not usuario_data:
            return False, "Usuario o contraseña incorrectos"
        
        # Crear objeto de permisos
        permisos = Permisos(
            puede_registrar=usuario_data['permisos']['puede_registrar'],
            puede_ver_historial=usuario_data['permisos']['puede_ver_historial'],
            puede_editar_movimientos=usuario_data['permisos']['puede_editar_movimientos'],
            puede_eliminar_movimientos=usuario_data['permisos']['puede_eliminar_movimientos'],
            puede_modificar_saldos=usuario_data['permisos']['puede_modificar_saldos'],
            puede_gestionar_config=usuario_data['permisos']['puede_gestionar_config'],
            puede_gestionar_usuarios=usuario_data['permisos']['puede_gestionar_usuarios'],
            es_admin=usuario_data['permisos']['es_admin'],
        )
        
        # Crear sesión
        self._sesion_actual = SesionUsuario(
            id=usuario_data['id'],
            username=usuario_data['username'],
            nombre_completo=usuario_data['nombre_completo'] or usuario_data['username'],
            email=usuario_data['email'],
            rol_id=usuario_data['rol_id'],
            rol_nombre=usuario_data['rol_nombre'],
            permisos=permisos,
        )
        
        # Notificar observers
        self._notificar_cambio()
        
        return True, f"Bienvenido, {self._sesion_actual.nombre_completo}"
    
    def logout(self):
        """Cierra la sesión actual."""
        self._sesion_actual = None
        self._notificar_cambio()
    
    @property
    def sesion(self) -> Optional[SesionUsuario]:
        """Retorna la sesión actual."""
        return self._sesion_actual
    
    @property
    def usuario_actual(self) -> Optional[SesionUsuario]:
        """Alias de sesion."""
        return self._sesion_actual
    
    def esta_autenticado(self) -> bool:
        """Verifica si hay un usuario autenticado."""
        return self._sesion_actual is not None
    
    def puede(self, permiso: str) -> bool:
        """Verifica si el usuario actual tiene un permiso."""
        if not self._sesion_actual:
            return False
        return self._sesion_actual.puede(permiso)
    
    def es_admin(self) -> bool:
        """Verifica si el usuario actual es admin."""
        if not self._sesion_actual:
            return False
        return self._sesion_actual.es_admin()
    
    def requiere_permiso(self, permiso: str) -> Callable:
        """
        Decorador para proteger funciones con permisos.
        
        Uso:
            @auth_service.requiere_permiso('puede_editar_movimientos')
            def editar_movimiento(...):
                ...
        """
        def decorator(func):
            def wrapper(*args, **kwargs):
                if not self.puede(permiso):
                    raise PermissionError(f"No tiene permiso para: {permiso}")
                return func(*args, **kwargs)
            return wrapper
        return decorator
    
    # === Observer pattern para notificar cambios de sesión ===
    
    def agregar_observer(self, callback: Callable):
        """Agrega un observer para cambios de sesión."""
        if callback not in self._observers:
            self._observers.append(callback)
    
    def remover_observer(self, callback: Callable):
        """Remueve un observer."""
        if callback in self._observers:
            self._observers.remove(callback)
    
    def _notificar_cambio(self):
        """Notifica a todos los observers del cambio de sesión."""
        for callback in self._observers:
            try:
                callback(self._sesion_actual)
            except Exception as e:
                print(f"Error notificando observer: {e}")
    
    # === Métodos de gestión de usuarios ===
    
    def obtener_usuarios(self) -> list:
        """Obtiene todos los usuarios (requiere permiso)."""
        if not self.puede('puede_gestionar_usuarios'):
            return []
        return self.usuario_repo.obtener_todos(solo_activos=False)
    
    def obtener_roles(self) -> list:
        """Obtiene todos los roles."""
        return self.rol_repo.obtener_todos()
    
    def crear_usuario(self, username: str, password: str, nombre_completo: str,
                      rol_id: int, email: str = None) -> tuple[bool, str]:
        """Crea un nuevo usuario."""
        if not self.puede('puede_gestionar_usuarios'):
            return False, "No tiene permiso para crear usuarios"
        
        if self.usuario_repo.existe_username(username):
            return False, f"El usuario '{username}' ya existe"
        
        try:
            created_by = self._sesion_actual.id if self._sesion_actual else None
            user_id = self.usuario_repo.crear(
                username, password, nombre_completo, rol_id, email, created_by
            )
            return True, f"Usuario creado exitosamente (ID: {user_id})"
        except Exception as e:
            return False, f"Error creando usuario: {str(e)}"
    
    def actualizar_usuario(self, user_id: int, **datos) -> tuple[bool, str]:
        """Actualiza un usuario."""
        if not self.puede('puede_gestionar_usuarios'):
            return False, "No tiene permiso para editar usuarios"
        
        try:
            self.usuario_repo.actualizar(user_id, **datos)
            return True, "Usuario actualizado exitosamente"
        except Exception as e:
            return False, f"Error actualizando usuario: {str(e)}"
    
    def cambiar_password_usuario(self, user_id: int, nueva_password: str) -> tuple[bool, str]:
        """Cambia la contraseña de un usuario (admin)."""
        if not self.puede('puede_gestionar_usuarios'):
            return False, "No tiene permiso para cambiar contraseñas"
        
        try:
            self.usuario_repo.cambiar_password(user_id, nueva_password)
            return True, "Contraseña cambiada exitosamente"
        except Exception as e:
            return False, f"Error cambiando contraseña: {str(e)}"
    
    def cambiar_mi_password(self, password_actual: str, nueva_password: str) -> tuple[bool, str]:
        """Cambia la contraseña del usuario actual."""
        if not self._sesion_actual:
            return False, "No hay sesión activa"
        
        if not self.usuario_repo.verificar_password(self._sesion_actual.id, password_actual):
            return False, "Contraseña actual incorrecta"
        
        try:
            self.usuario_repo.cambiar_password(self._sesion_actual.id, nueva_password)
            return True, "Contraseña cambiada exitosamente"
        except Exception as e:
            return False, f"Error cambiando contraseña: {str(e)}"
    
    def desactivar_usuario(self, user_id: int) -> tuple[bool, str]:
        """Desactiva un usuario."""
        if not self.puede('puede_gestionar_usuarios'):
            return False, "No tiene permiso para desactivar usuarios"
        
        # No permitir desactivarse a sí mismo
        if self._sesion_actual and self._sesion_actual.id == user_id:
            return False, "No puede desactivar su propia cuenta"
        
        try:
            self.usuario_repo.desactivar(user_id)
            return True, "Usuario desactivado exitosamente"
        except Exception as e:
            return False, f"Error desactivando usuario: {str(e)}"


# Instancia global
def get_auth() -> AuthService:
    """Obtiene la instancia del servicio de autenticación."""
    return AuthService()
