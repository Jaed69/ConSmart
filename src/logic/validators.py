"""
ConSmart - Validadores de Negocio
=================================
Validaciones para asegurar integridad de datos contables.
"""

from datetime import date, datetime
from typing import List, Tuple


class MovimientoValidator:
    """Valida los datos de un movimiento antes de guardarlo."""
    
    @staticmethod
    def validar(datos: dict) -> Tuple[bool, List[str]]:
        """
        Valida un movimiento completo.
        
        Args:
            datos: Diccionario con los campos del movimiento
            
        Returns:
            Tupla (es_valido, lista_de_errores)
        """
        errores = []
        
        # Validar campos obligatorios
        if not datos.get('hoja_id'):
            errores.append("Debe seleccionar una hoja/cuenta")
        
        if not datos.get('local_id'):
            errores.append("Debe seleccionar un local")
        
        if not datos.get('categoria_id'):
            errores.append("Debe seleccionar una categoría")
        
        # Validar fecha
        fecha = datos.get('fecha')
        if fecha:
            if isinstance(fecha, str):
                try:
                    fecha = datetime.strptime(fecha, "%Y-%m-%d").date()
                except ValueError:
                    errores.append("Formato de fecha inválido (use YYYY-MM-DD)")
                    fecha = None
            
            if fecha and fecha > date.today():
                errores.append("La fecha no puede ser futura")
        else:
            errores.append("La fecha es obligatoria")
        
        # Validar montos
        ingreso = datos.get('ingreso', 0)
        egreso = datos.get('egreso', 0)
        
        try:
            ingreso = float(ingreso) if ingreso else 0
            egreso = float(egreso) if egreso else 0
        except (ValueError, TypeError):
            errores.append("Los montos deben ser números válidos")
            ingreso = egreso = 0
        
        if ingreso < 0:
            errores.append("El ingreso no puede ser negativo")
        
        if egreso < 0:
            errores.append("El egreso no puede ser negativo")
        
        # Un movimiento no puede tener ambos al mismo tiempo
        if ingreso > 0 and egreso > 0:
            errores.append("Un movimiento no puede tener ingreso y egreso simultáneamente")
        
        # Debe tener al menos uno
        if ingreso == 0 and egreso == 0:
            errores.append("Debe ingresar un monto en ingreso o egreso")
        
        # Validar descripción (advertencia, no error crítico)
        # if not datos.get('descripcion'):
        #     errores.append("Se recomienda agregar una descripción")
        
        return (len(errores) == 0, errores)
    
    @staticmethod
    def validar_monto(valor: str) -> Tuple[bool, float, str]:
        """
        Valida y convierte un monto string a float.
        
        Returns:
            Tupla (es_valido, valor_float, mensaje_error)
        """
        if not valor or valor.strip() == "":
            return (True, 0.0, "")
        
        try:
            # Limpiar formato (comas, espacios)
            valor_limpio = valor.replace(",", "").replace(" ", "").strip()
            monto = float(valor_limpio)
            
            if monto < 0:
                return (False, 0.0, "El monto no puede ser negativo")
            
            # Redondear a 2 decimales
            monto = round(monto, 2)
            
            return (True, monto, "")
            
        except ValueError:
            return (False, 0.0, f"'{valor}' no es un número válido")
    
    @staticmethod
    def validar_fecha(fecha_str: str) -> Tuple[bool, date, str]:
        """
        Valida y convierte una fecha string a date.
        
        Returns:
            Tupla (es_valido, fecha, mensaje_error)
        """
        if not fecha_str:
            return (False, None, "La fecha es obligatoria")
        
        formatos = ["%Y-%m-%d", "%d/%m/%Y", "%d-%m-%Y"]
        
        for fmt in formatos:
            try:
                fecha = datetime.strptime(fecha_str.strip(), fmt).date()
                
                if fecha > date.today():
                    return (False, None, "La fecha no puede ser futura")
                
                return (True, fecha, "")
            except ValueError:
                continue
        
        return (False, None, "Formato de fecha inválido")


class ConfigValidator:
    """Valida datos de configuración del sistema."""
    
    @staticmethod
    def validar_nombre_unico(nombre: str, existentes: List[str]) -> Tuple[bool, str]:
        """Valida que un nombre sea único."""
        if not nombre or nombre.strip() == "":
            return (False, "El nombre no puede estar vacío")
        
        nombre_limpio = nombre.strip()
        
        if nombre_limpio.lower() in [e.lower() for e in existentes]:
            return (False, f"'{nombre_limpio}' ya existe")
        
        if len(nombre_limpio) < 2:
            return (False, "El nombre debe tener al menos 2 caracteres")
        
        if len(nombre_limpio) > 100:
            return (False, "El nombre es demasiado largo (máx. 100 caracteres)")
        
        return (True, "")
    
    @staticmethod
    def validar_tipo_cambio(compra: str, venta: str) -> Tuple[bool, dict, str]:
        """Valida tipo de cambio."""
        try:
            compra_f = float(compra)
            venta_f = float(venta)
            
            if compra_f <= 0 or venta_f <= 0:
                return (False, {}, "Los valores deben ser positivos")
            
            if compra_f > venta_f:
                return (False, {}, "El tipo de compra no puede ser mayor al de venta")
            
            return (True, {"compra": compra_f, "venta": venta_f}, "")
            
        except ValueError:
            return (False, {}, "Los valores deben ser números válidos")
