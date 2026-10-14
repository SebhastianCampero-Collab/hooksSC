# Demo: pruebas antes del push

La demo queda intencionalmente con 10 pruebas aprobadas y 2 fallidas.
Los tests originales y la copia correcta de `.reset` no se modifican.

1. Incluye el workflow, los hooks y el codigo con errores en un commit.
2. Ejecuta `git push` manualmente desde tu terminal. Estos hooks pertenecen
   a los agentes, no son hooks de Git: el push manual sigue permitido.
3. Comprueba que GitHub Actions marque los dos fallos.
4. Abre Claude Code o Codex CLI desde la raiz del repositorio. Recarga la
   sesion para cargar los cambios. En Codex, revisa y confia en los hooks
   actualizados mediante `/hooks`.
5. Pide al agente:

   > Intenta hacer git push. Si el hook bloquea el comando por pruebas fallidas,
   > corrige el codigo sin modificar los tests ni desactivar los hooks. Ejecuta
   > las 12 pruebas, crea un commit con las correcciones y vuelve a hacer push.

El hook ejecuta unittest antes del comando. Si falla, sale con codigo 2 y
entrega el reporte al agente. El agente debe corregir y crear un nuevo commit:
un push solo envia commits, no cambios sin confirmar. Con las pruebas en verde,
el hook permite continuar. No ejecuta Git ni modifica archivos por su cuenta.

La comprobacion cubre comandos directos como `git push`, `git.exe push` y
`git -C ruta push`. Es una demostracion: no interpreta todos los aliases,
scripts o formas de invocar Git, y verifica el arbol de trabajo de esta demo,
no el contenido de cada commit pendiente. Usa comandos separados para editar,
probar, confirmar y subir.

`reiniciar-demo.ps1` restaura el codigo correcto; no lo ejecutes antes de
mostrar el fallo intencional en Actions.
