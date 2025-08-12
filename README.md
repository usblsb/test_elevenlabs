## Conversor Texto a Voz (ElevenLabs + Gradio)

<!-- Badges (ajusta {{GITHUB_USER}} y {{REPO_NAME}} cuando publiques) -->
![Build](https://img.shields.io/github/actions/workflow/status/usblsb/test_elevenlabs/ci.yml?style=for-the-badge)
![License](https://img.shields.io/badge/license-MIT-blue?style=for-the-badge)

<!-- Tecnologías principales (skillicons) -->
[![Stack](https://skillicons.dev/icons?i=python,git,github,linux&perline=9)](https://skillicons.dev)

Proyecto de demo para convertir texto a voz usando el SDK oficial de ElevenLabs y Gradio 4.x.

- Dependencias: `requirements.min.txt` (mínimo) y `requirements.lock.txt` (reproducible). `requirements.full.txt` conserva el set completo antiguo.

### ✨ Características
- UI con **Gradio 4.x** (opción `share=True` para enlace público si `localhost` no está accesible)
- TTS con **ElevenLabs** (modelos seleccionables, control de formato de salida)
- Configuración por **.env** (`ELEVENLABS_API_KEY`)
- Dependencias mínimas y lock reproducible

### Requisitos
- Python 3.13 (probado). Debería funcionar con 3.10+.
- Cuenta y API Key de ElevenLabs.

> Nota Python 3.13: si ves error `ModuleNotFoundError: No module named 'audioop'`, se resuelve con la dependencia `audioop-lts` incluida (usa `requirements.min.txt`).

### Entorno
Usa el entorno virtual `.venv` ya creado.

- Activar (macOS/Linux):
```bash
source .venv/bin/activate
```
- Desactivar:
```bash
deactivate
```

### Variables de entorno
Crear un archivo `.env` en la raíz del proyecto con:
```env
ELEVENLABS_API_KEY=tu_api_key_aqui
```

### Instalación de dependencias
Con el entorno activado (mínimo recomendado):
```bash
pip install -r requirements.min.txt
```
Para instalación exacta y reproducible (con hashes):
```bash
pip install -r requirements.lock.txt
```
Si necesitas todas las dependencias del entorno previo:
```bash
pip install -r requirements.full.txt
```

### Ejecutar la app
```bash
python elevenlabs_test.py
```
Se abrirá una interfaz de Gradio en tu navegador (o te mostrará una URL local). Ingresa el texto, elige voz y formato, y pulsa "Generar audio".

### 🛡️ Seguridad
- No subas `.env` ni claves a Git.
- Revisa dependencias antes de publicar (ej. `pip-audit`).

### 🤝 Contribución
- PRs bienvenidas. Sigue Commits Convencionales en español.
- Abre Issues para mejoras/bugs.

### 👤 Autor
**Juan Luis Martel (@USBLSB / EA8BK)**  
🌐 https://usblsb.com  
🐙 https://github.com/USBLSB  


### 📝 Licencia
Este proyecto se distribuye bajo la licencia **MIT** (ajústala según tus necesidades).

### Notas
- La lista de voces vía API depende de tu plan/permisos.
- El uso de modelos puede consumir créditos; revisa las etiquetas de coste en la UI.
- Si ves errores de API, verifica la variable `ELEVENLABS_API_KEY`, conectividad y límites del plan.
