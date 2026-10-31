# Configuración de TikTok Developers

Este documento guía paso a paso para configurar la aplicación VANTS Clipper en TikTok Developers.

## 📋 Requisitos previos

- Cuenta de TikTok desarrollador
- Cuenta de YouTube (para configurar OAuth)
- Cuenta de Instagram (opcional)

## 🔐 Crear la aplicación

### 1. Iniciar sesión en TikTok Developers

1. Ve a https://developers.tiktok.com
2. Haz clic en "Login" en la esquina superior derecha
3. Inicia sesión con tu cuenta de TikTok

### 2. Crear una organización

1. Ve a **Organizations**
2. Haz clic en **Create Organization**
3. Pega la URL de tu perfil público de TikTok (opcional)
4. Ingresa un nombre para tu organización
5. Haz clic en **Create**

### 3. Crear la aplicación

1. Ve a **Apps**
2. Haz clic en **Create app**
3. Completa los siguientes campos:

   **App name:**
   ```
   VANTS Clipper
   ```

   **App type:**
   Selecciona: **Other** (Login with TikTok, Share Kit, Content Posting API, or others)

   **Description:**
   ```
   VANTS Clipper es una herramienta automática que convierte los mejores momentos de tus directos en Shorts/TikTok/Reels. Detecta clips de Razer Cortex, graba directos de Kick, detecta picos de hype en el chat y permite marcar momentos destacados con !clip. Los clips se convierten a formato vertical 9:16 y se publican automáticamente en YouTube Shorts, TikTok e Instagram Reels.
   ```

   **Terms of Service URL:**
   ```
   https://vants.vants.workers.dev/terminos.html
   ```

   **Privacy Policy URL:**
   ```
   https://vants.vants.workers.dev/privacidad.html
   ```

   ⚠️ Usa estas URLs exactas — son páginas públicas reales (verificado HTTP 200).
   No pongas enlaces a este repositorio de GitHub: es privado y TikTok no podrá
   verlo (rechazaría la revisión).

   **App icon:**
   Sube `vants-clipper-icon-512.png` (incluido en este repo, 512×512 PNG).

   **Platforms:**
   - ✅ Web
   - ✅ Desktop

4. Haz clic en **Create app**

## 🔑 Configurar las credenciales

### 1. Navegar a la página de la aplicación

1. Ve a **Organizations** → **VANTS**
2. Haz clic en **Apps**
3. Haz clic en **VANTS Clipper**

### 2. Ir a la sección de Credentials

1. En el menú lateral, haz clic en **Credentials**
2. Verás dos campos:
   - **Client key** (oculto con asteriscos)
   - **Client secret** (oculto con asteriscos)

### 3. Revelar las credenciales

1. Haz clic en el botón **Reset** al lado de **Client secret**
2. En el diálogo de confirmación, haz clic en **Reset** de nuevo
3. Las credenciales se revelarán inmediatamente
4. **Copia el Client Key y Client Secret** (¡es importante guardarlos!)

### 4. Actualizar config.json

Abre `config.json` en tu editor de texto y actualiza las siguientes líneas:

```json
"tiktok": {
  "activo": true,
  "client_key": "COPIA_EL_CLIENT_KEY_AQUI",
  "client_secret": "COPIA_EL_CLIENT_SECRET_AQUI",
  "token": "tiktok_token.json",
  "privacidad": "SELF_ONLY"
}
```

## 📦 Agregar productos

La app necesita **DOS productos** (el script usa OAuth de Login Kit + publicación
con Content Posting API — si falta cualquiera, la autorización falla):

### 1. Ir a la sección de Products

1. En el menú lateral, haz clic en **Products**
2. Haz clic en **Add products**

### 2. Seleccionar los dos productos

1. En el diálogo, busca y selecciona:
   - ✅ **Login Kit** (necesario para la ventana "Continuar con TikTok")
   - ✅ **Content Posting API** (necesario para publicar los videos)
2. Haz clic en **Add products**

### 3. Configurar el Redirect URI de Login Kit ⚠️ CRÍTICO

Este es el bloque que más se olvida. **Sin él, el navegador da error al autorizar:**

1. En **Products**, haz clic en **Login Kit** para abrir su configuración
2. En el campo **Redirect URI**, añade EXACTAMENTE esta URL:

   ```
   http://localhost:8777/callback
   ```

   (Debe coincidir carácter por carácter con la que usa `vants_clipper.py`,
   incluido el puerto `8777` y `/callback`.)

3. Guarda los cambios.

### 4. Verificar la configuración

1. Ve a **Products** en el menú lateral
2. Verifica que **Login Kit** y **Content Posting API** estén listados
3. En Login Kit, verifica que el redirect URI sea `http://localhost:8777/callback`

## 🔐 Configurar Scopes

### 1. Ir a la sección de Scopes

1. En el menú lateral, haz clic en **Scopes**
2. Haz clic en **Add scopes**

### 2. Seleccionar los scopes necesarios

Para la aplicación VANTS Clipper, necesitas los siguientes scopes:

- ✅ `user.info.basic` - Para obtener información básica del usuario
- ✅ `video.publish` - Para publicar videos en TikTok

### 3. Verificar la configuración

1. Ve a **Scopes** en el menú lateral
2. Verifica que los scopes anteriores estén listados
3. Haz clic en cada scope para ver los detalles

## 📋 Configurar Roles & Access

### 1. Ir a la sección de Roles & Access

1. En el menú lateral, haz clic en **Roles & Access**
2. Verifica que tu usuario (`feispla@hotmail.com`) tenga el rol de **Org owner**

### 2. Invitar a otros usuarios (opcional)

Si quieres compartir el acceso con otros usuarios:

1. Haz clic en **Invite app manager**
2. Ingresa el correo electrónico del usuario
3. Selecciona el rol (App manager, App reviewer, etc.)
4. Haz clic en **Invite**

## 📝 Configurar App Review

### 1. Ir a la sección de App Review

1. En el menú lateral, haz clic en **App review**
2. Lee la información de **App Review Guidelines**
3. Haz clic en el link para ver las guías completas

### 4. Explicación de la aplicación

En el campo **Explain how each product and scope works**, pega este texto
(en inglés — los revisores de TikTok lo leen en inglés; debajo está la versión
en español por si la interfaz la pide):

```
VANTS Clipper is a desktop tool used by our own team to automatically clip the
best moments of our live streams (Kick) and gameplay sessions (Razer Cortex),
convert them to vertical 9:16 format, and post them to our own TikTok account.

Products and scopes:
- Login Kit (user.info.basic): used only to authenticate the single TikTok
  account owned by our organization and to display the account's display name
  in our app's status screen after connecting.
- Content Posting API (video.publish): used to upload the generated clips
  directly to our own account. While the app is unaudited we post with
  privacy_level SELF_ONLY only; public posting is only enabled after this
  review is approved.

The app does not collect, store or share any end-user data: it authenticates
one account controlled by our organization, uploads videos we created
ourselves, and nothing else. There are no other users of this app.
```

Versión en español (por si la necesitas):

```
VANTS Clipper es una herramienta de escritorio usada por nuestro propio equipo
para recortar automáticamente los mejores momentos de nuestros directos (Kick)
y partidas (Razer Cortex), convertirlos a formato vertical 9:16 y publicarlos
en nuestra propia cuenta de TikTok.

Productos y scopes:
- Login Kit (user.info.basic): solo para autenticar la única cuenta de TikTok
  de nuestra organización y mostrar su nombre en la pantalla de estado de la app.
- Content Posting API (video.publish): para subir los clips generados
  directamente a nuestra propia cuenta. Mientras la app no está auditada
  publicamos solo con privacy_level SELF_ONLY; la publicación pública se
  activa tras la aprobación de esta revisión.

La app no recoge, almacena ni comparte datos de usuarios finales: autentica
una cuenta controlada por nuestra organización y sube videos creados por
nosotros. No tiene otros usuarios.
```

### 4b. Guion del demo video

Graba 60–90 s mostrando, en este orden:
1. El agente detectando un clip nuevo (carpeta de Razer Cortex o directo de Kick)
2. El clip convertiéndose a vertical 9:16
3. La ventana "Continuar con TikTok" (OAuth) y el permiso concedido
4. El clip apareciendo en tu perfil de TikTok como **privado (solo tú)**
5. `config.json` con `privacidad: "SELF_ONLY"` en pantalla

### 5. Subir demo video (opcional)

Si tu aplicación no ha sido aprobada antes, debes subir un demo video:

1. Haz clic en **Upload**
2. Sube un video que demuestre la funcionalidad de la aplicación
3. El video debe mostrar:
   - El flujo de captura de clips
   - La conversión a formato vertical
   - La publicación en TikTok

### 6. Solicitar revisión

1. Ve a **App review** en el menú lateral
2. Haz clic en **Submit for review**
3. Verifica que todos los campos estén completos
4. Haz clic en **Submit for review**

## ✅ Verificar la configuración

### 1. Chequeo rápido

1. Ve a **Apps** → **VANTS Clipper**
2. Haz clic en **Credentials**
3. Verifica que el **Client Key** y **Client Secret** estén visibles
4. Verifica que la aplicación esté en el entorno **Production** (no Sandbox)
5. **Products**: Login Kit + Content Posting API añadidos
6. **Login Kit**: redirect URI `http://localhost:8777/callback` guardado
7. **Scopes**: `user.info.basic` + `video.publish` solicitados
8. **App review**: explicación pegada + icono 512×512 subido + demo video subido
9. Pulsa **Submit for review**

Datos ya verificados (2026-10-31):
- App ID: `7702764230904023061`
- Organización: `7702803050838262804`
- Credenciales en `config.json` probadas contra el endpoint de tokens (HTTP 200)
- Mientras la app esté en *pending*, los videos se publican **privados
  (SELF_ONLY)** — ya está configurado así en `config.json`

### 2. Probar la conexión

1. Abre una terminal
2. Navega a la carpeta del proyecto
3. Ejecuta:
```bash
python vants_clipper.py --chequeo
```

4. Verifica que aparezca:
   - ✅ TikTok activo
   - ✅ Client key: [tu_client_key]
   - ✅ Client secret: [tu_client_secret]

## 🚨 Errores comunes

### Error: "TikTok no devolvió id"

**Solución:**
- Verifica que el `client_key` y `client_secret` estén correctos
- Verifica que la aplicación tenga el scope correcto habilitado
- Verifica que el token de OAuth sea válido

### Error: "TikTok init: [error]"

**Solución:**
- Verifica que el token de OAuth sea válido
- Verifica que la aplicación esté en el entorno correcto (Production o Sandbox)
- Verifica que los scopes estén habilitados

### Error: "TikTok fallo publicando"

**Solución:**
- Verifica que el video no supere los 60MB
- Verifica que el video tenga formato compatible (mp4, mov)
- Verifica que el token de OAuth sea válido
- Verifica que la aplicación esté aprobada (si es necesario)

## 📞 Soporte

Si tienes problemas con la configuración de TikTok Developers:

1. Ve a https://developers.tiktok.com/support
2. Abre un ticket de soporte
3. Incluye:
   - Nombre de la aplicación: VANTS Clipper
   - App ID: [tu_app_id]
   - Descripción del problema

## 📚 Referencias

- [TikTok Developers Documentation](https://developers.tiktok.com/docs)
- [Content Posting API](https://developers.tiktok.com/doc/content-posting-api/getting-started)
- [App Review Guidelines](https://developers.tiktok.com/doc/app-review-guidelines)
