# Glosario

Términos propios del proyecto, con una referencia de dónde surgieron cuando corresponde. Para conceptos técnicos generales (RAG, embeddings, WSL2), se da una definición breve orientada a este proyecto específico, no una definición exhaustiva del concepto en general.

**Route shadowing** — patrón de bug donde una regla de enrutamiento genérica intercepta una pregunta antes de que una regla más específica, y correcta, tenga oportunidad de responder. Nombrado así tras el bug del precio del oro (Sesión 34, 23-24/06/2026), consultando a cinco colegas de inteligencia artificial. Ver [`/tecnico/bugs_famosos.md`](bugs_famosos.md).

**Director Cognitivo** — el caché semántico de ARIA: guarda respuestas ya elaboradas para preguntas equivalentes, evitando pagar dos veces el costo de una consulta a un modelo externo cuando la pregunta ya se resolvió bien antes. Nace en paralelo a la migración de memoria personal a base de datos (Sesiones 60-61, julio de 2026).

**Handler** — patrón de diseño usado en `aria_core.py`: cada capacidad puntual del sistema (un precio, un cálculo, un dato de memoria personal) es una clase con un método `intentar()` que devuelve una respuesta o `None`. Introducido en la Sesión 54. Ver [`/tecnico/arquitectura.md`](../tecnico/arquitectura.md).

**Golden set** — conjunto fijo de preguntas de referencia, con la respuesta o ruta esperada para cada una, usado para medir con evidencia objetiva si un cambio mejora o empeora el sistema, en vez de confiar en la impresión subjetiva de que "ahora responde mejor". Creció de 54 a 78 preguntas hacia el cierre de la Sesión 122.

**Módulo 9 (Autonomía Acotada)** — el conjunto de capacidades de autonomía de ARIA, organizado en fases numeradas (0 a 4), cada una construida y verificada en producción antes de habilitar la siguiente. Ver [`/tecnico/decisiones.md`](../tecnico/decisiones.md).

**Modo Jefe** — nombre interno de un proyecto de agentes autónomos más ambicioso, tipo Plan-and-Execute, evaluado y descartado sin llegar a construirse. Ver la lista de "descartado explícitamente" en [`/meta/estado_actual.md`](estado_actual.md).

**SERVIDOR / PRUEBAS** — nomenclatura fija, desde la Sesión 101 (agosto de 2026), para las dos máquinas físicas del proyecto: la máquina principal original ("SERVIDOR") y una segunda máquina incorporada más tarde ("PRUEBAS").

**SabriBot** — proyecto de trading automatizado de Alejandro, separado de ARIA desde su origen (documentado en pie ya para la Sesión 33, junio de 2026), en carpetas y entornos propios. No es un módulo de ARIA ni corre bajo su supervisión.

**Curso Sabri** — el flujo de trabajo por el cual el contenido de los cursos de trading de Sabri Conessa se convierte en material indexable para ARIA: capturas de pantalla más transcripción de audio, combinadas en un documento de "clase" estructurado. Ver [`/historia/06_como_aria_aprendio_a_operar.md`](../historia/06_como_aria_aprendio_a_operar.md).

**RAG (Retrieval-Augmented Generation)** — el mecanismo por el cual ARIA responde preguntas sobre documentos indexados: busca los fragmentos de texto más relevantes en la biblioteca (por significado, no por palabra clave exacta) y se los pasa al modelo de lenguaje como contexto antes de generar la respuesta.

**Chunk** — un fragmento de texto en el que se divide un documento al indexarlo, la unidad mínima que ARIA puede recuperar y citar como fuente.

**WSL2 (Windows Subsystem for Linux 2)** — la capa que permite correr Ubuntu dentro de Windows sin reiniciar la máquina. Ver [`/tecnico/decisiones.md`](../tecnico/decisiones.md) para el porqué de esta elección sobre una instalación nativa.

**V6 / V7 / V8** — nombres de versión internos del proyecto a lo largo del tiempo. El salto de V6 a V7 ocurre hacia el cierre de la Sesión 33 (junio de 2026); de V7 a V8, en la Sesión 57 (julio de 2026, coincidiendo con la migración de memoria a base de datos real).

---

*Nota editorial: cada término de este glosario está tomado con cita textual de los manuales de sesión correspondientes. Las referencias de sesión indican dónde se originó o se documentó el término con más claridad, no necesariamente su primera mención absoluta en el material fuente.*
