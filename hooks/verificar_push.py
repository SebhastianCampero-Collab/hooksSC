"""Validacion previa al push para los hooks de los agentes; no ejecuta Git."""
from pathlib import Path
import re
import subprocess
import sys


def verificar_push(comando):
    # Incluye git push, git.exe push y opciones globales como git -C ruta push.
    if not re.search(r"\bgit(?:\.exe)?\b[^\r\n;&|]*\bpush\b", comando, re.IGNORECASE):
        return

    proyecto = Path(__file__).resolve().parents[1] / "proyecto-demo"
    try:
        resultado = subprocess.run(
            [sys.executable, "-B", "-m", "unittest", "discover", "-s", "tests", "-v"],
            cwd=proyecto,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=50,
        )
    except (OSError, subprocess.TimeoutExpired) as error:
        print(f"PUSH BLOQUEADO: no se pudieron verificar las pruebas: {error}", file=sys.stderr)
        sys.exit(2)

    salida = resultado.stdout + resultado.stderr
    if resultado.returncode != 0 or not re.search(r"Ran [1-9]\d* tests?\b", salida):
        print(
            "PUSH BLOQUEADO: las pruebas fallaron o no se encontraron pruebas.\n"
            "Corrige el codigo sin modificar los tests. Vuelve a ejecutar las pruebas, "
            "incluye las correcciones en un nuevo commit y reintenta el push.\n\n"
            + salida[-6000:],
            file=sys.stderr,
        )
        sys.exit(2)

    print("Hook previo al push: pruebas aprobadas; se permite continuar.\n" + salida, file=sys.stderr)
