# VANTS Clipper

Clips automáticos para Shorts/TikTok/Reels usando Razer Cortex, Kick y detección de hype en el chat.

## 🚀 Características

- ✅ **Clips de Razer Cortex**: Detecta automáticamente clips nuevos en la carpeta de Valorant
- 🎬 **Directos de Kick**: Graba directos completos y corta highlights automáticamente
- 🔥 **Detección de hype**: Detecta picos de actividad en el chat de Kick
- 📌 **Marcas manuales**: Puedes marcar momentos destacados con !clip desde el chat
- 🎞️ **Conversión automática**: Convierte clips a formato vertical 9:16 (Shorts/Reels)
- 📤 **Publicación automática**: Sube clips a YouTube Shorts, TikTok e Instagram Reels
- 🤖 **Agente en segundo plano**: Corre 24/7 sin necesidad de mantener la terminal abierta

## 📋 Requisitos previos

- Python 3.10+
- ffmpeg instalado
- streamlink instalado
- Cuenta de YouTube con credenciales OAuth
- Cuenta de TikTok con app creada en TikTok Developers (Content Posting API)
- Cuenta de Instagram con access_token y R2 Cloudflare (opcional pero recomendado)

## 🛠️ Instalación

### 1. Descargar el agente

```bash
git clone https://github.com/VANTSGAMES/VANTS-Clipper.git
cd VANTS-Clipper
```

### 2. Instalar dependencias

```bash
pip install -r requirements.txt
```

### 3. Instalar ffmpeg y streamlink

**Windows (winget):**
```bash
winget install Gyan.FFmpeg
pip install streamlink[webbrowser]
```

**Manual:**
- Descarga ffmpeg desde https://ffmpeg.org/download.html
- Instálalo y añádelo a tu PATH
- Instala streamlink: `pip install streamlink[webbrowser]`

### 4. Configurar la carpeta de Cortex

1. Abre Razer Cortex
2. Ve a: CLIPS DE JUEGO → Ajustes
3. Copia la ruta de la carpeta de clips
4. Edita `config.json` y actualiza `cortex_clip_dir`

### 5. Configurar TikTok Developers

1. Ve a https://developers.tiktok.com
2. Inicia sesión con tu cuenta de TikTok
3. Crea una nueva organización (si no tienes una)
4. Crea una nueva aplicación:
   - Nombre: VANTS Clipper
   - Tipo: Other (Login with TikTok, Share Kit, Content Posting API, o others)
5. Ve a la sección **Credentials** de tu aplicación
6. Haz clic en **Reset Client Secret** para revelar las credenciales
7. Copia el **Client Key** y **Client Secret**
8. Actualiza `config.json` con estas credenciales:
```json
"tiktok": {
  "activo": true,
  "client_key": "TU_CLIENT_KEY",
  "client_secret": "TU_CLIENT_SECRET",
  "token": "tiktok_token.json",
  "privacidad": "SELF_ONLY"
}
```

### 6. Configurar YouTube

1. Ve a https://console.cloud.google.com
2. Crea un nuevo proyecto
3. Habilita la API de YouTube Data API v3
4. Ve a **Credentials** → **Create Credentials** → **OAuth client ID**
5. Selecciona **Desktop app**
6. Descarga el archivo `client_secret.json`
7. Crea un token de acceso:
```bash
python vants_clipper.py
# El agente te guiará para obtener el token
```

### 7. Configurar Instagram (opcional)

1. Ve a https://developers.facebook.com
2. Crea una app en **Apps** → **Create App**
3. Selecciona **Use Case** → **Business** → **Other**
4. Ve a **Facebook Login** → **Settings**
5. Añade tu dominio a **Valid OAuth Redirect URIs**
6. Ve a **App Review** → **Basic Information** → **Instagram Basic Display**
7. Solicita acceso a **Instagram Basic Display API**
8. Una vez aprobado, ve a **App Review** → **Instagram Basic Display** → **Access Token**
9. Copia el access_token
10. Configura R2 Cloudflare (opcional pero recomendado para hosting público):
    - Crea una cuenta en Cloudflare R2
    - Crea un bucket
    - Copia las credenciales de AWS S3
11. Actualiza `config.json`:
```json
"instagram": {
  "activo": true,
  "access_token": "TU_ACCESS_TOKEN",
  "r2_account_id": "TU_R2_ACCOUNT_ID",
  "r2_bucket": "tu-bucket",
  "r2_access_key": "TU_R2_ACCESS_KEY",
  "r2_secret": "TU_R2_SECRET"
}
```

## 🚀 Uso

### Arrancar el agente

**Método 1 (recomendado):**
```bash
vants-clipper.bat
```

**Método 2 (manual):**
```bash
cd VANTS-Clipper
set PATH=C:\Users\feisp\AppData\Roaming\Python\Python314\Scripts;%PATH%
python vants_clipper.py
```

### Chequeo rápido

```bash
python vants_clipper.py --chequeo
```

### Prueba de conversión

```bash
python vants_clipper.py --test-convert ruta/a/video.mp4
```

## 📁 Estructura de directorios

```
VANTS-Clipper/
├── vants_clipper.py      # Script principal del agente
├── config.json           # Configuración
├── requirements.txt      # Dependencias de Python
├── estado.json           # Estado del agente (se crea automáticamente)
├── yt_token.json         # Token de YouTube (se crea automáticamente)
├── tiktok_token.json     # Token de TikTok (se crea automáticamente)
├── clips_originales/     # Clips cortados del directo
├── grabaciones/          # Grabaciones completas de Kick
└── clips_verticales/     # Clips convertidos a 9:16 (ya publicados)
```

## 📊 Comandos útiles

### Verificar estado del agente
```bash
python vants_clipper.py --chequeo
```

### Ver logs
Los logs se imprimen en consola. Para guardarlos en archivo:
```bash
python vants_clipper.py > vants_log.txt 2>&1
```

### Detener el agente
Presiona **Ctrl+C** en la terminal donde se está ejecutando.

## ⚙️ Configuración

### Parámetros principales

| Parámetro | Descripción | Default |
|-----------|-------------|---------|
| `canal_kick` | Nombre del canal de Kick | "feispla" |
| `grabar_directo` | Grabar directos automáticamente | true |
| `cortex_clip_dir` | Carpeta de clips de Razer Cortex | "" |
| `juego_default` | Juego por defecto para el título | "Valorant" |
| `titulo_template` | Plantilla del título del clip | "{clip} · {juego} 🔥 #VANTS" |
| `duracion_max` | Duración máxima del clip (segundos) | 177 |

### Configuración de plataformas

```json
"plataformas": {
  "youtube": {
    "activo": true,
    "client_secrets": "yt_client_secret.json",
    "token": "yt_token.json",
    "privacidad": "public"
  },
  "tiktok": {
    "activo": true,
    "client_key": "TU_CLIENT_KEY",
    "client_secret": "TU_CLIENT_SECRET",
    "token": "tiktok_token.json",
    "privacidad": "SELF_ONLY"
  },
  "instagram": {
    "activo": false,
    "access_token": "",
    "r2_account_id": "",
    "r2_bucket": "",
    "r2_access_key": "",
    "r2_secret": ""
  }
}
```

## 🔧 Troubleshooting

### El agente no detecta clips nuevos de Cortex
- Verifica que la ruta en `cortex_clip_dir` sea correcta
- Verifica que los clips tengan extensión .mp4, .mkv, .ts o .mov
- Verifica que el archivo no haya sido procesado antes (estado en `estado.json`)

### TikTok no publica videos
- Verifica que el `client_key` y `client_secret` estén correctos
- Verifica que la aplicación tenga el scope correcto habilitado
- Verifica el token en `tiktok_token.json`

### YouTube falla al subir
- Verifica que el `client_secret.json` esté en la ubicación correcta
- Verifica que el token de OAuth sea válido
- Verifica que el video no supere los 60MB (YouTube tiene límites de tamaño)

## 📝 Licencia

Este proyecto está bajo la Licencia MIT. Consulta el archivo LICENSE para más detalles.

## 🤝 Contribución

Las contribuciones son bienvenidas. Por favor, abre un issue o un pull request para contribuir.

## 📧 Contacto

- GitHub: https://github.com/VANTSGAMES/VANTS-Clipper
- Kick: https://kick.com/feispla

## 🙏 Agradecimientos

- Razer Cortex por su herramienta de clips automáticos
- TikTok Developers por su Content Posting API
- YouTube por su plataforma de distribución
- Todos los viewers que usan el bot VANTS
