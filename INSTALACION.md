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
   - **Windows 10/11:** Compatible con WSL2
   - **Instalación:** Ejecuta el instalador y sigue las instrucciones

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
1. Descarga Docker Desktop: https://www.docker.com/products/docker-desktop
2. Instala Docker Desktop
3. Inicia Docker Desktop (icono en la bandeja del sistema)
4. Espera a que Docker esté completamente iniciado (icono verde)
5. Reinicia `DJI_3D_Mapper.exe`

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

- **Docker Desktop:** ⚠️ **DEBES INSTALARLO POR SEPARADO**
  - Docker NO está incluido en la aplicación
  - Es necesario para que WebODM funcione
  - Descarga desde: https://www.docker.com/products/docker-desktop
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

**Solución:**
1. Descarga Docker Desktop: https://www.docker.com/products/docker-desktop
2. Instala Docker Desktop
3. Inicia Docker Desktop
4. Espera a que el icono en la bandeja muestre "Docker Desktop is running"
5. Haz clic en "Check Status" en la pestaña WebODM de la aplicación

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
