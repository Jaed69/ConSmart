"""
ConSmart - Repositorio de Usuarios y Roles
===========================================
Maneja las operaciones CRUD para usuarios y roles.
"""

import hashlib
from typing import Optional, List, Dict, Any
from datetime import datetime

from src.database import get_db


class UsuarioRepository:
    """Repositorio para operaciones de usuarios."""
    
    def __init__(self):
        self.db = get_db()
    
    def _hash_password(self, password: str) -> str:
        """Genera hash SHA-256 de la contraseña."""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def autenticar(self, username: str, password: str) -> Optional[Dict[str, Any]]:
        """
        Autentica un usuario y retorna sus datos si es válido.
        
        Returns:
            Dict con datos del usuario y permisos, o None si falla
        """
        password_hash = self._hash_password(password)
        
        result = self.db.fetchone("""
            SELECT u.id, u.username, u.nombre_completo, u.email, u.rol_id,
                   r.nombre as rol_nombre, r.puede_registrar, r.puede_ver_historial,
                   r.puede_editar_movimientos, r.puede_eliminar_movimientos,
                   r.puede_modificar_saldos, r.puede_gestionar_config,
                   r.puede_gestionar_usuarios, r.es_admin
            FROM usuarios u
            JOIN roles r ON u.rol_id = r.id
            WHERE u.username = ? AND u.password_hash = ? AND u.activo = TRUE AND r.activo = TRUE
        """, [username, password_hash])
        
        if result:
            # Actualizar último login
            self.db.execute("""
                UPDATE usuarios SET ultimo_login = CURRENT_TIMESTAMP WHERE id = ?
            """, [result[0]])
            
            return {
                'id': result[0],
                'username': result[1],
                'nombre_completo': result[2],
                'email': result[3],
                'rol_id': result[4],
                'rol_nombre': result[5],
                'permisos': {
                    'puede_registrar': result[6],
                    'puede_ver_historial': result[7],
                    'puede_editar_movimientos': result[8],
                    'puede_eliminar_movimientos': result[9],
                    'puede_modificar_saldos': result[10],
                    'puede_gestionar_config': result[11],
                    'puede_gestionar_usuarios': result[12],
                    'es_admin': result[13],
                }
            }
        return None
    
    def obtener_por_id(self, user_id: int) -> Optional[Dict[str, Any]]:
        """Obtiene un usuario por su ID."""
        result = self.db.fetchone("""
            SELECT u.id, u.username, u.nombre_completo, u.email, u.rol_id,
                   r.nombre as rol_nombre, u.activo, u.ultimo_login, u.created_at
            FROM usuarios u
            JOIN roles r ON u.rol_id = r.id
            WHERE u.id = ?
        """, [user_id])
        
        if result:
            return {
                'id': result[0],
                'username': result[1],
                'nombre_completo': result[2],
                'email': result[3],
                'rol_id': result[4],
                'rol_nombre': result[5],
                'activo': result[6],
                'ultimo_login': result[7],
                'created_at': result[8],
            }
        return None
    
    def obtener_todos(self, solo_activos: bool = True) -> List[Dict[str, Any]]:
        """Obtiene todos los usuarios."""
        query = """
            SELECT u.id, u.username, u.nombre_completo, u.email, u.rol_id,
                   r.nombre as rol_nombre, u.activo, u.ultimo_login, u.created_at
            FROM usuarios u
            JOIN roles r ON u.rol_id = r.id
        """
        if solo_activos:
            query += " WHERE u.activo = TRUE"
        query += " ORDER BY u.username"
        
        results = self.db.fetchall(query)
        return [{
            'id': r[0],
            'username': r[1],
            'nombre_completo': r[2],
            'email': r[3],
            'rol_id': r[4],
            'rol_nombre': r[5],
            'activo': r[6],
            'ultimo_login': r[7],
            'created_at': r[8],
        } for r in results]
    
    def crear(self, username: str, password: str, nombre_completo: str, 
              rol_id: int, email: str = None, created_by: int = None) -> int:
        """
        Crea un nuevo usuario.
        
        Returns:
            ID del nuevo usuario
        """
        password_hash = self._hash_password(password)
        
        self.db.execute("""
            INSERT INTO usuarios (username, password_hash, nombre_completo, email, rol_id, created_by)
            VALUES (?, ?, ?, ?, ?, ?)
        """, [username, password_hash, nombre_completo, email, rol_id, created_by])
        
        result = self.db.fetchone("SELECT MAX(id) FROM usuarios")
        return result[0]
    
    def actualizar(self, user_id: int, nombre_completo: str = None, 
                   email: str = None, rol_id: int = None, activo: bool = None) -> bool:
        """Actualiza datos de un usuario (sin contraseña)."""
        updates = []
        params = []
        
        if nombre_completo is not None:
            updates.append("nombre_completo = ?")
            params.append(nombre_completo)
        if email is not None:
            updates.append("email = ?")
            params.append(email)
        if rol_id is not None:
            updates.append("rol_id = ?")
            params.append(rol_id)
        if activo is not None:
            updates.append("activo = ?")
            params.append(activo)
        
        if not updates:
            return False
        
        params.append(user_id)
        query = f"UPDATE usuarios SET {', '.join(updates)} WHERE id = ?"
        self.db.execute(query, params)
        return True
    
    def cambiar_password(self, user_id: int, nueva_password: str) -> bool:
        """Cambia la contraseña de un usuario."""
        password_hash = self._hash_password(nueva_password)
        self.db.execute("""
            UPDATE usuarios SET password_hash = ? WHERE id = ?
        """, [password_hash, user_id])
        return True
    
    def verificar_password(self, user_id: int, password: str) -> bool:
        """Verifica si la contraseña es correcta."""
        password_hash = self._hash_password(password)
        result = self.db.fetchone("""
            SELECT id FROM usuarios WHERE id = ? AND password_hash = ?
        """, [user_id, password_hash])
        return result is not None
    
    def desactivar(self, user_id: int) -> bool:
        """Desactiva un usuario (soft delete)."""
        self.db.execute("UPDATE usuarios SET activo = FALSE WHERE id = ?", [user_id])
        return True
    
    def activar(self, user_id: int) -> bool:
        """Reactiva un usuario."""
        self.db.execute("UPDATE usuarios SET activo = TRUE WHERE id = ?", [user_id])
        return True
    
    def existe_username(self, username: str, excluir_id: int = None) -> bool:
        """Verifica si un username ya existe."""
        if excluir_id:
            result = self.db.fetchone(
                "SELECT id FROM usuarios WHERE username = ? AND id != ?",
                [username, excluir_id]
            )
        else:
            result = self.db.fetchone(
                "SELECT id FROM usuarios WHERE username = ?",
                [username]
            )
        return result is not None


class RolRepository:
    """Repositorio para operaciones de roles."""
    
    def __init__(self):
        self.db = get_db()
    
    def obtener_todos(self, solo_activos: bool = True) -> List[Dict[str, Any]]:
        """Obtiene todos los roles."""
        query = """
            SELECT id, nombre, descripcion, puede_registrar, puede_ver_historial,
                   puede_editar_movimientos, puede_eliminar_movimientos, puede_modificar_saldos,
                   puede_gestionar_config, puede_gestionar_usuarios, es_admin, activo
            FROM roles
        """
        if solo_activos:
            query += " WHERE activo = TRUE"
        query += " ORDER BY es_admin DESC, nombre"
        
        results = self.db.fetchall(query)
        return [{
            'id': r[0],
            'nombre': r[1],
            'descripcion': r[2],
            'puede_registrar': r[3],
            'puede_ver_historial': r[4],
            'puede_editar_movimientos': r[5],
            'puede_eliminar_movimientos': r[6],
            'puede_modificar_saldos': r[7],
            'puede_gestionar_config': r[8],
            'puede_gestionar_usuarios': r[9],
            'es_admin': r[10],
            'activo': r[11],
        } for r in results]
    
    def obtener_por_id(self, rol_id: int) -> Optional[Dict[str, Any]]:
        """Obtiene un rol por su ID."""
        result = self.db.fetchone("""
            SELECT id, nombre, descripcion, puede_registrar, puede_ver_historial,
                   puede_editar_movimientos, puede_eliminar_movimientos, puede_modificar_saldos,
                   puede_gestionar_config, puede_gestionar_usuarios, es_admin, activo
            FROM roles WHERE id = ?
        """, [rol_id])
        
        if result:
            return {
                'id': result[0],
                'nombre': result[1],
                'descripcion': result[2],
                'puede_registrar': result[3],
                'puede_ver_historial': result[4],
                'puede_editar_movimientos': result[5],
                'puede_eliminar_movimientos': result[6],
                'puede_modificar_saldos': result[7],
                'puede_gestionar_config': result[8],
                'puede_gestionar_usuarios': result[9],
                'es_admin': result[10],
                'activo': result[11],
            }
        return None
    
    def crear(self, nombre: str, descripcion: str = None, **permisos) -> int:
        """Crea un nuevo rol."""
        self.db.execute("""
            INSERT INTO roles (nombre, descripcion, puede_registrar, puede_ver_historial,
                puede_editar_movimientos, puede_eliminar_movimientos, puede_modificar_saldos,
                puede_gestionar_config, puede_gestionar_usuarios, es_admin)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, [
            nombre,
            descripcion,
            permisos.get('puede_registrar', True),
            permisos.get('puede_ver_historial', True),
            permisos.get('puede_editar_movimientos', False),
            permisos.get('puede_eliminar_movimientos', False),
            permisos.get('puede_modificar_saldos', False),
            permisos.get('puede_gestionar_config', False),
            permisos.get('puede_gestionar_usuarios', False),
            permisos.get('es_admin', False),
        ])
        
        result = self.db.fetchone("SELECT MAX(id) FROM roles")
        return result[0]
    
    def actualizar(self, rol_id: int, **datos) -> bool:
        """Actualiza un rol."""
        campos_permitidos = [
            'nombre', 'descripcion', 'puede_registrar', 'puede_ver_historial',
            'puede_editar_movimientos', 'puede_eliminar_movimientos', 
            'puede_modificar_saldos', 'puede_gestionar_config', 
            'puede_gestionar_usuarios', 'es_admin', 'activo'
        ]
        
        updates = []
        params = []
        
        for campo in campos_permitidos:
            if campo in datos:
                updates.append(f"{campo} = ?")
                params.append(datos[campo])
        
        if not updates:
            return False
        
        params.append(rol_id)
        query = f"UPDATE roles SET {', '.join(updates)} WHERE id = ?"
        self.db.execute(query, params)
        return True
    
    def contar_usuarios(self, rol_id: int) -> int:
        """Cuenta cuántos usuarios tienen este rol."""
        result = self.db.fetchone(
            "SELECT COUNT(*) FROM usuarios WHERE rol_id = ? AND activo = TRUE",
            [rol_id]
        )
        return result[0] if result else 0
