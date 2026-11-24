#!/usr/bin/env python3
"""
VANTS Clipper — Agente Windows para capturar clips de Razer Cortex (VALORANT y otros),
convertirlos a 9:16 (YouTube Shorts), optimizar título/tags con vidIQ MCP y subirlos
automáticamente a YouTube Shorts y VANTS GAMES (https://vants.cc).

Uso:
  python vants_clipper.py --chequeo
  python vants_clipper.py
  python vants_clipper.py --launch-valorant
  python vants_clipper.py --test-convert "C:\\ruta\\al\\clip.mp4"
"""

from __future__ import annotations

import argparse
import glob
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path
from typing import Any

try:
    import requests
except ImportError:
    requests = None

APP_VERSION = "1.1.1"
GITHUB_RELEASES_API = "https://api.github.com/repos/VANTSGAMES/VANTS-Clipper/releases/latest"

BASE_DIR = Path(__file__).resolve().parent
CONFIG_PATH = BASE_DIR / "config.json"
ESTADO_PATH = BASE_DIR / "estado.json"
VERTICAL_DIR = BASE_DIR / "clips_verticales"

VIDEO_EXTS = {".mp4", ".mkv", ".mov", ".ts", ".m4v", ".webm"}
VIDIQ_MCP_URL = "https://mcp.vidiq.com/mcp"
VANTS_INT_URL = "https://int.vants.cc"

# Solo los 2 scopes mínimos de YouTube (evita el scope completo `youtube`).
YOUTUBE_SCOPES = [
    "https://www.googleapis.com/auth/youtube.readonly",
    "https://www.googleapis.com/auth/youtube.upload",
]

RIOT_LAUNCH_ARGS = ["--launch-product=valorant", "--launch-patchline=live"]


def version_a_tupla(ver: str) -> tuple[int, ...]:
    nums = re.findall(r"\d+", str(ver or "0"))
    return tuple(int(n) for n in nums[:4]) if nums else (0,)


def comprobar_actualizacion(cfg: dict[str, Any], auto_instalar: bool = True) -> dict[str, Any]:
    """Comprueba si existe una nueva versión en GitHub Releases y la instala en Windows si procede."""
    info: dict[str, Any] = {"actual": APP_VERSION, "ultima": APP_VERSION, "hay_update": False, "instalada": False}
    if not requests or not cfg.get("auto_update", True):
        return info
    try:
        r = requests.get(GITHUB_RELEASES_API, headers={"Accept": "application/vnd.github+json"}, timeout=8)
        if not r.ok:
            return info
        rel = r.json()
        tag = str(rel.get("tag_name") or "").lstrip("v").strip()
        if not tag:
            return info
        info["ultima"] = tag
        info["url"] = rel.get("html_url") or "https://github.com/VANTSGAMES/VANTS-Clipper/releases/latest"
        if version_a_tupla(tag) <= version_a_tupla(APP_VERSION):
            return info

        info["hay_update"] = True
        print(f"[Update] Nueva versión disponible: v{tag} (actual: v{APP_VERSION})")
        if not auto_instalar or os.name != "nt":
            print(f"[Update] Descarga manual: {info['url']}")
            return info

        assets = rel.get("assets") or []
        exe_asset = next((a for a in assets if str(a.get("name", "")).endswith(".exe")), None)
        sha_asset = next((a for a in assets if str(a.get("name", "")) == "SHA256SUMS.txt"), None)
        if not exe_asset or not exe_asset.get("browser_download_url"):
            return info

        tmp_dir = Path(tempfile.gettempdir()) / "vants-clipper-update"
        tmp_dir.mkdir(parents=True, exist_ok=True)
        exe_path = tmp_dir / str(exe_asset["name"])
        print(f"[Update] Descargando {exe_asset['name']}...")
        with requests.get(exe_asset["browser_download_url"], stream=True, timeout=60) as dl:
            dl.raise_for_status()
            with exe_path.open("wb") as f:
                for chunk in dl.iter_content(chunk_size=1024 * 256):
                    if chunk:
                        f.write(chunk)

        if sha_asset and sha_asset.get("browser_download_url"):
            sha_txt = requests.get(sha_asset["browser_download_url"], timeout=15).text
            expected = None
            for line in sha_txt.splitlines():
                if exe_asset["name"] in line:
                    expected = line.strip().split()[0].upper()
                    break
            if expected:
                actual_hash = hashlib.sha256(exe_path.read_bytes()).hexdigest().upper()
                if actual_hash != expected:
                    print("[Update] Hash SHA-256 no coincide; instalación abortada por seguridad.")
                    return info

        print("[Update] Instalando nueva versión en segundo plano...")
        subprocess.Popen(
            [str(exe_path), "/VERYSILENT", "/SUPPRESSMSGBOXES", "/NORESTART"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        info["instalada"] = True
    except Exception as e:
        print(f"[Update] Comprobación omitida ({e})")
    return info


def cargar_config() -> dict[str, Any]:
    if not CONFIG_PATH.exists():
        raise FileNotFoundError(f"No existe {CONFIG_PATH}. Crea o restaura config.json.")
    return json.loads(CONFIG_PATH.read_text(encoding="utf-8"))


def cargar_estado() -> dict[str, Any]:
    if not ESTADO_PATH.exists():
        return {"procesados": {}}
    try:
        return json.loads(ESTADO_PATH.read_text(encoding="utf-8"))
    except Exception:
        return {"procesados": {}}


def guardar_estado(estado: dict[str, Any]) -> None:
    ESTADO_PATH.write_text(json.dumps(estado, indent=2, ensure_ascii=False), encoding="utf-8")


def detectar_carpetas_cortex(cfg: dict[str, Any]) -> list[Path]:
    """Devuelve las carpetas válidas de clips de Razer Cortex (y carpetas extra como OBS/ShadowPlay)."""
    candidatos: list[Path] = []
    dir_cfg = str(cfg.get("cortex_clip_dir") or "").strip()
    if dir_cfg:
        p = Path(os.path.expandvars(dir_cfg)).expanduser()
        if p.exists():
            candidatos.append(p)

    for extra in cfg.get("carpetas_extra") or []:
        s = str(extra or "").strip()
        if s:
            pe = Path(os.path.expandvars(s)).expanduser()
            if pe.is_dir() and pe not in candidatos:
                candidatos.append(pe)

    local_app = os.environ.get("LOCALAPPDATA") or ""
    if local_app:
        patron_val = os.path.join(local_app, "Razer", "Razer Cortex", "GameClips", "*", "Videos", "VALORANT")
        for match in glob.glob(patron_val):
            pm = Path(match)
            if pm.is_dir() and pm not in candidatos:
                candidatos.append(pm)
        # También revisa si existe carpeta raíz GameClips
        raiz = Path(local_app) / "Razer" / "Razer Cortex" / "GameClips"
        if raiz.is_dir() and not candidatos:
            candidatos.append(raiz)

    return candidatos


def localizar_riot_client(cfg: dict[str, Any]) -> Path | None:
    """Busca RiotClientServices.exe en el ordenador Windows para lanzar VALORANT."""
    val_cfg = cfg.get("valorant") or {}
    explicit = str(val_cfg.get("riot_client_path") or "").strip()
    if explicit:
        p = Path(os.path.expandvars(explicit))
        if p.is_file():
            return p

    program_data = os.environ.get("PROGRAMDATA") or r"C:\ProgramData"
    installs_json = Path(program_data) / "Riot Games" / "RiotClientInstalls.json"
    if installs_json.is_file():
        try:
            data = json.loads(installs_json.read_text(encoding="utf-8"))
            for key in ("rc_live", "rc_default", "rc_beta"):
                val = data.get(key)
                if isinstance(val, str) and Path(val).is_file():
                    return Path(val)
        except Exception:
            pass

    for drive in ("C:", "D:", "E:"):
        cand = Path(f"{drive}\\Riot Games\\Riot Client\\RiotClientServices.exe")
        if cand.is_file():
            return cand
    return None


def lanzar_valorant(cfg: dict[str, Any]) -> bool:
    riot_exe = localizar_riot_client(cfg)
    if not riot_exe:
        print("[VALORANT] No encontré RiotClientServices.exe automáticamente.")
        print("           Añade 'valorant.riot_client_path' en config.json si lo instalaste en otra ruta.")
        return False
    args = (cfg.get("valorant") or {}).get("args") or RIOT_LAUNCH_ARGS
    cmd = [str(riot_exe), *[str(a) for a in args]]
    print(f"[VALORANT] Lanzando: {' '.join(cmd)}")
    try:
        subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return True
    except Exception as e:
        print(f"[VALORANT] Error al lanzar Riot Client: {e}")
        return False


def esperar_archivo_estable(path: Path, checks: int = 3, intervalo: float = 1.5) -> bool:
    """Espera hasta que Razer Cortex termine de escribir el archivo de vídeo."""
    ultimo_tam = -1
    estables = 0
    for _ in range(40):
        if not path.exists():
            return False
        tam = path.stat().st_size
        if tam > 0 and tam == ultimo_tam:
            estables += 1
            if estables >= checks:
                return True
        else:
            estables = 0
            ultimo_tam = tam
        time.sleep(intervalo)
    return ultimo_tam > 0


def convertir_vertical_9_16(origen: Path, destino: Path, duracion_max: int = 59) -> Path:
    """Convierte el clip horizontal 16:9 a vertical 1080x1920 con fondo difuminado."""
    destino.parent.mkdir(parents=True, exist_ok=True)
    ffmpeg = shutil.which("ffmpeg")
    if not ffmpeg:
        raise RuntimeError("ffmpeg no está instalado en PATH. Ejecuta: winget install Gyan.FFmpeg")

    filtro = (
        "[0:v]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,boxblur=20:5[bg];"
        "[0:v]scale=1080:-2:force_original_aspect_ratio=decrease[fg];"
        "[bg][fg]overlay=(W-w)/2:(H-h)/2,fps=60"
    )
    cmd = [
        ffmpeg,
        "-y",
        "-i",
        str(origen),
        "-t",
        str(max(5, int(duracion_max))),
        "-filter_complex",
        filtro,
        "-c:v",
        "libx264",
        "-preset",
        "veryfast",
        "-crf",
        "20",
        "-c:a",
        "aac",
        "-b:a",
        "192k",
        "-movflags",
        "+faststart",
        str(destino),
    ]
    proc = subprocess.run(cmd, capture_output=True, text=True)
    if proc.returncode != 0:
        raise RuntimeError(f"ffmpeg falló: {proc.stderr[-500:]}")
    return destino


def parse_mcp_sse_json(raw_text: str) -> dict[str, Any] | None:
    txt = (raw_text or "").strip()
    if not txt:
        return None
    if txt.startswith("{"):
        try:
            return json.loads(txt)
        except Exception:
            return None
    for line in reversed(txt.splitlines()):
        s = line.strip()
        if s.startswith("data:"):
            payload = s[5:].strip()
            if payload and payload != "[DONE]":
                try:
                    return json.loads(payload)
                except Exception:
                    continue
    return None


def vants_int_url(cfg: dict[str, Any]) -> str:
    return str(os.environ.get("VANTS_INT_URL") or cfg.get("vants_integraciones_url") or VANTS_INT_URL).rstrip("/")


def headers_vants_auth(cfg: dict[str, Any]) -> dict[str, str]:
    token = (os.environ.get("VANTS_API_TOKEN") or "").strip()
    if token:
        return {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    clipper_secret = (os.environ.get("CLIPPER_SECRET") or "").strip()
    if clipper_secret:
        return {"x-clipper-secret": clipper_secret, "Content-Type": "application/json"}
    return {}


def consultar_cuota_vants(cfg: dict[str, Any]) -> dict[str, Any] | None:
    """Consulta el plan activo y los cupos diarios (Shorts/día + vidIQ/día) en vants-integraciones."""
    headers = headers_vants_auth(cfg)
    if not headers or not requests:
        return None
    try:
        r = requests.get(f"{vants_int_url(cfg)}/clips/cuota", headers=headers, timeout=10)
        if r.ok:
            data = r.json()
            if data.get("ok"):
                return data
    except Exception as e:
        print(f"[VANTS] No se pudo consultar tu cuota diaria ({e})")
    return None


def consumir_short_vants(cfg: dict[str, Any]) -> tuple[bool, str, dict[str, Any] | None]:
    """Valida y descuenta 1 Short automático del cupo diario del miembro.

    Si el usuario solo corre en modo propietario local sin VANTS_API_TOKEN, permite continuar.
    """
    if not (os.environ.get("VANTS_API_TOKEN") or "").strip():
        return True, "modo_local_propietario", None
    headers = headers_vants_auth(cfg)
    if not requests:
        return True, "sin_requests", None
    try:
        r = requests.post(f"{vants_int_url(cfg)}/clips/cuota/consumir-short", headers=headers, timeout=10)
        data = r.json() if r.headers.get("content-type", "").startswith("application/json") else {}
        if r.ok and data.get("ok"):
            return True, "ok", data.get("quota")
        err = str(data.get("error") or f"http_{r.status_code}")
        detalle = str(data.get("detalle") or "No tienes cupo de subida automática disponible hoy.")
        return False, f"{err}: {detalle}", data.get("quota")
    except Exception as e:
        return False, f"error_red: {e}", None


def optimizar_con_vidiq(titulo_base: str, juego: str, cfg: dict[str, Any]) -> dict[str, Any]:
    """Optimiza título/tags vía vants-integraciones (cuota diaria del plan) o vidIQ MCP local, con fallback SEO gratis."""
    tags_default = [juego.lower(), f"{juego.lower()} shorts", f"{juego.lower()} clips", "gaming", "esports", "vants games", "shorts"]
    plantilla_titulo = str(cfg.get("titulo_template") or "{clip} · {juego} 🔥 #VANTS")
    plantilla_desc = str(
        cfg.get("descripcion")
        or "🎮 {juego} en VANTS GAMES\n🏆 Únete a torneos y rankings: https://vants.cc\n\n#shorts #valorant #gaming #vants"
    )
    fallback = {
        "source": "local",
        "title": plantilla_titulo.format(clip=titulo_base, juego=juego)[:98],
        "description": plantilla_desc.format(clip=titulo_base, juego=juego),
        "tags": tags_default,
    }

    vidiq_cfg = cfg.get("vidiq") or {}
    if not vidiq_cfg.get("activo", True) or not requests:
        return fallback

    # 1) Preferido para miembros: proxy seguro en vants-integraciones (respeta cupo diario del plan + tope global)
    vants_headers = headers_vants_auth(cfg)
    if vants_headers:
        try:
            r = requests.post(
                f"{vants_int_url(cfg)}/clips/seo",
                headers=vants_headers,
                json={"titulo": titulo_base[:160], "juego": juego[:40], "formato": "short"},
                timeout=15,
            )
            if r.ok:
                data = r.json()
                if data.get("ok") and data.get("recommendedTitle"):
                    src = str(data.get("source") or "vants_seo")
                    reason = data.get("vidiqReason")
                    if reason:
                        print(f"[SEO] {src} ({reason})")
                    else:
                        print(f"[SEO] {src}: {data['recommendedTitle']}")
                    return {
                        "source": src,
                        "title": str(data["recommendedTitle"])[:98],
                        "description": str(data.get("description") or fallback["description"]),
                        "tags": list(data.get("tags") or tags_default),
                    }
        except Exception as e:
            print(f"[SEO] Fallback local tras fallo de vants-integraciones ({e})")

    # 2) Fallback directo para el dueño si tiene VIDIQ_MCP_TOKEN en su propio PC
    env_name = str(vidiq_cfg.get("env_token") or "VIDIQ_MCP_TOKEN")
    token = (os.environ.get(env_name) or "").strip()
    if not token:
        return fallback

    try:
        r = requests.post(
            VIDIQ_MCP_URL,
            headers={
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json",
                "Accept": "application/json, text/event-stream",
            },
            json={
                "jsonrpc": "2.0",
                "id": int(time.time()),
                "method": "tools/call",
                "params": {
                    "name": "vidiq_generate_titles",
                    "arguments": {
                        "title": f"{titulo_base} en {juego}"[:180],
                        "description": fallback["description"][:400],
                        "numTitles": 3,
                        "type": "short",
                        "language": "es",
                    },
                },
            },
            timeout=15,
        )
        if not r.ok:
            return fallback
        rpc = parse_mcp_sse_json(r.text)
        if not rpc or not rpc.get("result"):
            return fallback
        structured = rpc["result"].get("structuredContent")
        if not structured:
            for item in rpc["result"].get("content") or []:
                if isinstance(item, dict) and item.get("type") == "text":
                    try:
                        structured = json.loads(item["text"])
                        break
                    except Exception:
                        pass
        titles = (structured or {}).get("titles") or []
        if titles and isinstance(titles[0], dict) and titles[0].get("title"):
            best = str(titles[0]["title"]).strip()[:98]
            score = titles[0].get("score")
            print(f"[vidIQ MCP] Título optimizado (score {score}): {best}")
            return {
                "source": "vidiq_mcp",
                "title": best,
                "description": fallback["description"],
                "tags": tags_default,
            }
    except Exception as e:
        print(f"[vidIQ MCP] Fallback local ({e})")
    return fallback


def subir_youtube_short(video_path: Path, seo: dict[str, Any], cfg: dict[str, Any]) -> str | None:
    """Sube el clip vertical a YouTube Shorts con scopes mínimos youtube.readonly + youtube.upload."""
    yt_cfg = (cfg.get("plataformas") or {}).get("youtube") or {}
    if not yt_cfg.get("activo", False):
        return None

    try:
        from google.auth.transport.requests import Request
        from google.oauth2.credentials import Credentials
        from google_auth_oauthlib.flow import InstalledAppFlow
        from googleapiclient.discovery import build
        from googleapiclient.http import MediaFileUpload
    except ImportError:
        print("[YouTube] Instala dependencias: pip install -r requirements.txt")
        return None

    secrets_file = BASE_DIR / str(yt_cfg.get("client_secrets") or "yt_client_secret.json")
    token_file = BASE_DIR / str(yt_cfg.get("token") or "yt_token.json")
    if not secrets_file.exists():
        print(f"[YouTube] Falta {secrets_file.name}. Descarga tu OAuth Client ID (Desktop App) desde Google Cloud.")
        return None

    creds = None
    if token_file.exists():
        creds = Credentials.from_authorized_user_file(str(token_file), YOUTUBE_SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(str(secrets_file), YOUTUBE_SCOPES)
            creds = flow.run_local_server(port=0)
        token_file.write_text(creds.to_json(), encoding="utf-8")

    youtube = build("youtube", "v3", credentials=creds)
    body = {
        "snippet": {
            "title": seo["title"][:100],
            "description": seo["description"][:4800],
            "tags": seo.get("tags") or ["valorant", "shorts", "vants"],
            "categoryId": "20",
            "defaultLanguage": "es",
        },
        "status": {
            "privacyStatus": str(yt_cfg.get("privacidad") or "unlisted"),
            "selfDeclaredMadeForKids": False,
        },
    }
    media = MediaFileUpload(str(video_path), chunksize=4 * 1024 * 1024, resumable=True, mimetype="video/mp4")
    req = youtube.videos().insert(part="snippet,status", body=body, media_body=media)
    resp = None
    while resp is None:
        status, resp = req.next_chunk()
        if status:
            print(f"[YouTube] Subiendo... {int(status.progress() * 100)}%")
    vid_id = resp.get("id")
    url = f"https://www.youtube.com/shorts/{vid_id}" if vid_id else None
    if url:
        print(f"[YouTube] Publicado: {url}")
    return url


def publicar_en_vants(url_youtube: str, titulo: str, juego: str, cfg: dict[str, Any] | None = None) -> bool:
    """Opcional: registra el enlace del Short en https://vants.cc/clips si VANTS_API_TOKEN está definido."""
    token = (os.environ.get("VANTS_API_TOKEN") or "").strip()
    if not token or not requests or not url_youtube:
        return False
    slug = re.sub(r"[^a-z0-9]", "", juego.lower()) or "valorant"
    base_url = vants_int_url(cfg or {})
    try:
        r = requests.post(
            f"{base_url}/clips",
            headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
            json={"url": url_youtube, "titulo": titulo[:100], "juego": slug, "publico": True},
            timeout=12,
        )
        if r.ok:
            print("[VANTS] Clip sincronizado en https://vants.cc/clips")
            return True
    except Exception as e:
        print(f"[VANTS] No se pudo sincronizar en vants.cc: {e}")
    return False


def notificar_vantsbot(url_youtube: str, titulo: str, juego: str, seo_source: str, cfg: dict[str, Any]) -> bool:
    """Publica el evento clip.published a través del motor Cloudflare vantsbot -> VANTS-BUS -> Discord."""
    if not requests or not url_youtube:
        return False
    bot_url = str(os.environ.get("VANTSBOT_URL") or cfg.get("vantsbot_url") or "https://bot.vants.cc").rstrip("/")
    secret = (os.environ.get("VANTS_BOT_SECRET") or os.environ.get("CLIPPER_SECRET") or str(cfg.get("clipper_secret") or "")).strip()
    if not secret:
        return False
    headers = {"Content-Type": "application/json"}
    if os.environ.get("VANTS_BOT_SECRET"):
        headers["x-vants-bot"] = secret
    else:
        headers["x-clipper-secret"] = secret
    try:
        r = requests.post(
            f"{bot_url}/banter/clipper",
            headers=headers,
            json={"title": titulo[:140], "url": url_youtube, "juego": juego, "seoSource": seo_source},
            timeout=10,
        )
        if r.ok:
            print("[vantsbot] Clip anunciado al VANTS-BUS (Discord)")
            return True
    except Exception as e:
        print(f"[vantsbot] Aviso omitido ({e})")
    return False


def huella_archivo(path: Path) -> str:
    st = path.stat()
    raw = f"{path.name}|{st.st_size}|{int(st.st_mtime)}"
    return hashlib.sha1(raw.encode("utf-8")).hexdigest()[:16]


def procesar_clip(origen: Path, cfg: dict[str, Any], estado: dict[str, Any]) -> None:
    if not esperar_archivo_estable(origen):
        return
    fid = huella_archivo(origen)
    if fid in estado.setdefault("procesados", {}):
        return

    juego = origen.parent.name if origen.parent.name.lower() not in ("videos", "gameclips") else str(cfg.get("juego_default") or "VALORANT")
    titulo_limpio = re.sub(r"[_\-]+", " ", origen.stem).strip() or f"Jugada {juego}"
    print(f"\n[Cortex] Nuevo clip detectado: {origen.name} ({juego})")

    dur_max = min(59, int(cfg.get("duracion_max") or 59))
    salida = VERTICAL_DIR / f"{origen.stem}_9x16.mp4"
    convertir_vertical_9_16(origen, salida, duracion_max=dur_max)
    print(f"[FFmpeg] Convertido a 9:16 -> {salida.name}")

    permitido, motivo_cuota, cuota_info = consumir_short_vants(cfg)
    seo = optimizar_con_vidiq(titulo_limpio, juego, cfg)
    yt_url = None
    if permitido:
        yt_url = subir_youtube_short(salida, seo, cfg)
        if yt_url:
            publicar_en_vants(yt_url, seo["title"], juego, cfg)
            if not cuota_info or cuota_info.get("autoDiscord", True):
                notificar_vantsbot(yt_url, seo["title"], juego, seo["source"], cfg)
    else:
        print(f"[Cuota VANTS] Subida automática omitida ({motivo_cuota}).")
        print(f"[Cuota VANTS] Tu clip 9:16 quedó guardado gratis en: {salida}")
        print("[Cuota VANTS] Activa o mejora tu plan en https://vants.cc/membresias")

    estado["procesados"][fid] = {
        "archivo": str(origen),
        "vertical": str(salida),
        "titulo": seo["title"],
        "seo_source": seo["source"],
        "youtube_url": yt_url,
        "cuota_estado": motivo_cuota,
        "fecha": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    }
    guardar_estado(estado)


def ejecutar_chequeo(cfg: dict[str, Any]) -> int:
    print(f"=== VANTS Clipper v{APP_VERSION} · Chequeo de entorno ===")
    print(f"Python:          {sys.version.split()[0]}")
    print(f"ffmpeg:          {shutil.which('ffmpeg') or 'NO ENCONTRADO (winget install Gyan.FFmpeg)'}")
    print(f"streamlink:      {shutil.which('streamlink') or 'opcional (pip install streamlink)'}")
    carpetas = detectar_carpetas_cortex(cfg)
    if carpetas:
        for c in carpetas:
            clips = [p for p in c.rglob("*") if p.is_file() and p.suffix.lower() in VIDEO_EXTS]
            print(f"Carpeta clips:   OK -> {c} ({len(clips)} clips encontrados)")
    else:
        print(f"Carpeta clips:   NO ENCONTRADA (configurado: {cfg.get('cortex_clip_dir')})")
    riot = localizar_riot_client(cfg)
    print(f"VALORANT (Riot): {riot or 'No detectado automáticamente'} ({' '.join(RIOT_LAUNCH_ARGS)})")
    yt_sec = BASE_DIR / str(((cfg.get("plataformas") or {}).get("youtube") or {}).get("client_secrets") or "yt_client_secret.json")
    print(f"YouTube OAuth:   {'OK (' + yt_sec.name + ')' if yt_sec.exists() else 'Falta ' + yt_sec.name}")
    print("Motor VANTS IA:  Proxy diario por membresía VANTS (con fallback SEO VANTS básico)")
    cuota = consultar_cuota_vants(cfg)
    if cuota:
        s = cuota.get("shorts") or {}
        v = cuota.get("creditosVants") or cuota.get("vidiq") or {}
        print(f"Plan VANTS hoy:  {cuota.get('label')} · Shorts {s.get('usados', 0)}/{s.get('limite', 0)} · Créditos VANTS {v.get('usados', 0)}/{v.get('limite', 0)}")
    else:
        print("Plan VANTS hoy:  Sin VANTS_API_TOKEN (define VANTS_API_TOKEN para activar tus Créditos VANTS diarios)")
    upd = comprobar_actualizacion(cfg, auto_instalar=False)
    print(f"Auto-update:     v{upd['actual']} (última en GitHub: v{upd['ultima']})")
    return 0


def vigilar_cortex(cfg: dict[str, Any]) -> None:
    estado = cargar_estado()
    carpetas = detectar_carpetas_cortex(cfg)
    if not carpetas:
        print("[VANTS Clipper] No se encontró ninguna carpeta de clips todavía. Revisaré cada 5s...")
    else:
        for c in carpetas:
            print(f"[VANTS Clipper] Vigilando carpeta: {c}")

    print(f"[VANTS Clipper v{APP_VERSION}] Agente activo. Presiona Ctrl+C para detener.")
    try:
        while True:
            carpetas = detectar_carpetas_cortex(cfg)
            for carpeta in carpetas:
                for p in sorted(carpeta.rglob("*"), key=lambda x: x.stat().st_mtime if x.exists() else 0):
                    if p.is_file() and p.suffix.lower() in VIDEO_EXTS:
                        if huella_archivo(p) not in estado.get("procesados", {}):
                            try:
                                procesar_clip(p, cfg, estado)
                            except Exception as e:
                                print(f"[Error] Procesando {p.name}: {e}")
            time.sleep(5)
    except KeyboardInterrupt:
        print("\n[VANTS Clipper] Detenido por el usuario.")


def main() -> int:
    parser = argparse.ArgumentParser(description="VANTS Clipper · Razer Cortex + VALORANT + vidIQ + YouTube Shorts")
    parser.add_argument("--chequeo", action="store_true", help="Verifica ffmpeg, Razer Cortex, VALORANT, YouTube, cuota VANTS y actualizaciones")
    parser.add_argument("--check-update", action="store_true", help="Comprueba e instala si hay nueva versión en GitHub Releases")
    parser.add_argument("--no-auto-update", action="store_true", help="Desactiva la comprobación automática de actualizaciones al iniciar")
    parser.add_argument("--launch-valorant", action="store_true", help="Lanza VALORANT (--launch-product=valorant --launch-patchline=live) y vigila clips")
    parser.add_argument("--test-convert", type=str, default="", help="Convierte un vídeo de prueba a 9:16 sin subirlo")
    args = parser.parse_args()

    cfg = cargar_config()
    if args.check_update:
        upd = comprobar_actualizacion(cfg, auto_instalar=True)
        print(json.dumps(upd, ensure_ascii=False))
        return 0

    if args.chequeo:
        return ejecutar_chequeo(cfg)

    if not args.no_auto_update:
        upd = comprobar_actualizacion(cfg, auto_instalar=True)
        if upd.get("instalada"):
            print("[Update] Cerrando para aplicar la nueva versión...")
            return 0

    if args.test_convert:
        src = Path(args.test_convert).expanduser().resolve()
        if not src.is_file():
            print(f"No existe el archivo: {src}")
            return 1
        dst = VERTICAL_DIR / f"test_{src.stem}_9x16.mp4"
        convertir_vertical_9_16(src, dst, duracion_max=min(59, int(cfg.get("duracion_max") or 59)))
        print(f"OK -> {dst}")
        return 0

    if args.launch_valorant or (cfg.get("valorant") or {}).get("lanzar_con_clipper"):
        lanzar_valorant(cfg)

    vigilar_cortex(cfg)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
