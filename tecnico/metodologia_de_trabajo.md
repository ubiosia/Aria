# Metodología de trabajo

Hábitos de trabajo estandarizados a lo largo del proyecto, como referencia reutilizable — sin tener que leer la narrativa completa de `/historia/` para saber cómo se trabajaba en la práctica.

## Las tres capas de backup

Ninguna capa sola alcanza. Cada una cubre algo que las otras dos no cubren:

1. **Control de versiones (git)** — guarda la historia de cómo se llegó a cada estado del código, con la posibilidad de volver atrás con precisión quirúrgica. No cubre el disco virtual completo, ni el vectorstore (que vive fuera del repositorio por diseño), ni el estado del sistema operativo.
2. **Script dedicado de respaldo completo** (`backup_completo.sh`, con una versión liviana, `backup_liviano.sh`, para copias más rápidas) — copia el sistema completo, incluido lo que git no versiona. No reemplaza a git: una copia completa no tiene historial de cambios, solo una fotografía de un momento dado.
3. **Tarea automática nocturna (cron)** — corre sin intervención humana, todas las noches, como última red de seguridad. Existe desde etapas tempranas del proyecto, pero durante un tiempo cubría solo la carpeta de código, no el disco virtual completo de WSL2 — un límite real que se descubrió de la forma más costosa posible (ver más abajo).

Se sumó, más adelante, una cuarta pieza —`backup_git.sh`, un `git bundle`— pensada específicamente para poder reconstruir el repositorio completo en una máquina nueva sin depender de un servicio externo de hosting de código.

## Por qué ninguna alcanza sola: el incidente que lo probó

El disco virtual de WSL2 (`ext4.vhdx`) desapareció por completo tras una limpieza de disco corrida sin darse cuenta de que ese archivo era, para la herramienta de limpieza, "innecesario". El cron nocturno de esa etapa cubría la carpeta de código, no el disco virtual entero — no hubiera servido para este caso puntual. Lo que salvó el trabajo fue un backup manual, hecho por costumbre más que por previsión, apenas dos días antes.

De ahí salió la regla de las tres capas activas al mismo tiempo, no una sola: si una capa no cubre algo, que lo cubra otra. Ver [`/historia/03_aprender_a_trabajar_en_serio.md`](../historia/03_aprender_a_trabajar_en_serio.md) para el relato completo.

## La regla del cierre de sesión

Un backup automático corriendo bien puede dar una falsa sensación de que todo está cubierto. En una etapa del proyecto, cuatro sesiones de trabajo completas pasaron sin que se confirmara un solo cambio en git — el repositorio existía, se sabía usar, pero verificar y confirmar los cambios se había ido quedando afuera de la rutina diaria mientras los backups automáticos, esos sí corriendo cada noche, disimulaban el hueco.

La regla que quedó, sin excepciones desde entonces: **verificar el estado del repositorio (`git status`) al cerrar cada sesión de trabajo, siempre, además del backup — nunca en lugar del backup.** Un backup guarda una fotografía completa; git guarda el camino recorrido. Hacen falta los dos.

## Probar en aislamiento antes de tocar producción

Regla explícita del proyecto, con este orden fijo:

1. Escribir un script de prueba aislado (`test_xxx.py`, en una carpeta separada del código real) que simule el cambio.
2. Probar ese script aislado con evidencia real, no con la impresión de que "debería funcionar".
3. Solo si el script aislado funciona bien, aplicar el cambio al archivo de producción.

Un caso real de aplicación de esta regla: antes de escribir el enrutador central del sistema, se armó primero un archivo de pruebas con veinte casos conocidos, en una carpeta separada, y se validó contra ese archivo antes de tocar nada real — con el resultado completo (20/20) confirmado antes de migrar. La misma disciplina se aplicó, más adelante, a cualquier técnica que necesitara cargar un volumen grande de datos en memoria: medir el impacto real en aislado primero, porque un proceso así puede morir sin ningún aviso si se corre directo contra el sistema real.

Una excepción documentada y explícita: los propios scripts de backup, por vivir fuera de la carpeta versionada del proyecto, se editan con una copia de respaldo previa del archivo y verificación de sintaxis, pero sin pasar por el flujo completo de prueba aislada — no aplica de la misma forma cuando el archivo que se edita no forma parte del repositorio.

## Medir en vez de suponer: el golden set

Un conjunto fijo de preguntas de referencia, con la respuesta o ruta esperada para cada una, usado para confirmar con evidencia objetiva si un cambio mejora o empeora el sistema real — no con la impresión subjetiva de que "ahora responde mejor". Creció de 20 preguntas iniciales a 78 hacia el cierre del material disponible (Sesión 122), y se convirtió en el paso obligatorio antes de dar por cerrada cualquier mejora significativa de contenido o de enrutamiento. Ver [`/meta/glosario.md`](../meta/glosario.md).

## El flujo completo de un cambio real

Para cualquier cambio de código en producción, el patrón documentado y repetido es: backup del archivo antes de tocarlo, prueba en aislamiento, revisión del diff exacto antes de aplicar, aprobación explícita del cambio, aplicación en producción, y verificación posterior de que el sistema sigue funcionando. Ningún paso se salta para ahorrar tiempo, incluso en cambios que parecen triviales — varios de los bugs documentados en [`/tecnico/bugs_famosos.md`](bugs_famosos.md) empezaron, precisamente, como cambios que parecían triviales.

---

*Nota editorial: los hábitos de este documento están tomados con cita textual de instructivos de trabajo internos del proyecto y de manuales de sesión donde se aplicaron en la práctica, incluyendo el caso real de las veinte pruebas iniciales del enrutador y el incidente que originó la regla de las tres capas de backup.*
