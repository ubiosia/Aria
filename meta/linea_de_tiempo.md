# Línea de tiempo

Cronología corta de los hitos principales del proyecto, mayo-agosto de 2026. Para el detalle narrativo de cada hito, ver los capítulos correspondientes en [`/historia/`](../historia/00_indice.md).

| Fecha | Sesión | Hito |
|---|---|---|
| 25/05/2026 | 1 | Instalación inicial de ARIA sobre WSL2 (Windows 11 + Ubuntu). Hardware: Intel i9-10900, RTX 3080 10GB, 48GB RAM. |
| 31/05/2026 | 17 | Adopción del hotword de voz "SOFIA", tras varios intentos fallidos por limitaciones reales de reconocimiento de voz. |
| 01/06/2026 | 18 | Desaparición del disco virtual (`ext4.vhdx`) por una herramienta de limpieza de disco, y recuperación desde un backup manual. Origen de la disciplina de backups en tres capas. Ubuntu nativo (dual boot) evaluado y descartado. |
| ~15-17/06/2026 | 33 | Primera mención documentada de SabriBot como proyecto de trading separado, en la misma máquina que ARIA. |
| 23-24/06/2026 | 34 | Migración de disco principal. Intento fallido de segunda GPU en otra máquina. Primer bug del "precio del oro" diagnosticado (tres capas del sistema compitiendo por la misma palabra), con el término "route shadowing" acuñado tras consultar a cinco colegas de IA. |
| 24/06/2026 | 35 | Backups migran de Disco C a Disco D. |
| 04/07/2026 | 43 | Reaparición del bug del precio del oro por una causa distinta (un atajo de respuesta rápida sin las mismas excepciones). |
| 05/07/2026 | 44 | Primer archivo de pruebas automatizadas escrito antes que el código que debía validar — cambio de metodología. |
| 08/07/2026 | 49 | Medición real de precisión de enrutamiento: 22% sobre ~890 preguntas reales — hallazgo que instaló las pruebas automatizadas como práctica fija. |
| 13/07/2026 | 57 | Migración de la memoria personal de archivo de texto a base de datos real. El proyecto pasa internamente de "V7" a "V8". |
| 13-18/07/2026 | 56-58 | Bug del "dónde vivo" diagnosticado en tres pasadas hasta encontrar la causa real: un atajo que interceptaba la pregunta antes del enrutamiento general. |
| ~20/07/2026 | 70 | Entrenamiento y validación de un adaptador LoRA propio sobre el contenido del curso de trading (probado, luego descartado como estrategia). |
| 24/07/2026 | — | Alejandro completa el cuestionario de memoria y olvido de 14 preguntas, que define el criterio de qué debe recordar ARIA. |
| 28-29/07/2026 | 86-87 | Cuelgues de WSL2 por límite de memoria; ajuste de `.wslconfig`; RAM física sube de 32GB a 48GB. |
| ~09/08/2026 | 101 | Puesta en marcha de la segunda máquina ("PRUEBAS"), separada de la máquina principal ("SERVIDOR"). |
| ~13/08/2026 | 103-104 | Descarte explícito del fine-tuning local (LoRA/Unsloth) como camino para agregar conocimiento nuevo — el RAG existente cubre el objetivo. |
| 15/08/2026 | 110 | Incidente de corrupción del índice de ChromaDB, resuelto con recuperación completa. El vectorstore, ya reconstruido, llega a un pico de 1.476.391 chunks — cifra inflada por duplicación acumulada durante la propia reconstrucción, no solo contenido nuevo. |
| 16/08/2026 | 111-112 | Limpieza masiva y sistemática de la duplicación acumulada en el incidente anterior: el vectorstore pasa de ~1,4 millones a ~430.364 chunks, verificado con múltiples métodos. |
| 19-20/08/2026 | 116 | Ampliación grande de la biblioteca de trading: 173 libros nuevos indexados (vectorstore a 608.963 chunks). Primer uso real del "golden set" de preguntas de referencia. |
| 21/08/2026 | 119 | Resolución completa de un bug de enrutamiento heredado (pérdida de contexto en preguntas de seguimiento). Segunda limpieza de duplicados del vectorstore, en dos rondas (88.021 + 26.844 chunks eliminados): 608.963 → 494.098. |
| 22/08/2026 | 120 | 8 libros nuevos indexados (vectorstore a 606.064 chunks, la cifra más reciente confirmada). Primer costo real de una prueba de calidad cuantificado ($0.002 USD por 200 rondas). |
| 23/08/2026 | 121 | Módulo 9 (autonomía), Fase 3: conectados casos de uso reales de búsqueda web. Arranca el período de prueba formal de dos semanas. Documentado el plan de separación física ARIA/SabriBot. |
| 23-24/08/2026 | 122 | Golden set ampliado a 78 preguntas (84.6% de aprobación). Memoria personal limpiada (57→28 datos activos). Causa raíz de un cuelgue real del sistema encontrada y corregida. Cierre del material disponible al momento de preparar este repositorio. |

---

*Nota editorial: las fechas y números de sesión de esta tabla están tomados de la tabla interna de continuidad verificada durante la redacción de los capítulos de `/historia/` y de los manuales de sesión correspondientes, con cita textual confirmada en cada caso. Las Sesiones 5 a 19 (salvo la 17 y la 18, recuperadas) y la Sesión 27 no están representadas de forma independiente por no haberse conservado o no haber estado disponibles como documentos propios.*
