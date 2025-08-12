"""
Script de prueba para conversión TTS con ElevenLabs usando Gradio 4.x.
Lee la API key desde variables de entorno (.env) y usa el SDK moderno.
"""

# --- Configuración inicial de la aplicación ---

from __future__ import annotations

import os
from typing import List, Optional, Tuple

from dotenv import load_dotenv
import gradio as gr
from elevenlabs import ElevenLabs, save
try:
    # Para logs detallados de errores del SDK
    from elevenlabs.core.api_error import ApiError  # type: ignore
except Exception:  # pragma: no cover
    ApiError = Exception  # fallback tipado

# Cargar variables de entorno desde .env si existe
load_dotenv()

# Parámetros por defecto de la demo (no sensibles)
DEFAULT_MODEL: str = "eleven_flash_v2_5"  # Modelo TTS por defecto (más barato/baja latencia)
DEFAULT_VOICE_ID: Optional[str] = "cgSgspJ2msm6clMCkdW9"  # Voice ID por defecto (opcional)
DEFAULT_TEXT: str = "Hola, este es un texto de ejemplo para convertir a voz."
DEFAULT_OUTPUT: str = "MP3"  # "MP3" o "WAV"

# Modelos con coste (etiqueta visible y model_id)
MODEL_CHOICES: List[dict] = [
    {"id": "eleven_v3", "label": "Eleven v3 — eleven_v3 — 1 crédito/caracter"},
    {"id": "eleven_multilingual_v2", "label": "Eleven Multilingual v2 — eleven_multilingual_v2 — 1 crédito/caracter"},
    {"id": "eleven_flash_v2_5", "label": "Eleven Flash v2.5 — eleven_flash_v2_5 — 0.5 crédito/caracter"},
    {"id": "eleven_flash_v2", "label": "Eleven Flash v2 — eleven_flash_v2 — 0.5 crédito/caracter"},
    {"id": "eleven_turbo_v2_5", "label": "Eleven Turbo v2.5 — eleven_turbo_v2_5 — 0.5 crédito/caracter"},
    {"id": "eleven_turbo_v2", "label": "Eleven Turbo v2 — eleven_turbo_v2 — 0.5 crédito/caracter"},
    {"id": "eleven_monolingual_v1", "label": "English v1 — eleven_monolingual_v1 — 1 crédito/caracter"},
    {"id": "eleven_multilingual_v1", "label": "Multilingual v1 — eleven_multilingual_v1 — 1 crédito/caracter"},
]

def get_model_label_by_id(model_id: str) -> str:
    for m in MODEL_CHOICES:
        if m["id"] == model_id:
            return m["label"]
    # fallback a la primera si no coincide
    return MODEL_CHOICES[0]["label"]

# Opciones de salida por formato
MP3_OPTIONS: List[tuple[str, str]] = [
    ("MP3 22.05 kHz 32 kbps — mp3_22050_32 — estándar", "mp3_22050_32"),
    ("MP3 44.1 kHz 32 kbps — mp3_44100_32 — estándar", "mp3_44100_32"),
    ("MP3 44.1 kHz 64 kbps — mp3_44100_64 — estándar", "mp3_44100_64"),
    ("MP3 44.1 kHz 96 kbps — mp3_44100_96 — estándar", "mp3_44100_96"),
    ("MP3 44.1 kHz 128 kbps — mp3_44100_128 — estándar (defecto)", "mp3_44100_128"),
    ("MP3 44.1 kHz 192 kbps — mp3_44100_192 — Creator+", "mp3_44100_192"),
]

WAV_OPTIONS: List[tuple[str, str]] = [
    ("WAV 16 kHz (PCM 16-bit) — wav_16000 — estándar", "wav_16000"),
    ("WAV 22.05 kHz (PCM 16-bit) — wav_22050 — estándar (defecto)", "wav_22050"),
    ("WAV 24 kHz (PCM 16-bit) — wav_24000 — estándar", "wav_24000"),
    ("WAV 44.1 kHz (PCM 16-bit) — wav_44100 — Pro+", "wav_44100"),
]

PCM_OPTIONS: List[tuple[str, str]] = [
    ("PCM 16 kHz (WAV/PCM 16-bit) — pcm_16000 — estándar", "pcm_16000"),
    ("PCM 22.05 kHz (WAV/PCM 16-bit) — pcm_22050 — estándar (defecto)", "pcm_22050"),
    ("PCM 24 kHz (WAV/PCM 16-bit) — pcm_24000 — estándar", "pcm_24000"),
    ("PCM 44.1 kHz (WAV/PCM 16-bit) — pcm_44100 — Pro+", "pcm_44100"),
]

def get_default_output_label(fmt: str) -> str:
    if fmt == "MP3":
        return next(lbl for lbl, code in MP3_OPTIONS if code == "mp3_44100_128")
    if fmt == "WAV":
        return next(lbl for lbl, code in WAV_OPTIONS if code == "wav_22050")
    if fmt == "PCM":
        return next(lbl for lbl, code in PCM_OPTIONS if code == "pcm_22050")
    return MP3_OPTIONS[4][0]

# Lista de Voice IDs manuales (aportados por el usuario)
MANUAL_VOICE_IDS: List[str] = [
    "19STyYD15bswVz51nqLf",
    "gU0LNdkMOQCOrPrwtbee",
    "DGzg6RaUqxGRTHSBjfgF",
    "NOpBlnGInO9m6vDvFkFC",
    "cgSgspJ2msm6clMCkdW9",
    "BZgkqPqms7Kj9ulSkVzn",
    "wo6udizrrtpIxWGp2qJk",
    "TX3LPaxmHKxFdv7VOQHJ",
]

# --- Inicialización del cliente de ElevenLabs y obtención de voces disponibles ---

API_KEY: Optional[str] = os.getenv("ELEVENLABS_API_KEY")
if not API_KEY or not API_KEY.strip():
    raise ValueError(
        "ELEVENLABS_API_KEY no está configurada. Define la variable en tu entorno o en el archivo .env"
    )

client: ElevenLabs = ElevenLabs(api_key=API_KEY)

# Obtener lista de voces disponibles de manera segura
try:
    voices_data = client.voices.get_all()  # SDK moderno: listar voces
    # El SDK devuelve un objeto con atributo .voices o una lista directa, contemplamos ambos casos
    raw_voices = getattr(voices_data, "voices", voices_data)
    voice_options: List[Tuple[str, str]] = [
        (v.name, v.voice_id) for v in raw_voices
        if getattr(v, "name", None) and getattr(v, "voice_id", None)
    ]
except Exception as e:  # errores específicos dependen del SDK; se loguea y se continúa sin voces
    print("ERROR: No se pudieron obtener las voces. Verifica tu API Key y conexión.")
    print(f"Detalle: {e}")
    voice_options = []

# Si se definió DEFAULT_VOICE_ID y coincide con alguna voz de la lista, seleccionarla por nombre
default_voice_name: Optional[str] = None
if DEFAULT_VOICE_ID and voice_options:
    for name, vid in voice_options:
        if vid == DEFAULT_VOICE_ID:
            default_voice_name = name
            break

# Preparar lista de modelos soportados con etiquetas de coste
model_options: List[str] = [m["label"] for m in MODEL_CHOICES]
default_model_id: str = DEFAULT_MODEL if any(m["id"] == DEFAULT_MODEL for m in MODEL_CHOICES) else MODEL_CHOICES[0]["id"]
default_model_label: str = get_model_label_by_id(default_model_id)


# --- Definir función para conversión texto->voz usando ElevenLabs ---

def text_to_speech(
    text: str,
    max_chars: int,
    voice_source: str,
    voice_name: Optional[str],
    voice_id_manual: Optional[str],
    voice_id_manual_dropdown: Optional[str],
    model_label: str,
    output_choice: str,
) -> Tuple[Optional[str], str]:
    """
    Convierte el texto dado a habla utilizando la API de ElevenLabs.
    Devuelve la ruta del archivo de audio generado.
    """
    if not text:
        print("[ELS] Entrada vacía: falta texto")
        return None, "Por favor ingresa un texto."

    # Limitar longitud si se especifica para reducir créditos
    try:
        max_len = int(max_chars)
    except Exception:
        max_len = 0
    text_to_use = text[:max_len] if max_len and max_len > 0 else text

    # Buscar el voice_id correspondiente al nombre seleccionado
    voice_id: Optional[str] = None
    # Selección según fuente elegida
    source = (voice_source or "API").strip().lower()
    print(f"[ELS] Fuente de voz seleccionada: {voice_source}")
    if source.startswith("manual (selector)"):
        if voice_id_manual_dropdown and voice_id_manual_dropdown.strip():
            voice_id = voice_id_manual_dropdown.strip()
    elif source.startswith("manual (textbox)"):
        if voice_id_manual and voice_id_manual.strip():
            voice_id = voice_id_manual.strip()
    else:  # API
        if voice_name and voice_options:
            for name, vid in voice_options:
                if name == voice_name:
                    voice_id = vid
                    break
    if not voice_id:
        print("[ELS] No se pudo resolver un Voice ID válido desde la selección actual")
        return None, "No se pudo determinar un Voice ID. Selecciona una voz o pega un Voice ID manual válido."

    # Determinar formato de salida según opción elegida
    # Resolver model_id real a partir de la etiqueta
    model_id = next((m["id"] for m in MODEL_CHOICES if m["label"] == model_label), default_model_id)
    # Resolver output_format según selección
    selected_label = output_choice
    # Buscar en las 3 listas
    def _find_code(lbl: str) -> Optional[str]:
        for (l, c) in MP3_OPTIONS + WAV_OPTIONS + PCM_OPTIONS:
            if l == lbl:
                return c
        return None
    output_format = _find_code(selected_label) or "mp3_44100_128"
    # Extensión en base al código seleccionado
    file_ext: str = "mp3" if output_format.startswith("mp3_") else ("wav" if output_format.startswith("wav_") or output_format.startswith("pcm_") else "bin")
    output_filename: str = f"output.{file_ext}"

    print(
        f"[ELS] Iniciando TTS - model_id={model_id}, voice_id={voice_id}, output_format={output_format}, chars={len(text_to_use)}"
    )
    try:
        # Llamar a la API de ElevenLabs para convertir texto a voz
        audio = client.text_to_speech.convert(
            text=text_to_use,
            voice_id=voice_id,
            model_id=model_id,
            output_format=output_format,
        )
    except ApiError as api_err:  # tipo de error del SDK con headers/status/body
        try:
            # api_err suele tener .status_code, .headers, .body
            status = getattr(api_err, "status_code", None)
            headers = getattr(api_err, "headers", None)
            body = getattr(api_err, "body", None)
            print(f"[ELS][ApiError] status={status}\nheaders={headers}\nbody={body}")
        except Exception:
            pass
        error_msg = f"Error al generar audio: {api_err}"
        print(f"[ELS] {error_msg}")
        return None, error_msg
    except Exception as api_err:
        error_msg = f"Error al generar audio: {api_err}"
        print(f"[ELS] {error_msg}")
        return None, error_msg

    def _write_audio_bytes(audio_obj: object, path: str) -> None:
        """Intenta guardar el audio manejando bytes, streams o iterables de chunks."""
        with open(path, "wb") as f:
            # Caso 1: bytes directos
            if isinstance(audio_obj, (bytes, bytearray)):
                f.write(audio_obj)
                return

            # Caso 2: objeto con .read()
            read_fn = getattr(audio_obj, "read", None)
            if callable(read_fn):
                while True:
                    chunk = read_fn(8192)
                    if not chunk:
                        break
                    f.write(chunk)
                return

            # Caso 3: iterable de chunks (bytes)
            try:
                iterator = iter(audio_obj)  # puede lanzar TypeError si no es iterable
                for chunk in iterator:
                    if not chunk:
                        continue
                    if isinstance(chunk, (bytes, bytearray)):
                        f.write(chunk)
                    else:
                        # Si el chunk tiene .read(), leerlo
                        chunk_read = getattr(chunk, "read", None)
                        if callable(chunk_read):
                            data_chunk = chunk_read()
                            if data_chunk:
                                f.write(data_chunk)
                        # de lo contrario, ignorar tipos no soportados
                return
            except TypeError:
                pass

            # Caso 4: requests-like response con iter_content
            iter_content = getattr(audio_obj, "iter_content", None)
            if callable(iter_content):
                for chunk in iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                return

            # Si llega aquí, intentar SDK save como último recurso
            save(audio_obj, path)

    # Leer primero a memoria para detectar errores JSON y evitar archivos vacíos
    def _read_all_bytes(audio_obj: object) -> bytes:
        if isinstance(audio_obj, (bytes, bytearray)):
            return bytes(audio_obj)
        # Preferir .read() si existe
        read_fn = getattr(audio_obj, "read", None)
        if callable(read_fn):
            return read_fn()
        # Intentar iterar por chunks
        try:
            data_parts = []
            for chunk in audio_obj:  # type: ignore[assignment]
                if not chunk:
                    continue
                if isinstance(chunk, (bytes, bytearray)):
                    data_parts.append(bytes(chunk))
                else:
                    chunk_read = getattr(chunk, "read", None)
                    if callable(chunk_read):
                        sub = chunk_read()
                        if sub:
                            data_parts.append(sub)
            return b"".join(data_parts)
        except TypeError:
            pass
        # Fallback requests-like
        iter_content = getattr(audio_obj, "iter_content", None)
        if callable(iter_content):
            return b"".join(iter_content(chunk_size=8192))
        # Último recurso: delegar en SDK save a un buffer temporal
        from io import BytesIO
        buf = BytesIO()
        try:
            save(audio_obj, buf)  # type: ignore[arg-type]
            return buf.getvalue()
        except Exception:
            return b""

    try:
        data_bytes = _read_all_bytes(audio)
    except Exception as read_err:
        # Captura errores de API durante el streaming/conversión
        return None, f"Error de API al leer el audio: {read_err}"

    if not data_bytes:
        return None, "La API no devolvió audio (respuesta vacía). Verifica el Voice ID, permisos del plan o límite de voces personalizadas."

    # Si parece JSON de error, tratar de decodificar y mostrar el mensaje
    if data_bytes[:1] in (b"{", b"["):
        try:
            import json
            text_json = data_bytes.decode("utf-8", errors="ignore")
            print(f"[ELS] Respuesta JSON detectada en lugar de audio: {text_json[:400]}...")
            err = json.loads(text_json)
            detail = err.get("detail") if isinstance(err, dict) else err
            return None, f"Error de API: {detail}"
        except Exception:
            pass

    # Guardar a disco
    try:
        with open(output_filename, "wb") as f:
            f.write(data_bytes)
        # Verificar tamaño del archivo para evitar MP3 vacío
        try:
            size = os.path.getsize(output_filename)
        except OSError:
            size = 0
        if size == 0:
            print("[ELS] Archivo generado con tamaño 0 bytes: posible error de API o permisos/plan")
            return None, (
                "La API no devolvió audio válido (archivo vacío). "
                "Prueba con otro Voice ID o revisa permisos/plan."
            )
        print(f"[ELS] Audio guardado en archivo: {output_filename} ({size} bytes)")
        return output_filename, f"OK: Audio generado ({size} bytes)"
    except Exception as write_err:
        print(f"Error al escribir el archivo: {write_err}")
        return None, f"Error al escribir el archivo: {write_err}"
    # Para Gradio, devolvemos la ruta del archivo y un mensaje de estado
    # (las rutas de éxito ya retornan antes)
    return None, "Estado desconocido"


# --- Construir la interfaz de usuario con Gradio 4.x ---

description = (
    "Introduce un texto, selecciona la voz y configura los parámetros. "
    "Pulsa 'Generar audio' para sintetizar la voz."
)

def on_format_family_change(family: str):
    if family == "WAV":
        return gr.update(choices=[lbl for lbl, _ in WAV_OPTIONS], value=get_default_output_label("WAV"))
    if family == "PCM":
        return gr.update(choices=[lbl for lbl, _ in PCM_OPTIONS], value=get_default_output_label("PCM"))
    return gr.update(choices=[lbl for lbl, _ in MP3_OPTIONS], value=get_default_output_label("MP3"))

with gr.Blocks(title="Conversor Texto a Voz - ElevenLabs") as interface:
    gr.Markdown(description)

    with gr.Row():
        text = gr.Textbox(lines=5, label="Texto a convertir", value=DEFAULT_TEXT)
        maxc = gr.Number(value=120, precision=0, label="Máx. caracteres (para ahorrar créditos)")

    with gr.Row():
        vs = gr.Radio(
            choices=["API (lista de voces)", "Manual (selector)", "Manual (textbox)"],
            value="API (lista de voces)",
            label="Tipo de selección de voz",
        )
        vn = gr.Dropdown(
            choices=[name for name, _ in voice_options] if voice_options else [],
            label=("Voz (Voice)" if voice_options else "Voz (no disponible: usa Voice ID manual)"),
            value=default_voice_name or (voice_options[0][0] if voice_options else None),
        )

    with gr.Row():
        vid_txt = gr.Textbox(
            label="Voice ID (manual)",
            value=DEFAULT_VOICE_ID or "",
            placeholder="Pega aquí el Voice ID si el listado de voces no está disponible",
        )
        vid_sel = gr.Dropdown(
            choices=MANUAL_VOICE_IDS,
            label="Voice ID manual (selector)",
            value=DEFAULT_VOICE_ID if DEFAULT_VOICE_ID in MANUAL_VOICE_IDS else None,
        )

    with gr.Row():
        model = gr.Dropdown(choices=model_options, label="Modelo de síntesis (con coste)", value=default_model_label)

    with gr.Row():
        family = gr.Radio(choices=["MP3", "WAV", "PCM"], label="Familia de Formato", value="MP3")
        format_choice = gr.Dropdown(
            choices=[lbl for lbl, _ in MP3_OPTIONS],
            value=get_default_output_label("MP3"),
            label="Modelo de audio de salida",
        )

    out_audio = gr.Audio(label="Audio generado", type="filepath")
    out_status = gr.Textbox(label="Estado")

    family.change(
        fn=on_format_family_change,
        inputs=[family],
        outputs=[format_choice],
    )

    btn = gr.Button("Generar audio")
    btn.click(
        fn=text_to_speech,
        inputs=[text, maxc, vs, vn, vid_txt, vid_sel, model, format_choice],
        outputs=[out_audio, out_status],
    )

if __name__ == "__main__":
    interface.launch(share=True)