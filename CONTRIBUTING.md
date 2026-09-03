# Cómo contribuir a este repositorio

Este no es un proyecto de código abierto en el sentido tradicional: el código fuente completo de ARIA no está publicado (ver `/README.md`, sección "Qué vas a encontrar y qué no"). Lo que hay acá es documentación curada — historia, arquitectura, decisiones —, una carpeta `/codigo/` con varios archivos reales sanitizados más un core mínimo ejecutable de verdad (`aria_core_minimo.py`, ver "Cómo probar el core mínimo" más abajo), y una carpeta `/tests/` con tests de enrutamiento que corren en segundos. Eso no significa que esté cerrado a aportes: significa que, además de la documentación, la revisión y la conversación, ahora también hay código que se puede clonar, correr, y contra el que se pueden correr tests — no un pull request que se mergea directo a un sistema en producción que corre en la máquina de otra persona.

No hace falta pedir permiso para nada de esto. Si algo de lo que sigue te interesa, la forma más simple de empezar es abrir un issue o escribir directamente a **ubiosia@gmail.com** (ver "Legado" en el README).

## Escribir

Tres capítulos de `/historia/` siguen sin escribir — están definidos en su enfoque en [`/historia/00_indice.md`](historia/00_indice.md), pero no redactados:

- **Capítulo 8 — Crecer en módulos**: decisiones de diseño detrás del crecimiento por módulos del sistema, incluyendo por qué se descartó el "Modo Jefe".
- **Capítulo 9 — Los primeros pasos de autonomía**: el Módulo 9 y sus fases, incluida la búsqueda web.
- **Capítulo 10 — Lo que es ARIA hoy**: una fotografía del sistema al cierre del material disponible. Ojo con este: [`/meta/estado_actual.md`](meta/estado_actual.md) ya cumple esa función y se mantiene mejor actualizado de lo que un capítulo escrito una sola vez podría estarlo — si te tienta escribirlo, vale la pena leer esa nota en el índice antes de arrancar.

Si te da curiosidad reconstruir alguno de estos con las fuentes primarias (manuales de sesión, no publicados acá pero cuya existencia y alcance están descriptos en `/meta/`), escribí primero para coordinar — es más fácil evitar el trabajo duplicado con una conversación de cinco minutos que con un PR ya armado.

Más allá de los capítulos que faltan, también ayuda:

- **Señalar errores o inconsistencias** en la documentación existente — desde una fecha mal citada hasta una explicación técnica que no envejeció bien. Este proyecto tiene una disciplina fuerte de citar fuentes con precisión (ver `/tecnico/decisiones.md` y cualquier nota editorial al pie de un capítulo); si encontrás algo que no cierra, avisar es un aporte real.
- **Agregar un ADR nuevo** a [`/tecnico/decisiones.md`](tecnico/decisiones.md) si en algún momento se toma y documenta una decisión de diseño nueva que valga la pena registrar con ese formato (Contexto / Decisión / Alternativas consideradas / Consecuencias).
- **Ampliar `/codigo/`** con más archivos reales sanitizados, si en algún momento se libera más código siguiendo la misma disciplina de privacidad que ya se aplicó a los archivos actuales (ver [`/codigo/README.md`](codigo/README.md) para ver cómo se hizo esa sanitización, como referencia de proceso).

## Cómo probar el core mínimo

Esto sí es un entorno de pruebas real, aunque acotado — a diferencia del resto de "Probar" más abajo, esto se corre, no solo se lee:

1. Cloná el repo.
2. `python3 codigo/ingesta_minima.py` (una sola vez — crea contexto de ejemplo en ChromaDB).
3. `./arrancar_aria.sh "que es un modelo de lenguaje"` (Windows: `arrancar_aria.bat`).
4. Para ver el enrutamiento sin depender de Ollama: `./arrancar_aria.sh "que es un order block"` — rutea a `trading` y muestra el fallback de ChromaDB, porque `ingesta_minima.py` solo carga contexto de ejemplo para el dominio `ia`.
5. Para correr los tests de enrutamiento: `pytest tests/test_enrutador.py` (sin Ollama, sin ChromaDB, sin red — corre en segundos).

Ver [`/codigo/README.md`](codigo/README.md) para el detalle de qué está verificado funcionalmente y qué no (por ejemplo, `arrancar_aria.bat` no se pudo probar en Windows real).

## Probar

Más allá de correr el core mínimo (ver arriba), "probar" también significa poner el resto del material a prueba:

- Si estás armando un asistente parecido, seguir [`/tecnico/instalacion.md`](tecnico/instalacion.md) en tu propia máquina con WSL2 y reportar dónde el instructivo se queda corto o desactualizado es un aporte directo — ese documento se escribió reconstruyendo el proceso real, no probándolo paso a paso en una máquina limpia ajena.
- Revisar los archivos de [`/codigo/`](codigo/) en busca de errores, casos borde no cubiertos, o mejoras — los reales son código real, no pseudocódigo, así que se pueden leer con ojo crítico como se leería cualquier módulo de producción.
- Agregar un caso a [`/tests/test_enrutador.py`](tests/test_enrutador.py) si encontrás una pregunta real que el enrutador clasifica mal — misma disciplina que el resto de ese archivo: el test tiene que citar qué caso protege, no ser genérico.
- Si reconocés en tu propio proyecto el patrón de **route shadowing** descripto en [`/tecnico/bugs_famosos.md`](tecnico/bugs_famosos.md), o el patrón de "regla de negocio en un solo lugar hardcodeado" del [Capítulo 7](historia/07_los_bugs_que_ensenaron_mas.md), contar tu propia versión del bug (dónde apareció, cómo lo encontraste) enriquece el material para cualquiera que lo lea después.

## Programar

Como el código fuente completo no está publicado, no hay un flujo de pull requests contra un repositorio de producción. Lo que sí tiene sentido:

- **Proponer mejoras concretas** a los archivos de `/codigo/` — un fix, una simplificación, un caso no contemplado — vía issue o email, con el fragmento de código propuesto. Se evalúa y, si aplica, se aplica manualmente (ver el límite de seguridad del proyecto: ningún cambio en la máquina real se ejecuta sin revisión humana directa).
- **Aplicar los mismos patrones a tu propio proyecto** y compartir el resultado: la configuración centralizada de `config_dominios.py`, el auditor de solo lectura de `auditar_decision.py`, o el enfoque de backend intercambiable de `memoria.py` (SQLite con flag de emergencia a JSON) son ideas reutilizables más allá de este sistema puntual.
- **Abrir una discusión técnica** sobre cualquier decisión documentada en `/tecnico/decisiones.md` — si hay una alternativa que no se consideró, o una que se descartó por una razón que ya no aplica, es información útil incluso si no se traduce en un cambio inmediato.

---

*Este documento es nuevo (Fase 2 del repositorio, completando brechas técnicas identificadas por revisión externa). No reemplaza nada de lo dicho en la sección "Legado — cómo continuar este proyecto" del [`README.md`](README.md); la complementa con más detalle sobre las tres formas concretas de aportar.*
