"""HOOK 2 (Codex) · PreToolUse (Bash)
Bloquea comandos peligrosos antes de que se ejecuten.
Es idéntico al de Claude Code: ambos reciben el comando en tool_input.command.
"""
import json
import re
import sys
from pathlib import Path
from pathlib import Path

sys.stderr.reconfigure(encoding="utf-8")

PELIGROSOS = {
    r"\brm\s+-[a-z]*r[a-z]*f|\brm\s+-[a-z]*f[a-z]*r": "borrado recursivo forzado (rm -rf)",
    r"Remove-Item\b.*-Recurse": "borrado recursivo en PowerShell",
    r"git\s+push\b.*(--force|-f\b)": "git push --force (reescribe la historia del equipo)",
    r"git\s+reset\s+--hard": "git reset --hard (pierde cambios sin confirmar)",
    r"DROP\s+(TABLE|DATABASE)": "eliminar tablas o bases de datos",
    r"\bdel\s+/[sq]": "borrado masivo en Windows",
}

datos = json.loads(sys.stdin.buffer.read().decode("utf-8"))
comando = datos.get("tool_input", {}).get("command", "")

for patron, motivo in PELIGROSOS.items():
    if re.search(patron, comando, re.IGNORECASE):
        print(
            f"⛔ BLOQUEADO por hook: {motivo}.\nComando: {comando}\n"
            "Si de verdad es necesario, pide al usuario que lo ejecute manualmente.",
            file=sys.stderr,
        )
        sys.exit(2)

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "hooks"))
from verificar_push import verificar_push

verificar_push(comando)
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "hooks"))
from verificar_push import verificar_push

verificar_push(comando)
sys.exit(0)
