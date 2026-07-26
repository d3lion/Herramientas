# 📋 Clipboard Logger Pro

Aplicación de escritorio para capturar y estructurar datos desde el portapapeles, diseñada para facilitar la entrada de datos repetitiva y organizada.

![Python Version](https://img.shields.io/badge/python-3.7+-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)
![Status](https://img.shields.io/badge/status-stable-brightgreen.svg)

## 📝 Descripción

**Clipboard Logger Pro** es una herramienta que permite capturar datos del portapapeles y estructurarlos automáticamente en filas y columnas. Ideal para:

- ✅ Captura de datos en lote
- ✅ Entrada de datos estructurada
- ✅ Migración de datos desde documentos
- ✅ Automatización de tareas repetitivas
- ✅ Creación de bases de datos desde contenido copiado

## ✨ Características Principales

### 🎯 Captura Inteligente
- Captura automática del portapapeles al hacer Ctrl+C
- Relleno por columnas (cada copia llena una columna)
- Inicio automático de nueva fila al completar la anterior
- Vista previa en tiempo real del contenido copiado

### 📁 Formatos Soportados
- **CSV** - Con delimitador personalizable
- **JSON** - Formato estructurado y legible
- **XML** - Con formato indentado

### 🎮 Controles Avanzados
- ▶ Play/Stop - Iniciar/detener monitoreo
- ⏸ Pausa/Reanudar - Control de flujo
- ↩ Deshacer último - Eliminar último registro
- 📊 Nueva fila - Iniciar fila manualmente
- 🗑 Limpiar datos - Borrar todos los registros

### 💾 Guardado Automático
- Guardado inmediato tras cada fila completada
- Auto-guardado cada 5 registros
- Persistencia de datos en tiempo real

### 🖥️ Interfaz Intuitiva
- Vista previa del portapapeles
- Listado de datos capturados
- Contador de registros
- Estado de la fila actual
- Barra de estado informativa

## 🚀 Instalación

### Requisitos Previos
- Python 3.7 o superior
- pip (gestor de paquetes de Python)

### Instalación Rápida

```bash
# Clonar el repositorio
git clone https://github.com/tu-usuario/clipboard-logger-pro.git
cd clipboard-logger-pro

# Instalar dependencias
pip install pyperclip

# Ejecutar la aplicación
python clipboard_logger.py
```

### Instalación con entorno virtual (recomendado)

```bash
# Crear entorno virtual
python -m venv venv

# Activar entorno virtual (Windows)
venv\Scripts\activate
# Activar entorno virtual (Linux/Mac)
source venv/bin/activate

# Instalar dependencias
pip install pyperclip

# Ejecutar
python clipboard_logger.py
```

## 📖 Guía de Uso

### 1. Configuración Inicial

1. **Seleccionar ruta de destino**: Haz clic en "Seleccionar" y elige dónde guardar el archivo
2. **Elegir formato**: Selecciona CSV, JSON o XML
3. **Definir columnas**: 
   - Establece el número de columnas
   - Asigna nombres descriptivos a cada columna
4. **Opciones avanzadas** (opcional):
   - Delimitador CSV (por defecto: coma)
   - Encoding (UTF-8, Latin-1, CP1252)

### 2. Flujo de Trabajo

```
1. Play → Inicia el monitoreo
2. La aplicación espera el primer Ctrl+C
3. Ctrl+C → Captura el contenido (solo vista previa)
4. Ctrl+C → Rellena la Columna 1
5. Ctrl+C → Rellena la Columna 2
6. Ctrl+C → Rellena la Columna 3 → ¡Fila completada!
7. Se guarda automáticamente y comienza nueva fila
```

### 3. Ejemplo Práctico

**Configuración:**
- Columnas: `Nombre`, `Edad`, `Ciudad`
- Formato: CSV
- Ruta: `datos/personas.csv`

**Acciones:**
1. Ctrl+C → "Juan" (vista previa)
2. Ctrl+C → "Juan" → Columna "Nombre" llena
3. Ctrl+C → "25" → Columna "Edad" llena  
4. Ctrl+C → "Madrid" → Columna "Ciudad" llena → ¡Fila guardada!

**Resultado en CSV:**
```csv
timestamp,Nombre,Edad,Ciudad
2024-01-15 10:30:45,Juan,25,Madrid
```

### 4. Atajos y Controles

| Control | Función |
|---------|---------|
| **Play** | Inicia el monitoreo del portapapeles |
| **Stop** | Detiene el monitoreo y guarda datos |
| **Pausa** | Pausa temporalmente la captura |
| **Reanudar** | Continúa la captura |
| **Nueva fila** | Inicia una fila manualmente |
| **Deshacer** | Elimina el último registro |
| **Limpiar** | Elimina todos los registros |

## 🔧 Personalización

### Configuración de Columnas
```python
# En la interfaz, los nombres de columnas se pueden personalizar
# Ejemplo: "Nombre", "Apellido", "Email", "Teléfono"
```

### Formatos de Archivo

**CSV**: Ideal para hojas de cálculo
```csv
timestamp,Nombre,Edad,Ciudad
2024-01-15 10:30:45,Juan,25,Madrid
```

**JSON**: Ideal para APIs y aplicaciones web
```json
[
  {
    "timestamp": "2024-01-15 10:30:45",
    "data": {
      "Nombre": "Juan",
      "Edad": "25",
      "Ciudad": "Madrid"
    }
  }
]
```

**XML**: Ideal para intercambio de datos
```xml
<data>
  <record>
    <timestamp>2024-01-15 10:30:45</timestamp>
    <data>
      <Nombre>Juan</Nombre>
      <Edad>25</Edad>
      <Ciudad>Madrid</Ciudad>
    </data>
  </record>
</data>
```

## 🛠️ Tecnologías

- **Python 3.7+** - Lenguaje principal
- **Tkinter** - Interfaz gráfica nativa
- **pyperclip** - Manejo del portapapeles
- **json** - Procesamiento de JSON
- **csv** - Procesamiento de CSV
- **xml** - Procesamiento de XML

## 📁 Estructura del Proyecto

```
clipboard-logger-pro/
├── clipboard_logger.py    # Aplicación principal
├── README.md              # Documentación
├── requirements.txt       # Dependencias
└── LICENSE               # Licencia
```

## 🐛 Solución de Problemas

### Error: "pyperclip no encontrado"
```bash
pip install pyperclip
```

### Error: "No se puede guardar el archivo"
- Verifica que la ruta seleccionada sea válida
- Asegúrate de tener permisos de escritura
- Comprueba que el directorio existe

### El programa no captura el portapapeles
- Verifica que el monitoreo esté activo (Play)
- Comprueba que no esté en pausa
- Asegúrate de que el contenido del portapapeles no esté vacío

## 💡 Consejos y Trucos

1. **Uso eficiente**: Configura las columnas antes de empezar para evitar interrupciones
2. **Datos masivos**: Para grandes volúmenes de datos, usa el auto-guardado para no perder información
3. **Formatos**: CSV es el más ligero, JSON es el más flexible, XML es el más estandarizado
4. **Deshacer**: Úsalo para corregir errores sin perder el progreso
5. **Pausa**: Ideal para cuando necesitas copiar algo que no quieres capturar

## 🔄 Actualizaciones Futuras

- [ ] Soporte para múltiples portapapeles
- [ ] Expresiones regulares para parseo avanzado
- [ ] Plantillas de columnas predefinidas
- [ ] Exportación a Excel
- [ ] Modo oscuro
- [ ] Notificaciones de sistema
- [ ] Historial de sesiones


## 🤝 Contribuciones

Las contribuciones son bienvenidas. Por favor, sigue estos pasos:

1. Fork el proyecto
2. Crea tu rama de características (`git checkout -b feature/AmazingFeature`)
3. Commitea tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

## ⭐ Agradecimientos

- A la comunidad de Python por las herramientas y librerías
- A todos los usuarios que aportan feedback y sugerencias

---

**Hecho con ❤️ para facilitar la captura de datos**

*Si te gusta este proyecto, no olvides darle una ⭐ en GitHub*
