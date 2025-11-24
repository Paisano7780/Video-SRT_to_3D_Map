# Guía de Instalación - DJI Video to 3D Map Pipeline

## ¿Qué necesito instalar?

### 📦 Incluido en la Aplicación (NO necesitas instalarlo)

Estos componentes están **INCLUIDOS** en la aplicación y se instalan automáticamente:

1. **FFmpeg** ✅
   - Incluido en el ejecutable `DJI_3D_Mapper.exe`
   - Se descarga automáticamente en la primera ejecución si no está incluido
   - Usado para extraer frames de los videos

2. **ExifTool** ✅
   - Incluido en el ejecutable `DJI_3D_Mapper.exe`
   - Se descarga automáticamente en la primera ejecución si no está incluido
   - Usado para inyectar metadatos GPS en las imágenes

3. **WebODM** ✅
   - Incluido como submódulo en el código fuente
   - La aplicación lo gestiona automáticamente
   - NO necesitas descargarlo o instalarlo por separado
   - Se encuentra en la carpeta `./webodm` del repositorio

### ⬇️ Debes Instalar Por Separado (REQUERIDO para reconstrucción 3D)

Solo necesitas instalar **Docker Desktop** si quieres usar las funciones de reconstrucción 3D:

1. **Docker Desktop** ⚠️ REQUERIDO
   - **Descarga desde:** https://www.docker.com/products/docker-desktop
   - **Tamaño:** ~500 MB de descarga
   - **Espacio en disco:** ~2-3 GB después de instalar
   - **Necesario para:** Crear mapas 3D con WebODM
   - **Windows 10/11:** Requiere WSL 2 (Windows Subsystem for Linux 2)
   - **Instalación:** Ahora disponible instalación automática desde la aplicación con backend WSL 2 (requiere privilegios de administrador)

## Instalación Paso a Paso

### Opción 1: Usando el Ejecutable (Recomendado)

#### Paso 1: Descargar la Aplicación
1. Ve a [Releases](https://github.com/Paisano7780/Video-SRT_to_3D_Map/releases)
2. Descarga los archivos:
   - `DJI_3D_Mapper.exe` - Aplicación principal
   - `Install_Dependencies.exe` - Instalador de dependencias (opcional)

#### Paso 2: Primera Ejecución
1. Ejecuta `DJI_3D_Mapper.exe`
2. La aplicación automáticamente:
   - ✅ Verifica FFmpeg y ExifTool
   - ✅ Los descarga e instala si faltan
   - ⚠️ Te avisa si Docker no está instalado

#### Paso 3: Instalar Docker (Solo para Reconstrucción 3D)

**Requisitos Previos:**
- Windows 10 versión 1903 o superior (Build 18362+) o Windows 11
- WSL 2 (Windows Subsystem for Linux 2) instalado
  - Si no tienes WSL 2, la instalación automática intentará configurarlo
  - Puedes verificar ejecutando `wsl --list --verbose` en PowerShell

**Opción A: Instalación Automática (Recomendado)**

1. Al iniciar la aplicación por primera vez, si Docker no está instalado, aparecerá un diálogo
2. Selecciona "Sí" para instalar Docker Desktop automáticamente
3. **IMPORTANTE:** Gestión de privilegios de administrador
   - Si ya estás ejecutando como Administrador, la instalación procederá directamente
   - Si NO estás como Administrador, aparecerá un diálogo UAC (Control de Cuentas de Usuario)
   - Haz clic en "Sí" en el diálogo UAC para permitir la instalación
   - Alternativamente, puedes ejecutar la aplicación como Administrador desde el inicio
4. La aplicación descargará e instalará Docker Desktop con backend WSL 2 (~500 MB)
5. Cuando termine, aparecerá un mensaje pidiendo que reinicies tu computadora
6. **Reinicia tu computadora** (necesario para habilitar virtualización y WSL 2)
7. Después del reinicio:
   - Inicia Docker Desktop desde el menú de inicio
   - Espera a que Docker esté completamente iniciado (icono verde)
   - Reinicia `DJI_3D_Mapper.exe`

**Opción B: Instalación Manual**

1. Asegúrate de tener WSL 2 instalado
2. Descarga Docker Desktop: https://www.docker.com/products/docker-desktop
3. Instala Docker Desktop manualmente (selecciona WSL 2 como backend durante la instalación)
4. Reinicia tu computadora si se solicita
5. Inicia Docker Desktop (icono en la bandeja del sistema)
6. Espera a que Docker esté completamente iniciado (icono verde)
7. Reinicia `DJI_3D_Mapper.exe`

### Opción 2: Desde el Código Fuente

#### Paso 1: Clonar el Repositorio
```bash
# IMPORTANTE: Usar --recurse-submodules para incluir WebODM
git clone --recurse-submodules https://github.com/Paisano7780/Video-SRT_to_3D_Map.git
cd Video-SRT_to_3D_Map
```

**Si ya clonaste sin submodules:**
```bash
git submodule update --init --recursive
```

#### Paso 2: Instalar Dependencias de Python
```bash
pip install -r requirements.txt
```

#### Paso 3: Instalar Docker Desktop (para reconstrucción 3D)
1. Descarga: https://www.docker.com/products/docker-desktop
2. Instala y ejecuta Docker Desktop

#### Paso 4: Ejecutar la Aplicación
```bash
python main_app.py
```

## Resumen de Componentes

| Componente | ¿Incluido? | ¿Necesitas Instalarlo? | ¿Para Qué Sirve? |
|------------|------------|------------------------|------------------|
| **FFmpeg** | ✅ Sí | ❌ No | Extraer frames de videos |
| **ExifTool** | ✅ Sí | ❌ No | Añadir GPS a imágenes |
| **WebODM** | ✅ Sí (en código) | ❌ No | Software de reconstrucción 3D |
| **Docker Desktop** | ❌ No | ⚠️ **SÍ** | Ejecutar WebODM |

## Respuesta a tu Pregunta

### "¿Docker y WebODM tengo que instalarlos por separado o están incluidos en la app?"

**Respuesta:**

- **WebODM:** ✅ **INCLUIDO** en la aplicación (como submódulo git)
  - No necesitas descargarlo ni instalarlo
  - La aplicación lo gestiona automáticamente
  - Se inicia y se detiene desde la aplicación

- **Docker Desktop:** ⚠️ **DEBES INSTALARLO POR SEPARADO (AHORA CON INSTALACIÓN AUTOMÁTICA)**
  - Docker NO está incluido en la aplicación por defecto
  - Es necesario para que WebODM funcione
  - **NUEVO:** La aplicación puede descargar e instalar Docker automáticamente
  - Requiere privilegios de administrador y reinicio del sistema
  - También puedes instalarlo manualmente desde: https://www.docker.com/products/docker-desktop
  - La aplicación te avisará si Docker no está instalado

**¿Por qué Docker no está incluido?**
- Docker Desktop es un software grande y complejo
- Requiere privilegios de administrador para instalar
- Tiene su propio instalador oficial
- Funciona como un servicio del sistema operativo

## Funcionalidades Sin Docker

Puedes usar estas funciones **SIN Docker:**
- ✅ Extraer frames de videos DJI
- ✅ Parsear telemetría de archivos .SRT
- ✅ Sincronizar GPS con frames
- ✅ Inyectar metadatos EXIF en imágenes
- ✅ Exportar imágenes geoetiquetadas

**NO puedes hacer sin Docker:**
- ❌ Crear mapas 3D con WebODM
- ❌ Generar ortofotografías
- ❌ Crear modelos de elevación (DSM/DTM)
- ❌ Generar nubes de puntos

## Requisitos del Sistema

### Mínimos (Sin Reconstrucción 3D)
- Windows 10 o superior
- 4 GB RAM
- 2 GB espacio en disco

### Recomendados (Con Reconstrucción 3D)
- Windows 10/11 (64-bit)
- 16 GB RAM (mínimo 8 GB)
- 50 GB espacio en disco libre
- Docker Desktop instalado
- Procesador multi-núcleo

## Primera Vez Usando WebODM

Cuando uses WebODM por primera vez:

1. Docker descargará imágenes de WebODM (~2-3 GB)
2. La primera descarga puede tardar **10-15 minutos**
3. Los siguientes inicios serán **mucho más rápidos** (30-60 segundos)
4. Asegúrate de tener buena conexión a internet

## Solución de Problemas Comunes

### ❌ Error: "Docker is not installed"

**Solución Automática (Recomendado):**
1. Verifica que tienes Windows 10 versión 1903+ o Windows 11
2. Asegúrate de que WSL 2 está instalado (ejecuta `wsl --install` en PowerShell como Administrador si es necesario)
3. Ejecuta la aplicación (no necesita ser como Administrador inicialmente)
4. Cuando aparezca el diálogo de Docker no encontrado, selecciona "Sí" para instalación automática
5. Aparecerá un diálogo UAC - haz clic en "Sí" para permitir la instalación
6. Espera a que se descargue e instale Docker Desktop con backend WSL 2
7. Cuando se solicite, reinicia tu computadora
8. Después del reinicio, inicia Docker Desktop desde el menú de inicio
9. Espera a que el icono en la bandeja muestre "Docker Desktop is running"
10. Reinicia la aplicación

**Si la instalación automática falla:**
- Verifica que permitiste el diálogo UAC
- Verifica que WSL 2 está instalado correctamente
- Intenta ejecutar la aplicación como Administrador desde el inicio (clic derecho → "Ejecutar como administrador")

**Solución Manual:**
1. Instala WSL 2 si no lo tienes: `wsl --install` en PowerShell como Administrador
2. Descarga Docker Desktop: https://www.docker.com/products/docker-desktop
3. Instala Docker Desktop (asegúrate de seleccionar WSL 2 backend)
4. Inicia Docker Desktop
5. Espera a que el icono en la bandeja muestre "Docker Desktop is running"
6. Haz clic en "Check Status" en la pestaña WebODM de la aplicación

### ❌ Error: "Docker is not running"

**Solución:**
1. Inicia Docker Desktop desde el menú de inicio
2. Espera a que el icono en la bandeja del sistema se ponga verde
3. Haz clic en "Check Status" en la aplicación

### ❌ Error: "WebODM not found in ./webodm"

**Solución (Código Fuente):**
```bash
git submodule update --init --recursive
```

**Solución (Ejecutable):**
- Este error no debería aparecer con el ejecutable
- Si aparece, descarga nuevamente desde Releases

### ❌ FFmpeg o ExifTool no funcionan

**Solución:**
1. Cierra y abre la aplicación nuevamente
2. La aplicación detectará que faltan y los descargará
3. Si persiste el problema, ejecuta `Install_Dependencies.exe`

## Preguntas Frecuentes

**P: ¿Necesito internet después de instalar?**
R: Solo para la primera ejecución de WebODM (descarga imágenes Docker). Después puedes usar la aplicación sin internet (excepto WebODM).

**P: ¿La aplicación puede instalar Docker automáticamente?**
R: Sí, la aplicación puede descargar e instalar Docker Desktop automáticamente con backend WSL 2. Necesitas:
- Windows 10 versión 1903+ o Windows 11
- WSL 2 instalado (la aplicación intentará configurarlo)
- Aproximadamente 500 MB de descarga
- Un reinicio del sistema después de la instalación
- Conexión a internet
- Aceptar el diálogo UAC cuando aparezca

**P: ¿Qué es WSL 2 y por qué lo necesito?**
R: WSL 2 (Windows Subsystem for Linux 2) es una capa de compatibilidad de Linux para Windows. Docker Desktop lo usa como backend porque:
- Es más rápido que Hyper-V
- Usa menos recursos del sistema
- Es más estable y eficiente
- Es el backend recomendado por Docker para Windows 10/11

**P: ¿Cómo instalo WSL 2?**
R: 
1. Abre PowerShell como Administrador
2. Ejecuta: `wsl --install`
3. Reinicia tu computadora
4. WSL 2 estará listo para usar con Docker

**P: ¿Por qué necesito ejecutar como Administrador para instalar Docker?**
R: Docker Desktop requiere privilegios de administrador para:
- Instalar componentes del sistema (WSL 2)
- Configurar servicios de Windows
- Modificar configuraciones de red
La aplicación solicitará elevación UAC automáticamente si no estás ejecutando como Administrador.

**P: ¿Puedo usar la aplicación sin Docker?**
R: Sí, pero solo para procesar imágenes. No podrás crear mapas 3D.

**P: ¿Docker es gratis?**
R: Sí, Docker Desktop es gratuito para uso personal.

**P: ¿Cuánto espacio necesito?**
R: 
- Sin WebODM: ~2 GB
- Con WebODM: ~15-20 GB (incluye imágenes Docker y datos procesados)

**P: ¿WebODM guarda mis datos?**
R: Sí, WebODM almacena proyectos en contenedores Docker. Puedes eliminarlos desde Docker Desktop cuando no los necesites.

## Soporte

Si tienes problemas:
1. Revisa esta guía
2. Consulta [TROUBLESHOOTING en README.md](README.md#troubleshooting)
3. Abre un issue en GitHub con:
   - Descripción del error
   - Captura de pantalla
   - Logs de la aplicación

## Enlaces Útiles

- **Docker Desktop:** https://www.docker.com/products/docker-desktop
- **Documentación Docker:** https://docs.docker.com/desktop/
- **WebODM GitHub:** https://github.com/OpenDroneMap/WebODM
- **Releases de esta app:** https://github.com/Paisano7780/Video-SRT_to_3D_Map/releases
