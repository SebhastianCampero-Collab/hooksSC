// Hooks de OpenCode: los 4 hooks de la demo en UN plugin de JavaScript.
//
// Diferencia clave con Claude Code y Codex: no hay settings.json/hooks.json.
// El mismo archivo REGISTRA el evento y CONTIENE la lógica.
//   - "tool.execute.before" = PreToolUse  → lanzar un Error BLOQUEA la herramienta
//   - "tool.execute.after"  = PostToolUse → se modifica output.output (lo que ve el modelo)
//
// Formato OpenCode 1.x: export default { id, server: async (ctx) => ({ hooks }) }
// El directorio del proyecto llega en ctx.directory.
import { appendFileSync } from "node:fs"
import { join } from "node:path"
import { execFile } from "node:child_process"

const PELIGROSOS = [
  [/\brm\s+-[a-z]*r[a-z]*f|\brm\s+-[a-z]*f[a-z]*r/i, "borrado recursivo forzado (rm -rf)"],
  [/Remove-Item\b.*-Recurse/i, "borrado recursivo en PowerShell"],
  [/git\s+push\b.*(--force|-f\b)/i, "git push --force (reescribe la historia del equipo)"],
  [/git\s+reset\s+--hard/i, "git reset --hard (pierde cambios sin confirmar)"],
  [/DROP\s+(TABLE|DATABASE)/i, "eliminar tablas o bases de datos"],
  [/\bdel\s+\/[sq]/i, "borrado masivo en Windows"],
]

// ¿La herramienta modifica archivos? (edit, write, patch, multiedit...)
const editaArchivos = (tool) => /edit|write|patch/i.test(String(tool))

// Rutas que toca una herramienta: campo directo o, si es un parche, las líneas "*** Update File: ruta"
const rutasDe = (input = {}) => {
  const rutas = [input.filePath, input.path, input.file_path].filter(Boolean).map(String)
  for (const valor of Object.values(input)) {
    if (typeof valor === "string") {
      for (const m of valor.matchAll(/^\*\*\* (?:Add|Update|Delete) File: (.+)$/gm)) rutas.push(m[1].trim())
    }
  }
  return rutas.map((r) => r.replace(/\\/g, "/"))
}

// Ejecuta las pruebas y devuelve { ok, reporte }
const ejecutarPruebas = (proyecto) =>
  new Promise((resolve) => {
    execFile("python", ["-m", "unittest", "discover", "-s", "tests"], { cwd: proyecto, timeout: 50_000 }, (error, _stdout, stderr) =>
      resolve({ ok: !error, reporte: String(stderr).trim() }), // unittest escribe su reporte en stderr
    )
  })

export default {
  id: "upb.guardian",
  async server({ directory }) {
    const auditar = (accion, detalle) => {
      const fecha = new Date().toLocaleString("sv-SE") // formato local AAAA-MM-DD HH:MM:SS
      const texto = String(detalle ?? "").replace(/\n/g, " ").slice(0, 120)
      appendFileSync(join(directory, ".opencode", "auditoria.log"), `${fecha} | ${String(accion).padEnd(18)} | ${texto}\n`)
    }

    auditar("PLUGIN cargado", "guardian.js está activo") // prueba de que OpenCode cargó el plugin

    return {
      // ── HOOK 1 y 2 · ANTES de usar una herramienta ───────────────────────
      "tool.execute.before": async (input, output) => {
        const args = output.args ?? {}

        // HOOK 1: archivos protegidos
        if (editaArchivos(input.tool)) {
          for (const ruta of rutasDe(args)) {
            const nombre = ruta.split("/").pop()
            if (ruta.includes("tests/")) {
              throw new Error(
                `⛔ BLOQUEADO por hook: '${nombre}' es una prueba y las pruebas están protegidas. ` +
                  "Si una falla, corrige el código, no la prueba.",
              )
            }
            if (nombre.startsWith(".env")) {
              throw new Error(`⛔ BLOQUEADO por hook: '${nombre}' contiene secretos y no se puede modificar.`)
            }
          }
        }

        // HOOK 2: comandos peligrosos (cualquier herramienta que reciba un "command")
        if (typeof args.command === "string") {
          for (const [patron, motivo] of PELIGROSOS) {
            if (patron.test(args.command)) {
              throw new Error(`⛔ BLOQUEADO por hook: ${motivo}. Comando: ${args.command}`)
            }
          }
        }
      },

      // ── HOOK 3 y 4 · DESPUÉS de usar una herramienta ─────────────────────
      "tool.execute.after": async (input, output) => {
        const args = input.args ?? {}

        // HOOK 4: auditoría (los subagentes se lanzan con la herramienta "task")
        if (input.tool === "task") {
          auditar("SUBAGENTE terminó", args.subagent_type ?? args.agent ?? args.description ?? "")
        } else {
          auditar(input.tool ?? "?", rutasDe(args)[0] ?? args.command ?? args.pattern ?? "")
        }

        // HOOK 3: pruebas automáticas después de editar código Python
        if (!editaArchivos(input.tool)) return
        if (!rutasDe(args).some((r) => r.endsWith(".py"))) return

        const { ok, reporte } = await ejecutarPruebas(join(directory, "proyecto-demo"))
        const aviso = ok
          ? `✅ Hook de pruebas: ${reporte.split("\n").find((l) => l.startsWith("Ran ")) ?? ""} → OK`
          : `❌ El hook ejecutó las pruebas y FALLARON. Corrige el código (no las pruebas):\n${reporte.slice(-3000)}`
        auditar("PRUEBAS", ok ? "OK" : "FALLARON")

        // Se agrega el aviso a la salida que ve el modelo para que se corrija solo
        output.output = `${output.output ?? ""}\n\n${aviso}`
      },
    }
  },
}
