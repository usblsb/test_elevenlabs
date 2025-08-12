## Guía de conector TTS ElevenLabs (Python + LangChain)

- Objetivo: convertir texto a voz y guardar el audio localmente usando ElevenLabs desde Python, integrable en LangChain.
- Requisitos: Python 3.10+, `elevenlabs`, `python-dotenv` (opcional), y LangChain si deseas integrarlo como Runnable/Tool.

### 1) Autenticación y entorno
- Variable de entorno requerida: `ELEVENLABS_API_KEY`
- Carga recomendada: `python-dotenv` o export en shell.
- Cliente SDK:
```python
from elevenlabs import ElevenLabs
client = ElevenLabs(api_key=os.environ["ELEVENLABS_API_KEY"])
```

### 2) Modelos disponibles y coste
- Nombre comercial — model_id — coste (créditos/caracter)
- Eleven v3 — `eleven_v3` — 1
- Eleven Multilingual v2 — `eleven_multilingual_v2` — 1
- Eleven Flash v2.5 — `eleven_flash_v2_5` — 0.5
- Eleven Flash v2 — `eleven_flash_v2` — 0.5
- Eleven Turbo v2.5 — `eleven_turbo_v2_5` — 0.5
- Eleven Turbo v2 — `eleven_turbo_v2` — 0.5
- English v1 — `eleven_monolingual_v1` — 1
- Multilingual v1 — `eleven_multilingual_v1` — 1

### 3) Formatos de salida soportados (output_format)
- MP3
  - MP3 22.05 kHz 32 kbps — `mp3_22050_32`
  - MP3 44.1 kHz 32 kbps — `mp3_44100_32`
  - MP3 44.1 kHz 64 kbps — `mp3_44100_64`
  - MP3 44.1 kHz 96 kbps — `mp3_44100_96`
  - MP3 44.1 kHz 128 kbps — `mp3_44100_128` (defecto)
  - MP3 44.1 kHz 192 kbps — `mp3_44100_192` (Creator+)

- WAV (PCM 16-bit)
  - WAV 16 kHz — `wav_16000`
  - WAV 22.05 kHz — `wav_22050` (defecto)
  - WAV 24 kHz — `wav_24000`
  - WAV 44.1 kHz — `wav_44100` (Pro+)

- PCM (raw PCM 16-bit)
  - PCM 16 kHz — `pcm_16000`
  - PCM 22.05 kHz — `pcm_22050` (defecto)
  - PCM 24 kHz — `pcm_24000`
  - PCM 44.1 kHz — `pcm_44100` (Pro+)

- Nota: Extensiones recomendadas
  - `mp3_*` → `.mp3`
  - `wav_*` → `.wav`
  - `pcm_*` → `.wav` si encapsulas; si guardas PCM crudo, `.pcm`

### 4) Voice IDs validados
- IDs confirmados como válidos en la cuenta actual:
```
19STyYD15bswVz51nqLf
gU0LNdkMOQCOrPrwtbee
DGzg6RaUqxGRTHSBjfgF
NOpBlnGInO9m6vDvFkFC
cgSgspJ2msm6clMCkdW9
BZgkqPqms7Kj9ulSkVzn
wo6udizrrtpIxWGp2qJk
TX3LPaxmHKxFdv7VOQHJ
```

### 5) Endpoint/URL
- Base pública: `https://api.elevenlabs.io/v1`
- El SDK moderno usa internamente endpoints como `/text-to-speech/{voice_id}/convert` o `/text-to-speech/{voice_id}/stream`.
- Recomendación: usar el SDK (`client.text_to_speech.convert`) en lugar del HTTP directo.

### 6) Esquema de configuración (Pydantic)
```python
from pydantic import BaseModel, Field, constr

class ElsTTSConfig(BaseModel):
    model_id: constr(strip_whitespace=True)
    voice_id: constr(strip_whitespace=True)
    output_format: constr(strip_whitespace=True)  # p.ej. 'mp3_44100_128' | 'wav_22050' | 'pcm_22050'
    max_chars: int = Field(ge=0)  # 0 = sin límite
    output_path: constr(strip_whitespace=True)  # ruta del archivo destino
```

### 7) Función TTS pura (robusta en lectura/guardado)
```python
from typing import Tuple, Optional
from elevenlabs import ElevenLabs, save
from elevenlabs.core.api_error import ApiError

def els_text_to_speech(client: ElevenLabs, text: str, cfg: ElsTTSConfig) -> Tuple[Optional[str], str]:
    if not text:
        return None, "Texto vacío"

    text_to_use = text if cfg.max_chars == 0 else text[:cfg.max_chars]
    try:
        audio = client.text_to_speech.convert(
            text=text_to_use,
            voice_id=cfg.voice_id,
            model_id=cfg.model_id,
            output_format=cfg.output_format,
        )
    except ApiError as e:
        return None, f"ApiError TTS status={getattr(e,'status_code',None)} body={getattr(e,'body',None)}"
    except Exception as e:
        return None, f"Error TTS: {e}"

    def read_all_bytes(a: object) -> bytes:
        if isinstance(a, (bytes, bytearray)):
            return bytes(a)
        read = getattr(a, "read", None)
        if callable(read):
            return read()
        try:
            chunks = []
            for ch in a:  # iterable de chunks
                if isinstance(ch, (bytes, bytearray)):
                    chunks.append(bytes(ch))
                else:
                    r = getattr(ch, "read", None)
                    if callable(r):
                        b = r()
                        if b:
                            chunks.append(b)
            return b"".join(chunks)
        except TypeError:
            pass
        iter_content = getattr(a, "iter_content", None)
        if callable(iter_content):
            return b"".join(iter_content(chunk_size=8192))
        from io import BytesIO
        buf = BytesIO()
        save(a, buf)
        return buf.getvalue()

    data = read_all_bytes(audio)
    if not data:
        return None, "Respuesta vacía de la API (sin audio)"

    try:
        with open(cfg.output_path, "wb") as f:
            f.write(data)
    except Exception as e:
        return None, f"Error escribiendo archivo: {e}"

    return cfg.output_path, "OK"
```

### 8) Integración mínima con LangChain
- Runnable (LCEL):
```python
from langchain_core.runnables import RunnableLambda

def make_tts_runnable(client: ElevenLabs, cfg: ElsTTSConfig) -> RunnableLambda:
    def _fn(txt: str) -> str:
        path, status = els_text_to_speech(client, txt, cfg)
        if path is None:
            raise ValueError(f"TTS falló: {status}")
        return path
    return RunnableLambda(_fn)
```
- Tool (para agentes):
```python
from langchain_core.tools import tool

@tool("elevenlabs_tts", return_direct=True)
def elevenlabs_tts_tool(text: str) -> str:
    path, status = els_text_to_speech(client, cfg)
    if path is None:
        raise ValueError(status)
    return path
```

### 9) Manejo de errores frecuentes
- `missing_permissions` (401): la API key carece de `voices_read` o permisos TTS.
- `voice_limit_reached` (400): límite de voces personalizadas.
- `quota_exceeded` (401): créditos insuficientes.
- Respuesta JSON en lugar de audio: parsear `detail` y registrar `x-trace-id` si está presente.

### 10) Recomendaciones operativas
- Por coste/rendimiento: `model_id = eleven_flash_v2_5` + `output_format = mp3_44100_128`.
- Usar Voice ID premade si hay límites de voces personalizadas; mantener lista blanca de Voice IDs válidos.
- Añadir `max_chars` como control de gasto.

### 11) Ejemplo listo para usar
```python
import os
from dotenv import load_dotenv
from elevenlabs import ElevenLabs

load_dotenv()
client = ElevenLabs(api_key=os.environ["ELEVENLABS_API_KEY"])

cfg = ElsTTSConfig(
    model_id="eleven_flash_v2_5",
    voice_id="cgSgspJ2msm6clMCkdW9",  # o cualquier ID validado
    output_format="mp3_44100_128",
    max_chars=0,
    output_path="output.mp3",
)

path, status = els_text_to_speech(client, "Hola mundo desde ElevenLabs", cfg)
print(path, status)
```
