## Plan del proyecto

1. Estado actual
   - Entorno virtual `.venv` creado.
   - Script principal: `elevenlabs_test.py` con interfaz Gradio y uso del SDK ElevenLabs.

2. Estado final
   - Dependencias instaladas desde `requirements.min.txt` (o `requirements.lock.txt`).
   - `.env` configurado con `ELEVENLABS_API_KEY`.
   - App ejecutándose correctamente y generando audio.

3. Archivos y cambios
   - Añadido `requirements.min.txt` (mínimo), `requirements.lock.txt` (reproducible) y `requirements.full.txt` (completo previo).
   - Actualizado `README.md` con instrucciones de instalación.
   - `PLAN.md` (este archivo) con estado y tareas.

4. Lista de tareas
   - [ ] Activar entorno: `source .venv/bin/activate`
   - [ ] Instalar deps (mínimo): `pip install -r requirements.min.txt`
   - [ ] (Opcional) Instalar deps reproducibles: `pip install -r requirements.lock.txt`
   - [ ] (Opcional) Instalar deps completas antiguas: `pip install -r requirements.full.txt`
   - [ ] Crear `.env` con `ELEVENLABS_API_KEY`
   - [ ] Ejecutar: `python elevenlabs_test.py`
   - [ ] Validar que se genera `output.mp3`/`output.wav`

Extras/ideas (opcional)
   - [ ] Añadir `.env.example`
   - [ ] Dockerfile para distribución
   - [ ] Tests básicos del flujo TTS
