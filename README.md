# VANTS Clipper — Agente Automático de Clips y Shorts

Agente de escritorio para Windows del ecosistema **VANTS GAMES** que detecta clips de **Razer Cortex** y directos de **Kick**, los convierte a formato vertical 9:16, optimiza títulos SEO vía **`https://int.vants.cc/clips/seo`** (con cuotas diarias por membresía VANTS + vidIQ MCP) y los publica automáticamente en YouTube Shorts / TikTok anunciándolos en Discord a través de **`https://bot.vants.cc`**.

---

## Características

- **Detección automática Razer Cortex:** monitorea tu carpeta de clips (VALORANT, CS2, Fortnite, etc.).
- **Directos de Kick:** grabación y recorte de highlights por picos de chat o comando `!clip` (`https://vants.cc/kick`).
- **Conversión vertical 9:16:** generación de Shorts/Reels con `ffmpeg`.
- **Optimización SEO VANTS:** consulta `https://int.vants.cc/clips/seo` y respeta cuotas diarias (`PASE S4`, `VANTS PRO`, `VANTS CREATOR`, `SOCIO VANTS`).
- **Publicación y avisos:** sube a YouTube Shorts (scopes mínimos `youtube.readonly` y `youtube.upload`) y notifica `clip.published` a `https://bot.vants.cc` → `vants-bus` → Discord.

---

## Instalación

### Vía WinGet (Windows)
```powershell
winget install VANTSGAMES.VANTSClipper
```

### Desde código fuente
```bash
git clone https://github.com/VANTSGAMES/VANTS-Clipper.git
cd VANTS-Clipper
pip install -r requirements.txt
winget install Gyan.FFmpeg
```

---

## Configuración segura (sin secretos en Git)

> **Importante:** nunca guardes claves privadas ni tokens en commits de `config.json`. Usa variables de entorno o archivos locales ignorados por Git:

| Variable de entorno | Uso |
| --- | --- |
| `CLIPPER_SECRET` | Autenticación contra `https://int.vants.cc` y `https://bot.vants.cc` |
| `VANTS_BOT_SECRET` | Alternativa directa para notificar a `https://bot.vants.cc` |
| `VANTSBOT_URL` | Por defecto `https://bot.vants.cc` |
| `VANTS_API_TOKEN` | Opcional: sincroniza el enlace del Short en `https://vants.cc/clips` |

URLs oficiales preconfiguradas en `config.json`:
- `worker_url`: `https://vants.cc/kick`
- `vants_integraciones_url`: `https://int.vants.cc`

---

## Ejecución y verificación

```bash
python3 -m py_compile vants_clipper.py
python vants_clipper.py
```

---

## Ecosistema VANTS (`vants.cc`)

- **Web oficial:** https://vants.cc
- **Integraciones API:** https://int.vants.cc
- **Bot Discord:** https://bot.vants.cc
- **App PC (`VANTS.exe`):** https://github.com/VANTSGAMES/banter
