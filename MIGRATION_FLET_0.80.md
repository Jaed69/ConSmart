# Guía de Migración a Flet 0.80 (Flet v1)

## 📋 Resumen de Cambios Importantes

Flet 0.80 representa la versión 1.0 del framework y trae cambios significativos (breaking changes) que debes conocer.

---

## 🔴 CAMBIOS CRÍTICOS (Breaking Changes)

### 1. **Eliminación de Métodos `_async`**

**ANTES (Flet < 0.80):**
```python
# Métodos con sufijo _async
await page.update_async()
await control.update_async()
await dialog.open_async()
```

**AHORA (Flet 0.80+):**
```python
# Métodos sin sufijo _async - todos son síncronos por defecto
page.update()
control.update()
dialog.open()
```

**✅ Estado en tu código:** Tu código YA usa los métodos correctos (`page.update()`), así que **NO necesitas cambios aquí**.

---

### 2. **Intercambio de Button y ElevatedButton**

En Flet 0.80, `Button` y `ElevatedButton` **intercambiaron sus roles visuales**:

**ANTES (Flet < 0.80):**
- `Button` → Botón plano sin elevación
- `ElevatedButton` → Botón con elevación y sombra

**AHORA (Flet 0.80+):**
- `Button` → Botón con elevación y sombra (antes ElevatedButton)
- `ElevatedButton` → Botón plano sin elevación (antes Button)

**⚠️ Impacto en tu código:** Usas `ft.Button` en múltiples archivos. **Es probable que notes cambios visuales** en tus botones, pero **funcionarán correctamente**.

**Archivos afectados:**
- `main.py` (línea 184)
- `src/ui/views/login_view.py` (línea 57)
- `src/ui/views/history_view.py` (líneas 102, 142, 419, 452)
- `src/ui/views/admin_view.py` (líneas 166, 261, 365)
- `src/ui/views/dashboard_view.py` (línea 99)
- `src/ui/components/excel_grid.py` (líneas 339, 345, 353, 359)

**Solución:** Si quieres mantener el aspecto visual anterior, intercambia:
- `ft.Button` → `ft.ElevatedButton` (para botones planos)
- `ft.ElevatedButton` → `ft.Button` (para botones con elevación)

---

### 3. **Cambios en Colores**

**ANTES (Flet < 0.80):**
```python
ft.Colors.BLACK54  # ❌ Ya no funciona
ft.Colors.WHITE70  # ❌ Ya no funciona
```

**AHORA (Flet 0.80+):**
```python
ft.Colors.BLACK_54  # ✅ Correcto
ft.Colors.WHITE_70  # ✅ Correcto
```

**✅ Estado en tu código:** No encontré uso de estos colores específicos, así que **NO necesitas cambios aquí**.

---

### 4. **Método `copy_with` → `copy`**

**ANTES (Flet < 0.80):**
```python
new_style = style.copy_with(color="red")  # ❌ Ya no funciona
```

**AHORA (Flet 0.80+):**
```python
new_style = style.copy(color="red")  # ✅ Correcto
```

**✅ Estado en tu código:** No encontré uso de `copy_with`, así que **NO necesitas cambios aquí**.

---

### 5. **PageView → BasePage**

El componente `PageView` fue refactorizado a `BasePage`.

**✅ Estado en tu código:** No usas `PageView`, así que **NO necesitas cambios aquí**.

---

### 6. **NavigationDrawer y Pagelet API**

Hubo cambios en la API de `NavigationDrawer` y `Pagelet`.

**✅ Estado en tu código:** Usas `NavigationRail` (no `NavigationDrawer`), así que **NO necesitas cambios aquí**.

---

## 🆕 NUEVAS CARACTERÍSTICAS EN FLET 0.80

### 1. **ContextMenu Control**
Nuevo control para menús contextuales (clic derecho).

### 2. **RadarChart**
Nuevo tipo de gráfico disponible en `flet_charts`.

### 3. **Testing Framework**
Nuevo framework de testing integrado.

### 4. **ExpansionTile Programático**
Ahora puedes expandir/colapsar `ExpansionTile` programáticamente.

### 5. **TextField Selection Control**
Control y escucha de cambios de selección/cursor en `TextField`.

### 6. **Device Info**
Nueva función `page.get_device_info()` para obtener información del dispositivo.

### 7. **Dropdown Mejorado**
- Nueva propiedad `Dropdown.text`
- Nuevo evento `on_select`
- Nueva propiedad `menu_width`

---

## 📝 ACCIONES REQUERIDAS PARA TU APLICACIÓN

### ✅ 1. Actualizar `requirements.txt`

Tu `pyproject.toml` ya especifica `flet[all]>=0.80.0`, pero `requirements.txt` está desactualizado.

**Archivo actual:**
```txt
flet>=0.21.0  # ❌ Versión muy antigua
```

**Debe ser:**
```txt
flet[all]>=0.80.0  # ✅ Versión correcta
```

### ⚠️ 2. Revisar Apariencia de Botones (Opcional)

Debido al intercambio de `Button`/`ElevatedButton`, tus botones pueden verse diferentes. 

**Opciones:**
1. **Mantener el cambio:** Acepta la nueva apariencia (recomendado)
2. **Revertir apariencia:** Intercambia `Button` ↔ `ElevatedButton` en tu código

### ✅ 3. Instalar/Actualizar Flet

Usando `uv` (recomendado, ya que tienes `uv.lock`):
```bash
uv sync
```

O con pip:
```bash
pip install --upgrade "flet[all]>=0.80.0"
```

---

## 🔧 INSTALACIÓN Y ACTUALIZACIÓN

### Opción 1: Usando UV (Recomendado)
```bash
cd /home/luciel/Documentos/GitHub/ConSmart
uv sync
```

### Opción 2: Usando pip
```bash
cd /home/luciel/Documentos/GitHub/ConSmart
pip install --upgrade "flet[all]>=0.80.0"
pip install -r requirements.txt
```

---

## 🧪 VERIFICAR INSTALACIÓN

```bash
python3 -c "import flet; print(f'Flet version: {flet.__version__}')"
```

Debería mostrar: `Flet version: 0.80.0` o superior.

---

## 🚀 EJECUTAR TU APLICACIÓN

```bash
flet run main.py
```

O en modo desarrollo:
```bash
flet run -d main.py
```

---

## 🔗 RECURSOS ADICIONALES

### Documentación Oficial
- **Documentación Flet 0.80:** https://flet.dev/docs/
- **Releases en GitHub:** https://github.com/flet-dev/flet/releases/tag/v0.80.0
- **Pull Request de cambios async:** https://github.com/flet-dev/flet/pull/5537

### Cambios Principales (Pull Requests)
- **Eliminación de sufijo `_async`:** https://github.com/flet-dev/flet/pull/5537
- **Intercambio Button/ElevatedButton:** https://github.com/flet-dev/flet/pull/5592
- **Cambios en colores:** https://github.com/flet-dev/flet/pull/5752
- **Refactorización NavigationDrawer:** https://github.com/flet-dev/flet/pull/5754

### Comunidad
- **Discord:** https://discord.gg/dzWXP8SHG8
- **GitHub Discussions:** https://github.com/flet-dev/flet/discussions

---

## ⚠️ PROBLEMAS CONOCIDOS EN 0.80

### 1. Rendimiento con Listas Grandes
Algunos usuarios reportan que las listas grandes con componentes complejos pueden ser más lentas en 0.80.

**Referencia:** https://github.com/flet-dev/flet/discussions/5940

**Solución temporal:** Considera usar virtualización o paginación para listas grandes (tu implementación en `HistoryView` ya tiene paginación, lo cual es bueno).

### 2. TextField puede no renderizarse en ciertas circunstancias
**Referencia:** https://github.com/flet-dev/flet/discussions/5963

**Solución:** Asegúrate de llamar `page.update()` después de agregar TextFields dinámicamente.

---

## 📊 COMPATIBILIDAD DE TU CÓDIGO

| Componente | Estado | Acción Requerida |
|------------|--------|------------------|
| `page.update()` | ✅ Compatible | Ninguna |
| `control.update()` | ✅ Compatible | Ninguna |
| `ft.Button` | ⚠️ Cambio visual | Revisar apariencia |
| `ft.ElevatedButton` | ⚠️ Cambio visual | Revisar apariencia |
| Colors | ✅ Compatible | Ninguna |
| NavigationRail | ✅ Compatible | Ninguna |
| DataTable | ✅ Compatible | Ninguna |
| TextField | ✅ Compatible | Ninguna |
| Dropdown | ✅ Compatible | Considerar nuevas funciones |

---

## 🎯 RESUMEN EJECUTIVO

### ✅ Buenas Noticias
Tu código es **mayormente compatible** con Flet 0.80. Ya usas los métodos correctos (`page.update()` en lugar de `page.update_async()`).

### ⚠️ Cambios Necesarios
1. **Obligatorio:** Actualizar dependencias (`uv sync` o `pip install --upgrade flet[all]>=0.80.0`)
2. **Opcional:** Revisar apariencia de botones (cambio visual por intercambio Button/ElevatedButton)

### 🚀 Siguiente Paso
1. Actualizar dependencias
2. Ejecutar tu aplicación: `flet run main.py`
3. Revisar visualmente que los botones se vean como esperas
4. Si es necesario, intercambiar `Button` ↔ `ElevatedButton` para mantener apariencia anterior

---

## 📞 SOPORTE

Si encuentras problemas específicos después de migrar:
1. Verifica los errores en la consola
2. Consulta el Discord de Flet: https://discord.gg/dzWXP8SHG8
3. Revisa los issues en GitHub: https://github.com/flet-dev/flet/issues

---

**Última actualización:** Enero 2026
**Versión de esta guía:** 1.0
**Flet target version:** 0.80.0+
