#!/bin/bash
# Rebrand Open WebUI -> "Sathvik AI" inside the running container.
# Patches: WEBUI_NAME constant, built index.html title, static logo set,
# and installs a light Sathvik-AI theme into /static/custom.css.
# Survives docker restarts (container FS persists); re-run after image updates.
set -e

echo "=== 1. Generate logo set inside container ==="
docker cp "$(dirname "$0")/make_logos.py" open-webui:/tmp/make_logos.py
docker exec open-webui python3 /tmp/make_logos.py

echo "=== 2. Patch WEBUI_NAME (kill the '(Open WebUI)' suffix rule) ==="
docker exec -i open-webui python3 - <<'PYEOF'
p = "/app/backend/open_webui/env.py"
src = open(p).read()
src = src.replace(
    "WEBUI_NAME = os.getenv('WEBUI_NAME', 'Open WebUI')",
    "WEBUI_NAME = os.getenv('WEBUI_NAME', 'Sathvik AI')",
)
src = src.replace("if WEBUI_NAME != 'Open WebUI':\n    WEBUI_NAME += ' (Open WebUI)'", "")
open(p, "w").write(src)
print("env.py patched")
PYEOF

echo "=== 3. Patch built index.html title/meta ==="
docker exec -i open-webui python3 - <<'PYEOF'
import re
p = "/app/build/index.html"
src = open(p).read()
src = re.sub(r"<title>.*?</title>", "<title>Sathvik AI</title>", src, flags=re.S)
src = src.replace("Open WebUI", "Sathvik AI")
open(p, "w").write(src)
print("index.html patched")
PYEOF

echo "=== 4. Install logos into static ==="
docker exec open-webui sh -c 'cp /tmp/sathvik_static/logo.png /tmp/sathvik_static/logo-dark.png /tmp/sathvik_static/favicon.png /tmp/sathvik_static/favicon-96x96.png /tmp/sathvik_static/favicon.svg /tmp/sathvik_static/favicon.ico /tmp/sathvik_static/apple-touch-icon.png /tmp/sathvik_static/web-app-manifest-192x192.png /tmp/sathvik_static/web-app-manifest-512x512.png /tmp/sathvik_static/splash.png /tmp/sathvik_static/splash-dark.png /app/build/static/ && ls -la /app/build/static/favicon.png'

echo "=== 5. Theme (custom.css) ==="
docker exec open-webui sh -c 'cat > /app/build/static/custom.css <<CSSEOF
/* Sathvik AI theme */
:root {
  --brand-color: #6c8cff;
  --brand-color-dark: #9a6cff;
}
[data-theme="dark"] .app-logo,
img.app-logo { border-radius: 10px; }
CSSEOF
echo custom.css installed'

echo "=== 6. Restart container ==="
docker restart open-webui
echo "done - Sathvik AI branding applied"
