# Estado actual de ARIA

> **Sello de frescura**: este documento refleja el estado del proyecto al cierre de la Sesión 122 (23-24 de agosto de 2026). No hay garantía de que siga siendo exacto más allá de esa fecha — ARIA es un proyecto activo, no archivado. Último commit conocido de esa sesión: `27ca543` (documentación de una limpieza del vectorstore en `ENTORNO.md`). Un commit anterior de la misma sesión, `c5673d1`, aplicó un fix real de caché — se lista aquí para no perder la referencia, pero `27ca543` es el más reciente de los dos según el orden de trabajo documentado en el manual de la Sesión 122.

## Qué funciona

- **Routing y respuesta**: el enrutador central (`config_dominios.py` + lógica asociada) clasifica preguntas por dominio (trading, tecnología, IA, memoria personal, general) y las dirige al agente correspondiente. El golden set de verificación —78 preguntas de referencia, ampliado desde 54 en la propia Sesión 122— midió 84.6% de aprobación al cierre del material disponible, sin regresiones respecto a la corrida anterior (73.1%).
- **Biblioteca RAG**: cerca de mil archivos distintos indexados en ChromaDB entre los dominios de trading, programación, IA/ML y tecnología general, con **606.064 fragmentos de texto (chunks) buscables al cierre de la Sesión 120 (22/08/2026)**, la cifra más reciente confirmada. El conteo total no es estable en el tiempo: llegó a un pico de 1.476.391 chunks a mediados de agosto (Sesión 110, tras reconstruir el sistema de un incidente de corrupción del índice), antes de una limpieza masiva de duplicación acumulada en esa reconstrucción (Sesiones 111-112) que lo bajó a ~430.364, seguida de nuevas incorporaciones de contenido y una segunda limpieza de duplicados (Sesión 119) que lo dejaron en la cifra actual — ver el detalle completo en `/tecnico/arquitectura.md`. Incluye la biblioteca propia del curso de trading (ver `/historia/06_como_aria_aprendio_a_operar.md`).
- **Memoria personal**: migrada de un archivo de texto plano a una base de datos real (Sesión 57). Al cierre de la Sesión 122 tenía 28 datos activos, tras una limpieza que eliminó 41% de contaminación acumulada (duplicados exactos y preguntas técnicas guardadas por error).
- **Caché semántico ("Director Cognitivo")**: reutiliza respuestas ya elaboradas para preguntas parecidas, para no pagar dos veces el costo de una consulta a un modelo externo.
- **Módulo 9 — autonomía, Fase 3**: búsqueda web conectada a casos de uso reales (tipo de cambio, precio de plata, índice de miedo y codicia del mercado). **En período de prueba formal desde el 23 de agosto de 2026** — no cerrado ni presentado como funcionalidad definitiva.
- **Infraestructura de dos máquinas**: "SERVIDOR" (máquina principal) y "PRUEBAS" (máquina secundaria, con GPU propia desde la Sesión 102), con la nomenclatura fija desde la Sesión 101.

## Qué falta o está en curso

- **Divergencia de commits entre SERVIDOR y PRUEBAS**: pendiente de comparación completa con acceso a ambas máquinas — sin resolver al cierre del material disponible.
- **Ruido nuevo en memoria personal**: preguntas sueltas guardadas por error como si fueran datos personales (el filtro de `aprendizaje_auto.py` no distingue bien pregunta de dato real) — detectado en la Sesión 122, no corregido todavía, mismo criterio de prudencia que en la Sesión 121.
- **Plan de separación física ARIA/SabriBot**: conversado y documentado (ver `PLAN_FUTURO_ARIA_SabriBot_22_08_2026.md` en el material fuente, con siete pasos definidos), pero no ejecutado al cierre de la Sesión 122. La idea es migrar ARIA a la máquina de Pruebas y transformar el servidor actual en la máquina dedicada a SabriBot.
- **`dataset_trading.jsonl` desactualizado**: un archivo de preguntas y respuestas pre-armadas sobre el curso de trading que no se sincronizó con el contenido nuevo del vectorstore. Decisión explícita: no se resuelve ahora, se resolverá naturalmente con la separación ARIA/SabriBot.
- **Fase 4 del Módulo 9**: su alcance concreto está pendiente de reinterpretarse a la luz del plan de migración a dos máquinas.

## Descartado explícitamente (no se retoma sin razón nueva)

- **Fine-tuning local como camino de conocimiento** (LoRA/Unsloth): se entrenó y validó un adaptador real (Sesión 70), pero se descartó como estrategia general — el RAG ya existente cubre el objetivo de que ARIA sepa más sobre un tema, y el fine-tuning es la herramienta equivocada para agregar datos nuevos (sirve para tono/estilo, no para conocimiento).
- **"Modo Jefe"** (agentes autónomos tipo Plan-and-Execute): descartado como línea de trabajo.
- **Ejecución de operaciones de trading real desde ARIA**: descartado como límite de diseño, no como pendiente técnico.
- **Agentes autónomos sin las salvaguardas del proyecto**: descartado.
- **Webhooks públicos**: descartados.
- **Subir el repositorio de código a un servicio externo de hosting**: descartado (nota: esta publicación documental es un proyecto distinto, decidido aparte).
- **Automatizar el arranque de ARIA al iniciar Windows**: descartado.
- **Graphiti/Zep como memoria temporal de trading**: descartado.
- **Mapa de liquidaciones de criptomonedas**: investigado con evidencia real, descartado para ARIA — queda documentado como idea válida para SabriBot en el material fuente, no para este sistema.
- **Agenda con recordatorios telefónicos**: descartada.
- **Mecanismos de lectura y ejecución automática de señales de trading de terceros** (por ejemplo, vía captura de pantalla y OCR de un canal o grupo ajeno): excluidos de este repositorio por decisión ética, no solo técnica. Aunque hayan existido como experimento dentro del ecosistema más amplio de SabriBot, no se documentan ni se explican acá — el objetivo de este repositorio es enseñar ingeniería de un asistente personal, no ofrecer una receta para automatizar decisiones de trading basadas en señales de otra persona sin el criterio para evaluar el riesgo real.
- **Sincronización del filtro de detección de `aprendizaje_auto.py`**: descartada por ahora, sin razón nueva para retomarla.

## Límite de seguridad vigente

ARIA no ejecuta operaciones de trading reales. No tiene acceso de escritura a ninguna cuenta de mercado. Cualquier decisión de trading la toma Alejandro Ubios, no el sistema.

---

*Nota editorial: los datos numéricos de este documento (golden set, memoria personal, biblioteca indexada, commits) están tomados directamente del manual de cierre de la Sesión 122 y de manuales de sesiones inmediatamente anteriores, con cita textual verificada. La discrepancia entre los commits `c5673d1` y `27ca543` como "el último" se deja señalada de forma transparente en vez de resuelta a criterio propio — a confirmar por Alejandro si hace falta mayor precisión.*
