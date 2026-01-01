#!/usr/bin/env python3
"""
Script de verificación para Flet 0.80
Verifica que tu instalación de Flet sea compatible con ConSmart
"""

import sys

def verificar_flet():
    """Verifica la versión de Flet instalada."""
    try:
        import flet as ft
        version = ft.__version__
        print(f"✅ Flet instalado: v{version}")
        
        # Verificar versión mínima
        from packaging import version as pkg_version
        if pkg_version.parse(version) >= pkg_version.parse("0.80.0"):
            print(f"✅ Versión compatible con ConSmart (0.80.0+)")
            return True
        else:
            print(f"⚠️  Versión antigua detectada: v{version}")
            print(f"   Se requiere Flet 0.80.0 o superior")
            print(f"   Ejecuta: uv sync  o  pip install --upgrade 'flet[all]>=0.80.0'")
            return False
            
    except ImportError:
        print("❌ Flet no está instalado")
        print("   Ejecuta: uv sync  o  pip install 'flet[all]>=0.80.0'")
        return False
    except ImportError as e:
        # packaging no instalado, asumir OK si version >= 0.80
        try:
            major, minor = map(int, version.split('.')[:2])
            if major > 0 or (major == 0 and minor >= 80):
                print(f"✅ Versión compatible (verificación básica)")
                return True
            else:
                print(f"⚠️  Versión antigua detectada")
                return False
        except:
            print(f"⚠️  No se pudo verificar la versión automáticamente")
            return True  # Asumir OK

def verificar_dependencias():
    """Verifica las demás dependencias."""
    dependencias = {
        'duckdb': 'DuckDB (base de datos)',
        'pandas': 'Pandas (análisis de datos)',
        'openpyxl': 'OpenPyXL (exportación Excel)',
        'dateutil': 'Python-dateutil (manejo de fechas)'
    }
    
    print("\n📦 Verificando dependencias adicionales:")
    todas_ok = True
    
    for modulo, nombre in dependencias.items():
        try:
            __import__(modulo)
            print(f"  ✅ {nombre}")
        except ImportError:
            print(f"  ❌ {nombre} - NO instalado")
            todas_ok = False
    
    return todas_ok

def verificar_estructura():
    """Verifica la estructura del proyecto."""
    from pathlib import Path
    
    print("\n📁 Verificando estructura del proyecto:")
    
    directorios_requeridos = [
        'src',
        'src/ui',
        'src/ui/views',
        'src/ui/components',
        'src/database',
        'src/logic',
        'data'
    ]
    
    archivos_requeridos = [
        'main.py',
        'src/__init__.py',
        'src/ui/theme.py'
    ]
    
    todas_ok = True
    
    for directorio in directorios_requeridos:
        ruta = Path(directorio)
        if ruta.exists() and ruta.is_dir():
            print(f"  ✅ {directorio}/")
        else:
            print(f"  ❌ {directorio}/ - NO encontrado")
            todas_ok = False
    
    for archivo in archivos_requeridos:
        ruta = Path(archivo)
        if ruta.exists() and ruta.is_file():
            print(f"  ✅ {archivo}")
        else:
            print(f"  ❌ {archivo} - NO encontrado")
            todas_ok = False
    
    return todas_ok

def main():
    """Función principal."""
    print("=" * 60)
    print("   ConSmart - Verificación de Flet 0.80")
    print("=" * 60)
    
    print("\n🔍 Verificando instalación de Flet...")
    flet_ok = verificar_flet()
    
    deps_ok = verificar_dependencias()
    
    struct_ok = verificar_estructura()
    
    print("\n" + "=" * 60)
    print("   RESUMEN")
    print("=" * 60)
    
    if flet_ok and deps_ok and struct_ok:
        print("✅ Todo está listo para ejecutar ConSmart")
        print("\nPara ejecutar la aplicación:")
        print("  $ flet run main.py")
        print("\nO en modo desarrollo:")
        print("  $ flet run -d main.py")
        return 0
    else:
        print("⚠️  Se encontraron problemas")
        
        if not flet_ok:
            print("\n📥 Para instalar/actualizar Flet:")
            print("  Opción 1 (uv):  $ uv sync")
            print("  Opción 2 (pip): $ pip install --upgrade 'flet[all]>=0.80.0'")
        
        if not deps_ok:
            print("\n📥 Para instalar dependencias faltantes:")
            print("  $ pip install -r requirements.txt")
        
        if not struct_ok:
            print("\n⚠️  Verifica que estés en el directorio correcto del proyecto")
        
        return 1

if __name__ == "__main__":
    sys.exit(main())
