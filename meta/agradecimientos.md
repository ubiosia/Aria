# Agradecimientos

## Sabri Conessa

> Sabri Conessa confirmó directamente el uso de su nombre real en este documento antes de la publicación del repositorio.

Buena parte de lo que ARIA sabe sobre trading viene de los cursos gratuitos de Sabri Conessa, un trader que opera en vivo con su propio dinero — una condición que Alejandro valora en particular, porque no todo el que enseña a operar también lo demuestra en público. Su forma de explicar, clara y honesta, es la base sobre la que se construyó el "Curso Sabri" documentado en [`/historia/06_como_aria_aprendio_a_operar.md`](../historia/06_como_aria_aprendio_a_operar.md).

Sabri Conessa no participó del proyecto ARIA de ninguna forma, no lo asesoró, y no tiene ninguna relación con sus decisiones técnicas ni con los resultados de trading que Alejandro obtenga usando lo aprendido en sus cursos. Cualquier resultado, bueno o malo, es responsabilidad exclusiva de Alejandro.

## Claude

El compañero de trabajo constante del proyecto, de principio a fin, fue Claude (Anthropic) — no un consejo rotativo de asistentes en igualdad de condiciones. La enorme mayoría de las sesiones de trabajo documentadas en este repositorio se hicieron en conversación directa con Claude: diagnóstico de bugs, diseño de arquitectura, redacción de código, y también la redacción de este mismo repositorio.

## Consultas puntuales

Otros modelos de inteligencia artificial aportaron revisión cruzada y una segunda opinión en momentos puntuales del proyecto — no como compañeros de trabajo constantes, sino como consultas específicas: Qwen, ChatGPT, Grok, DeepSeek, y Kimi.

Kimi, en particular, tuvo una participación repetida y real en la revisión de varios módulos del sistema de memoria: revisó el diseño del módulo de preferencias, aportó la evaluación que dio origen a la unificación de umbrales del caché semántico, y aprobó —con condiciones— el diseño de consolidación automática de conocimiento del Módulo 6, incluyendo un ajuste real sobre el límite de lo que se inyecta en el contexto de cada respuesta.

## Un límite de responsabilidad

Este proyecto no tuvo ningún socio humano. Es un trabajo individual de Alejandro Ubios, con Claude como compañero de trabajo constante y consultas puntuales a otras inteligencias artificiales para revisión cruzada de ideas — no un equipo, ni una empresa, ni un proyecto colaborativo con otras personas.

---

*Nota editorial: la participación de Kimi está documentada con cita textual en varios manuales de sesión de julio de 2026 (módulo de preferencias, Módulo 5, Módulo 6). No se pudo verificar con cita textual una versión anterior de este agradecimiento que atribuía a Kimi el hallazgo de una vulnerabilidad de seguridad o inyección específicamente durante la revisión del Módulo 9 — lo documentado y verificado es su participación real en el Módulo 6 (memoria avanzada), incluyendo un ajuste sobre el límite de inyección de contexto en `obtener_contexto()`, que es lo que se describe aquí en su lugar.*
